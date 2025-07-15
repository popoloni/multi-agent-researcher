import xml.etree.ElementTree as ET
import os
import json

### load config
def load_config(config_file: str) -> dict:
    with open(config_file, 'r') as f:
        return json.load(f)

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_xml_element(element, filename):
    tree = ET.ElementTree(element)
    ET.register_namespace('DTS', "www.microsoft.com/SqlServer/Dts")
    ET.register_namespace('SQLTask', "www.microsoft.com/sqlserver/dts/tasks/sqltask")
    with open(filename, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

def process_executable(executable, parent_dir, counter):
    """Process a single executable element and its nested executables"""
    ref_id = executable.get('{www.microsoft.com/SqlServer/Dts}refId', '')
    if ref_id.startswith('Package\\'):
        ref_id = ref_id.replace('Package\\', '')
    
    # Create safe filename with counter
    safe_filename = ref_id.replace('\\', '_').replace('/', '_')
    numbered_filename = f"{counter:03d}_{safe_filename}"
    
    # Check if this executable contains nested executables
    nested_executables = executable.find(".//{www.microsoft.com/SqlServer/Dts}Executables")
    
    if nested_executables is not None:
        # Create a subfolder for this executable
        subfolder_path = os.path.join(parent_dir, numbered_filename)
        create_directory_if_not_exists(subfolder_path)
        
        # Create a copy of the executable without nested executables
        executable_copy = ET.Element(executable.tag, executable.attrib)
        for child in executable:
            if child.tag.endswith('Executables'):
                # Create new Executables element without the nested executables
                new_executables = ET.SubElement(executable_copy, child.tag)
            else:
                executable_copy.append(child)
        
        # Write the main executable file
        output_file = os.path.join(parent_dir, f"{numbered_filename}.xml")
        write_xml_element(executable_copy, output_file)
        print(f"Writing executable: {ref_id} to {output_file}")
        
        # Process nested executables
        nested_counter = 1
        for nested_exec in nested_executables:
            if nested_exec.tag.endswith('Executable'):
                process_executable(nested_exec, subfolder_path, nested_counter)
                nested_counter += 1
    else:
        # Write the executable file directly
        output_file = os.path.join(parent_dir, f"{numbered_filename}.xml")
        write_xml_element(executable, output_file)
        print(f"Writing executable: {ref_id} to {output_file}")
    
    return counter + 1

def process_xml(xml_content, output_dir = "output"):
    root = ET.fromstring(xml_content)   
    create_directory_if_not_exists(output_dir)
    executables_dir = os.path.join(output_dir, 'Executables')
    create_directory_if_not_exists(executables_dir)
    
    metadata_root = ET.Element(root.tag, root.attrib)
    
    for child in root:
        tag_name = child.tag.split('}')[-1]
        print(f"Processing tag: {tag_name}")
        
        if tag_name == 'PackageParameters':
            write_xml_element(child, os.path.join(output_dir, 'Parameters.xml'))
        
        elif tag_name == 'Variables':
            write_xml_element(child, os.path.join(output_dir, 'Variables.xml'))
        
        elif tag_name == 'Executables':
            counter = 1
            for executable in child:
                if executable.tag.endswith('Executable'):
                    counter = process_executable(executable, executables_dir, counter)
        
        elif tag_name == 'PrecedenceConstraints':
            write_xml_element(child, os.path.join(output_dir, 'PrecedenceConstraints.xml'))
        
        elif tag_name == 'DesignTimeProperties':
            write_xml_element(child, os.path.join(output_dir, 'DesignTimeProperties.xml'))
        
        else:
            metadata_root.append(child)
    
    write_xml_element(metadata_root, os.path.join(output_dir, 'METADATA.xml'))

def main():
    config = load_config("config.json")
    
    # Get input XML file from command line or config
    import sys
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
    else:
        xml_file = config.get("xml_input_file", "input.xml")
    
    if not os.path.exists(xml_file):
        print(f"Error: XML file '{xml_file}' not found")
        return
    
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    output_dir = config.get("src_dir", "output")
    process_xml(xml_content, output_dir=output_dir)
    print(f"XML preprocessing completed. Output saved to: {output_dir}")

if __name__ == "__main__":
    main()
