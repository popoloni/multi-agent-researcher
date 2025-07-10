# 🔧 Comprehensive Troubleshooting Plan

**Date**: July 1, 2025  
**Issues Reported**:
1. Ollama still used for documentation generation (should use Anthropic)
2. Documentation persistence bug still occurring (docs disappear on navigation)

## 🔍 Root Cause Analysis

### Issue 1: Ollama Still Used for Documentation Generation

**Root Cause Identified**: 
- The documentation generation code in `app/main.py` (lines 1432-1710) makes **direct HTTP calls to Ollama** instead of using the model manager
- Despite `.env` having `AI_PROVIDER=anthropic`, the documentation generation bypasses this configuration
- The code hardcodes Ollama API calls for function/class descriptions and overview generation

**Evidence**:
```python
# Line 1444 in app/main.py - Direct Ollama HTTP call
ollama_response = await client.post(
    f"{settings.OLLAMA_HOST}/api/generate",
    json={
        "model": "llama3.2:1b",  # Hardcoded Ollama model
        "prompt": description_prompt,
        "stream": False
    }
)
```

### Issue 2: Documentation Persistence Bug

**Potential Root Causes**:
1. **Environment-specific caching issues**: Python bytecode cache (`__pycache__`) may contain old code
2. **Database state inconsistency**: Documentation may be corrupted in user's local database
3. **Frontend state management**: React state not properly persisting during navigation
4. **API endpoint caching**: Browser or server-side caching of old responses

## 🛠️ Correction Plan

### Phase 1: Fix Documentation Generation AI Provider (Priority 1)

**Problem**: Documentation generation bypasses model manager and directly calls Ollama

**Solution**: Replace direct Ollama calls with model manager calls

**Files to Fix**:
- `app/main.py` (lines 1432-1710): Replace all direct Ollama HTTP calls with model manager calls

**Implementation**:
1. Import model manager in documentation generation functions
2. Replace direct HTTP calls with `model_manager.call_model()`
3. Use `settings.DOCUMENTATION_MODEL` instead of hardcoded models
4. Add proper error handling and fallback

### Phase 2: Fix Documentation Persistence (Priority 1)

**Problem**: Documentation disappears during navigation

**Solution**: Multi-layered approach to ensure persistence

**Steps**:
1. **Clear Python cache**: Remove `__pycache__` directories
2. **Reset database**: Clear and regenerate documentation entries
3. **Verify API responses**: Ensure JSON parsing works correctly
4. **Test frontend state**: Verify React context persistence

### Phase 3: Environment Configuration Verification (Priority 2)

**Problem**: User's local environment may have configuration issues

**Solution**: Comprehensive environment validation

**Steps**:
1. Verify `.env` file is properly loaded
2. Check Python virtual environment
3. Validate API keys and configuration
4. Test model provider connectivity

## 📋 Step-by-Step Correction Instructions

### Step 1: Fix Documentation Generation AI Provider

```bash
# 1. Update the documentation generation code to use model manager
# This will be done by modifying app/main.py
```

### Step 2: Clear Python Cache and Reset Environment

```bash
# 1. Stop all services
./stop_all.sh

# 2. Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# 3. Clear documentation database entries
# (We'll provide a script for this)

# 4. Restart services
./start_all.sh
```

### Step 3: Verify Environment Configuration

```bash
# 1. Check .env file
cat .env | grep AI_PROVIDER

# 2. Test configuration loading
python -c "from app.core.config import settings; print(f'AI_PROVIDER: {settings.AI_PROVIDER}')"

# 3. Test model manager
python -c "from app.core.model_providers import model_manager; print('Model manager loaded successfully')"
```

### Step 4: Test Documentation Generation End-to-End

```bash
# 1. Generate documentation for a test repository
# 2. Navigate away and back to documentation page
# 3. Verify documentation persists and uses correct AI provider
```

## 🔧 Technical Implementation Details

### Fix 1: Replace Direct Ollama Calls in Documentation Generation

**Current Code Pattern**:
```python
# Direct HTTP call to Ollama (WRONG)
ollama_response = await client.post(
    f"{settings.OLLAMA_HOST}/api/generate",
    json={"model": "llama3.2:1b", "prompt": prompt, "stream": False}
)
```

**Corrected Code Pattern**:
```python
# Use model manager (CORRECT)
from app.core.model_providers import model_manager
from app.core.config import settings

response, token_count = await model_manager.call_model(
    model=settings.DOCUMENTATION_MODEL,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=4000,
    temperature=0.7
)
```

### Fix 2: Ensure Proper JSON Serialization

**Verify the fix in documentation_service.py is working**:
```python
def _extract_content(self, documentation_data: Dict[str, Any]) -> str:
    import json
    # ... existing code ...
    return json.dumps(doc_content, indent=2)  # This should be working
```

### Fix 3: Frontend State Management

**Verify React context is properly configured**:
- Check `DocumentationContext.jsx` is properly providing state
- Ensure navigation doesn't reset documentation state
- Verify API calls are made correctly

## 🧪 Testing Protocol

### Test 1: AI Provider Verification
1. Generate documentation for a repository
2. Check backend logs for model calls
3. Verify Anthropic API is used (not Ollama)

### Test 2: Documentation Persistence
1. Generate documentation
2. Navigate: Documentation → Functionalities → Documentation
3. Verify documentation content persists
4. Check all tabs (Overview, API Reference, Architecture, Usage Guide)

### Test 3: Environment Configuration
1. Verify `.env` settings are loaded correctly
2. Test model manager initialization
3. Check database connectivity

## 🚨 Potential Issues and Solutions

### Issue: "Module not found" errors
**Solution**: Ensure virtual environment is activated and dependencies installed

### Issue: Database connection errors
**Solution**: Check database file permissions and path

### Issue: API key errors
**Solution**: Verify Anthropic API key is valid and properly set

### Issue: Frontend build errors
**Solution**: Clear node_modules and rebuild frontend

## 📊 Success Criteria

✅ **Documentation Generation**: Uses Anthropic Claude models (not Ollama)  
✅ **Documentation Persistence**: Content persists through navigation  
✅ **Environment Configuration**: All settings loaded correctly  
✅ **End-to-End Functionality**: Complete workflow works without errors  

## 🔄 Rollback Plan

If issues persist:
1. Revert to previous working commit
2. Apply fixes incrementally
3. Test each change individually
4. Identify specific failure points

---

**This plan addresses both reported issues with systematic fixes and comprehensive testing.**