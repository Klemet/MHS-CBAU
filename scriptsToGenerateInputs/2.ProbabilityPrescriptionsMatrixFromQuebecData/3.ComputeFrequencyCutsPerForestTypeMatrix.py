import json
import pandas as pd
import numpy as np
from pathlib import Path
import fiona
from fiona.crs import from_epsg
import geopandas as gpd
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from shapely import STRtree, intersection, area, prepare
import pyogrio
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Paths
forest_inv_gdb = "./InputData/CARTE_ECO_ORI_PROV.gdb"
forest_cut_gdb = "./InputData/INTERV_FORES_PROV.gdb"
clipped_gpkg = "INTERV_FORES_PROV_CLIPPED.gpkg"
BUFFER_SIZE = 5000

# Load JSON files
print("=== Step 1: Loading JSON files ===")
with open('./InputData/ShadeToleranceSpeciesQuebec.json', 'r', encoding='utf-8') as f:
    shade_tolerance = json.load(f)

with open('./InputData/CutTypeCategories.json', 'r', encoding='utf-8') as f:
    cut_categories = json.load(f)

# Load forest cut data (smaller dataset)
if not Path(clipped_gpkg).exists():
    print("\n=== Step 2: Loading forest cut data ===")
    interv_fores_gdf = pyogrio.read_dataframe(
        forest_cut_gdb,
        layer="INTERV_FORES_PROV",
        columns=['EXERCICE', 'ORIGINE', 'AN_ORIGINE', 'PERTURB', 'AN_PERTURB', 
                 'REB_ESS1', 'REB_ESS2', 'REB_ESS3'],
        use_arrow=True
    )
    print(f"Loaded {len(interv_fores_gdf)} forest cut polygons")

# Build spatial index for interventions
print("Building spatial index for interventions...")
interv_geoms = interv_fores_gdf.geometry.values
for geom in interv_geoms:
    prepare(geom)
interv_tree = STRtree(interv_geoms)
print("Spatial index built")

# Reclassification functions
age_classes = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100", "110", "120", "130", "140"]

def reclassify_cl_age(cl_age):
    if pd.notna(cl_age) and str(cl_age) in age_classes:
        return "Even"
    elif pd.notna(cl_age):
        return "Uneven"
    return None

def classify_shade_tolerance(gr_ess):
    if pd.isna(gr_ess):
        return None
    species_code = str(gr_ess)[:2]
    if species_code in shade_tolerance:
        tolerance = shade_tolerance[species_code].get('tolerance_ombre', 'Unknown')
        return "Tol" if tolerance == "Tolérant" else "Intol" if tolerance == "Intolérant" else "Unknown"
    return "Unknown"

def extract_polygons(geom):
    """Extract individual polygons from geometry (handles both Polygon and MultiPolygon)"""
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    elif isinstance(geom, Polygon):
        return [geom]
    else:
        return []

# Check if clipped data exists
if Path(clipped_gpkg).exists():
    del(interv_fores_gdf)
    print(f"\n=== Step 3: Loading existing clipped data with Fiona ===")
    try:
        # # Read using Fiona and convert to GeoDataFrame
        # with fiona.open(clipped_gpkg) as src:
            # features = list(src)
            # crs = src.crs

        # # Convert to GeoDataFrame
        # geometries = [shape(f['geometry']) for f in features]
        # properties = [f['properties'] for f in features]
        # interv_clipped = gpd.GeoDataFrame(properties, geometry=geometries, crs=crs)
        interv_clipped = pyogrio.read_dataframe(
            clipped_gpkg, 
            use_arrow=True
        )
        print(f"Loaded {len(interv_clipped)} clipped polygons")
    except Exception as e:
        print(f"Error reading existing file: {e}")
        print("Deleting corrupted file and regenerating...")
        Path(clipped_gpkg).unlink()
        interv_clipped = None
else:
    interv_clipped = None

if interv_clipped is None:
    print(f"\n=== Step 3: Processing forest inventory polygons one-by-one ===")

    with fiona.open(forest_inv_gdb, layer="PEE_ORI_PROV") as src:
        total_features = len(src)
        crs = src.crs

        # Define schema for output
        schema = {
            'geometry': 'Polygon',
            'properties': {
                'EXERCICE': 'str',
                'ORIGINE': 'str',
                'AN_ORIGINE': 'str',
                'PERTURB': 'str',
                'AN_PERTURB': 'str',
                'REB_ESS1': 'str',
                'REB_ESS2': 'str',
                'REB_ESS3': 'str',
                'CL_AGE': 'str',
                'GR_ESS': 'str',
                'CO_TER': 'str'
            }
        }

        print(f"Total forest inventory polygons: {total_features}")
        print("Filtering and intersecting polygons...")

        # Open output file for writing with buffering
        with fiona.open(clipped_gpkg, 'w', driver='GPKG', crs=crs, schema=schema) as dst:
            buffer = []
            count = 0

            for feature in tqdm(src, total=total_features, desc="Processing"):
                pee_geom = shape(feature['geometry'])
                props = feature['properties']

                cl_age = props.get('CL_AGE')
                gr_ess = props.get('GR_ESS')
                co_ter = props.get('CO_TER')

                cl_age_reclass = reclassify_cl_age(cl_age)
                gr_ess_reclass = classify_shade_tolerance(gr_ess)

                potential_idx = interv_tree.query(pee_geom, predicate='intersects')

                if len(potential_idx) == 0:
                    continue

                for interv_idx in potential_idx:
                    interv_geom = interv_geoms[interv_idx]
                    intersect_geom = intersection(pee_geom, interv_geom)

                    if intersect_geom.is_empty or intersect_geom.area < 1:
                        continue

                    interv_row = interv_fores_gdf.iloc[interv_idx]

                    # Extract individual polygons (handles MultiPolygon)
                    polygons = extract_polygons(intersect_geom)

                    for poly in polygons:
                        if poly.area < 1:
                            continue

                        # Add to buffer
                        feature_out = {
                            'geometry': mapping(poly),
                            'properties': {
                                'EXERCICE': str(interv_row['EXERCICE']) if pd.notna(interv_row['EXERCICE']) else None,
                                'ORIGINE': str(interv_row['ORIGINE']) if pd.notna(interv_row['ORIGINE']) else None,
                                'AN_ORIGINE': str(interv_row['AN_ORIGINE']) if pd.notna(interv_row['AN_ORIGINE']) else None,
                                'PERTURB': str(interv_row['PERTURB']) if pd.notna(interv_row['PERTURB']) else None,
                                'AN_PERTURB': str(interv_row['AN_PERTURB']) if pd.notna(interv_row['AN_PERTURB']) else None,
                                'REB_ESS1': str(interv_row['REB_ESS1']) if pd.notna(interv_row['REB_ESS1']) else None,
                                'REB_ESS2': str(interv_row['REB_ESS2']) if pd.notna(interv_row['REB_ESS2']) else None,
                                'REB_ESS3': str(interv_row['REB_ESS3']) if pd.notna(interv_row['REB_ESS3']) else None,
                                'CL_AGE': cl_age_reclass,
                                'GR_ESS': gr_ess_reclass,
                                'CO_TER': str(co_ter) if pd.notna(co_ter) else None
                            }
                        }
                        buffer.append(feature_out)
                        count += 1

                        # Write buffer when it reaches BUFFER_SIZE
                        if len(buffer) >= BUFFER_SIZE:
                            dst.writerecords(buffer)
                            buffer = []

            # Write remaining features in buffer
            if buffer:
                dst.writerecords(buffer)

        print(f"\nWrote {count} intersected polygons to {clipped_gpkg}")

    # Load the file we just created using Fiona
    print("Loading clipped data...")
    del(interv_fores_gdf)
    # with fiona.open(clipped_gpkg) as src:
        # features = list(src)
        # crs = src.crs
    # geometries = [shape(f['geometry']) for f in features]
    # properties = [f['properties'] for f in features]
    # interv_clipped = gpd.GeoDataFrame(properties, geometry=geometries, crs=crs)
    interv_clipped = pyogrio.read_dataframe(
            clipped_gpkg, 
            use_arrow=True
        )

# Calculate area
print("\n=== Step 4: Calculating polygon areas ===")
interv_clipped['AREACUT'] = interv_clipped.geometry.apply(lambda g: area(g))
print(f"Area calculated, total area: {interv_clipped['AREACUT'].sum():.2f} m²")

# Create CUTTYPE attribute
print("\n=== Step 5: Creating CUTTYPE attribute ===")
interv_clipped['CUTTYPE'] = interv_clipped.apply(
    lambda row: row['PERTURB'] if pd.notna(row['PERTURB']) else row['ORIGINE'], axis=1
)

# Reclassify CUTTYPE
print("\n=== Step 6: Reclassifying CUTTYPE ===")
def reclassify_cuttype(cuttype):
    if pd.isna(cuttype):
        return None
    cuttype_str = str(cuttype)
    if cuttype_str in cut_categories:
        return cut_categories[cuttype_str].get('english_category', cuttype_str)
    return cuttype_str

interv_clipped['CUTTYPE'] = interv_clipped['CUTTYPE'].apply(reclassify_cuttype)
print(f"CUTTYPE reclassified: {interv_clipped['CUTTYPE'].value_counts().to_dict()}")

# Save final version
interv_clipped.to_file(clipped_gpkg, driver='GPKG')
print(f"Final version saved to {clipped_gpkg}")

# Create forest type classification
print("\n=== Step 7: Creating forest type classification ===")
def classify_forest_type(row):
    cl_age = row['CL_AGE']
    gr_ess = row['GR_ESS']

    if pd.isna(cl_age) or gr_ess == 'Unknown' or pd.isna(gr_ess):
        return 'Unknown/Unclassified'
    elif cl_age == 'Even' and gr_ess == 'Tol':
        return 'Even/Tol'
    elif cl_age == 'Uneven' and gr_ess == 'Tol':
        return 'Uneven/Tol'
    elif cl_age == 'Even' and gr_ess == 'Intol':
        return 'Even/Intol'
    elif cl_age == 'Uneven' and gr_ess == 'Intol':
        return 'Uneven/Intol'
    else:
        return 'Unknown/Unclassified'

interv_clipped['FOREST_TYPE'] = interv_clipped.apply(classify_forest_type, axis=1)

# Create matrix
print("\n=== Step 8: Creating matrix ===")
total_area = interv_clipped['AREACUT'].sum()

matrix = interv_clipped.groupby(['CUTTYPE', 'FOREST_TYPE'])['AREACUT'].sum().unstack(fill_value=0)
matrix_pct = (matrix / total_area * 100).round(2)

# Ensure all forest types are present
forest_types = ['Even/Tol', 'Uneven/Tol', 'Even/Intol', 'Uneven/Intol', 'Unknown/Unclassified']
for ft in forest_types:
    if ft not in matrix_pct.columns:
        matrix_pct[ft] = 0.0

matrix_pct = matrix_pct[forest_types]

print("\n=== MATRIX: Percentage of surface harvested by cut type and forest type ===")
print(matrix_pct)

# Export to CSV
output_csv = "forest_cut_matrix.csv"
matrix_pct.to_csv(output_csv)
print(f"\nMatrix exported to {output_csv}")

# Create filtered matrix (no Unknown/Unclassified, no Commercial thinning/Others)
print("\n=== Step 9: Creating filtered probability matrix ===")

# Read the previously exported matrix
matrix_pct = pd.read_csv("forest_cut_matrix.csv", index_col=0)
print(f"Loaded matrix from forest_cut_matrix.csv")

# Convert percentages back to areas for proper normalization
total_area = interv_clipped['AREACUT'].sum()
matrix = (matrix_pct / 100) * total_area

# Filter out unwanted columns and rows
matrix_filtered = matrix.copy()

# Remove Unknown/Unclassified column if it exists
if 'Unknown/Unclassified' in matrix_filtered.columns:
    matrix_filtered = matrix_filtered.drop(columns=['Unknown/Unclassified'])

# Remove Commercial thinning and Others rows if they exist
rows_to_remove = ['Commercial thinning', 'Others']
for row_name in rows_to_remove:
    if row_name in matrix_filtered.index:
        matrix_filtered = matrix_filtered.drop(index=row_name)

# Convert to probabilities (normalize each column to sum to 1)
matrix_prob = matrix_filtered.div(matrix_filtered.sum(axis=0), axis=1)

# Handle any NaN values (from columns that sum to 0)
matrix_prob = matrix_prob.fillna(0)

# Round to reasonable precision
matrix_prob = matrix_prob.round(4)

print("\n=== FILTERED MATRIX: Probabilities by cut type and forest type ===")
print(matrix_prob)
print(f"\nColumn sums (should all be 1.0): {matrix_prob.sum(axis=0).to_dict()}")

# Export to CSV
output_csv_prob = "forest_cut_matrix_probabilities.csv"
matrix_prob.to_csv(output_csv_prob)
print(f"\nFiltered probability matrix exported to {output_csv_prob}")
