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

def match_species(abbreviated, full_name):
    """Match abbreviated species name (PINU.BAN) with full name (Pinus banksiana)"""
    parts = abbreviated.split('.')
    if len(parts) != 2:
        return False

    genus_abbr, species_abbr = parts[0].upper(), parts[1].upper()
    full_parts = full_name.split()

    if len(full_parts) < 2:
        return False

    genus_full = full_parts[0].upper()
    species_full = full_parts[1].upper()

    # Match first 4 letters of genus and first 3 letters of species
    return (genus_full.startswith(genus_abbr[:4]) and 
            species_full.startswith(species_abbr[:3]))

def main():
    # Step 1: Download and extract wood density database
    wood_db_url = "https://zenodo.org/records/13322441/files/archive.zip?download=1"
    download_file(wood_db_url, "archive.zip")

    print("Extracting archive...")
    with zipfile.ZipFile("archive.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    print("Extraction complete")

    # Step 2: Merge wood density data
    wood_density_data = merge_wood_density_data()

    # Step 3: Download NFI species list
    nfi_url = "https://nfi.nfis.org/resources/biomass_models/appendix2_table6_tb.csv"
    download_file(nfi_url, "nfi_species.csv")

    # Step 4: Read NFI species and create abbreviated names
    print("Reading NFI species list...")
    with open('nfi_species.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        nfi_data = list(reader)

    # Create species_fullname and get unique values
    nfi_species = set()
    for row in nfi_data:
        genus = row.get('genus', '').strip()
        species = row.get('species', '').strip()
        if genus and species:
            species_fullname = f"{genus}.{species}"
            nfi_species.add(species_fullname)

    print(f"Found {len(nfi_species)} unique NFI species")

    # Step 5: Match species and build dictionary
    wood_density_dict = {}
    not_found = []

    for nfi_sp in sorted(nfi_species):
        matched = False

        for wd_row in wood_density_data:
            if match_species(nfi_sp, wd_row['SpeciesName']):
                wood_density_dict[nfi_sp] = {
                    "wood_density_value": wd_row['WoodDensity_MetricTons_per_m3'],
                    "unit": "oven dry mass/fresh volume as metricTons per m3",
                    "species_full_name": wd_row['SpeciesName']
                }
                matched = True
                break

        if not matched:
            not_found.append(nfi_sp)
            print(f"No match found for: {nfi_sp}")

    print(f"\nMatched {len(wood_density_dict)} species")
    print(f"Not found: {len(not_found)} species")
    
    print("WARNING : Unmatched species are normally generic species identificators (e.g. PINU.SPP for unidentified pines) or shrubs or disputed status (like BETU.ALA which should be Betu alaskana for which there is no mention appart from the species code of the NFI in https://nfi.nfis.org/resources/general/3-TreeSpeciesList-Version4.5.pdf).")

    # Step 6: Export to JSON
    with open('woodDensityDictionnary.json', 'w', encoding='utf-8') as f:
        json.dump(wood_density_dict, f, indent=2, ensure_ascii=False)

    print("\nExported to woodDensityDictionnary.json")

    # Step 7: Clean up downloaded files
    print("\nCleaning up...")
    files_to_remove = ['archive.zip', 'nfi_species.csv', 'measurements or facts.txt', 'occurrences.txt', 'agents.txt', 'associations.txt', 'events.txt', 'media.txt', 'meta.xml', 'taxa.txt']
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")
    if os.path.exists("__MACOSX"):
        shutil.rmtree("./__MACOSX")

    # Remove extracted directory if it exists
    if os.path.exists('archive'):
        shutil.rmtree('archive')

    print("Cleanup complete!")

if __name__ == "__main__":
    main()
