import os
import shutil
import subprocess
import sys

"""
Materials Informatics Pipeline: Clean Slate Rebuild Script
This script purges all generated data/models and re-executes the entire ML pipeline.
"""

def purge_artifacts():
    print("--- Phase 1: The Great Purge (Cleanup) ---")
    
    # Extensions to delete
    extensions_to_purge = ['.csv', '.pkl']
    # Directories to delete
    dirs_to_purge = ['__pycache__', '.pytest_cache']
    
    deleted_files_count = 0
    deleted_dirs_count = 0

    # Walk through root and production/ directory
    for root_dir in ['.', 'production']:
        if not os.path.exists(root_dir):
            continue
            
        for root, dirs, files in os.walk(root_dir):
            # Protect critical directories from traversal
            for protected in ['venv', '.git', 'node_modules', 'dist']:
                if protected in dirs:
                    dirs.remove(protected)
                    
            # 1. Purge Files
            for file in files:
                if any(file.endswith(ext) for ext in extensions_to_purge):
                    # SAFETY: Do not delete config or source files (extra check)
                    if file in ['requirements.txt', 'package.json', 'package-lock.json']:
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted_files_count += 1
                        print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

            # 2. Purge Directories
            # We iterate in reverse to allow modifying the list during iteration
            for d in list(dirs):
                if d in dirs_to_purge:
                    dir_path = os.path.join(root, d)
                    try:
                        shutil.rmtree(dir_path)
                        deleted_dirs_count += 1
                        print(f"Deleted directory: {dir_path}")
                        # Remove from 'dirs' so walk doesn't try to enter it
                        dirs.remove(d)
                    except Exception as e:
                        print(f"Error deleting {dir_path}: {e}")

    print(f"Purge complete: {deleted_files_count} files and {deleted_dirs_count} directories removed.\n")

def run_script(script_name):
    """Utility to run a python script using the current interpreter."""
    print(f"Executing: {script_name}...")
    try:
        # We use sys.executable to ensure we use the same venv
        result = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(f"Finished {script_name} successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! CRITICAL ERROR executing {script_name} !!!")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def rebuild_pipeline():
    print("--- Phase 2: The Sequential Rebuild ---")
    
    pipeline_scripts = [
        "code_1_generate.py",
        "code_2_structural.py",
        "code_3_polybert.py",
        "code_4_physical.py",
        "code_5_morgan.py",
        "code_6_main.py",
        "code_7_train_model.py"
    ]
    
    for script in pipeline_scripts:
        if not os.path.exists(script):
            print(f"Warning: {script} not found in root. Skipping.")
            continue
            
        success = run_script(script)
        if not success:
            print("\nRebuild failed at a critical step. Aborting.")
            return

    print("\n" + "="*60)
    print("PIPELINE REBUILT SUCCESSFULLY!")
    print("Please restart your Docker containers or Uvicorn server to load the fresh ML models into RAM.")
    print("="*60)

if __name__ == "__main__":
    # Ensure we are in the project root
    purge_artifacts()
    rebuild_pipeline()
