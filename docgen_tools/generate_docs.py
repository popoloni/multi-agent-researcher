#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
import logging
import json
import sys
import boto3
import time
from anthropic import Anthropic

### Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('doc_generation.log')
    ]
)

### load config
def load_config(config_file: str) -> dict:
    with open(config_file, 'r') as f:
        return json.load(f)

### clean code functions
def clean_source_code(content: str, language: str) -> str:
    if language == "COBOL":
        return clean_cobol(content.splitlines())
        #return content
    elif language == "PL/1":
        return clean_pl1(content.splitlines()) 
    elif language == "JAVA" or language == "EGL" or language == "CSHARP" or language == "JS" or language == "JSP":
        return clean_java(content)
    elif language == "PL/SQL":
        return clean_plsql(content)
    elif language == 'XML':
        return clean_xml(content)
    return content

def clean_cobol(lines: list) -> str:
    holder = []
    output = []
    division = ''
    
    for row in lines:
        row = row[6:72].rstrip()
        if row.strip() == "" or row.strip() == 'EJECT':
            continue
            
        if 'IDENTIFICATION DIVISION' in row:
            division = 'IDENTIFICATION DIVISION'
        elif 'ENVIRONMENT DIVISION' in row:
            division = 'ENVIRONMENT DIVISION'
        elif 'DATA DIVISION' in row:
            division = 'DATA DIVISION'
        elif 'PROCEDURE DIVISION' in row:
            division = 'PROCEDURE DIVISION'

        holder.append(row if len(holder) == 0 else row.strip())

        if row[-1] == ".":
            line = " ".join(holder)
            line = re.sub(r'(?<!^)\s+', ' ', line)
            output.append(line)
            holder = []

    return "\n".join(output)

def clean_pl1(lines: list) -> str:
    holder = []
    output = []
    in_comment = False
    
    for row in lines:
        row = row.rstrip().strip()
        if row == "":
            continue
            
        # if row.startswith('/*'):
        #     in_comment = True
        #     continue
            
        #if not in_comment:
        holder.append(row if len(holder) == 0 else row.strip())

        if row.strip().endswith(';') or row.strip().endswith('*/'):
            # if not in_comment:
            line = " ".join(holder)
            line = re.sub(r'(?<!^)\s+', ' ', line)
            output.append(line)
            #
            holder = []
            # in_comment = False

    return "\n".join(output)

def clean_java(content: str) -> str:
    #content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    #content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def clean_plsql(content: str) -> str:
    #content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
    #content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def clean_xml(xml_code):
    xml_code = re.sub(r">\s+<", "><", xml_code)
    return xml_code.strip()

def create_source_prompt(content: str, filename: str, package_name: str, language: str, config: dict) -> str:
    return config["general_source_prompt"].format(
        language=language.lower(),
        filename=filename,
        package_name=package_name,
        content=content
    )

def create_summary_prompt(folder_path: str, md_contents: list, config: dict) -> str:
    return config["general_summary_prompt"].format(
        folder_name=os.path.basename(folder_path),
        md_contents=md_contents
    )

def create_hierarchical_summary_prompt(folder_path: str, readme_contents: list, config: dict) -> str:
    return config["general_hierarchical_summary_prompt"].format(
        folder_name=os.path.basename(folder_path),
        readme_contents=readme_contents
    )

def create_error_response(prompt: str) -> str:
    title = "# " + prompt.split('\n')[6]
    package = "## Package\n" + prompt.split('\n')[8]
    template = """
## Overview
[Error generating documentation - Using template]
Documentation generation failed."""
    
    return title + "\n\n" + package + template

def call_llm(prompt: str, config: dict) -> str:
    if config["llm_provider"] == "anthropic":
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        anthropic = Anthropic(api_key=api_key)
        
        try:
            response = anthropic.messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                system=config["general_system_prompt"],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
            
        except Exception as e:
            logging.error(f"Error calling Anthropic API: {str(e)}")
            return create_error_response(prompt)
            
    elif config["llm_provider"] == "bedrock":
        try:
            session = boto3.Session(profile_name=config["aws_profile"])
            bedrock = session.client(
                service_name='bedrock-runtime',
                region_name=config["aws_region"]
            )
            
            body = {
                "anthropic_version": config["anthropic_version"],
                "max_tokens": config["max_tokens"],
                "temperature": config["temperature"],
                "top_p": config["top_p"],
                "top_k": config["top_k"],
                "stop_sequences": config["stop_sequences"],
                "system": config["general_system_prompt"],
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = bedrock.invoke_model(
                body=json.dumps(body),
                modelId=config["model"],
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logging.error(f"Error calling Bedrock API: {str(e)}")
            return create_error_response(prompt)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {config['llm_provider']}")

def generate_documentation(source_file: str, docs_dir: str, config: dict, only_md_name: bool = False) -> str:
    try:
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        filename = os.path.basename(source_file)
        extension = os.path.splitext(filename)[1].lower()
        
        if extension == '.egl':
            language = 'EGL'
        elif extension == '.cbl' or extension == '.cob' or extension == '.cpy' or extension == '.cobol':
            language = 'COBOL'
        elif extension == '.pli':
            language = 'PL/1'
        elif extension == '.java':
            language = 'JAVA'
        elif extension == '.sql' or extension == '.ddl' or extension == '.src':
            language = 'PL/SQL'
        elif extension == '.xml':
            language = 'XML'
        elif extension == '.cs':
            language = 'CSHARP'
        elif extension == '.txt':
            language = 'OTHER'
        elif extension == '.jsp':
            language = 'JSP'
        elif extension == '.js':
            language = 'JS'
        else:
            language = 'OTHER'
            
        
        if only_md_name == False:
            logging.info(f"Processing {source_file} ({language})")
        
        if '/src/' in source_file:
            package_name = source_file.split('/src/')[1].split('/')[0]
        else:
            package_name = 'unknown'
        
        if only_md_name == False:
            cleaned_content = clean_source_code(content, language)
            prompt = create_source_prompt(cleaned_content, filename, package_name, language, config)
            documentation = call_llm(prompt, config)
        
        # Create output directory structure
        rel_path = os.path.relpath(source_file, config["src_dir"])
        output_path = os.path.join(docs_dir, os.path.dirname(rel_path))
        os.makedirs(output_path, exist_ok=True)
        
        # Generate markdown filename
        md_filename = os.path.splitext(filename)[0] + '.md'
        md_file = os.path.join(output_path, md_filename)
        
        if only_md_name == False:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(documentation)
        
        return md_file
        
    except Exception as e:
        logging.error(f"Error processing {source_file}: {str(e)}")
        return None

def create_index(docs_dir: str):
    index_content = "# System Documentation\n\n"
    
    for root, dirs, files in os.walk(docs_dir):
        if files:
            level = root.replace(docs_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            index_content += f"{indent}- {os.path.basename(root)}/\n"
            
            subindent = ' ' * 2 * (level + 1)
            for file in sorted(files):
                if file.endswith('.md'):
                    index_content += f"{subindent}- [{file}]({os.path.relpath(os.path.join(root, file), docs_dir).replace(os.sep, '/')})\n"
    
    with open(os.path.join(docs_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write(index_content)

def generate_folder_summary(folder_path: str, config: dict, retry_count: int = 0) -> tuple[str, bool]:
    logging.info(f"Generating summary for folder: {folder_path}")
    
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md') and f != 'README.md']
    
    if not md_files:
        logging.info(f"No markdown files found in {folder_path}")
        return None, False
    
    md_contents = []
    for md_file in sorted(md_files):
        with open(os.path.join(folder_path, md_file), 'r', encoding='utf-8') as f:
            md_contents.append(f"## {md_file}\n{f.read()}")
    
    prompt = create_summary_prompt(folder_path, "\n".join(md_contents), config)
    summary = call_llm(prompt, config)
    
    if '[Error generating documentation - Using template]' in summary:
        return None, False
    return summary, True

def generate_recursive_summaries(docs_dir: str, config: dict, max_retries: int = 3):
    retry_folders = []
    processed_folders = []
    
    for root, dirs, files in os.walk(docs_dir, topdown=False):
        readme_path = os.path.join(root, 'README.md')
        
        if files or dirs:
            summary, success = generate_folder_summary(root, config)
            if success:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                processed_folders.append(root)
            else:
                retry_folders.append(root)

    retry_count = 0
    while retry_folders and retry_count < max_retries:
        retry_count += 1
        logging.info(f"\nRetry attempt {retry_count} for {len(retry_folders)} folders...")
        
        still_failed = []
        for folder_path in retry_folders:
            summary, success = generate_folder_summary(folder_path, config, retry_count)
            if success:
                readme_path = os.path.join(folder_path, 'README.md')
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                processed_folders.append(folder_path)
            else:
                still_failed.append(folder_path)
        
        retry_folders = still_failed

    if retry_folders:
        logging.error(f"\nFailed to generate README.md for {len(retry_folders)} folders after {max_retries} attempts:")
        for folder in retry_folders:
            logging.error(f"  - {folder}")
    
    return processed_folders, retry_folders

def generate_hierarchical_summaries(docs_dir: str, config: dict, max_retries: int = 3):
    """Generate hierarchical README.md files from bottom to top"""
    # First, collect all folders with README.md files
    folders_with_readme = []
    for root, dirs, files in os.walk(docs_dir):
        if 'README.md' in files or dirs:
            folders_with_readme.append(root)
    
    # Sort folders by depth (deepest first)
    folders_with_readme.sort(key=lambda x: get_folder_depth(x, docs_dir), reverse=True)
    
    processed_folders = []
    failed_folders = []
    
    # Process each folder
    for folder_path in folders_with_readme:
        logging.info(f"\nProcessing hierarchical summary for: {folder_path}")
        
        # Collect README contents from subfolders
        subfolder_readmes = []
        has_subfolders = False
        
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                has_subfolders = True
                readme_path = os.path.join(item_path, 'README.md')
                if os.path.exists(readme_path):
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        subfolder_readmes.append(f"## {item}\n{f.read()}")
        
        # Only process folders that have subfolders
        if has_subfolders:
            prompt = create_hierarchical_summary_prompt(folder_path, "\n".join(subfolder_readmes), config)
            summary = call_llm(prompt, config)
            
            if '[Error generating documentation - Using template]' not in summary:
                readme_path = os.path.join(folder_path, 'README.md')
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                processed_folders.append(folder_path)
            else:
                failed_folders.append(folder_path)
        else:
            logging.info(f"Skipping {folder_path} - no subfolders")
    
    return processed_folders, failed_folders


def check_md_needs_regeneration(md_file: str) -> bool:
    """Check if a markdown file needs to be regenerated"""
    print(md_file)
    if not os.path.exists(md_file):
        return True
        
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '[Error generating documentation - Using template]' in content:
                return True
    except Exception as e:
        logging.error(f"Error reading {md_file}: {str(e)}")
        return True
    
    return False

def check_readme_needs_regeneration(readme_path: str, hierarchical: bool = False) -> bool:
    """Check if a README.md file needs to be regenerated"""
    if not os.path.exists(readme_path):
        return True
        
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '[Error generating documentation - Using template]' in content:
                return True
    except Exception as e:
        logging.error(f"Error reading {readme_path}: {str(e)}")
        return True
    
    return False

def get_folder_depth(path: str, base_path: str) -> int:
    """Calculate the depth of a folder relative to the base path"""
    rel_path = os.path.relpath(path, base_path)
    return len(rel_path.split(os.sep))

def main():
    try:
        config = load_config("config.json")
        docs_dir = config.get("docs_dir", "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        processed_files = []
        failed_files = []
        retry_files = []
        
        # Process all source files
        for root, dirs, files in os.walk(config["src_dir"]):
            for file in files:
                source_file = os.path.join(root, file)
                extension = os.path.splitext(file)[1].lower()
                
                if extension in ['.egl', '.cbl', '.cob', '.cpy', '.cobol', '.pli', '.java', '.sql', '.ddl', '.src', '.xml', '.cs', '.txt', '.jsp', '.js']:
                    md_file = generate_documentation(source_file, docs_dir, config)
                    if md_file:
                        if check_md_needs_regeneration(md_file):
                            retry_files.append(source_file)
                        else:
                            processed_files.append(source_file)
                    else:
                        failed_files.append(source_file)
        
        # Retry failed files
        if retry_files:
            logging.info(f"\nRetrying {len(retry_files)} files...")
            for source_file in retry_files:
                md_file = generate_documentation(source_file, docs_dir, config)
                if md_file and not check_md_needs_regeneration(md_file):
                    processed_files.append(source_file)
                else:
                    failed_files.append(source_file)
        
        # Generate basic folder summaries 
        logging.info("\nGenerating folder summaries...")
        processed_folders, failed_folders = generate_recursive_summaries(docs_dir, config)
        
        # Generate hierarchical summaries
        logging.info("\nGenerating hierarchical documentation summaries...")
        hier_processed, hier_failed = generate_hierarchical_summaries(docs_dir, config)
        
        # Create index
        create_index(docs_dir)
        
        logging.info(f"\nDocumentation generation complete:")
        logging.info(f"- Processed {len(processed_files)} files")
        logging.info(f"- Generated {len(processed_folders)} basic README.md summaries")
        logging.info(f"- Failed to process {len(failed_files)} files")
        logging.info(f"- Failed to generate {len(failed_folders)} basic README.md files")
        logging.info(f"- Failed to generate {len(hier_failed)} hierarchical README.md files")
        logging.info(f"- Documentation available in {docs_dir}/")
        logging.info(f"- Index available at {docs_dir}/index.md")
        
    except Exception as e:
        logging.error(f"Error during documentation generation: {str(e)}")
        raise

if __name__ == "__main__":
    main()
