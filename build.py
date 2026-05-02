"""
build.py — Build Cosmic Byte Ares Controller Manager as .exe
Usage: python build.py
"""

import subprocess
import os


def build():
    print("🔨 Building Cosmic Byte Ares Controller Manager .exe ...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=CosmicByteAresManager",
        "--add-data=profiles;profiles",
        "main.py"
    ]

    if os.path.exists("assets/icon.ico"):
        cmd.insert(4, "--icon=assets/icon.ico")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Build successful!")
        print("📁 Your .exe is in the 'dist' folder: dist/CosmicByteAresManager.exe")
    else:
        print("\n❌ Build failed. Check the errors above.")


if __name__ == "__main__":
    build()
