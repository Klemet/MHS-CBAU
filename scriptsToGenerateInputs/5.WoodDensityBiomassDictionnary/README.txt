✅ Goal of these scripts : To create a python dictionnary in JSON format that associates values of wood density (in oven dry mass/fresh volume as metricTons per m3) from the Global Wood Density Database (see https://zenodo.org/records/13322441) to the tree species codes used in the National Forest Inventory of Canada. The tree species codes for which we'll be getting the wood density from the database are taken from a .csv file also used in 4.MerchantableBiomassDictionnary, which contains equation parameters compiled by the NFI to compute the different ratios of biomass in a tree (stem, bark, branches, leaf) for many different species used in the NFI.

⚠ WARNING : Many of the species code from the NFI .csv don't match because they are codes for generic species (e.g. PINU.SPP for unidentified pines), or are for shrubs (for which the Global Wood Density Database do not have values), or for species names that are disputed or not referenced anywhere else (e.g. BEUT.ALA for Betula alaskana). 

⚠ WARNING : You might get errors when the script downloads some files because of your VPN. If this happens, try to disable your VPN temporarely and re-launch the script.

📋 REQUIREMENTS : You need Python installed on your computer. See https://www.python.org/downloads/ to install.

👉 HOW TO RUN :

- If on your own Windows computer :
	- Run the python scripts 1 in a powershell or command prompt using the "python" command (e.g. "python 1.createDictionnaryOfWoodDensity.py"). The results should be wood_density_dictionary.json.