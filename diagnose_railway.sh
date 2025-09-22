#!/bin/bash

# 🔧 Railway Build/Publish Diagnostic Script
# Helps identify and fix common Railway deployment issues

echo "🔧 RAILWAY BUILD/PUBLISH DIAGNOSTICS"
echo "====================================="
echo ""

echo "📋 CHECKING PROJECT CONFIGURATION"
echo "--------------------------------"

# Check Python version
echo "🐍 Python Version:"
if [ -f "runtime.txt" ]; then
    echo "   runtime.txt: $(cat runtime.txt)"
else
    echo "   No runtime.txt found (Railway will use default Python)"
fi
echo ""

# Check main application file
echo "📁 Application Entry Point:"
if [ -f "app.py" ]; then
    echo "   ✅ app.py found"
else
    echo "   ❌ app.py not found!"
fi

if [ -f "main.py" ]; then
    echo "   ℹ️  main.py also exists"
fi
echo ""

# Check Railway configuration
echo "🚂 Railway Configuration:"
if [ -f "railway.toml" ]; then
    echo "   ✅ railway.toml found"
    echo "   Start command: $(grep 'startCommand' railway.toml | cut -d'"' -f2)"
else
    echo "   ⚠️  No railway.toml (Railway will auto-detect)"
fi

if [ -f "nixpacks.toml" ]; then
    echo "   ✅ nixpacks.toml found"
    echo "   Start cmd: $(grep 'cmd' nixpacks.toml | cut -d'"' -f2)"
fi
echo ""

# Check requirements
echo "📦 Dependencies:"
if [ -f "requirements.txt" ]; then
    echo "   ✅ requirements.txt found ($(wc -l < requirements.txt) lines)"
    
    # Check for critical dependencies
    echo "   🔍 Critical dependencies:"
    if grep -q "fastapi" requirements.txt; then
        echo "      ✅ FastAPI: $(grep fastapi requirements.txt | head -1)"
    else
        echo "      ❌ FastAPI not found!"
    fi
    
    if grep -q "uvicorn" requirements.txt; then
        echo "      ✅ Uvicorn: $(grep uvicorn requirements.txt | head -1)"
    else
        echo "      ❌ Uvicorn not found!"
    fi
    
    if grep -q "pydantic" requirements.txt; then
        echo "      ✅ Pydantic: $(grep pydantic requirements.txt | head -1)"
    else
        echo "      ❌ Pydantic not found!"
    fi
else
    echo "   ❌ requirements.txt not found!"
fi
echo ""

# Check environment files
echo "🌍 Environment Configuration:"
env_files=(.env.example .env.production.ready .env.railway)
for file in "${env_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file found"
    fi
done
echo ""

# Check for common issues
echo "🚨 COMMON ISSUES CHECK"
echo "--------------------"

# Check for Python path issues
echo "🔍 Import Issues:"
if python3 -c "import app" 2>/dev/null; then
    echo "   ✅ app.py imports successfully"
else
    echo "   ❌ app.py import failed - check for syntax/import errors"
fi
echo ""

# Check Railway status
echo "🚂 Railway Project Status:"
if railway status 2>/dev/null; then
    echo "   ✅ Railway project linked"
else
    echo "   ⚠️  Railway project not linked or not logged in"
    echo "   Try: railway login && railway link"
fi
echo ""

echo "🎯 RECOMMENDED ACTIONS"
echo "====================="
echo ""
echo "1. 🔧 Fix Configuration Issues (if any found above)"
echo ""
echo "2. 🚂 Link Railway Project:"
echo "   railway login"
echo "   railway link"
echo ""
echo "3. 📋 Check Railway Logs:"
echo "   railway logs"
echo ""
echo "4. 🔄 Trigger New Deployment:"
echo "   git push origin main"
echo ""
echo "5. 🌐 Check Environment Variables:"
echo "   Go to Railway Dashboard → Your Project → Variables"
echo "   Ensure these are set:"
echo "   - OPENAI_API_KEY"
echo "   - JWT_SECRET_KEY"
echo "   - API_BEARER"
echo "   - USE_LIVE=true"
echo ""

echo "💡 If you're still having issues, please share:"
echo "   - The specific error message"
echo "   - Railway logs (railway logs)"
echo "   - Build output from Railway dashboard"
