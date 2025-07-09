# Kairos Integration Setup Guide

## 🚀 Complete Setup Instructions

This guide provides detailed step-by-step instructions to set up the Kairos Integration Framework for automated TradingView strategy testing.

## 📋 Prerequisites

- Python 3.10 or higher
- Chrome or Chromium browser
- TradingView account
- Google account (grimm@greysson.com)
- Internet connection

## 🔧 Step 1: Install Python Dependencies

### 1.1 Navigate to Project Directory
```bash
cd /home/grimm/gits/trading-setups
```

### 1.2 Install Required Packages
```bash
# Install all integration framework dependencies
pip install -r kairos_integration/requirements.txt
```

### 1.3 Verify Installation
```bash
# Test that the framework loads without errors
python -c "
try:
    from kairos_integration import GrimmAuthManager
    print('✅ Kairos Integration Framework installed successfully')
except ImportError as e:
    print(f'❌ Installation error: {e}')
"
```

## 🔐 Step 2: Google OAuth Setup (Detailed)

### 2.1 Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with grimm@greysson.com

2. **Create New Project (if needed)**
   - Click "Select a project" dropdown at top
   - Click "New Project"
   - Project name: "Kairos Trading Integration"
   - Click "Create"

3. **Select Your Project**
   - Ensure the correct project is selected in the dropdown

### 2.2 Enable Required APIs

1. **Navigate to APIs & Services**
   - Left sidebar: "APIs & Services" → "Library"

2. **Enable Google+ API**
   - Search for "Google+ API"
   - Click on it and click "Enable"
   - (Note: This API is needed for basic profile access)

3. **Enable People API (Alternative)**
   - If Google+ API is not available, search for "People API"
   - Click on it and click "Enable"

### 2.3 Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"

2. **Create Credentials**
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"

3. **Configure OAuth Consent Screen** (if prompted)
   - Click "Configure Consent Screen"
   - User Type: "External" (unless you have Google Workspace)
   - Click "Create"

4. **Fill OAuth Consent Screen**
   - App name: "Kairos Trading Integration"
   - User support email: grimm@greysson.com
   - Developer contact: grimm@greysson.com
   - Click "Save and Continue"

5. **Add Scopes**
   - Click "Add or Remove Scopes"
   - Add these scopes:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
     - `openid`
   - Click "Save and Continue"

6. **Add Test Users**
   - Click "Add Users"
   - Add: grimm@greysson.com
   - Click "Save and Continue"

7. **Create OAuth Client ID**
   - Go back to "Credentials"
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "Kairos Integration Client"
   - Click "Create"

### 2.4 Download Credentials

1. **Download JSON File**
   - After creating, you'll see a dialog with client ID and secret
   - Click "Download JSON"
   - Save the file

2. **Rename and Move File**
   ```bash
   # Move the downloaded file to your project root and rename it
   mv ~/Downloads/client_secret_*.json /home/grimm/gits/trading-setups/credentials.json
   ```

3. **Verify File Location**
   ```bash
   # Check that the file is in the correct location
   ls -la /home/grimm/gits/trading-setups/credentials.json
   ```

## 🧪 Step 3: Test Authentication

### 3.1 Run Authentication Test
```bash
cd /home/grimm/gits/trading-setups

python -c "
from kairos_integration import GrimmAuthManager
import sys

print('🔐 Testing Google OAuth authentication...')
try:
    auth = GrimmAuthManager()
    print('✅ Auth manager created successfully')
    print('📁 Credentials file found')
    print('🚀 Ready for authentication!')
    print()
    print('Next: Run auth.authenticate() to start OAuth flow')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"
```

### 3.2 Run Full Authentication Flow
```bash
python -c "
import asyncio
from kairos_integration import GrimmAuthManager

async def test_auth():
    print('🔐 Starting OAuth authentication flow...')
    print('📧 Account: grimm@greysson.com')
    print()
    
    auth = GrimmAuthManager()
    
    # This will open browser and prompt for OAuth
    success = auth.authenticate()
    
    if success:
        print('✅ Authentication successful!')
        print(f'📧 Authenticated as: {auth.get_user_email()}')
        print('💾 Tokens cached for future use')
        return True
    else:
        print('❌ Authentication failed')
        return False

# Run the test
result = asyncio.run(test_auth())
print(f'Final result: {\"SUCCESS\" if result else \"FAILED\"}')
"
```

**Expected Flow:**
1. Browser will open automatically
2. You'll be redirected to Google OAuth page
3. Sign in with grimm@greysson.com
4. Grant permissions to the application
5. Browser will show success page or redirect
6. Authentication tokens will be cached locally

## 🚀 Step 4: Test Integration Framework

### 4.1 Run Quick Demo
```bash
# Test the framework with simulated data
python run_integration_demo.py
```

### 4.2 Test Real Integration Components
```bash
python -c "
import asyncio
from kairos_integration import (
    GrimmAuthManager, 
    TradingViewTestRunner,
    StrategyBacktester,
    ChartScreenshotManager,
    CompleteWorkflow
)

async def test_components():
    print('🧪 Testing all integration components...')
    
    # Test authentication
    auth = GrimmAuthManager()
    if not auth.is_authenticated():
        print('⚠️  Not authenticated yet - run authentication first')
        return False
    
    print('✅ Authentication: OK')
    
    # Test component initialization
    try:
        test_runner = TradingViewTestRunner(auth)
        backtester = StrategyBacktester(auth)
        screenshot_manager = ChartScreenshotManager(auth)
        workflow = CompleteWorkflow()
        
        print('✅ Test Runner: OK')
        print('✅ Backtester: OK') 
        print('✅ Screenshot Manager: OK')
        print('✅ Complete Workflow: OK')
        print()
        print('🎉 All components initialized successfully!')
        print('🚀 Framework ready for strategy testing!')
        return True
        
    except Exception as e:
        print(f'❌ Component test failed: {e}')
        return False

asyncio.run(test_components())
"
```

## 📊 Step 5: Test with Real Strategy

### 5.1 Create Example Strategy
```bash
# The demo script creates an example strategy automatically
python run_integration_demo.py

# Check that it was created
ls -la strategies/example-rsi-strategy/
```

### 5.2 Run Complete Workflow Test
```bash
python -c "
import asyncio
from kairos_integration import CompleteWorkflow

async def test_real_workflow():
    print('🚀 Testing complete workflow with real strategy...')
    print('📈 Strategy: example-rsi-strategy')
    print('🎯 Ticker: MNQ1!')
    print()
    
    try:
        workflow = CompleteWorkflow()
        
        # This will run the complete workflow:
        # 1. Authentication check
        # 2. Strategy loading
        # 3. Indicator testing (if authenticated)
        # 4. Backtesting (if authenticated)
        # 5. Screenshots (if authenticated)
        # 6. Report generation
        
        results = await workflow.run_complete_workflow('strategies/example-rsi-strategy')
        
        print(f'📊 Results:')
        print(f'   Overall Success: {results[\"overall_success\"]}')
        print(f'   Authentication: {results[\"authentication\"][\"success\"]}')
        print(f'   Strategy: {results[\"strategy_name\"]}')
        
        if results['overall_success']:
            print('🎉 Complete workflow test PASSED!')
            print('✅ Framework fully operational!')
        else:
            print('⚠️  Some components need authentication')
            print('💡 Run authentication first for full testing')
            
        return results['overall_success']
        
    except Exception as e:
        print(f'❌ Workflow test failed: {e}')
        return False

success = asyncio.run(test_real_workflow())
print(f'Final test result: {\"PASSED\" if success else \"NEEDS_AUTH\"}')
"
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Issues

**Issue**: `Authentication failed`
```bash
# Solutions:
# 1. Check credentials file exists
ls -la credentials.json

# 2. Verify file format
head -5 credentials.json  # Should show JSON structure

# 3. Clear cached tokens and retry
rm -rf ~/.kairos_auth/
python -c "from kairos_integration import GrimmAuthManager; GrimmAuthManager().authenticate()"
```

**Issue**: `Browser doesn't open for OAuth`
```bash
# Solutions:
# 1. Check if running in SSH session
echo $SSH_CLIENT  # If shows IP, you're in SSH

# 2. Forward X11 for GUI (if SSH)
ssh -X username@hostname

# 3. Or copy the OAuth URL manually when prompted
```

#### 2. Import Errors

**Issue**: `ImportError: No module named 'kairos_integration'`
```bash
# Solutions:
# 1. Ensure you're in the right directory
pwd  # Should be /home/grimm/gits/trading-setups

# 2. Install dependencies
pip install -r kairos_integration/requirements.txt

# 3. Check Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

**Issue**: `ImportError: No module named 'tv.core'`
```bash
# Solutions:
# 1. Add grimm-kairos to Python path
export PYTHONPATH="${PYTHONPATH}:/home/grimm/gits/grimm-kairos"

# 2. Or add to .bashrc for permanent
echo 'export PYTHONPATH="${PYTHONPATH}:/home/grimm/gits/grimm-kairos"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Browser Issues

**Issue**: `WebDriver not found`
```bash
# Solutions:
# 1. Update Chrome
sudo apt update && sudo apt upgrade google-chrome-stable

# 2. Clear WebDriver cache
rm -rf ~/.cache/selenium

# 3. Install Chromium as fallback
sudo apt install chromium-browser
```

#### 4. Permission Issues

**Issue**: `Permission denied` errors
```bash
# Solutions:
# 1. Fix credentials file permissions
chmod 600 credentials.json

# 2. Fix auth cache directory permissions
chmod -R 700 ~/.kairos_auth/

# 3. Ensure Python packages are accessible
pip install --user -r kairos_integration/requirements.txt
```

### Getting Help

#### Check Logs
```bash
# Enable debug logging
export KAIROS_LOG_LEVEL=DEBUG

# Run with verbose output
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from kairos_integration import GrimmAuthManager
auth = GrimmAuthManager()
"
```

#### Test Individual Components
```bash
# Test just authentication
python -c "from kairos_integration import GrimmAuthManager; print('Auth OK')"

# Test just configuration
python -c "from kairos_integration.config import create_mnq_config; print('Config OK')"

# Test just workflow
python -c "from kairos_integration import CompleteWorkflow; print('Workflow OK')"
```

## ✅ Verification Checklist

After completing setup, verify everything works:

- [ ] Python dependencies installed (`pip list | grep selenium`)
- [ ] Credentials file exists (`ls credentials.json`)
- [ ] Authentication works (`auth.authenticate()` succeeds)
- [ ] Components load (`from kairos_integration import *`)
- [ ] Demo runs successfully (`python run_integration_demo.py`)
- [ ] Real workflow initializes (even if not fully functional without TradingView)

## 🎉 You're Ready!

Once all steps are complete, you can use the full Kairos Integration Framework:

```python
from kairos_integration import CompleteWorkflow

# Run complete automated strategy testing
workflow = CompleteWorkflow()
results = await workflow.run_complete_workflow("strategies/my-strategy")
```

**Features available:**
- ✅ Google OAuth authentication for grimm@greysson.com
- ✅ Automated TradingView indicator testing
- ✅ Comprehensive strategy backtesting  
- ✅ Automated chart screenshot capture
- ✅ MNQ1! futures optimization
- ✅ End-to-end workflow automation

---

**Setup Complete**: 🎉 **Ready for automated strategy testing!**