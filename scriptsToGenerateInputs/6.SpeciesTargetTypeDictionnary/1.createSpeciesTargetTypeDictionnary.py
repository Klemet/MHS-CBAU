import json

# Known gymnosperm genera in Canada (true softwoods)
GYMNOSPERM_GENERA = {
    'PINU', 'PICE', 'ABIE', 'TSUG', 'LARI', 'THUJ', 
    'PSEU', 'TAXU', 'JUNI', 'CHAM', 'CUPR'
}

# Read the wood density dictionary
with open('wood_density_dictionary.json', 'r') as f:
    wood_density_dict = json.load(f)

# Create species target type dictionary
species_target_type = {}

for species_code in wood_density_dict.keys():
    # Extract genus (first 4 letters before the dot)
    genus_code = species_code.split('.')[0][:4].upper()

    # Classify: gymnosperms as "softwood"
    if genus_code in GYMNOSPERM_GENERA:
        species_target_type[species_code] = "softwood"
    else:
        # Per user instruction: angiosperms classified as "hardwoods"
        species_target_type[species_code] = "hardwood"

# Output to JSON file
with open('speciesTargetType.json', 'w') as f:
    json.dump(species_target_type, f, indent=2)

print(f"Created speciesTargetType.json with {len(species_target_type)} species")
