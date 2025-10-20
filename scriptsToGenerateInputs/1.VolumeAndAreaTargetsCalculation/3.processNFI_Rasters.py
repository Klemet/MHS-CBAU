import rasterio
from rasterio.mask import mask
import numpy as np
import geopandas as gpd
from pathlib import Path

def get_province_from_landscape(provinces_shapefile='ne_50m_admin_1_states_provinces.shp', 
                                 landscape_shapefile='study_landscape.shp'):
    """
    Returns a single Canadian province multipolygon that intersects with a study landscape.

    Parameters:
    -----------
    provinces_shapefile : str
        Path to the Natural Earth provinces/states shapefile
    landscape_shapefile : str
        Path to the study landscape shapefile

    Returns:
    --------
    gpd.GeoDataFrame
        Single-row GeoDataFrame containing the province multipolygon

    Raises:
    -------
    ValueError
        If landscape intersects multiple provinces, US states, or no provinces
    """

    # Read shapefiles
    provinces = gpd.read_file(provinces_shapefile)
    landscape = gpd.read_file(landscape_shapefile)

    # Ensure same CRS
    if provinces.crs != landscape.crs:
        landscape = landscape.to_crs(provinces.crs)

    # Spatial join to find intersecting provinces/states
    intersecting = gpd.sjoin(provinces, landscape, how='inner', predicate='intersects')

    # Check if any intersection exists
    if len(intersecting) == 0:
        raise ValueError("Study landscape does not intersect any province or state")

    # Check for US states
    us_states = intersecting[intersecting['adm0_a3'] == 'USA']
    if len(us_states) > 0:
        raise ValueError("Study landscape intersects with US state(s). Only Canadian provinces are allowed.")

    # Filter for Canadian provinces only
    canadian_provinces = intersecting[intersecting['adm0_a3'] == 'CAN']

    # Check if exactly one Canadian province
    if len(canadian_provinces) == 0:
        raise ValueError("Study landscape does not intersect any Canadian province")

    if len(canadian_provinces) > 1:
        province_names = canadian_provinces['name'].tolist() if 'name' in canadian_provinces.columns else 'multiple'
        raise ValueError(f"Study landscape intersects multiple Canadian provinces: {province_names}")

    # Return the single province as a GeoDataFrame
    return canadian_provinces.iloc[[0]].reset_index(drop=True)

def process_nfi_rasters():
    print("Starting NFI raster processing...")

    # Paths
    base_path = Path("./InputData/Rasters")
    print("Finding canadian province polygon...")
    canadianProvince = get_province_from_landscape(provinces_shapefile='./InputData/ne_50m_admin_1_states_provinces.shp', 
                                 landscape_shapefile='./InputData/study_landscape.shp')

    # Load a reference raster to get CRS
    print("Getting CRS from NFI raster...")
    ref_raster_path = base_path / "NFI_MODIS250m_2001_kNN_Structure_Volume_Merch_v1.tif"
    with rasterio.open(ref_raster_path) as src:
        raster_crs = src.crs

    print(f"Raster CRS: {raster_crs}")
    print(f"Canadian Province shapefile CRS: {canadianProvince.crs}")

    # Reproject Canadian Province shapefile if needed
    if canadianProvince.crs != raster_crs:
        print(f"Reprojecting Canadian Province shapefile from {canadianProvince.crs} to {raster_crs}...")
        canadianProvince = canadianProvince.to_crs(raster_crs)

    # NFI raster paths
    nfi_files = {
        2001: {
            'volume': base_path / "NFI_MODIS250m_2001_kNN_Structure_Volume_Merch_v1.tif",
            'broadleaf': base_path / "NFI_MODIS250m_2001_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
            'needleleaf': base_path / "NFI_MODIS250m_2001_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
            'unknown': base_path / "NFI_MODIS250m_2001_kNN_SpeciesGroups_Unknown_Spp_v1.tif"
        },
        2011: {
            'volume': base_path / "NFI_MODIS250m_2011_kNN_Structure_Volume_Merch_v1.tif",
            'broadleaf': base_path / "NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
            'needleleaf': base_path / "NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
            'unknown': base_path / "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1.tif"
        }
    }

    # Load 2001 rasters
    print("Loading 2001 NFI rasters...")
    with rasterio.open(nfi_files[2001]['volume']) as src:
        volume_2001 = src.read(1)
        profile = src.profile

    with rasterio.open(nfi_files[2001]['broadleaf']) as src:
        broadleaf_pct_2001 = src.read(1)

    with rasterio.open(nfi_files[2001]['needleleaf']) as src:
        needleleaf_pct_2001 = src.read(1)

    with rasterio.open(nfi_files[2001]['unknown']) as src:
        unknown_pct_2001 = src.read(1)

    # Load 2011 rasters
    print("Loading 2011 NFI rasters...")
    with rasterio.open(nfi_files[2011]['volume']) as src:
        volume_2011 = src.read(1)

    with rasterio.open(nfi_files[2011]['broadleaf']) as src:
        broadleaf_pct_2011 = src.read(1)

    with rasterio.open(nfi_files[2011]['needleleaf']) as src:
        needleleaf_pct_2011 = src.read(1)

    with rasterio.open(nfi_files[2011]['unknown']) as src:
        unknown_pct_2011 = src.read(1)

    # Calculate estimated volumes
    print("Calculating estimated volumes for 2001...")
    deciduous_vol_2001 = volume_2001 * (broadleaf_pct_2001 / 100.0)
    conifer_vol_2001 = volume_2001 * (needleleaf_pct_2001 / 100.0)

    print("Calculating estimated volumes for 2011...")
    deciduous_vol_2011 = volume_2011 * (broadleaf_pct_2011 / 100.0)
    conifer_vol_2011 = volume_2011 * (needleleaf_pct_2011 / 100.0)

    # Handle unknown species
    print("Handling unknown species pixels...")
    mask_unknown_2001 = unknown_pct_2001 > 20
    mask_unknown_2011 = unknown_pct_2011 > 20

    # Replace 2001 values with 2011 where 2001 has >20% unknown
    deciduous_vol_2001[mask_unknown_2001] = deciduous_vol_2011[mask_unknown_2001]
    conifer_vol_2001[mask_unknown_2001] = conifer_vol_2011[mask_unknown_2001]

    # Set to 0 where both years have >20% unknown
    mask_both_unknown = mask_unknown_2001 & mask_unknown_2011
    deciduous_vol_2001[mask_both_unknown] = 0
    conifer_vol_2001[mask_both_unknown] = 0

    # Crop to Canadian Province extent
    print("Cropping to Canadian Province extent...")
    canadianProvince_geom = [canadianProvince.geometry.unary_union.__geo_interface__]

    # Mask and save conifer
    print("Saving temporary conifer volume raster...")
    with rasterio.open(nfi_files[2001]['volume']) as src:
        out_conifer, out_transform = mask(src, canadianProvince_geom, crop=True, all_touched=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_conifer.shape[1],
            "width": out_conifer.shape[2],
            "transform": out_transform,
            "nodata": 0,
            "dtype": 'float32'
        })

        # Get mask indices
        mask_array = out_conifer[0] != src.nodata

        # Create output array
        conifer_output = np.zeros((out_conifer.shape[1], out_conifer.shape[2]), dtype=np.float32)

        # Map full array to cropped array
        with rasterio.open(nfi_files[2001]['volume']) as src_full:
            window = src_full.window(*canadianProvince.total_bounds)
            row_off = int(window.row_off)
            col_off = int(window.col_off)
            height = out_conifer.shape[1]
            width = out_conifer.shape[2]

            conifer_subset = conifer_vol_2001[row_off:row_off+height, col_off:col_off+width]
            conifer_output = np.where(mask_array, conifer_subset, 0)

        conifer_temp_path = base_path / "temp_conifer_volume_2001.tif"
        with rasterio.open(conifer_temp_path, 'w', **out_meta) as dst:
            dst.write(conifer_output.astype('float32'), 1)

    print(f"Saved: {conifer_temp_path}")

    # Mask and save deciduous
    print("Saving temporary deciduous volume raster...")
    with rasterio.open(nfi_files[2001]['volume']) as src:
        with rasterio.open(nfi_files[2001]['volume']) as src_full:
            window = src_full.window(*canadianProvince.total_bounds)
            row_off = int(window.row_off)
            col_off = int(window.col_off)
            height = out_conifer.shape[1]
            width = out_conifer.shape[2]

            deciduous_subset = deciduous_vol_2001[row_off:row_off+height, col_off:col_off+width]
            deciduous_output = np.where(mask_array, deciduous_subset, 0)

        deciduous_temp_path = base_path / "temp_deciduous_volume_2001.tif"
        with rasterio.open(deciduous_temp_path, 'w', **out_meta) as dst:
            dst.write(deciduous_output.astype('float32'), 1)

    print(f"Saved: {deciduous_temp_path}")
    print("NFI raster processing complete!")

    return conifer_temp_path, deciduous_temp_path

if __name__ == "__main__":
    process_nfi_rasters()
