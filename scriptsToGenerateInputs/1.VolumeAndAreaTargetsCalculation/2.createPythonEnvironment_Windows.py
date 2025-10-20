import urllib.request
import zipfile
import os
import sys
import subprocess
from pathlib import Path

def download_file(url, destination):
    """Download a file from URL to destination."""
    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, destination)
    print(f"Saved to: {destination}")

def extract_filtered_zip(zip_path, extract_to, include_string, exclude_strings):
    """Extract only files containing include_string and not containing any exclude_strings from zip."""
    print(f"Extracting files containing '{include_string}'...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        filtered_files = []
        for f in zip_ref.namelist():
            if include_string in f and not any(excl in f for excl in exclude_strings):
                filtered_files.append(f)

        for file in filtered_files:
            zip_ref.extract(file, extract_to)
            print(f"  Extracted: {file}")
    print(f"Extraction complete. {len(filtered_files)} files extracted.")

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    python_env_dir = script_dir / "PythonEnv"

    # Step 1: Create Python environment and install packages
    print("\n=== Step 1: Creating Python environment ===")

    # Create virtual environment
    print(f"Creating virtual environment in {python_env_dir}...")
    subprocess.run([sys.executable, "-m", "venv", str(python_env_dir)], check=True)

    # Determine python path based on OS
    if sys.platform == "win32":
        python_path = python_env_dir / "Scripts" / "python.exe"
    else:
        python_path = python_env_dir / "bin" / "python"

    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # Install packages
    packages = ["rasterio", "numpy", "geopandas", "gdal-installer"]

    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([str(python_path), "-m", "pip", "install", package], check=True)
        
    # Finish by installing gdal-installer
    print(f"Preactivating python environment and installing GDAL...")
    subprocess.run("cd PythonEnv/Scripts && activate.bat && install-gdal.exe", shell=True)

    print("\n=== Setup Complete ===")
    print(f"Python environment created at: {python_env_dir}")
    print("\nTo activate the environment:")
    if sys.platform == "win32":
        print(f"  {python_env_dir}\\Scripts\\activate")
    else:
        print(f"  source {python_env_dir}/bin/activate")

if __name__ == "__main__":
    main()
