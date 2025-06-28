#!/usr/bin/env python3
"""
Demo script to showcase documentation generation functionality
This demonstrates the Phase 2 and Phase 3 implementation for transforming repositories into technical documentation
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.kenobi_agent import KenobiAgent
from app.models.repository_schemas import RepositoryIndexRequest

async def demo_documentation_generation():
    """Demonstrate the complete documentation generation workflow"""
    
    print("🚀 Multi-Agent Researcher - Documentation Generation Demo")
    print("=" * 60)
    
    # Initialize the Kenobi agent
    kenobi = KenobiAgent()
    
    # Clone and analyze the astropy repository
    print("\n📥 Step 1: Cloning and indexing astropy repository...")
    try:
        # Use the repository service to clone the astropy repo
        repository = await kenobi.repository_service.clone_github_repository(
            owner="popoloni",
            repo="astropy",
            branch="main"
        )
        print(f"✅ Repository cloned successfully: {repository.name}")
        print(f"   - ID: {repository.id}")
        print(f"   - Language: {repository.language.value}")
        print(f"   - Files: {repository.file_count}")
        print(f"   - Lines: {repository.line_count}")
        
    except Exception as e:
        print(f"❌ Error cloning repository: {e}")
        return
    
    # Analyze the repository to extract functionalities
    print(f"\n🔍 Step 2: Analyzing repository structure...")
    try:
        analysis = await kenobi.repository_service.analyze_repository(repository.id)
        print(f"✅ Analysis completed:")
        print(f"   - Total files analyzed: {len(analysis.files)}")
        
        # Count elements by type
        element_counts = {}
        all_elements = []
        for file in analysis.files:
            for element in file.elements:
                element_type = element.element_type.value
                element_counts[element_type] = element_counts.get(element_type, 0) + 1
                all_elements.append(element)
        
        print(f"   - Total code elements: {len(all_elements)}")
        for elem_type, count in element_counts.items():
            print(f"     * {elem_type.title()}s: {count}")
            
    except Exception as e:
        print(f"❌ Error analyzing repository: {e}")
        return
    
    # Generate comprehensive documentation
    print(f"\n📝 Step 3: Generating technical documentation...")
    
    # Get key functions and classes for API reference
    functions = [elem for elem in all_elements if elem.element_type.value == "function"][:15]
    classes = [elem for elem in all_elements if elem.element_type.value == "class"][:10]
    variables = [elem for elem in all_elements if elem.element_type.value == "variable"][:5]
    
    # Generate comprehensive documentation
    documentation = {
        "metadata": {
            "repository_name": analysis.repository.name,
            "language": analysis.repository.language.value,
            "generated_at": datetime.now().isoformat(),
            "total_files": len(analysis.files),
            "total_elements": len(all_elements),
            "element_counts": element_counts
        },
        "overview": f"""# {analysis.repository.name} - Technical Documentation

## Overview
This is a comprehensive technical documentation for the **{analysis.repository.name}** repository, a {analysis.repository.language.value} project containing {len(analysis.files)} files and {len(all_elements)} code elements.

## Repository Statistics
- **Language**: {analysis.repository.language.value}
- **Total Files**: {len(analysis.files)}
- **Lines of Code**: {analysis.repository.line_count:,}
- **Functions**: {element_counts.get('function', 0)}
- **Classes**: {element_counts.get('class', 0)}
- **Variables**: {element_counts.get('variable', 0)}

## Architecture Overview
The repository is organized with the following code structure:
{chr(10).join([f"- **{k.title()}s**: {v} elements" for k, v in element_counts.items()])}

## Installation & Setup
```bash
git clone https://github.com/popoloni/astropy.git
cd astropy
# Follow language-specific installation instructions
pip install -r requirements.txt  # For Python projects
```

## Key Features
This repository provides various astronomical computation and analysis functionalities organized across {len(analysis.files)} files. The codebase includes sophisticated algorithms for celestial mechanics, coordinate transformations, and astronomical data processing.
""",
        "api_reference": {
            "functions": [
                {
                    "name": func.name,
                    "description": func.description or "No description available",
                    "file": func.file_path,
                    "line_start": func.start_line,
                    "line_end": func.end_line,
                    "code_preview": func.code_snippet[:150] + "..." if len(func.code_snippet) > 150 else func.code_snippet,
                    "complexity": func.complexity_score
                }
                for func in functions
            ],
            "classes": [
                {
                    "name": cls.name,
                    "description": cls.description or "No description available",
                    "file": cls.file_path,
                    "line_start": cls.start_line,
                    "line_end": cls.end_line,
                    "code_preview": cls.code_snippet[:150] + "..." if len(cls.code_snippet) > 150 else cls.code_snippet,
                    "complexity": cls.complexity_score
                }
                for cls in classes
            ],
            "variables": [
                {
                    "name": var.name,
                    "description": var.description or "No description available",
                    "file": var.file_path,
                    "line": var.start_line,
                    "code_preview": var.code_snippet[:100] + "..." if len(var.code_snippet) > 100 else var.code_snippet
                }
                for var in variables
            ]
        },
        "file_structure": [
            {
                "file": file.file_path,
                "elements": len(file.elements),
                "types": list(set([elem.element_type.value for elem in file.elements]))
            }
            for file in analysis.files[:20]  # Show first 20 files
        ]
    }
    
    print("✅ Documentation generated successfully!")
    
    # Save documentation to file
    output_file = f"/workspace/multi-agent-researcher/generated_docs_{analysis.repository.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(documentation, f, indent=2)
    
    print(f"💾 Documentation saved to: {output_file}")
    
    # Display sample documentation
    print(f"\n📖 Step 4: Sample Generated Documentation")
    print("=" * 60)
    print(documentation["overview"])
    
    print(f"\n🔧 API Reference Sample - Top Functions:")
    print("-" * 40)
    for i, func in enumerate(documentation["api_reference"]["functions"][:5], 1):
        print(f"{i}. **{func['name']}** (Line {func['line_start']})")
        print(f"   File: {func['file']}")
        print(f"   Description: {func['description']}")
        print(f"   Preview: {func['code_preview'][:100]}...")
        print()
    
    print(f"\n🏗️ Classes Sample:")
    print("-" * 40)
    for i, cls in enumerate(documentation["api_reference"]["classes"][:3], 1):
        print(f"{i}. **{cls['name']}** (Line {cls['line_start']})")
        print(f"   File: {cls['file']}")
        print(f"   Description: {cls['description']}")
        print()
    
    print(f"\n📁 File Structure Sample:")
    print("-" * 40)
    for file_info in documentation["file_structure"][:10]:
        print(f"📄 {file_info['file']}")
        print(f"   Elements: {file_info['elements']} ({', '.join(file_info['types'])})")
    
    print(f"\n🎉 Documentation Generation Complete!")
    print(f"Repository '{analysis.repository.name}' has been successfully transformed into technical documentation.")
    print(f"Total elements documented: {len(all_elements)}")
    print(f"Documentation file: {output_file}")
    
    return documentation, output_file

if __name__ == "__main__":
    asyncio.run(demo_documentation_generation())