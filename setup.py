#!/usr/bin/env python3
"""
Setup script for Meter CLI
Makes installation easier across different platforms
"""

import os
import sys
import shutil
from pathlib import Path

def setup_windows():
    """Setup for Windows environment"""
    print("Setting up Meter CLI for Windows...")
    
    # Detect if running in virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Virtual environment detected: {venv_path}")
        # Install in virtual environment's Scripts directory
        install_dir = Path(venv_path) / 'Scripts'
        python_exe = Path(venv_path) / 'Scripts' / 'python.exe'
    else:
        # Get user's local app data directory
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        install_dir = Path(appdata) / 'MeterCLI'
        python_exe = 'python'
    
    # Create installation directory
    install_dir.mkdir(exist_ok=True)
    
    # Copy main script
    shutil.copy2('meter_cli.py', install_dir / 'meter_cli.py')
    
    # Create batch file for easy execution
    batch_content = f'@echo off\n"{python_exe}" "{install_dir / "meter_cli.py"}" %*'
    batch_file = install_dir / 'meter-cli.bat'
    
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"Meter CLI installed to: {install_dir}")
    print(f"Batch file created: {batch_file}")
    
    if venv_path:
        print("\nInstalled in virtual environment. Activate the environment and use:")
        print("  meter-cli")
    else:
        print("\nTo use globally, add the following directory to your PATH:")
        print(f"  {install_dir}")
        print("\nOr run directly with:")
        print(f"  {batch_file}")

def setup_unix():
    """Setup for Unix-like systems (macOS, Linux)"""
    print("Setting up Meter CLI for Unix-like system...")
    
    # Make script executable
    os.chmod('meter_cli.py', 0o755)
    
    # Detect if running in virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    script_path = Path.cwd() / 'meter_cli.py'
    
    if venv_path:
        print(f"Virtual environment detected: {venv_path}")
        # Install in virtual environment's bin directory
        venv_bin = Path(venv_path) / 'bin'
        symlink_path = venv_bin / 'meter-cli'
        
        try:
            if symlink_path.exists():
                symlink_path.unlink()
            symlink_path.symlink_to(script_path)
            print(f"Symlink created: {symlink_path} -> {script_path}")
            print("\nInstalled in virtual environment. Activate the environment and use:")
            print("  meter-cli")
        except OSError as e:
            print(f"Could not create symlink: {e}")
            print(f"You can run the script directly: python3 {script_path}")
    else:
        # Try to create symlink in user's local bin
        local_bin = Path.home() / '.local' / 'bin'
        local_bin.mkdir(parents=True, exist_ok=True)
        symlink_path = local_bin / 'meter-cli'
        
        try:
            if symlink_path.exists():
                symlink_path.unlink()
            symlink_path.symlink_to(script_path)
            print(f"Symlink created: {symlink_path} -> {script_path}")
            print("\nMake sure ~/.local/bin is in your PATH")
            print("Add this to your shell profile if needed:")
            print("  export PATH=\"$HOME/.local/bin:$PATH\"")
        except OSError as e:
            print(f"Could not create symlink: {e}")
            print(f"You can run the script directly: python3 {script_path}")

def main():
    """Main setup function"""
    print("Meter CLI Setup")
    print("===============")
    
    # Check for virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Running in virtual environment: {Path(venv_path).name}")
    else:
        print("Running in system Python environment")
    
    if not Path('meter_cli.py').exists():
        print("Error: meter_cli.py not found in current directory")
        sys.exit(1)
    
    if sys.platform.startswith('win'):
        setup_windows()
    else:
        setup_unix()
    
    print("\nSetup complete!")
    print("\nTest the installation with:")
    if venv_path:
        print("  meter-cli --version")
        print("  (make sure your virtual environment is activated)")
    else:
        if sys.platform.startswith('win'):
            print("  meter-cli --version")
        else:
            print("  meter-cli --version")
            print("  or: python3 meter_cli.py --version")

if __name__ == '__main__':
    main()