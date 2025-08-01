#!/usr/bin/env python3
"""
Test script to verify setup and dependencies
"""

import sys
import subprocess
import os
from pathlib import Path

def test_dependency(name, command=None):
    """Test if a dependency is available"""
    if command is None:
        command = name
    
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: Failed (exit code {result.returncode})")
            return False
    except FileNotFoundError:
        print(f"❌ {name}: Not found")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ {name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def test_python_import(module_name):
    """Test if a Python module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ Python {module_name}: OK")
        return True
    except ImportError:
        print(f"❌ Python {module_name}: Not installed")
        return False

def test_directory(path, description):
    """Test if a directory exists and is accessible"""
    path_obj = Path(path)
    if path_obj.exists():
        if path_obj.is_dir():
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: Exists but is not a directory")
            return False
    else:
        print(f"⚠️  {description}: Not found (will be created when needed)")
        return True

def main():
    print("=== Testing Large Archive Import Setup ===\n")
    
    all_passed = True
    
    # Test system dependencies
    print("System Dependencies:")
    deps = [
        ("osxphotos", "osxphotos"),
        ("exiftool", "exiftool"),
        ("jq", "jq"),
        ("bc", "bc"),
        ("python3", "python3"),
    ]
    
    for name, command in deps:
        if not test_dependency(name, command):
            all_passed = False
    
    print("\nPython Dependencies:")
    python_deps = ["PIL", "exiftool"]
    for dep in python_deps:
        if not test_python_import(dep):
            all_passed = False
    
    print("\nDirectories:")
    dirs = [
        ("/Volumes/SlowDisk/iCloud", "Source directory"),
        ("/tmp", "Temporary directory"),
    ]
    
    for path, desc in dirs:
        if not test_directory(path, desc):
            all_passed = False
    
    print("\nScripts:")
    scripts = [
        ("import_large_archive.sh", "Main import script"),
        ("date_fixer.py", "Date fixer script"),
        ("import_status.py", "Status checker script"),
        ("setup_import.sh", "Setup script"),
    ]
    
    for script, desc in scripts:
        script_path = Path(script)
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"✅ {desc}: OK")
            else:
                print(f"❌ {desc}: Not executable")
                all_passed = False
        else:
            print(f"❌ {desc}: Not found")
            all_passed = False
    
    print("\n=== Summary ===")
    if all_passed:
        print("✅ All tests passed! System is ready for import.")
        print("\nNext steps:")
        print("1. Ensure /Volumes/SlowDisk/iCloud contains your photo archive")
        print("2. Run: ./import_large_archive.sh")
        print("3. Monitor progress: python3 import_status.py status")
    else:
        print("❌ Some tests failed. Please run ./setup_import.sh to fix issues.")
        print("\nMissing dependencies will be installed automatically.")

if __name__ == "__main__":
    main() 