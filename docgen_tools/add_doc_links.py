#!/usr/bin/env python3
import os
import re
import logging
import sys
from pathlib import Path
import shutil
from typing import Dict, List, Set, Tuple
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('doc_linking.log')
    ]
)

### load config
def load_config(config_file: str) -> dict:
    with open(config_file, 'r') as f:
        return json.load(f)

class FolderStructure:
    def __init__(self, path: str):
        self.path = path
        self.md_files = []
        self.subfolders = []
        self.has_meaningful_content = False
        self.needs_readme = False
        self.parent_readme = None
        self.child_readmes = []
        self.meaningful_subfolder_count = 0

def create_relative_link(from_path: str, to_path: str) -> str:
    from_path = Path(from_path)
    to_path = Path(to_path)
    try:
        relative_path = os.path.relpath(to_path, from_path.parent)
        return relative_path.replace('\\', '/').replace(' ', '%20')
    except ValueError:
        logging.error(f"Could not create relative link from {from_path} to {to_path}")
        return str(to_path)

def get_folder_path_display(folder_path: str, docs_dir: str) -> str:
    rel_path = os.path.relpath(folder_path, docs_dir)
    if rel_path == '.':
        return 'root'
    return rel_path.replace(os.sep, ' > ')

def collect_markdown_filenames(folder_info: Dict[str, FolderStructure]) -> Dict[str, str]:
    """Collect all markdown filenames and their full paths."""
    md_files_map = {}
    for folder_path, info in folder_info.items():
        for md_file in info.md_files:
            # Store filename without extension as key, full path as value
            name = os.path.splitext(os.path.basename(md_file))[0]
            md_files_map[name] = md_file
    return md_files_map

def replace_references_with_links(content: str, current_file: str, md_files_map: Dict[str, str]) -> str:
    """Replace markdown file references with proper relative links, skipping existing links."""
    # First, collect all text that's already part of a link
    existing_links = set()
    link_pattern = r'\[([^\]]+)\]\([^)]+\)'
    for match in re.finditer(link_pattern, content):
        existing_links.add(match.group(1))

    # Sort filenames by length (descending) to handle longer names first
    filenames = sorted(md_files_map.keys(), key=len, reverse=True)
    
    # Create pattern to match whole words only
    pattern = r'\b(' + '|'.join(re.escape(name) for name in filenames) + r')\b'
    
    def replace_match(match):
        name = match.group(0)
        # Skip if this text is already part of a link
        if name in existing_links:
            return name
        
        target_file = md_files_map[name]
        # Don't create link if it's referencing itself
        if os.path.abspath(target_file) == os.path.abspath(current_file):
            return name
        relative_link = create_relative_link(current_file, target_file)
        return f'[{name}]({relative_link})'
    
    # Split content into chunks: inside code blocks and outside code blocks
    code_blocks = re.split(r'(```[^`]*```)', content)
    
    # Process only the non-code blocks
    for i in range(0, len(code_blocks), 2):
        code_blocks[i] = re.sub(pattern, replace_match, code_blocks[i])
    
    return ''.join(code_blocks)

def analyze_folder_structure(docs_dir: str) -> Dict[str, FolderStructure]:
    folder_info = {}
    
    # First pass: collect basic information
    for root, dirs, files in os.walk(docs_dir, topdown=False):
        folder = FolderStructure(root)
        
        md_files = [f for f in files if f.endswith('.md') and f != 'README.md']
        has_readme = 'README.md' in files
        
        folder.md_files = [os.path.join(root, f) for f in md_files]
        if md_files or has_readme:
            folder.has_meaningful_content = True
        
        # Store all subfolders, not just meaningful ones
        folder.subfolders = [os.path.join(root, dir_name) for dir_name in dirs]
        folder.meaningful_subfolder_count = len(folder.subfolders)
        
        # Determine if folder needs README
        folder.needs_readme = (
            root == docs_dir or
            has_readme or
            folder.meaningful_subfolder_count >= 1 or
            bool(folder.md_files)
        )
        
        folder_info[root] = folder
    
    # Second pass: establish nearest README relationships
    for root, folder in folder_info.items():
        if folder.needs_readme:
            # Find nearest parent README
            current_path = os.path.dirname(root)
            while current_path and current_path != os.path.dirname(docs_dir):
                if (current_path in folder_info and 
                    folder_info[current_path].needs_readme and 
                    os.path.exists(os.path.join(current_path, 'README.md'))):
                    folder.parent_readme = current_path
                    break
                current_path = os.path.dirname(current_path)
            
            # Find nearest child READMEs in each subfolder branch
            def find_nearest_child_readme(start_path):
                if not os.path.exists(start_path):
                    return None
                
                # Check current folder
                if os.path.exists(os.path.join(start_path, 'README.md')):
                    return start_path
                
                # Check immediate subfolders
                for item in os.listdir(start_path):
                    item_path = os.path.join(start_path, item)
                    if os.path.isdir(item_path):
                        result = find_nearest_child_readme(item_path)
                        if result:
                            return result
                
                return None
            
            # Check each subfolder branch
            for subfolder in folder.subfolders:
                nearest_child = find_nearest_child_readme(subfolder)
                if nearest_child and nearest_child not in folder.child_readmes:
                    folder.child_readmes.append(nearest_child)
    
    return folder_info

def update_readme_file(folder_path: str, folder_info: FolderStructure, docs_dir: str, md_files_map: Dict[str, str]):
    readme_path = os.path.join(folder_path, 'README.md')
    try:
        if not os.path.exists(readme_path):
            content = f"# {os.path.basename(folder_path)} Documentation\n\n"
        else:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Replace references with links
        content = replace_references_with_links(content, readme_path, md_files_map)
        
        navigation = "## Navigation\n\n"
        has_navigation = False
        
        # Add up link to first meaningful parent README
        if folder_info.parent_readme:
            parent_readme = os.path.join(folder_info.parent_readme, 'README.md')
            parent_link = create_relative_link(readme_path, parent_readme)
            parent_path = get_folder_path_display(folder_info.parent_readme, docs_dir)
            navigation += f"↑ Up: [{parent_path}]({parent_link})\n\n"
            has_navigation = True
        
        # Add down links to first meaningful child READMEs
        if folder_info.child_readmes:
            navigation += "### Subsections\n\n"
            for child in sorted(folder_info.child_readmes):
                child_readme = os.path.join(child, 'README.md')
                child_link = create_relative_link(readme_path, child_readme)
                child_path = get_folder_path_display(child, docs_dir)
                navigation += f"↓ [{child_path}]({child_link})\n\n"
            navigation += "\n"
            has_navigation = True
        
        # Add links to markdown files in this folder
        if folder_info.md_files:
            navigation += "### Documentation Files\n\n"
            for md_file in sorted(folder_info.md_files):
                file_link = create_relative_link(readme_path, md_file)
                file_name = os.path.splitext(os.path.basename(md_file))[0]
                navigation += f"- [{file_name}]({file_link})\n"
            navigation += "\n"
            has_navigation = True
        
        if has_navigation:
            if not content.startswith("## Navigation"):
                content = navigation + "\n---\n\n" + content
            else:
                content = navigation + "\n---\n\n" + content.split("---\n\n", 1)[1]
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Error updating README in {folder_path}: {str(e)}")

def update_regular_md_file(md_file: str, readme_path: str, md_files_map: Dict[str, str]):
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove existing navigation section if present
        if "## Navigation" in content:
            content = content.split("---\n\n", 1)[1] if "---\n\n" in content else content
        
        # Replace references with links
        content = replace_references_with_links(content, md_file, md_files_map)
        
        # Create new navigation section
        navigation = "## Navigation\n\n"
        readme_link = create_relative_link(md_file, readme_path)
        folder_name = os.path.basename(os.path.dirname(md_file))
        navigation += f"↑ Folder Documentation: [{folder_name}]({readme_link})\n"
        
        # Combine navigation with content
        content = f"{navigation}\n---\n\n{content}"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Error updating {md_file}: {str(e)}")

def process_documentation(docs_dir: str) -> Tuple[int, int, int]:
    folder_info = analyze_folder_structure(docs_dir)
    
    # Collect all markdown filenames
    md_files_map = collect_markdown_filenames(folder_info)
    
    readme_count = 0
    md_count = 0
    removed_count = 0
    
    # Remove unnecessary README files
    for folder_path, info in folder_info.items():
        readme_path = os.path.join(folder_path, 'README.md')
        
        if os.path.exists(readme_path):
            if not info.needs_readme and info.meaningful_subfolder_count < 2:
                try:
                    os.remove(readme_path)
                    removed_count += 1
                    logging.info(f"Removed unnecessary README: {readme_path}")
                except Exception as e:
                    logging.error(f"Error removing README {readme_path}: {str(e)}")
    
    # Update README files
    for folder_path, info in folder_info.items():
        if info.needs_readme:
            update_readme_file(folder_path, info, docs_dir, md_files_map)
            readme_count += 1
            
            # Update regular markdown files in this folder
            if info.md_files:
                readme_path = os.path.join(folder_path, 'README.md')
                for md_file in info.md_files:
                    update_regular_md_file(md_file, readme_path, md_files_map)
                    md_count += 1
    
    return readme_count, md_count, removed_count

def main():
    try:
        config = load_config("config.json")
        docs_dir = config.get("docs_dir", "docs")
        if not os.path.exists(docs_dir):
            raise ValueError(f"Documentation directory '{docs_dir}' not found")
        
        logging.info("Starting documentation linking process...")
        readme_count, md_count, removed_count = process_documentation(docs_dir)
        
        logging.info("\nDocumentation linking complete:")
        logging.info(f"- Updated {readme_count} README files")
        logging.info(f"- Updated {md_count} markdown files")
        logging.info(f"- Removed {removed_count} unnecessary README files")
        logging.info(f"- Documentation available in {docs_dir}/")
        
    except Exception as e:
        logging.error(f"Error during documentation linking: {str(e)}")
        raise

if __name__ == "__main__":
    main()
