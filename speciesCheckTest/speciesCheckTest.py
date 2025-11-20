import json
import os
import glob
import re
import csv

def readJSONDictionnary(path):
    """
    Reads a Python Dictionnary from a JSON file. Used to load the dictionnaries
    containing biomass ratios values (see /scriptsToGenerateInputs/4.MerchantableBiomassDictionnary)
    and the wood density values (see scriptsToGenerateInputs/5.WoodDensityBiomassDictionnary)

    Returns a Python dictionnary.
    """
    try:
        with open(path, 'r') as f:
            data_dict = json.load(f)
    except FileNotFoundError:
        print(f"    MHS-CBAU :  Error: The file '{path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"    MHS-CBAU :  Error: Could not decode JSON from the file '{path}'. Ensure it's valid JSON.")
        return None
    except Exception as e:
        print(f"    MHS-CBAU :  An unexpected error occurred: {e}")
        return None
    return data_dict

def main():
    # Load JSON files
    json_files = {
        'merchantableBiomassRatiosDictionnary.json': None,
        'shadeToleranceSpeciesCanada.json': None,
        'speciesTargetType.json': None,
        'woodDensityDictionnary.json': None
    }

    for json_file in json_files.keys():
        json_files[json_file] = readJSONDictionnary(json_file)
        if json_files[json_file] is None:
            return

    # Find CSV file
    csv_files = glob.glob('*.csv')

    if len(csv_files) == 0:
        print("    MHS-CBAU :  Error: No CSV file found in the current directory.")
        return
    elif len(csv_files) > 1:
        print("    MHS-CBAU :  Error: Multiple CSV files found. Please ensure only one CSV file is present.")
        return

    csv_path = csv_files[0]

    # Read CSV and extract first column
    species_codes = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header if present
        for row in reader:
            if row:  # Skip empty rows
                species_codes.append(row[0])

    # Check species code format (XXXX.YYY)
    species_pattern = re.compile(r'^[A-Z]{4}\.[A-Z]{3}$')
    invalid_codes = [code for code in species_codes if not species_pattern.match(code)]

    if invalid_codes:
        print("    MHS-CBAU :  Error: Invalid species code format detected.")
        print("    Expected format: XXXX.YYY (e.g., ABIE.BAL)")
        print("    Invalid entries:")
        for code in invalid_codes:
            print(f"        - {code}")
        return

    # Check if species exist in JSON files
    unique_species = list(set(species_codes))

    for json_filename, json_dict in json_files.items():
        json_keys = set(json_dict.keys())
        missing_species = [species for species in unique_species if species not in json_keys]

        if missing_species:
            for species in missing_species:
                print(f"    MHS-CBAU :  The species {species} found in your csv file is not found in {json_filename}")

    print("    MHS-CBAU :  Validation complete.")

if __name__ == "__main__":
    main()
