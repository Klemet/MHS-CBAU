import urllib.request
import zipfile
import os
import sys
import subprocess
from pathlib import Path

def download_file(url, destination):
    """Download a file from URL to destination if it doesn't already exist."""
    if destination.exists():
        print(f"File already exists, skipping: {destination.name}")
        return False

    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, destination)
    print(f"Saved to: {destination}")
    return True

def extract_filtered_zip(zip_path, extract_to, include_string, exclude_strings):
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
    rasters_dir = input_data_dir / "Rasters"
    nfd_dir = input_data_dir / "NationalForestryDatabase"

    # Create directories
    input_data_dir.mkdir(exist_ok=True)
    rasters_dir.mkdir(exist_ok=True)
    nfd_dir.mkdir(exist_ok=True)

    # Step 1: Download and extract Natural Earth data
    print("\n=== Step 1: Downloading Natural Earth cultural data ===")
    # The URL used here is not the URL that can be found on the website; it's a special URL to access it by script.
    # See https://github.com/nvkelso/natural-earth-vector/issues/246#issuecomment-1134290221
    ne_zip_url = "https://naciscdn.org/naturalearth/5.1.2/50m/cultural/50m_cultural.zip"
    ne_zip_path = input_data_dir / "50m_cultural.zip"

    downloaded = download_file(ne_zip_url, ne_zip_path)

    if downloaded or ne_zip_path.exists():
        extract_filtered_zip(
            ne_zip_path, 
            input_data_dir, 
            "ne_50m_admin_1_states_provinces",
            ["lakes", "lines", "rank"]
        )

        # Delete the zip file
        ne_zip_path.unlink()
        print(f"Deleted: {ne_zip_path}")

    # Step 2: Download CANLAD raster files
    print("\n=== Step 2: Downloading CANLAD raster files ===")
    canlad_base_url = "https://ftp.maps.canada.ca/pub/nrcan_rncan/Forests_Foret/canlad_including_insect_defoliation/v1/Disturbances_Time_Series/"

    for year in range(2000, 2025):
        filename = f"canlad_annual_{year}_v1.tif"
        url = canlad_base_url + filename
        destination = rasters_dir / filename

        try:
            download_file(url, destination)
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

    # Step 3: Download NFI species group rasters
    print("\n=== Step 3: Downloading NFI species group rasters ===")

    # Define the files to download
    nfi_files = {
        2001: [
            "NFI_MODIS250m_2001_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
            "NFI_MODIS250m_2001_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
            "NFI_MODIS250m_2001_kNN_SpeciesGroups_Unknown_Spp_v1.tif",
            "NFI_MODIS250m_2001_kNN_Structure_Volume_Merch_v1.tif"
        ],
        2011: [
            "NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
            "NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
            "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1.tif",
            "NFI_MODIS250m_2011_kNN_Structure_Volume_Merch_v1.tif"
        ]
    }

    nfi_base_urls = {
        2001: "https://ftp.maps.canada.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2001-attributes_attributs-2001/",
        2011: "https://ftp.maps.canada.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/"
    }

    for year, files in nfi_files.items():
        base_url = nfi_base_urls[year]
        for filename in files:
            url = base_url + filename
            destination = rasters_dir / filename

            try:
                download_file(url, destination)
            except Exception as e:
                print(f"Error downloading {filename}: {e}")

    # Step 4: Download National Forestry Database CSV files
    print("\n=== Step 4: Downloading National Forestry Database CSV files ===")
    
    # See http://nfdp.ccfm.org/en/download.php for more info on these CSV file and their content

    nfd_files = [
        ("http://nfdp.ccfm.org/download/data/csv/NFD%20-%20Net%20Merchantable%20Volume%20of%20Roundwood%20Harvested%20by%20Category%20and%20Ownership%20-%20EN%20FR.csv",
         "NFD_Net_Merchantable_Volume_of_Roundwood_Harvested.csv"),
        ("http://nfdp.ccfm.org/download/data/csv/NFD%20-%20Area%20harvested%20by%20ownership%20and%20harvesting%20method%20-%20EN%20FR.csv",
         "NFD_Area_harvested_by_ownership_and_harvesting_method.csv"),
        ("http://nfdp.ccfm.org/download/data/csv/NFD%20-%20Area%20of%20stand%20tending%20by%20ownership,%20treatment%20-%20EN%20FR.csv",
         "NFD_Area_of_stand_tending_by_ownership_treatment.csv")
    ]

    for url, filename in nfd_files:
        destination = nfd_dir / filename
        try:
            download_file(url, destination)
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

    print("\n=== Setup Complete ===")
    print(f"Data downloaded to: {input_data_dir}")
    print(f"All rasters saved to: {rasters_dir}")
    print(f"NFD CSV files saved to: {nfd_dir}")

if __name__ == "__main__":
    main()
