import os
import re
import time
import requests
import json

import subprocess
from pathlib import Path
from markdown import markdown
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import shutil
import uuid
import logging
import base64
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from PIL import Image

# Configure file logging with detailed output
file_handler = logging.FileHandler('diagram_conversion.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure console logging with minimal output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('Processing: %(message)s'))

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

### load config
def load_config(config_file: str) -> dict:
    with open(config_file, 'r') as f:
        return json.load(f)

class MarkdownToWordConverter:
    def __init__(self, root_folder, output_file):
        self.root_folder = Path(root_folder)
        self.output_file = output_file
        self.temp_dir = Path('temp_conversion')
        self.image_dir = self.temp_dir / 'images'
        self.processed_files = set()
        
        # Configure robust session
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def setup_temp_directories(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True)
        self.image_dir.mkdir(parents=True)

    def validate_mermaid_syntax(self, code):
        """Basic validation of mermaid syntax"""
        if not isinstance(code, str) or not code.strip():
            return ""
            
        common_patterns = {
            'graph': r'^graph\s+(TD|LR|RL|BT)',
            'sequence': r'^sequenceDiagram',
            'class': r'^classDiagram',
            'state': r'^stateDiagram-v2',
            'er': r'^erDiagram',
            'gantt': r'^gantt',
            'pie': r'^pie',
            'flow': r'^flowchart\s+(TD|LR|RL|BT)',
        }
        
        # Check if code matches any known diagram type
        code = code.strip()
        for pattern in common_patterns.values():
            if re.match(pattern, code):
                return code
        
        # If no match, try to determine the type and add appropriate header
        if '-->' in code or '--|>' in code:
            return 'graph TD\n' + code
        elif ':' in code and '->' in code:
            return 'sequenceDiagram\n' + code
        elif 'class' in code.lower():
            return 'classDiagram\n' + code
        
        # Default to graph TD if no specific type is detected
        return 'graph TD\n' + code

    def convert_mermaid_to_image(self, mermaid_code):
        """Convert mermaid diagram to image using Mermaid Ink API with repair attempts"""
        if not isinstance(mermaid_code, str) or not mermaid_code.strip():
            logger.error("Invalid mermaid code received")
            return None

        def try_repair_diagram(code):
            if not isinstance(code, str):
                return ""
            # Common syntax repairs
            repairs = [
                # Fix inheritance arrows
                (r'--|>', '-->'),
                # Fix relationship arrows
                (r'-\+-', '--'),
                # Fix invalid characters
                (r'[^\w\s\-><:\[\]\(\){}]', '_'),
                # Fix spacing issues
                (r'\s+', ' '),
                # Fix common class diagram syntax
                (r'(\w+)\s+([<>])\s+(\w+)', r'\1\2\3'),
                # Fix relationship syntax
                (r'(\w+)\s+([-\.]+)\s+(\w+)', r'\1-->\3'),
            ]
            
            repaired = code
            for pattern, replacement in repairs:
                if callable(pattern):
                    repaired = pattern(repaired)
                else:
                    repaired = re.sub(pattern, replacement, repaired)
            return repaired

        def try_convert(code, attempt=0, max_attempts=3):
            try:
                if not code or not isinstance(code, str):
                    return None, "Invalid code"
                    
                # Clean up the mermaid code
                code = code.strip()
                
                # Encode the Mermaid code in base64
                encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
                
                # Create the Mermaid Ink URL
                url = f"https://mermaid.ink/img/{encoded_code}"
                
                # Download the image with timeout
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    image_filename = f"diagram_{uuid.uuid4()}.png"
                    image_path = self.image_dir / image_filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    
                    return image_path, None
                
                return None, f"Status {response.status_code}"
                
            except requests.Timeout:
                if attempt < max_attempts:
                    time.sleep(1)  # Wait before retry
                    return try_convert(code, attempt + 1, max_attempts)
                return None, "Timeout after multiple attempts"
                
            except Exception as e:
                return None, str(e)

        try:
            # Log the incoming code
            logger.debug(f"Converting diagram:\n{mermaid_code}")

            # First attempt with original code
            image_path, error = try_convert(mermaid_code)
            if image_path:
                return image_path

            # Try with repaired code
            repaired_code = try_repair_diagram(mermaid_code)
            if repaired_code != mermaid_code:
                logger.info("Attempting with repaired diagram syntax...")
                image_path, error = try_convert(repaired_code)
                if image_path:
                    return image_path

            # If both attempts failed, try with simplified version
            simplified_code = f"""graph TD
        A["{mermaid_code[:50]}..."]
        """
            logger.info("Attempting with simplified diagram...")
            image_path, error = try_convert(simplified_code)
            if image_path:
                return image_path

            # Log the original and repaired code for debugging
            logger.error(f"Failed to convert diagram. Error: {error}")
            logger.debug("Original code:\n%s", mermaid_code)
            logger.debug("Repaired code:\n%s", repaired_code)
            
            return None

        except Exception as e:
            logger.error(f"Failed to convert mermaid diagram: {e}")
            return None

    def process_markdown_content(self, content, file_path):
        """Process markdown content with enhanced diagram handling"""
        # Remove navigation sections
        content = re.sub(
            r'## Navigation.*?---\s*\n',
            '',
            content,
            flags=re.DOTALL
        )

        def replace_mermaid(match):
            try:
                mermaid_code = match.group(1)
                if not mermaid_code.strip():
                    return ''
                
                # Validate and potentially fix syntax
                validated_code = self.validate_mermaid_syntax(mermaid_code)
                
                # Log the code for debugging
                logger.debug(f"Processing diagram:\nOriginal:\n{mermaid_code}\nValidated:\n{validated_code}")
                
                image_path = self.convert_mermaid_to_image(validated_code)
                if image_path:
                    return f"![Diagram]({image_path})"
                
                # If conversion failed, return original code as code block
                return f"```\n{mermaid_code}\n```"
            except Exception as e:
                logger.error(f"Error in replace_mermaid: {e}")
                return f"```\n{match.group(1)}\n```"

        # Convert mermaid blocks
        content = re.sub(
            r'```mermaid\n(.*?)\n```',
            replace_mermaid,
            content,
            flags=re.DOTALL
        )

        # Update relative links
        def replace_links(match):
            link_text = match.group(1)
            link_path = match.group(2)
            
            if link_path.endswith('.md'):
                target_path = (file_path.parent / link_path).resolve()
                try:
                    target_path = target_path.relative_to(self.root_folder)
                    return f"{link_text} (see section: {target_path.stem})"
                except ValueError:
                    return link_text
            
            return match.group(0)

        content = re.sub(
            r'\[(.*?)\]\((.*?)\)',
            replace_links,
            content
        )

        return content

    def add_content_to_document(self, doc, content):
        """Add processed markdown content to Word document"""
        lines = content.split('\n')
        

        def clean_list_item_text(line):
            """Remove list markers and extra numbers from text"""
            # Remove leading numbers and dots, including any following numbers
            text = re.sub(r'^\s*\d+\.\s*(?:\d+\.)?\s*', '', line)
            # Remove bullet points if present
            text = re.sub(r'^\s*[•\-\*\+]\s*', '', text)
            return text.strip()

        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()

            # Handle headers
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2)
                doc.add_heading(text, level=level)
                i += 1
                continue
            
            # Handle ordered lists
            if re.match(r'^\s*\d+\.\s+', line):

                # Get the indent level
                indent_level = len(line) - len(line.lstrip())
                
                # Check if original line started with "1." BEFORE cleaning the text
                # starts_new_list = bool(re.match(r'^\s*1\.\s+', line.lstrip()))

                paragraph = doc.add_paragraph()

                if indent_level == 0:
                    paragraph.style = 'List Bullet' #'List Number'
                elif indent_level > 2:
                    paragraph.style = 'List Bullet 3' #'List Number 3'
                else:
                    paragraph.style = f'List Bullet {indent_level}' #f'List Number {indent_level}'

                # Then clean the text and add to the paragraph
                text = clean_list_item_text(line)
                run = paragraph.add_run(text)
                i += 1
                continue

            # Handle bullet lists
            if line.strip().startswith(('-', '•', '*')):

                indent_level = len(line) - len(line.lstrip())
                
                paragraph = doc.add_paragraph()
                #paragraph.style = 'List Bullet'
                if indent_level == 0:
                    paragraph.style = 'List Bullet'
                elif indent_level > 2:
                    paragraph.style = 'List Bullet 3'
                else:
                    paragraph.style = f'List Bullet {indent_level}'

                # Then clean the text and add to the paragraph
                text = clean_list_item_text(line)
                paragraph.text = text
                i += 1
                continue

            # Handle tables
            if line.startswith('|') and i + 1 < len(lines) and lines[i + 1].startswith('|---'):
                headers = [cell.strip() for cell in line.split('|')[1:-1]]
                i += 2
                
                rows = []
                while i < len(lines) and lines[i].startswith('|'):
                    cells = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                    rows.append(cells)
                    i += 1
                
                table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                table.style = 'Table Grid'
                
                for j, header in enumerate(headers):
                    table.cell(0, j).text = header
                    for paragraph in table.cell(0, j).paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
                
                for row_idx, row_data in enumerate(rows):
                    for col_idx, cell_data in enumerate(row_data):
                        table.cell(row_idx + 1, col_idx).text = cell_data
                
                doc.add_paragraph()
                continue

            # Handle images
            image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if image_match:
                try:
                    img_path = image_match.group(2)
                    if os.path.exists(img_path):
                        # Get image dimensions
                        with Image.open(img_path) as img:
                            width, height = img.size
                            
                        # Calculate aspect ratio
                        aspect_ratio = height / width
                        
                        # Set maximum width to 6 inches
                        max_width = Inches(6)
                        
                        # Calculate height based on aspect ratio
                        calculated_height = max_width * aspect_ratio
                        
                        # If height is too large, adjust width to maintain aspect ratio
                        if calculated_height > Inches(9):  # Maximum height
                            max_width = Inches(9) / aspect_ratio
                        
                        # Add the image with calculated dimensions
                        doc.add_picture(img_path, width=max_width)
                    i += 1
                    continue
                except Exception as e:
                    logger.error(f"Failed to add image: {e}")

            # Regular paragraph
            if line.strip():
                doc.add_paragraph(line)
            i += 1

    def process_file(self, file_path, doc):
        """Process a single markdown file"""
        if file_path in self.processed_files or file_path.name == 'index.md':
            return
        
        logger.info(f"{file_path}")  # Simple console output
        logger.debug(f"Starting processing of {file_path}")  # Detailed log file output
        self.processed_files.add(file_path)
        
        try:
            if len(self.processed_files) > 1:
                doc.add_page_break()
                
            content = file_path.read_text(encoding='utf-8')
            processed_content = self.process_markdown_content(content, file_path)
            
            doc.add_heading(file_path.stem, level=1)
            self.add_content_to_document(doc, processed_content)

            self.processed_files.add(file_path)
            logger.info(f"{file_path} - Successfully processed")
            
        except Exception as e:
            logger.debug(f"Error processing {file_path}: {e}")  # Detailed error in log file
            logger.info(f"Error processing {file_path.name}")   # Simple error in console

    def organize_files_by_folder(self):
        """Organize markdown files by folder structure"""
        folder_structure = {}
        
        for root, _, files in os.walk(self.root_folder):
            md_files = [f for f in files if f.endswith('.md')]
            if md_files:
                rel_path = os.path.relpath(root, self.root_folder)
                
                # Use "Root" as the name for files in the root directory
                folder_name = "Root" if rel_path == '.' else rel_path
                    
                folder_structure[folder_name] = {
                    'readme': None,
                    'other_files': []
                }
                
                for file in md_files:
                    file_path = Path(root) / file
                    if file.lower() == 'readme.md':
                        folder_structure[folder_name]['readme'] = file_path
                    else:
                        folder_structure[folder_name]['other_files'].append(file_path)
                
                # Sort other files alphabetically
                folder_structure[folder_name]['other_files'].sort()
        
        return folder_structure

    def convert(self, concise=False):
        """Main conversion process"""
        try:
            self.setup_temp_directories()
            
            logger.info("Starting conversion...")
            logger.debug("Initializing document conversion")
            
            doc = Document()
            
            # Add TOC
            doc.add_heading('Table of Contents', level=1)
            doc.add_paragraph('').add_run().add_break()
            paragraph = doc.add_paragraph()
            run = paragraph.add_run()
            run.bold = True
            run.text = 'Select the rows below, RIGHT-CLICK AND SELECT "UPDATE FIELD" TO SHOW the TABLE OF CONTENTS.'
            doc.add_paragraph()
            toc = doc.add_paragraph()
            run = toc.add_run()
            fld_char = OxmlElement('w:fldChar')
            fld_char.set(qn('w:fldCharType'), 'begin')
            run._r.append(fld_char)
            instr_text = OxmlElement('w:instrText')
            instr_text.text = 'TOC \\o "1-2" \\h \\z \\u'
            run._r.append(instr_text)
            fld_char = OxmlElement('w:fldChar')
            fld_char.set(qn('w:fldCharType'), 'end')
            run._r.append(fld_char)
            
            # Add page break after TOC
            # doc.add_page_break()
            
            # Process files by folder structure
            folder_structure = self.organize_files_by_folder()
            
            for folder_path, files in folder_structure.items():
                # Add chapter heading (folder name)
                doc.add_page_break()
                doc.add_heading(folder_path, level=1)  # Chapter title at level 0
                
                # Process README first
                if files['readme']:
                    content = files['readme'].read_text(encoding='utf-8')
                    processed_content = self.process_markdown_content(content, files['readme'])
                    
                    # When processing README content, increase all heading levels by 1
                    processed_content = re.sub(
                        r'^(#{1,5})',
                        lambda m: '#' * (len(m.group(1))+1),
                        processed_content,
                        flags=re.MULTILINE
                    )
                    
                    self.add_content_to_document(doc, processed_content)
                    self.processed_files.add(files['readme'])
                
                # Process other files
                if (not concise) and files['other_files']:
                    for file_path in files['other_files']:
                        doc.add_page_break()
                        doc.add_heading(file_path.stem, level=2)  # Subchapter at level 2
                        content = file_path.read_text(encoding='utf-8')
                        processed_content = self.process_markdown_content(content, file_path)
                        
                        # Increase all heading levels by 2
                        processed_content = re.sub(
                            r'^(#{1,5})',
                            lambda m: '#' * (len(m.group(1)) + 2),
                            processed_content,
                            flags=re.MULTILINE
                        )
                        
                        self.add_content_to_document(doc, processed_content)
                        self.processed_files.add(file_path)
            

            logger.info(f"\nConversion completed: {len(self.processed_files)} files processed to {self.output_file}")
            
        except Exception as e:
            logger.debug(f"Conversion failed: {e}")
            logger.info("Conversion failed. Check log file for details.")
        finally:
            # Save document
            doc.save(self.output_file)
            logger.debug(f"Document saved as {self.output_file} with {len(self.processed_files)} files processed")
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

def main():
    config = load_config("config.json")
    root_folder = config.get("docs_dir", "docs")
    output_file = config.get("doc_name", "documentation.docx")
    concise = config.get("doc_concise", False)  # Set to True to skip sub-chapters
    
    converter = MarkdownToWordConverter(root_folder, output_file)
    converter.convert(concise=concise)

if __name__ == "__main__":
    main()
