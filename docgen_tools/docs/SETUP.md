# Installation and Setup Guide

This guide will help you install dependencies and configure the consolidated documentation tools.

## Prerequisites

- Python 3.8 or higher
- Internet connection for package installation and API calls
- AWS account (for Bedrock) or Anthropic API key

## Step 1: Install Python Dependencies

### Option A: Using pip (Recommended)
```bash
pip install -r requirements.txt
```

### Option B: Manual Installation
```bash
pip install anthropic>=0.25.0 boto3>=1.34.0 requests>=2.31.0 python-docx>=0.8.11 markdown>=3.5.0 pathlib>=1.0.1 pillow>=10.0.0 urllib3>=1.26.0
```

## Step 2: Configure LLM Provider

### Option A: AWS Bedrock Setup

#### 1. Set up AWS Profile
First, ensure you have AWS CLI installed:
```bash
aws --version
```

If not installed, install it:
```bash
pip install awscli
```

#### 2. Configure AWS Profile for Bedrock
Create or configure an AWS profile with Bedrock permissions:

1. Log into AWS Console
2. Go to IAM and create a user with Bedrock permissions
3. Generate access keys for the user
4. Copy the credentials text provided by AWS

#### 3. Add Credentials to AWS Config
**On Windows:**
```bash
# Edit the credentials file
notepad %USERPROFILE%\.aws\credentials
```

**On Linux/Mac:**
```bash
# Edit the credentials file
nano ~/.aws/credentials
```

Add the credentials section (replace with your actual credentials):
```ini
[your-profile-name]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
aws_session_token = YOUR_SESSION_TOKEN  # if using temporary credentials
```

#### 4. Update config.json
Edit the `config.json` file to use your AWS profile:
```json
{
    "llm_provider": "bedrock",
    "aws_profile": "your-profile-name",
    "aws_region": "eu-west-1",
    "model": "eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
    ...
}
```

### Option B: Anthropic API Setup

#### 1. Get Anthropic API Key
1. Go to https://console.anthropic.com/
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new API key

#### 2. Set Environment Variable
**On Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
# Or permanently:
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-api-key-here', [System.EnvironmentVariableTarget]::User)
```

**On Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
# Or add to ~/.bashrc or ~/.zshrc:
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

#### 3. Update config.json
Edit the `config.json` file to use Anthropic:
```json
{
    "llm_provider": "anthropic",
    "model": "claude-3-5-sonnet-20240620",
    ...
}
```

## Step 3: Configure Directories

Edit `config.json` to set your source and output directories:

```json
{
    "src_dir": "path/to/your/source/code",
    "docs_dir": "path/to/output/documentation",
    "doc_name": "your_documentation.docx",
    ...
}
```

## Step 4: Verify Installation

Run the test script to verify everything is working:
```bash
python test_tools.py
```

Expected output:
```
Testing Consolidated Documentation Tools
========================================

File Structure Test:
--------------------
✓ config.json exists
✓ add_doc_links.py exists
✓ generate_docs.py exists
✓ folder2word.py exists
✓ preprocess_xml.py exists
✓ README.md exists
✓ test_src/TestClass.java exists

Configuration Test:
--------------------
✓ Configuration loaded successfully
  - Source directory: test_src
  - Docs directory: component_doc
  - LLM Provider: bedrock

Dependencies Test:
--------------------
✓ json package available
✓ os package available
✓ pathlib package available
✓ logging package available
✓ requests package available
✓ boto3 package available
✓ anthropic package available
✓ docx package available
✓ markdown package available
✓ PIL package available

Module Imports Test:
--------------------
✓ add_doc_links.py imports successfully
✓ generate_docs.py imports successfully
✓ folder2word.py imports successfully
✓ preprocess_xml.py imports successfully

========================================
✓ All tests passed! The consolidated tools are ready to use.
```

## Step 5: Running the Documentation Pipeline

### Full Pipeline
```bash
# 1. Generate documentation from source code
python generate_docs.py

# 2. Add navigation links between files
python add_doc_links.py

# 3. Convert to Word document
python folder2word.py
```

### Individual Tools

#### Process XML files (optional)
```bash
python preprocess_xml.py input.xml
```

#### Generate documentation only
```bash
python generate_docs.py
```

#### Add links only
```bash
python add_doc_links.py
```

#### Convert to Word only
```bash
python folder2word.py
```

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. AWS Credentials errors
```bash
# Test AWS configuration
aws sts get-caller-identity --profile your-profile-name
```

#### 3. Anthropic API errors
```bash
# Test API key
python -c "import os; print('API Key:', os.environ.get('ANTHROPIC_API_KEY', 'NOT SET'))"
```

#### 4. Permission errors
```bash
# Check file permissions
ls -la config.json
```

#### 5. Network/firewall issues
- Ensure internet access for API calls
- Check corporate firewall settings for:
  - api.anthropic.com
  - bedrock-runtime.*.amazonaws.com
  - mermaid.ink (for diagram generation)

### Log Files
The tools generate log files for debugging:
- `doc_generation.log` - Documentation generation issues
- `doc_linking.log` - Link creation issues
- `diagram_conversion.log` - Word conversion issues

### Support

If you encounter issues:
1. Check the log files for detailed error messages
2. Verify your API credentials are correct
3. Ensure all dependencies are installed
4. Test with a small sample before processing large codebases

## Configuration Options

### Basic Configuration
```json
{
    "llm_provider": "bedrock",  // or "anthropic"
    "src_dir": "source_code",
    "docs_dir": "documentation",
    "doc_name": "output.docx",
    "doc_concise": false
}
```

### Advanced Configuration
```json
{
    "max_tokens": 128000,
    "temperature": 0.2,
    "top_p": 0.85,
    "top_k": 20,
    "xml_input_file": "input.xml"
}
```

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Regularly rotate API keys
- Use IAM roles instead of access keys when possible
- Keep your AWS credentials file secure

---

**Next Steps**: After successful installation, see `README.md` for detailed usage instructions and examples.
