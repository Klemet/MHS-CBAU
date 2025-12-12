# -*- coding: utf-8 -*-

import subprocess
import sys
import tempfile
from pathlib import Path
import urllib.request
import zipfile
import csv
import json
import os
import shutil

def download_file(url, filename):
    """Download a file from URL"""
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded {filename}")

def read_tsv(filename):
    """Read tab-separated file into list of dictionaries"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return list(reader)

def merge_wood_density_data():
    """Merge measurements and occurrences data"""
    print("Merging wood density data...")

    measurements = read_tsv('measurements or facts.txt')
    occurrences = read_tsv('occurrences.txt')

    # Create lookup dictionary for occurrences
    occ_dict = {row['OccurrenceID']: row for row in occurrences}

    # Merge data
    wood_density_data = []
    for meas in measurements:
        occ_id = meas.get('Occurrence ID', '')
        occ = occ_dict.get(occ_id, {})

        try:
            density_value = float(meas.get('Measurement Value', ''))
        except (ValueError, TypeError):
            continue

        wood_density_data.append({
            'SpeciesName': occ.get('TaxonID', ''),
            'WorldRegion': occ.get('Locality', ''),
            'WoodDensity_MetricTons_per_m3': density_value
        })

    print(f"Total records: {len(wood_density_data)}")
    print(f"Unique species: {len(set(row['SpeciesName'] for row in wood_density_data))}")

    return wood_density_data

def create_nfi_species_mapping(csv_file):
    """Create mapping from scientific name to GENU.SPE code"""
    print("Creating NFI species mapping...")

    mapping = {}
    nfi_codes = set()

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scientific_name = row.get('Scientific Name', '').strip()
            genus_code = row.get('Code Genus', '').strip()
            species_code = row.get('Species', '').strip()

            if scientific_name and genus_code and species_code:
                genu_spe_code = f"{genus_code}.{species_code}"
                mapping[scientific_name] = genu_spe_code
                nfi_codes.add(genu_spe_code)

    print(f"Created mapping for {len(mapping)} species")
    print(f"Found {len(nfi_codes)} unique NFI codes")

    return mapping, nfi_codes

def main():
    wood_db_url = "https://nfi.nfis.org/resources/general/3-TreeSpeciesList-Version4.5.pdf"
    download_file(wood_db_url, "3-TreeSpeciesList-Version4.5.pdf")
    
    # Create temporary directory for virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "venv"

        # Create virtual environment
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

        # Determine pip and python paths based on OS
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"

        # Install camelot-py with opencv support
        print("Installing camelot-py...")
        subprocess.run([
            str(pip_path), "install", "camelot-py"
        ], check=True, capture_output=True)

        print("Installing pandas...")
        subprocess.run([
            str(pip_path), "install", "pandas"
        ], check=True, capture_output=True)

        # Use camelot in the virtual environment
        print("Running camelot...")
        code = """
import camelot
import pandas as pd

# Extract all tables
tables = camelot.read_pdf('3-TreeSpeciesList-Version4.5.pdf', pages='all')

# Process tables with two header rows
dataframes = []
for table in tables:
    df = table.df

    # Combine two header rows into single column names
    new_columns = []
    for i in range(len(df.columns)):
        header1 = str(df.iloc[0, i]).strip()
        header2 = str(df.iloc[1, i]).strip()
        combined = f"{header1} {header2}".strip()
        new_columns.append(combined)

    # Set new column names and remove header rows
    df.columns = new_columns
    df = df.iloc[2:].reset_index(drop=True)

    dataframes.append(df)

# Merge all tables into one
merged_df = pd.concat(dataframes, ignore_index=True)

# Remove all \\n characters from all cells
merged_df = merged_df.replace('\\n', '', regex=True)

# Save to CSV
merged_df.to_csv('NFI_Species_Codes.csv', index=False)
    """
        try:
            subprocess.run([str(python_path), "-c", code], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(f"Error output: {e.stderr}")
        except FileNotFoundError:
            print("Error: The command was not found. Please ensure it's in your PATH.")

        # Virtual environment is automatically cleaned up when exiting
    
    # Step 1: Download and extract wood density database
    wood_db_url = "https://zenodo.org/records/13322441/files/archive.zip?download=1"
    download_file(wood_db_url, "archive.zip")

    print("Extracting archive...")
    with zipfile.ZipFile("archive.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    print("Extraction complete")

    # Step 2: Merge wood density data
    wood_density_data = merge_wood_density_data()

    # Step 3: Read NFI species codes mapping
    # Assumes NFI_Species_Codes.csv is in the same directory
    if not os.path.exists('NFI_Species_Codes.csv'):
        print("ERROR: NFI_Species_Codes.csv not found in current directory!")
        print("Please ensure the file is present before running the script.")
        return

    nfi_mapping, nfi_codes = create_nfi_species_mapping('NFI_Species_Codes.csv')
    
    # print("nfi_mapping :")
    # print(nfi_mapping)
    # print("nfi_codes : ")
    # print(nfi_codes)

    # Step 4: Match wood density data with NFI species
    wood_density_dict = {}
    matched_species = set()
    not_found = []

    print("\nMatching wood density data with NFI species...")

    for wd_row in wood_density_data:
        full_scientific_name = wd_row['SpeciesName'].strip()
        # print("Full species name from wood density database : "+ str(full_scientific_name))

        # Check if this species is in the NFI mapping
        if full_scientific_name in nfi_mapping:
            genu_spe_code = nfi_mapping[full_scientific_name]
            # print("Genu species code from NFI based on full scientific name : "+ str(genu_spe_code))

            # Check if this code is in the NFI data
            if genu_spe_code in nfi_codes:
                # Only add if not already present (keep first occurrence)
                # print("Found "+ str(genu_spe_code) + " in full species code")
                if genu_spe_code not in wood_density_dict:
                    wood_density_dict[genu_spe_code] = {
                        "wood_density_value": wd_row['WoodDensity_MetricTons_per_m3'],
                        "unit": "oven dry mass/fresh volume as metricTons per m3",
                        "species_full_name": full_scientific_name
                    }
                    matched_species.add(genu_spe_code)

    # Find NFI species without wood density data
    for full_scientific_name in nfi_mapping:
        if nfi_mapping[full_scientific_name] not in matched_species:
            not_found.append(nfi_mapping[full_scientific_name])
            print(f"No wood density data found for: {nfi_mapping[full_scientific_name]} ({full_scientific_name})")

    print(f"\nMatched {len(wood_density_dict)} species")
    print(f"Not found: {len(not_found)} species")
    
    print("Species not matched are species that are found in the National Forest Inventory Tree species list (https://nfi.nfis.org/resources/general/3-TreeSpeciesList-Version4.5.pdf), but not in the wood density database. The reasons why these are missing from the wood density database might vary, but it's most often a scientific name not in used anymore, or a general name (e.g. QUER.SPP for unidentified oaks).")

    # Step 5: Export to JSON
    with open('woodDensityDictionnary.json', 'w', encoding='utf-8') as f:
        json.dump(wood_density_dict, f, indent=2, ensure_ascii=False)

    print("\nExported to woodDensityDictionnary.json")

    # Step 6: Clean up downloaded files
    print("\nCleaning up...")
    files_to_remove = ['archive.zip', 'measurements or facts.txt', 'occurrences.txt',
                       'agents.txt', 'associations.txt', 'events.txt', 'taxa.txt', 'media.txt', 'meta.xml',
                       'NFI_Species_Codes.csv', '3-TreeSpeciesList-Version4.5.pdf']
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")

    # Remove extracted directory if it exists
    if os.path.exists('archive'):
        shutil.rmtree('archive')
    if os.path.exists('__MACOSX'):
        shutil.rmtree('__MACOSX')

    print("Cleanup complete!")

if __name__ == "__main__":
    main()
