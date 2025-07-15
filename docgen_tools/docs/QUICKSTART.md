# Quick Start Guide

Get up and running with the consolidated documentation tools in 5 minutes.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Automatic setup (recommended)
python setup.py

# Or manual installation
pip install -r requirements.txt
```

### 2. Configure LLM Provider

#### Option A: AWS Bedrock
1. Create AWS user with Bedrock permissions
2. Copy credentials to `~/.aws/credentials`:
   ```ini
   [your-profile-name]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   ```
3. Update `config.json`:
   ```json
   {
     "llm_provider": "bedrock",
     "aws_profile": "your-profile-name"
   }
   ```

#### Option B: Anthropic API
1. Get API key from https://console.anthropic.com/
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```
3. Update `config.json`:
   ```json
   {
     "llm_provider": "anthropic"
   }
   ```

### 3. Configure Paths
Edit `config.json`:
```json
{
  "src_dir": "path/to/your/source/code",
  "docs_dir": "output/documentation",
  "doc_name": "my_docs.docx"
}
```

### 4. Verify Setup
```bash
python test_tools.py
```

**Expected output:**
```
Testing Consolidated Documentation Tools
========================================
✓ config.json exists
✓ All Python scripts exist
✓ Configuration loaded successfully
✓ All dependencies available
```

## 🔧 Basic Usage

### Generate Documentation
```bash
# Full pipeline
python generate_docs.py      # Convert source to markdown
python add_doc_links.py      # Add navigation links
python folder2word.py        # Create Word document

# Individual steps
python preprocess_xml.py input.xml  # (Optional) Process XML first
```

**Expected output from folder2word.py:**
```
Processing: Starting conversion...
Processing: 
Conversion completed: X files processed to [output_file].docx
```

**Note**: The number of files processed should match the actual markdown files in your docs directory. If you see "0 files processed", check the troubleshooting section.

### Supported File Types
- **COBOL**: `.cbl`, `.cob`, `.cpy`, `.cobol`
- **PL/1**: `.pli`
- **Java**: `.java`
- **EGL**: `.egl`
- **SQL**: `.sql`, `.ddl`, `.src`
- **XML**: `.xml`
- **C#**: `.cs`
- **JavaScript**: `.js`
- **JSP**: `.jsp`

## 📁 Example Directory Structure

### Input
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

### Output
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

## ⚙️ Common Configuration

### Basic Settings
```json
{
  "llm_provider": "bedrock",
  "src_dir": "source_code",
  "docs_dir": "documentation",
  "doc_name": "output.docx",
  "doc_concise": false,
  "max_tokens": 128000,
  "temperature": 0.2
}
```

### Documentation Styles
Choose prompt template by editing config keys:
- `general_*_prompt`: Standard documentation
- `datamodel_*_prompt`: Data model focused
- `csd_*_prompt`: Financial systems
- `system_*_prompt`: System architecture

## 🛠️ Troubleshooting

### Common Issues

#### folder2word.py reports "0 files processed" ✅ FIXED
**Problem**: Script was skipping files in the root directory.
**Solution**: This has been fixed in the consolidated version. The script now properly processes files in the root documentation directory.

#### Dependencies Missing
```bash
pip install -r requirements.txt --force-reinstall
```

#### API Credentials
```bash
# Test AWS
aws sts get-caller-identity --profile your-profile-name

# Test Anthropic
python -c "import os; print(os.environ.get('ANTHROPIC_API_KEY', 'NOT SET'))"
```

#### Network Issues
- Check firewall for API access
- Verify internet connection
- Corporate proxy settings

### Log Files
Check these for errors:
- `doc_generation.log`
- `doc_linking.log`
- `diagram_conversion.log`

### Verification Steps
1. **Test suite passes**: `python test_tools.py` shows all green checkmarks
2. **File count accurate**: `folder2word.py` reports actual number of processed files
3. **Output quality**: Generated Word document contains all markdown files with proper formatting

## 📚 More Information

- **Detailed Setup**: See `SETUP.md`
- **Full Documentation**: See `README.md`
- **Consolidation Info**: See `CONSOLIDATION_SUMMARY.md`

---

**Need Help?** Run `python setup.py` for interactive setup or check the log files for detailed error messages.
