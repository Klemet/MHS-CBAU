✅ Goal of these scripts : To create a python dictionnary written in a JSON format that contains the ratios to use to compute the merchantable aboveground biomass (trunk biomass, without bark) from the aboveground biomass in LANDIS-II. This dictionnary is created using equation parameters from the National Forest Inventory of Canada (see http://cfs.nrcan.gc.ca/publications?id=27434 for documentation, and https://nfi.nfis.org/en/biomass_models for links to the dataset Appendix 2 Table 6 tb which we use). The dictionnary contains values for all species in the NFI, with species being named with the nomenclature of a 4 letters for the genus (e.g. PINU for Pinus) and 3 letters for the species name (e.g. BAN for Banksiana), separated by a point (e.g. PINU.BAN). You have to be certain that you use the same nomenclature in LANDIS-II, or you'll have to change the values in the output dictionnary to match the species names you use in LANDIS-II. The scripts will also generate a map for your study area that contains a code which refers to the combination of province/ecozone so that the main scripts of MHS-CBAU can lookup the right biomass ratio for a given stand.

⚠ WARNING : The script download some files from the Open Canada datasets to work; these files are small, but you might get download errors if you have a VPN. Try to turn your VPN off temporarely.

📋 REQUIREMENTS : You need Python installed on your computer. See https://www.python.org/downloads/ to install.

👉 HOW TO RUN :

- If on your own Windows computer :
	- Take one of the rasters used in your LANDIS-II simulation (it can be anything; initial communities raster, stand rasters, etc.; it just has to be a raster of your simulation to get the extent/resolution of your landscape) and put it in the folder ./InputData with the name "Study_landscape" (the extension can be anything; .tif, .img, etc., as long as it is a raster). The script will detect it and use it.
	- Run the python scripts 1 in a powershell or command prompt using the "python" command (e.g. "python 1.downloadInputFiles.py").
	- Then, load the python environment in a terminal using .\PythonEnv\Scripts\Activate.ps1 if you are in a powershell on Windows, or .\PythonEnv\Scripts\activate.bat in a command prompt.
	- Run script 2. The result should be in merchantableBiomassRatiosDictionnary.json and EcozonesRaster.tif.