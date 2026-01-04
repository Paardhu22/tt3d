"""
Quick setup and verification script for Tsuana 3D World Generator.
Run this to verify your installation and API keys.
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Verify Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. You have:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = {
        "dotenv": "python-dotenv",
        "requests": "requests",
        "openai": "openai",
        "numpy": "numpy"
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"    pip install {' '.join(missing)}")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Copy .env.template to .env and add your API keys")
        return False
    
    print("✅ .env file exists")
    
    # Check for required keys
    required_keys = ["OPENAI_API_KEY", "TRIPO_API_KEY"]
    missing_keys = []
    
    with open(env_path) as f:
        content = f.read()
        for key in required_keys:
            if f"{key}=" in content:
                value = [line for line in content.split('\n') if line.startswith(f"{key}=")]
                if value and "your_" not in value[0] and value[0].split('=')[1].strip():
                    print(f"✅ {key} configured")
                else:
                    print(f"⚠️  {key} needs to be set")
                    missing_keys.append(key)
            else:
                print(f"❌ {key} missing")
                missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️  Update these keys in .env:")
        for key in missing_keys:
            if key == "OPENAI_API_KEY":
                print(f"    {key}=sk-...  (from https://platform.openai.com/api-keys)")
            elif key == "TRIPO_API_KEY":
                print(f"    {key}=tsk-... (from https://platform.tripo3d.ai/)")
        return False
    
    return True

def check_project_structure():
    """Verify all required files exist"""
    required_files = [
        "main.py",
        "tsuana.py",
        "user_profile.py",
        "prompts.py",
        "threed_generator.py",
        "scene_composer.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            missing.append(file)
    
    return len(missing) == 0

def main():
    """Run all setup checks"""
    print("=" * 50)
    print("   TSUANA 3D World Generator - Setup Check")
    print("=" * 50)
    
    print("\n1. Checking Python version...")
    python_ok = check_python_version()
    
    print("\n2. Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n3. Checking environment configuration...")
    env_ok = check_env_file()
    
    print("\n4. Checking project structure...")
    structure_ok = check_project_structure()
    
    print("\n" + "=" * 50)
    
    if python_ok and deps_ok and env_ok and structure_ok:
        print("✅ All checks passed! You're ready to generate 3D worlds.")
        print("\n🚀 Run: python main.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n📖 See README.md for detailed setup instructions")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
