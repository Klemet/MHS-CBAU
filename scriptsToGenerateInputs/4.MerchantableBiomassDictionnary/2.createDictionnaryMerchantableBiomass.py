import os
import json
import zipfile
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.strtree import STRtree
import numpy as np
from io import BytesIO
from tqdm import tqdm
import glob
import rasterio
from rasterio.features import rasterize

# Province code mapping
PROVINCE_CODES = {
    'Newfoundland and Labrador': 'NL',
    'Prince Edward Island': 'PE',
    'Nova Scotia': 'NS',
    'New Brunswick': 'NB',
    'Quebec': 'QC',
    'Ontario': 'ON',
    'Manitoba': 'MB',
    'Saskatchewan': 'SK',
    'Alberta': 'AB',
    'British Columbia': 'BC',
    'Yukon': 'YT',
    'Northwest Territories': 'NT',
    'Nunavut': 'NU'
}

print("Starting script...")

# Download provinces shapefile
print("\n1. Downloading provinces shapefile...")
provinces_url = "https://naciscdn.org/naturalearth/5.1.2/50m/cultural/50m_cultural.zip"
provinces_zip = "50m_cultural.zip"

response = requests.get(provinces_url)
with open(provinces_zip, 'wb') as f:
    f.write(response.content)

with zipfile.ZipFile(provinces_zip, 'r') as zip_ref:
    zip_ref.extractall("provinces_data")
print("Provinces shapefile downloaded and extracted.")

# Download ecozones GeoJSON
print("\n2. Downloading ecozones GeoJSON...")
ecozones_url = "https://agriculture.canada.ca/atlas/data_donnees/nationalEcologicalFramework/data_donnees/geoJSON/ez/nef_ca_ter_ecozone_v2_2.geojson"
ecozones_file = "ecozones.geojson"

response = requests.get(ecozones_url)
with open(ecozones_file, 'wb') as f:
    f.write(response.content)
print("Ecozones GeoJSON downloaded.")

# Download CSV parameters
print("\n3. Downloading equation parameters CSV...")
csv_url = "https://nfi.nfis.org/resources/biomass_models/appendix2_table6_tb.csv"
csv_file = "appendix2_table6_tb.csv"

response = requests.get(csv_url)
with open(csv_file, 'wb') as f:
    f.write(response.content)
print("CSV parameters downloaded.")

# Load spatial datasets
print("\n4. Loading spatial datasets...")
provinces_gdf = gpd.read_file("provinces_data/ne_50m_admin_1_states_provinces.shp")
provinces_gdf = provinces_gdf[provinces_gdf['adm0_a3'] == 'CAN']
ecozones_gdf = gpd.read_file(ecozones_file)
print(f"Loaded {len(provinces_gdf)} provinces and {len(ecozones_gdf)} ecozones.")

# Ensure same CRS
print("\n5. Reprojecting to common CRS...")
provinces_gdf = provinces_gdf.to_crs(ecozones_gdf.crs)

# Add JURIS_ID to provinces
print("\n6. Adding province codes...")
provinces_gdf['JURIS_ID'] = provinces_gdf['postal']

# Intersect provinces and ecozones
print("\n7. Intersecting provinces and ecozones (this may take a while)...")
intersected_gdf = gpd.overlay(provinces_gdf, ecozones_gdf, how='intersection')
intersected_gdf = intersected_gdf[['JURIS_ID', 'ECOZONE_ID', 'geometry']]
intersected_gdf = intersected_gdf[intersected_gdf.geometry.is_valid]
print(f"Created {len(intersected_gdf)} province-ecozone intersection polygons.")

# Load CSV with parameters
print("\n8. Loading equation parameters from CSV...")
params_df = pd.read_csv(csv_file)
params_df['species_fullname'] = params_df['genus'] + '.' + params_df['species']
print(f"Loaded {len(params_df)} parameter rows for {params_df['species_fullname'].nunique()} unique species.")

# Get unique combinations
unique_species = params_df['species_fullname'].unique()
unique_combos = intersected_gdf[['JURIS_ID', 'ECOZONE_ID']].drop_duplicates()
print(f"\n9. Creating dictionary structure with {len(unique_combos)} unique province-ecozone combinations.")


# Pre-compute all border-to-border distances between polygons
print("\n12. Pre-computing distances between all polygon pairs...")
n_polygons = len(intersected_gdf)
distance_dict = {}

# Create list of geometries and keys for faster access
geom_list = []
key_list = []
for idx, row in intersected_gdf.iterrows():
    geom_list.append(row.geometry)
    key_list.append(f"{row['JURIS_ID']}-{row['ECOZONE_ID']}")

# Calculate distances with progress bar
total_pairs = n_polygons * (n_polygons - 1) // 2
print(f"Computing {total_pairs} distance pairs for {n_polygons} polygons...")

with tqdm(total=total_pairs, desc="Computing distances") as pbar:
    for i in range(n_polygons):
        geom_i = geom_list[i]
        key_i = key_list[i]

        for j in range(i + 1, n_polygons):
            geom_j = geom_list[j]
            key_j = key_list[j]

            # Calculate distance
            dist = geom_i.distance(geom_j)

            # Store in both directions for easy lookup
            distance_dict[(key_i, key_j)] = dist
            distance_dict[(key_j, key_i)] = dist

            pbar.update(1)

print(f"Distance computation complete. Stored {len(distance_dict)} distance pairs.")

# Load CSV with parameters and clean column names
print("\n13. Loading equation parameters from CSV...")
params_df = pd.read_csv(csv_file)

# Clean column names (remove leading/trailing spaces)
params_df.columns = params_df.columns.str.strip()

# Filter out rows where variety is not null
print("Filtering out variety-specific rows...")
initial_rows = len(params_df)
params_df = params_df[params_df['variety'].isna()].copy()
filtered_rows = len(params_df)
print(f"Filtered from {initial_rows} to {filtered_rows} rows (removed {initial_rows - filtered_rows} variety-specific rows).")

# Verify 'ecozone' column exists after cleaning
if 'ecozone' not in params_df.columns:
    raise ValueError(f"'ecozone' column not found after cleaning. Available columns: {list(params_df.columns)}")

params_df['species_fullname'] = params_df['genus'] + '.' + params_df['species']
print(f"Loaded {len(params_df)} parameter rows for {params_df['species_fullname'].nunique()} unique species.")

# Get unique combinations
unique_species = params_df['species_fullname'].unique()
unique_combos = intersected_gdf[['JURIS_ID', 'ECOZONE_ID']].drop_duplicates()
print(f"\n14. Creating dictionary structure with {len(unique_combos)} unique province-ecozone combinations.")

# We prepare the dictionnary of unique province/ecozones combo ID
# Starts at 1, and goes up to the max number of combos
comboCodes_dict = {}
comboCode = 1
for _, row in unique_combos.iterrows():
    juris = row['JURIS_ID']
    ecozone = int(row['ECOZONE_ID'])
    if juris not in comboCodes_dict:
        comboCodes_dict[juris] = dict()
    comboCodes_dict[juris][ecozone] = comboCode
    comboCode += 1

# Initialize dictionary of ratios
ratio_dict = {}
for species in unique_species:
    ratio_dict[species] = {}
    for _, row in unique_combos.iterrows():
        juris = row['JURIS_ID']
        ecozone = int(row['ECOZONE_ID'])
        if comboCodes_dict[juris][ecozone] not in ratio_dict[species]:
            ratio_dict[species][comboCodes_dict[juris][ecozone]] = {
                'substitution': None,
                'ratio': None,
                'province': juris,
                'ecozone_id' : ecozone
            }

# Initialize dictionary of ratios - outdated
# ratio_dict = {}
# for species in unique_species:
    # ratio_dict[species] = {}
    # for _, row in unique_combos.iterrows():
        # juris = row['JURIS_ID']
        # ecozone = int(row['ECOZONE_ID'])
        # if juris not in ratio_dict[species]:
            # ratio_dict[species][juris] = {}
        # ratio_dict[species][juris][ecozone] = {
            # 'substitution': None,
            # 'ratio': None
        # }

# Function to calculate ratio
def calculate_ratio(params, aboveground_biomass=100):
    a = params['a1'] + params['a2'] * aboveground_biomass + params['a3'] * np.log(aboveground_biomass)
    b = params['b1'] + params['b2'] * aboveground_biomass + params['b3'] * np.log(aboveground_biomass)
    c = params['c1'] + params['c2'] * aboveground_biomass + params['c3'] * np.log(aboveground_biomass)
    ratio = 1 / (1 + np.exp(a) + np.exp(b) + np.exp(c))
    return ratio

# Fill dictionary
print("\n15. Filling dictionary with ratios...")
total_entries = len(unique_species) * len(unique_combos)
substitutions = 0

with tqdm(total=total_entries, desc="Processing entries") as pbar:
    for species in unique_species:
        # Get available combos for this species
        species_params = params_df[params_df['species_fullname'] == species]

        for _, combo_row in unique_combos.iterrows():
            juris = combo_row['JURIS_ID']
            ecozone = int(combo_row['ECOZONE_ID'])

            # Check if parameters exist
            matching_params = species_params[
                (species_params['juris_id'] == juris) & 
                (species_params['ecozone'] == ecozone)
            ]

            if len(matching_params) > 1:
                # Check if all duplicate rows are identical
                param_cols = ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']
                first_row = matching_params.iloc[0][param_cols]
                all_identical = all(
                    matching_params.iloc[i][param_cols].equals(first_row) 
                    for i in range(1, len(matching_params))
                )

                if not all_identical:
                    # Check if canfi_spec values are different
                    canfi_spec_values = matching_params['canfi_spec'].unique()
                    if len(canfi_spec_values) > 1:
                        # Different canfi_spec values, use first row
                        params_row = matching_params.iloc[0]
                    else:
                        # Same canfi_spec but different parameters - this is an error
                        raise ValueError(f"Multiple non-identical parameter rows found for {species}, {juris}, {ecozone} with same canfi_spec")
                else:
                    # Use first row if all are identical
                    params_row = matching_params.iloc[0]
            elif len(matching_params) == 1:
                params_row = matching_params.iloc[0]
            else:
                params_row = None

            if params_row is not None:
                # Direct match found
                ratio = calculate_ratio(params_row)
                ratio_dict[species][comboCodes_dict[juris][ecozone]]['ratio'] = float(ratio)
                ratio_dict[species][comboCodes_dict[juris][ecozone]]['substitution'] = 'none'
            else:
                # Need substitution
                substitutions += 1

                # Find available combos for this species
                available_combos = species_params[['juris_id', 'ecozone']].drop_duplicates()

                if len(available_combos) == 0:
                    # No parameters available for this species at all
                    ratio_dict[species][comboCodes_dict[juris][ecozone]]['ratio'] = None
                    ratio_dict[species][comboCodes_dict[juris][ecozone]]['substitution'] = 'no_data_available'
                else:
                    # Find closest polygon using pre-computed distances
                    target_key = f"{juris}-{ecozone}"
                    min_distance = float('inf')
                    closest_juris = None
                    closest_ecozone = None

                    for _, avail_row in available_combos.iterrows():
                        avail_juris = avail_row['juris_id']
                        avail_ecozone = int(avail_row['ecozone'])
                        avail_key = f"{avail_juris}-{avail_ecozone}"

                        # Look up pre-computed distance
                        dist_key = (target_key, avail_key)
                        if dist_key in distance_dict:
                            dist = distance_dict[dist_key]
                            if dist < min_distance:
                                min_distance = dist
                                closest_juris = avail_juris
                                closest_ecozone = avail_ecozone

                    if closest_juris is not None:
                        # Get parameters and calculate ratio
                        substitute_params = species_params[
                            (species_params['juris_id'] == closest_juris) & 
                            (species_params['ecozone'] == closest_ecozone)
                        ].iloc[0]

                        ratio = calculate_ratio(substitute_params)
                        ratio_dict[species][comboCodes_dict[juris][ecozone]]['ratio'] = float(ratio)
                        ratio_dict[species][comboCodes_dict[juris][ecozone]]['substitution'] = f'Substituted with {closest_juris}-{closest_ecozone}'
                    else:
                        ratio_dict[species][comboCodes_dict[juris][ecozone]]['ratio'] = None
                        ratio_dict[species][comboCodes_dict[juris][ecozone]]['substitution'] = 'no_data_available'

            pbar.update(1)

print(f"\nCompleted processing. Total substitutions made: {substitutions}")

# Fix ALNU species with problematic small ratios
print("\n15b. Fixing ALNU species with problematic small ratios...")
alnu_species = [sp for sp in ratio_dict.keys() if sp.startswith('ALNU.')]
fixed_count = 0

for species in alnu_species:
    for comboCodeProvEcozone in ratio_dict[species]:
        current_ratio = ratio_dict[species][comboCodeProvEcozone]['ratio']

        # Check if ratio is too small (< 0.001)
        if current_ratio is not None and current_ratio < 0.001:
            # Replace with BC-4 ratio
            ratio_dict[species][comboCodeProvEcozone]['ratio'] = 0.6174823234548655
            ratio_dict[species][comboCodeProvEcozone]['substitution'] = 'Replacement of ratios that were too small due to problematic parameters (see ALNU SPP for QC 6 in the .csv for an example); only 5 trees were available for these parameters. Substituted for BC-4.'
            fixed_count += 1

print(f"Fixed {fixed_count} ALNU entries with ratios < 0.001")

# Export to JSON
print("\n16. Exporting dictionary to JSON...")
output_file = "merchantableBiomassRatiosDictionnary.json"
with open(output_file, 'w') as f:
    json.dump(ratio_dict, f, indent=2)

print(f"\nDictionary exported to {output_file}")

# Making the raster of ecozones

# Find the raster file with name "Study_landscape" and any extension
raster_pattern = os.path.join('./InputData/', 'Study_landscape.*')
raster_files = glob.glob(raster_pattern)

if not raster_files:
    raise FileNotFoundError("No raster file found with name 'Study_landscape'")
if len(raster_files) > 1:
    raise ValueError(f"Multiple files found: {raster_files}. Please ensure only one exists.")

raster_path = raster_files[0]

# Read the reference raster to get dimensions and transform
with rasterio.open(raster_path) as src:
    transform = src.transform
    shape = src.shape
    crs = src.crs
    profile = src.profile

# Create UNIQUE_ID attribute in intersected_gdf using the dictionary
intersected_gdf['UNIQUE_ID'] = intersected_gdf.apply(
    lambda row: comboCodes_dict[row['JURIS_ID']][row['ECOZONE_ID']], 
    axis=1
)

# Ensure the GeoDataFrame has the same CRS as the raster
if intersected_gdf.crs != crs:
    intersected_gdf = intersected_gdf.to_crs(crs)

# Create list of (geometry, value) pairs for rasterization
shapes = [(geom, value) for geom, value in zip(intersected_gdf.geometry, intersected_gdf['UNIQUE_ID'])]

# Burn the UNIQUE_ID values into a new raster
burned_raster = rasterize(
    shapes=shapes,
    out_shape=shape,
    transform=transform,
    fill=0,  # Background value for areas not covered by polygons
    dtype=rasterio.uint16  # Adjust dtype based on your unique ID range
)

# Write the burned raster to file
profile.update(dtype=rasterio.uint16, count=1, nodata=0)
with rasterio.open('./EcozonesRaster.tif', 'w', **profile) as dst:
    dst.write(burned_raster, 1)

# Clean up downloaded files
print("\n17. Cleaning up downloaded files...")
import shutil

files_to_delete = [
    provinces_zip,
    ecozones_file,
    csv_file
]

folders_to_delete = [
    "provinces_data"
]

# Delete files
for file_path in files_to_delete:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"  Deleted: {file_path}")
        except Exception as e:
            print(f"  Could not delete {file_path}: {e}")

# Delete folders
for folder_path in folders_to_delete:
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"  Deleted folder: {folder_path}")
        except Exception as e:
            print(f"  Could not delete folder {folder_path}: {e}")

print("\nCleanup complete!")


print("Script completed successfully!")
