# build_exe.py
# ─────────────────────────────────────────────
# Compiles big_back_virus.py → standalone .exe with PyInstaller
# Automatically bundles entire 'resources' folder (or change the name)
# Does NOT run the prank — only builds the executable.
#
# Requirements:
#   pip install pyinstaller
#
# Usage:
#   python build_exe.py
#
# Output: dist/big_back_virus.exe (single file)
# ─────────────────────────────────────────────

import os
import sys
import subprocess

# ─────────────────────────────────────────────
# CONFIG – customize here
# ─────────────────────────────────────────────

SCRIPT_TO_COMPILE = "big_back_virus.py"          # your main prank script
EXE_NAME = "big_back_virus.exe"                  # final exe name

# Folder that contains music.mp3, byebyte.wav, bsod.png, images/, etc.
RESOURCES_FOLDER = "resources"                   # ← change if your folder has different name

ICON_PATH = None                                 # optional: "icon.ico" or full path

ONEFILE = True                                   # True = single .exe   False = folder
WINDOWED = True                                  # True = no console window (recommended for prank)
UPX_COMPRESS = False                             # True = smaller file (needs UPX installed)

# ─────────────────────────────────────────────
# MAIN BUILD LOGIC
# ─────────────────────────────────────────────

def main():
    if not os.path.isfile(SCRIPT_TO_COMPILE):
        print(f"Error: {SCRIPT_TO_COMPILE} not found in current directory.")
        sys.exit(1)

    print("Preparing to build standalone executable...\n")

    # Base PyInstaller command
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--name", os.path.splitext(EXE_NAME)[0],
    ]

    if ONEFILE:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if WINDOWED:
        cmd.append("--noconsole")   # hides console / no black window

    if ICON_PATH and os.path.isfile(ICON_PATH):
        cmd.extend(["--icon", ICON_PATH])

    if UPX_COMPRESS:
        cmd.append("--upx-dir")     # assumes UPX is in PATH; or specify path below
        # cmd.extend(["--upx-dir", r"C:\path\to\upx"])  # ← uncomment & edit if needed

    # ─────────────────────────────────────────────
    # Automatically add the entire resources folder
    # ─────────────────────────────────────────────
    if os.path.isdir(RESOURCES_FOLDER):
        print(f"Found resources folder: {RESOURCES_FOLDER}")
        # --add-data "resources;resources"  → keeps folder structure inside exe
        cmd.extend(["--add-data", f"{RESOURCES_FOLDER}{os.pathsep}{RESOURCES_FOLDER}"])
    else:
        print(f"Warning: '{RESOURCES_FOLDER}' folder not found → no extra files bundled.")

    # Add the main script last
    cmd.append(SCRIPT_TO_COMPILE)

    print("PyInstaller command:")
    print(" ".join(cmd))
    print("\n" + "="*80 + "\n")

    # Run PyInstaller
    try:
        subprocess.check_call(cmd, shell=False)
        print("\n" + "="*80)
        print("Build completed!")

        if ONEFILE:
            exe_path = os.path.join("dist", EXE_NAME)
            if os.path.isfile(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"→ Created: {exe_path}")
                print(f"  Size: ≈ {size_mb:.1f} MB")
                print("  (size depends on pygame, PIL, resources folder contents)")
            else:
                print("→ .exe not found in dist/ — check errors above")
        else:
            print(f"→ Output folder: dist/{os.path.splitext(EXE_NAME)[0]}")

        print("\nReady to test/distribute — run only in VM with snapshot!")
    
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed (code {e.returncode})")
        print("Check output above for errors (missing modules, paths, etc.)")
    except FileNotFoundError:
        print("\nPyInstaller not found. Install it first:")
        print("   pip install pyinstaller")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\nDone.")

if __name__ == "__main__":
    main()