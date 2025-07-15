# Consolidated Documentation Tools

This folder contains the consolidated versions of the Python documentation generation tools that were scattered across multiple directories in the DEV workspace.

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials** (see [Setup Guide](docs/SETUP.md) for details):
   ```bash
   aws configure
   ```

3. **Test the setup**:
   ```bash
   python test_tools.py
   ```

4. **Run the complete workflow**:
   ```bash
   python generate_docs.py      # Generate documentation from code
   python add_doc_links.py      # Add navigation links
   python folder2word.py        # Convert to Word document
   ```

5. **Verify output**:
   - Check the generated markdown files in your `docs_dir`
   - Verify the Word document contains all processed files
   - Review log files for any issues or warnings

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[📚 Setup Guide](docs/SETUP.md)** | Comprehensive installation and configuration instructions |
| **[⚡ Quick Start](docs/QUICKSTART.md)** | 5-minute setup guide for immediate use |
| **[📋 Consolidation Summary](docs/CONSOLIDATION_SUMMARY.md)** | Details about what was consolidated and why |
| **[✅ Installation Complete](docs/INSTALLATION_COMPLETE.md)** | Post-installation guide and validation |
| **[🎯 Final Status Report](docs/FINAL_STATUS_REPORT.md)** | Complete project status and issue resolution summary |

## 🔧 Tools Overview

### Core Components

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| **`generate_docs.py`** | Convert source code to markdown | Source files | Markdown documentation |
| **`add_doc_links.py`** | Add navigation links | Markdown files | Linked documentation |
| **`folder2word.py`** | Convert to Word format | Markdown files | Professional Word document |
| **`preprocess_xml.py`** | Process XML files | XML files | Processed XML for documentation |
| **`config.json`** | Configuration | Settings | Unified configuration |

### Supported Languages

- **COBOL** (`.cbl`, `.cob`, `.cpy`, `.cobol`)
- **PL/1** (`.pli`)
- **Java** (`.java`)
- **EGL** (`.egl`)
- **SQL** (`.sql`, `.ddl`, `.src`)
- **XML** (`.xml`)
- **C#** (`.cs`)
- **JavaScript** (`.js`)
- **JSP** (`.jsp`)

## ⚙️ Configuration

Edit `config.json` to configure:

1. **LLM Provider**: Choose between `"anthropic"` or `"bedrock"`
2. **Directories**: Set `src_dir` and `docs_dir` paths
3. **Output**: Configure Word document name and style
4. **Prompts**: Choose documentation style (general, datamodel, csd, system)

Example configuration:
```json
{
  "llm_provider": "bedrock",
  "src_dir": "source_code",
  "docs_dir": "documentation",
  "doc_name": "output.docx",
  "doc_concise": false
}
```
2. **API Credentials**: Set appropriate AWS profile or Anthropic API key
3. **Directories**: 
   - `src_dir`: Source code directory
   - `docs_dir`: Output documentation directory
   - `doc_name`: Word document filename

### Basic Workflow

1. **Preprocess XML files** (if needed):
   ```bash
   python preprocess_xml.py input.xml
   ```

2. **Generate documentation from source code**:
## 🧪 Testing and Validation

### Quick Test
```bash
python test_tools.py
```

**Expected output:**
```
Testing Consolidated Documentation Tools
========================================
✓ All files exist
✓ Configuration loaded successfully
✓ All dependencies available
```

### Full Pipeline Test
```bash
python generate_docs.py      # Process test_src/TestClass.java
python add_doc_links.py      # Add navigation links
python folder2word.py        # Convert to Word
```

**Expected output from folder2word.py:**
```
Processing: Starting conversion...
Processing: 
Conversion completed: 3 files processed to test_doc.docx
```

## 🛠️ Troubleshooting

### Common Issues

#### ✅ folder2word.py reports "0 files processed" - FIXED
**Problem**: Script was skipping files in the root documentation directory.
**Solution**: Fixed in the consolidated version. The script now properly handles files in the root directory.

#### ✅ Missing file count tracking - FIXED
**Problem**: Script wasn't tracking which files were processed.
**Solution**: Added proper file tracking with accurate count reporting.

#### AWS Bedrock authentication
**Problem**: Credential setup for AWS Bedrock can be complex.
**Solution**: Follow the detailed setup instructions in [Setup Guide](docs/SETUP.md).

#### Missing dependencies
**Problem**: Required Python packages are not installed.
**Solution**: Run `pip install -r requirements.txt` or use automated setup: `python setup.py`

### Verification Steps

1. **Run the test suite**: `python test_tools.py` shows all green checkmarks
2. **Check file processing**: `folder2word.py` reports actual number of files processed (not 0)
3. **Validate output**: Generated Word document contains all markdown files with proper formatting
4. **Review logs**: Log files show successful processing without errors

### Log Files
- `doc_generation.log` - Documentation generation details
- `doc_linking.log` - Link creation process
- `diagram_conversion.log` - Word conversion with diagram processing

## 📁 Example Usage

### Input Structure
```
src_dir/
├── cobol/
│   ├── main.cbl
│   └── utils.cpy
├── java/
│   └── Service.java
└── xml/
    └── config.xml
```

### Output Structure
```
docs_dir/
├── index.md
├── cobol/
│   ├── README.md
│   ├── main.md
│   └── utils.md
├── java/
│   ├── README.md
│   └── Service.md
└── documentation.docx
```

## 🔄 Migration from Old Versions

If you were using the scattered versions:

1. **Copy your existing `config.json`** to this directory
2. **Update paths** in the configuration to match your setup
3. **Test with a small sample** before processing large codebases
4. **Remove old versions** once you've verified the consolidated tools work

## 🏗️ Features Added in Consolidation

- **Unified configuration**: All tools use the same config.json
- **Enhanced error handling**: Better logging and retry mechanisms
- **Improved Word formatting**: Professional document generation
- **Fixed critical bugs**: Root directory processing and file count tracking
- **Comprehensive testing**: Full validation suite
- **Complete documentation**: Setup guides and troubleshooting

## 🎯 Next Steps

1. **Get Started**: Follow the [Quick Start Guide](docs/QUICKSTART.md)
2. **Detailed Setup**: See [Setup Guide](docs/SETUP.md) for comprehensive instructions
3. **Understand Consolidation**: Read [Consolidation Summary](docs/CONSOLIDATION_SUMMARY.md)
4. **Post-Installation**: Check [Installation Complete](docs/INSTALLATION_COMPLETE.md)
5. **Project Status**: Review [Final Status Report](docs/FINAL_STATUS_REPORT.md) for complete resolution details

---

**Ready to use!** The consolidated documentation tools are now fully functional and ready to generate professional documentation from your source code.
