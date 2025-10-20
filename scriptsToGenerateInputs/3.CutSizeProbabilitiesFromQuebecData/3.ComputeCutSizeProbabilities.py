# Python code used to get the cut sizes and associated probabilities from INTERV_FORES_PROV.gdb
# Requires the JSON dictionnary to recategorize all of the cut types of Quebec into
# the more limited cut categories found the datasets of the National Forestry Database of Canada

# %% Imports and Configuration
import fiona
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from scipy import stats
from tqdm import tqdm

# Configuration
GDB_PATH = r"./InputData/INTERV_FORES_PROV.gdb"
JSON_PATH = "./InputData/CutTypeCategories.json"
OUTPUT_JSON = "cut_size_distributions.json"

# %% Load Reclassification Dictionary
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    reclass_dict = json.load(f)

print(f"Loaded {len(reclass_dict)} reclassification codes")

# %% Read Data from GDB
data = []
with fiona.open(GDB_PATH, layer=0) as src:
    total_features = len(src)
    print(f"Loading {total_features} features...")

    for feature in tqdm(src, total=total_features, desc="Reading polygons"):
        props = feature['properties']
        data.append({
            'ORIGINE': props.get('ORIGINE', ''),
            'PERTURB': props.get('PERTURB', ''),
            'SUPERFICIE': props.get('SUPERFICIE', 0)
        })

print(f"Loaded {len(data)} records")

# %% Create and Reclassify CUTTYPE
# Create CUTTYPE attribute
for record in data:
    record['CUTTYPE'] = record['PERTURB'] if record['PERTURB'] else record['ORIGINE']

# Reclassify CUTTYPE using dictionary
for record in data:
    code = record['CUTTYPE']
    if code in reclass_dict and 'english_category' in reclass_dict[code]:
        record['CUTTYPE'] = reclass_dict[code]['english_category']

print("CUTTYPE created and reclassified")

# %% Group Data by Cut Category
categories = defaultdict(list)
for record in data:
    if record['SUPERFICIE'] > 0:  # Filter out zero or invalid areas
        categories[record['CUTTYPE']].append(record['SUPERFICIE'])

print(f"Found {len(categories)} cut categories")

# %% Generate Plots and Statistics
output_stats = {}

for category, surfaces in categories.items():
    if len(surfaces) < 2:
        continue

    surfaces = np.array(surfaces)
    n_polygons = len(surfaces)

    # Create percentile-based bins (each bin ≈ 1% of polygons)
    percentiles = np.linspace(0, 100, 101)  # 0, 1, 2, ..., 100
    bins = np.percentile(surfaces, percentiles)

    # Remove duplicate bin edges (can occur if many identical values)
    bins = np.unique(bins)
    n_bins = len(bins) - 1

    bin_upper_bounds = bins[1:].tolist()

    # Calculate actual frequencies
    hist, _ = np.histogram(surfaces, bins=bins)
    probabilities = (hist / n_polygons * 100).tolist()

    # Store in output dictionary
    output_stats[category] = {
        'bin_upper_bounds': bin_upper_bounds,
        'probabilities_percent': probabilities,
        'n_bins': n_bins,
        'n_polygons': n_polygons
    }

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram with percentile bins
    ax1.hist(surfaces, bins=bins, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Surface Area (ha)')
    ax1.set_ylabel('Frequency')
    ax1.set_title(f'{category} - Histogram ({n_bins} bins)')
    ax1.grid(alpha=0.3)

    # KDE
    kde = stats.gaussian_kde(surfaces)
    x_range = np.linspace(surfaces.min(), surfaces.max(), 500)
    ax2.plot(x_range, kde(x_range), linewidth=2)
    ax2.fill_between(x_range, kde(x_range), alpha=0.3)
    ax2.set_xlabel('Surface Area (ha)')
    ax2.set_ylabel('Density')
    ax2.set_title(f'{category} - KDE')
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{category.replace(" ", "_")}_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Processed {category}: {n_polygons} cuts, {n_bins} bins")

# %% Save Statistics to JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(output_stats, f, indent=2, ensure_ascii=False)

print(f"\nAnalysis complete. Statistics saved to {OUTPUT_JSON}")
print(f"Total categories processed: {len(output_stats)}")
