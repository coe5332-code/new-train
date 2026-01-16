"""
Quick verification script to check if the environment is set up correctly
for deployment.
"""

import os
import sys

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment setup...\n")
    
    errors = []
    warnings = []
    
    # Check required environment variables
    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API key",
        "UNSPLASH_ACCESS_KEY": "Unsplash API access key"
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var} ({description}) is not set")
        elif len(value) < 10:
            warnings.append(f"⚠️  {var} seems too short, please verify")
        else:
            print(f"✅ {var} is set")
    
    # Check optional variables
    imagemagick = os.getenv("IMAGEMAGICK_BINARY")
    if imagemagick:
        if not os.path.exists(imagemagick):
            warnings.append(f"⚠️  IMAGEMAGICK_BINARY path doesn't exist: {imagemagick}")
        else:
            print(f"✅ IMAGEMAGICK_BINARY is set: {imagemagick}")
    else:
        print("ℹ️  IMAGEMAGICK_BINARY not set (will use system PATH if available)")
    
    # Check directories
    required_dirs = ["output_videos", "images", "generated_pdfs"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created directory: {dir_name}")
            except Exception as e:
                errors.append(f"❌ Cannot create directory {dir_name}: {e}")
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    # Check Python packages
    print("\n📦 Checking Python packages...")
    required_packages = [
        "streamlit",
        "google.genai",
        "edge_tts",
        "moviepy",
        "PIL",
        "requests",
        "pymupdf",
        "reportlab"
    ]
    
    for package in required_packages:
        try:
            if package == "PIL":
                __import__("PIL")
            elif package == "google.genai":
                __import__("google.genai")
            else:
                __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            errors.append(f"❌ {package} is not installed")
    
    # Summary
    print("\n" + "="*50)
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  {error}")
        print("\nPlease fix these errors before deployment.")
        return False
    else:
        print("✅ All checks passed!")
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
        print("\n🚀 Your environment is ready for deployment!")
        return True

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)

