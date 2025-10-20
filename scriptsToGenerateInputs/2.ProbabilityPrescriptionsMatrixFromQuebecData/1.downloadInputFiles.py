import urllib.request
import zipfile
import os
import sys
import subprocess
from pathlib import Path

def progress_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100)
    sys.stdout.write(f"\rDownloading: {percent:.1f}%")
    sys.stdout.flush()

def download_file(url, destination):
    """Download a file from URL to destination if it doesn't already exist."""
    if destination.exists():
        print(f"File already exists, skipping: {destination.name}")
        return False

    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, destination, reporthook=progress_hook)
    print(f"Saved to: {destination}")
    return True

def extract_filtered_zip(zip_path, extract_to, include_string="", exclude_strings=[]):
    """Extract only files containing include_string and not containing any exclude_strings from zip."""
    print(f"Extracting files containing '{include_string}'...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        filtered_files = []
        for f in zip_ref.namelist():
            if include_string in f and not any(excl in f for excl in exclude_strings):
                filtered_files.append(f)

        for file in filtered_files:
            file_path = extract_to / file
            if file_path.exists():
                print(f"  Already exists, skipping: {file}")
            else:
                zip_ref.extract(file, extract_to)
                print(f"  Extracted: {file}")
    print(f"Extraction complete.")

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    input_data_dir = script_dir / "InputData"

    # Create directories
    input_data_dir.mkdir(exist_ok=True)

    # Step 1: Download and extract provincial forest inventory data
    print("\n=== Step 1: Downloading provincial forest inventory data ===")
    ne_zip_url = "https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/DONNEES_FOR_ECO_SUD/Resultats_inventaire_et_carte_ecofor/02-Donnees/PROV/CARTE_ECO_ORI_PROV_GDB.zip"
    ne_zip_path = input_data_dir / "CARTE_ECO_ORI_PROV_GDB.zip"

    downloaded = download_file(ne_zip_url, ne_zip_path)

    if downloaded or ne_zip_path.exists():
        extract_filtered_zip(
            ne_zip_path, 
            input_data_dir
        )

        # Delete the zip file
        ne_zip_path.unlink()
        print(f"Deleted: {ne_zip_path}")
        
    # Step 2: Download and extract Quebec forest operations data
    print("\n=== Step 2: Downloading Quebec forest operations data ===")
    ne_zip_url = "https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/INTERVENTIONS_FORESTIERES/Recolte_et_reboisement/02-Donnees/PROV/INTERV_FORES_PROV_GDB.zip"
    ne_zip_path = input_data_dir / "INTERV_FORES_PROV_GDB.zip"

    downloaded = download_file(ne_zip_url, ne_zip_path)

    if downloaded or ne_zip_path.exists():
        extract_filtered_zip(
            ne_zip_path, 
            input_data_dir
        )

        # Delete the zip file
        ne_zip_path.unlink()
        print(f"Deleted: {ne_zip_path}")

    print("\n=== Setup Complete ===")
    print(f"Data downloaded to: {input_data_dir}")

if __name__ == "__main__":
    main()
