import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject, Resampling
from rasterio.windows import Window
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from osgeo import gdal, gdalconst, osr
import tempfile
import os

def get_province_from_landscape(provinces_shapefile='./InputData/ne_50m_admin_1_states_provinces.shp', 
                                 landscape_shapefile='./InputData/study_landscape.shp'):
    """
    Returns a tuple with the Canadian province name and its multipolygon that intersects with a study landscape.

    Parameters:
    -----------
    provinces_shapefile : str
        Path to the Natural Earth provinces/states shapefile
    landscape_shapefile : str
        Path to the study landscape shapefile

    Returns:
    --------
    tuple
        (province_name: str, province_gdf: gpd.GeoDataFrame)
        Province name from 'gn_name' attribute and single-row GeoDataFrame containing the province multipolygon

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
        province_names = canadian_provinces['gn_name'].tolist() if 'gn_name' in canadian_provinces.columns else 'multiple'
        raise ValueError(f"Study landscape intersects multiple Canadian provinces: {province_names}")

    # Extract province name and GeoDataFrame
    province_gdf = canadian_provinces.iloc[[0]].reset_index(drop=True)
    province_name = province_gdf['gn_name'].iloc[0]

    return (province_name, province_gdf)

def get_thinning_areas(year, province):
    """
    Extract commercial and precommercial thinning areas for a given year and province.

    Parameters:
    year (int): The year to query
    province (str): The province name (English)

    Returns:
    tuple: (commercial_thinning_ha, precommercial_thinning_ha)
    """
    # Read CSV files
    # Had to precise encoding as it's not UTF-8
    harvesting_df = pd.read_csv("./InputData/NationalForestryDatabase/NFD_Area_harvested_by_ownership_and_harvesting_method.csv", encoding='ISO-8859-1')
    tending_df = pd.read_csv("./InputData/NationalForestryDatabase/NFD_Area_of_stand_tending_by_ownership_treatment.csv", encoding='ISO-8859-1')

    # Filter commercial thinning from harvesting data
    commercial_mask = (
        (harvesting_df['Year'] == year) &
        (harvesting_df['Jurisdiction'] == province) &
        (harvesting_df['Harvesting method'] == 'Commercial thinning')
    )
    commercial_thinning = harvesting_df[commercial_mask]['Area (hectares)'].sum()

    # Filter precommercial thinning from tending data
    precommercial_mask = (
        (tending_df['Year'] == year) &
        (tending_df['Jurisdiction'] == province) &
        (tending_df['Treatment'] == 'Precommercial thinning')
    )
    precommercial_thinning = tending_df[precommercial_mask]['Area (hectares)'].sum()

    return (commercial_thinning, precommercial_thinning)


def load_harvest_data(provinceName):
    print("Loading harvest data CSV...")
    csv_path = "./InputData/NationalForestryDatabase/NFD_Net_Merchantable_Volume_of_Roundwood_Harvested.csv"
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    # Filter for provinceName
    quebec_data = df[df['Jurisdiction'] == provinceName].copy()

    # Group by year and species, summing volumes
    harvest_by_year = quebec_data.groupby(['Year', 'Species group'])['Volume (cubic metres) (En)'].sum().reset_index()
    
    # print(harvest_by_year)

    print(f"\nFound {len(harvest_by_year)} year-species combinations for {provinceName}")
    print(f"Years range: {harvest_by_year['Year'].min()} to {harvest_by_year['Year'].max()}")
    print(f"Species groups: {harvest_by_year['Species group'].unique()}")

    # Check unspecified volumes
    print("\nChecking unspecified volumes...")
    for year in sorted(harvest_by_year['Year'].unique()):
        year_data = harvest_by_year[harvest_by_year['Year'] == year]
        
        # print(year_data)

        hardwood_rows = year_data[year_data['Species group'] == 'Hardwoods']
        softwood_rows = year_data[year_data['Species group'] == 'Softwoods']
        unspecified_rows = year_data[year_data['Species group'] == 'Unspecified']

        hardwood = hardwood_rows['Volume (cubic metres) (En)'].sum() if len(hardwood_rows) > 0 else 0
        softwood = softwood_rows['Volume (cubic metres) (En)'].sum() if len(softwood_rows) > 0 else 0
        unspecified = unspecified_rows['Volume (cubic metres) (En)'].sum() if len(unspecified_rows) > 0 else 0

        # print("Year : " + str(year))
        # print("Hardwoods : " + str(hardwood))
        # print("Softwood : " + str(softwood))

        if unspecified > 0.05 * hardwood or unspecified > 0.05 * softwood:
            print(f"WARNING: Year {year} - Unspecified volume ({unspecified:.0f} m³) exceeds 5% threshold")
            print(f"  Hardwood: {hardwood:.0f} m³, Softwood: {softwood:.0f} m³")

    return harvest_by_year


def fast_resample_sum(src_array, src_transform, src_crs, dst_shape, dst_transform, dst_crs, output_path=None):
    """Faster resampling using GDAL"""

    # Create temporary input file
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_src:
        tmp_src_path = tmp_src.name

    # Write source array to temporary file
    driver = gdal.GetDriverByName('GTiff')
    src_ds = driver.Create(tmp_src_path, src_array.shape[1], src_array.shape[0], 1, gdal.GDT_Int16)
    src_ds.SetGeoTransform([src_transform[2], src_transform[0], src_transform[1],
                            src_transform[5], src_transform[3], src_transform[4]])

    # Set CRS
    srs = osr.SpatialReference()
    if hasattr(src_crs, 'to_wkt'):
        srs.ImportFromWkt(src_crs.to_wkt())
    else:
        srs.ImportFromWkt(str(src_crs))
    src_ds.SetProjection(srs.ExportToWkt())

    # Write data
    band = src_ds.GetRasterBand(1)
    band.WriteArray(src_array)
    band.SetNoDataValue(0)
    band.FlushCache()
    src_ds = None

    # Create output file path
    if output_path is not None:
        out_path = str(output_path)
    else:
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_dst:
            out_path = tmp_dst.name

    # Set up warp options
    warp_options = gdal.WarpOptions(
        format='GTiff',
        outputBounds=(dst_transform[2], 
                     dst_transform[5] + dst_shape[0] * dst_transform[4],
                     dst_transform[2] + dst_shape[1] * dst_transform[0],
                     dst_transform[5]),
        xRes=abs(dst_transform[0]),
        yRes=abs(dst_transform[4]),
        dstSRS=dst_crs.to_wkt() if hasattr(dst_crs, 'to_wkt') else str(dst_crs),
        resampleAlg='sum',
        outputType=gdal.GDT_Float32,
        creationOptions=['COMPRESS=LZW'],
        dstNodata=0
    )

    # Perform warp
    print(f"    Running GDAL warp...")
    gdal.Warp(out_path, tmp_src_path, options=warp_options)

    # Read result
    dst_ds = gdal.Open(out_path, gdalconst.GA_ReadOnly)
    result = dst_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
    dst_ds = None

    # Clean up temporary source file
    os.unlink(tmp_src_path)

    # Clean up temporary output file if not saving
    if output_path is None:
        os.unlink(out_path)
    else:
        print(f"    Saved resampled raster to: {output_path}")

    # Ensure result matches expected shape
    if result.shape != dst_shape:
        padded = np.zeros(dst_shape, dtype=np.float32)
        copy_h = min(result.shape[0], dst_shape[0])
        copy_w = min(result.shape[1], dst_shape[1])
        padded[:copy_h, :copy_w] = result[:copy_h, :copy_w]
        return padded

    return result

def process_year(year, conifer_vol, deciduous_vol, conifer_profile, provincePolygon, study_area, pixel_ratio):
    print(f"\nProcessing year {year}...")

    # Load CanLad raster
    canlad_path = f"./InputData/Rasters/canlad_annual_{year}_v1.tif"

    try:
        with rasterio.open(canlad_path) as src:
            # Get raster CRS
            raster_crs = src.crs

            # Reproject provincePolygon if needed
            if provincePolygon.crs != raster_crs:
                provincePolygon_reprojected = provincePolygon.to_crs(raster_crs)
            else:
                provincePolygon_reprojected = provincePolygon

            print(f"  Cropping CanLad raster to {provincePolygon['gn_name']}...")
            provincePolygon_geom = [provincePolygon_reprojected.geometry.union_all().__geo_interface__]
            canlad_data, canlad_transform = mask(src, provincePolygon_geom, crop=True, all_touched=True)
            canlad_profile = src.profile.copy()
            canlad_profile.update({
                "height": canlad_data.shape[1],
                "width": canlad_data.shape[2],
                "transform": canlad_transform
            })
    except FileNotFoundError:
        print(f"  WARNING: CanLad file not found for year {year}, skipping...")
        return None, None

    # Reclassify: 2 or 5 -> 1, else -> 0
    print(f"  Reclassifying harvest pixels...")
    harvest_mask = np.isin(canlad_data[0], [2, 5]).astype(np.int16)

    # Resample to 250m with sum - using GDAL
    print(f"  Resampling to 250m resolution...")
    dst_shape = (conifer_vol.shape[0], conifer_vol.shape[1])

    # Create output path for debugging
    output_dir = Path("./InputData/Rasters/resampled_debug")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"canlad_resampled_250m_{year}.tif"

    resampled = fast_resample_sum(
        harvest_mask, 
        canlad_transform, 
        canlad_profile['crs'],
        dst_shape,
        conifer_profile['transform'],
        conifer_profile['crs'],
        output_path=output_path
    )

    # Convert count to percentage
    print(f"  Converting to harvest percentage...")
    harvest_percentage = resampled * pixel_ratio
    harvest_percentage = np.clip(harvest_percentage, 0, 100) / 100.0  # Convert to 0-1 range

    # Calculate harvested volumes
    print(f"  Calculating harvested volumes...")
    conifer_harvested = conifer_vol * harvest_percentage
    deciduous_harvested = deciduous_vol * harvest_percentage

    # Sum for Province
    conifer_provincePolygon_sum = np.sum(conifer_harvested[conifer_harvested > 0])
    deciduous_provincePolygon_sum = np.sum(deciduous_harvested[deciduous_harvested > 0])

    print(f"  Province totals - Conifer: {conifer_provincePolygon_sum:.2f} m³, Deciduous: {deciduous_provincePolygon_sum:.2f} m³")

    # Mask to study area
    print(f"  Masking to study area...")

    # Reproject study area if needed
    if study_area.crs != conifer_profile['crs']:
        study_area_reprojected = study_area.to_crs(conifer_profile['crs'])
    else:
        study_area_reprojected = study_area

    study_geom = [study_area_reprojected.geometry.union_all().__geo_interface__]

    # Create temporary raster for masking
    with rasterio.MemoryFile() as memfile:
        with memfile.open(**conifer_profile) as mem_dataset:
            mem_dataset.write(conifer_harvested, 1)
            conifer_study, _ = mask(mem_dataset, study_geom, crop=False, all_touched=True)

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**conifer_profile) as mem_dataset:
            mem_dataset.write(deciduous_harvested, 1)
            deciduous_study, _ = mask(mem_dataset, study_geom, crop=False, all_touched=True)

    # Sum for study area
    conifer_study_sum = np.sum(conifer_study[conifer_study > 0])
    deciduous_study_sum = np.sum(deciduous_study[deciduous_study > 0])

    print(f"  Study area totals - Conifer: {conifer_study_sum:.2f} m³, Deciduous: {deciduous_study_sum:.2f} m³")

    # Calculate ratios
    conifer_ratio = conifer_study_sum / conifer_provincePolygon_sum if conifer_provincePolygon_sum > 0 else 0
    deciduous_ratio = deciduous_study_sum / deciduous_provincePolygon_sum if deciduous_provincePolygon_sum > 0 else 0

    print(f"  Ratios - Conifer: {conifer_ratio:.6f}, Deciduous: {deciduous_ratio:.6f}")

    return conifer_ratio, deciduous_ratio

def main():
    print("="*60)
    print("ANNUAL HARVEST VOLUME ANALYSIS")
    print("="*60)

    # Load shapefiles
    print("\nLoading shapefiles...")
    provinceName, provincePolygon = get_province_from_landscape()
    study_area = gpd.read_file("./InputData/study_landscape.shp")

    print(f"{provinceName} shapefile CRS: {provincePolygon.crs}")
    print(f"Study area shapefile CRS: {study_area.crs}")
    
    # Load harvest data
    harvest_data = load_harvest_data(provinceName)

    # Load temporary NFI rasters
    print("\nLoading temporary NFI volume rasters...")
    base_path = Path("./InputData/Rasters")
    conifer_path = base_path / "temp_conifer_volume_2001.tif"
    deciduous_path = base_path / "temp_deciduous_volume_2001.tif"

    with rasterio.open(conifer_path) as src:
        conifer_vol = src.read(1)
        conifer_profile = src.profile
        print(f"NFI raster CRS: {src.crs}")

    with rasterio.open(deciduous_path) as src:
        deciduous_vol = src.read(1)

    # Calculate pixel ratio (30m to 250m)
    pixel_ratio = (30 * 30) / (250 * 250)
    print(f"Pixel ratio (30m to 250m): {pixel_ratio:.6f}")

    # Process each year
    results = []

    for year in range(2000, 2021):
        conifer_ratio, deciduous_ratio = process_year(
            year, conifer_vol, deciduous_vol, conifer_profile, 
            provincePolygon, study_area, pixel_ratio
        )

        if conifer_ratio is not None:
            # Get harvest volumes from CSV - FIXED
            year_harvest = harvest_data[harvest_data['Year'] == year]

            softwood_rows = year_harvest[year_harvest['Species group'] == 'Softwoods']
            hardwood_rows = year_harvest[year_harvest['Species group'] == 'Hardwoods']

            softwood_vol = softwood_rows['Volume (cubic metres) (En)'].sum() if len(softwood_rows) > 0 else 0
            hardwood_vol = hardwood_rows['Volume (cubic metres) (En)'].sum() if len(hardwood_rows) > 0 else 0

            print(f"  CSV volumes - Softwoods: {softwood_vol:.2f} m³, Hardwoods: {hardwood_vol:.2f} m³")

            # Calculate study area volumes
            study_softwood = softwood_vol * conifer_ratio
            study_hardwood = hardwood_vol * deciduous_ratio
            
            # Compute areas for thinning
            commercialThinningAreaProvince, preComThinningAreaProvince = get_thinning_areas(year, provinceName)
            study_commercialThinningArea = commercialThinningAreaProvince * ((conifer_ratio+deciduous_ratio)/2)
            study_preComThinningArea = preComThinningAreaProvince * ((conifer_ratio+deciduous_ratio)/2)

            results.append({
                'Year': year,
                'Softwood_m3': study_softwood,
                'Hardwood_m3': study_hardwood,
                'Commercial Thinning Area Ha': study_commercialThinningArea,
                'Pre Commercial Thinning Area Ha': study_preComThinningArea
            })

            print(f"  Estimated study area harvest - Softwood: {study_softwood:.2f} m³, Hardwood: {study_hardwood:.2f} m³")

    # Calculate and display averages
    with open('AnnualHarvestAnalysis_Output.txt', 'w') as f:
        print("\n" + "="*60, file=f)
        print("RESULTS - AVERAGE ANNUAL HARVEST VOLUMES", file=f)
        print("="*60, file=f)

        if len(results) > 0:
            results_df = pd.DataFrame(results)
            avg_softwood = results_df['Softwood_m3'].mean()
            avg_hardwood = results_df['Hardwood_m3'].mean()
            avg_study_commercialThinningArea = results_df['Commercial Thinning Area Ha'].mean()
            avg_study_preComThinningArea = results_df['Pre Commercial Thinning Area Ha'].mean()

            print(f"\nAverage annual softwood harvest: {avg_softwood:.2f} m³", file=f)
            print(f"Average annual hardwood harvest: {avg_hardwood:.2f} m³", file=f)
            print(f"\nTotal average annual harvest: {avg_softwood + avg_hardwood:.2f} m³", file=f)
            print(f"\nAverage annual area harvested with Commercial thinning: {avg_study_commercialThinningArea:.2f} ha", file=f)
            print(f"\nAverage annual area harvested with Pre Commercial thinning: {avg_study_preComThinningArea:.2f} ha", file=f)

            # Display year-by-year results
            print("\n" + "-"*60, file=f)
            print("Year-by-year breakdown:", file=f)
            print("-"*60, file=f)
            for _, row in results_df.iterrows():
                print(f"{int(row['Year'])}: Softwood={row['Softwood_m3']:.2f} m³, Hardwood={row['Hardwood_m3']:.2f} m³, Com. Thinning={row['Commercial Thinning Area Ha']:.2f} ha, Pre-Com. Thinning={row['Pre Commercial Thinning Area Ha']:.2f} ha", file=f)
        else:
            print("\nNo results to display - no years were successfully processed.", file=f)

if __name__ == "__main__":
    main()
