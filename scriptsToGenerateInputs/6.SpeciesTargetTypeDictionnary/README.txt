✅ Goal of these scripts : To create a python dictionnary in JSON format that associates tree species code to the wood volume target they participate to if they are harvested. Wood volume targets are defined in 1.VolumeAndAreaTargetsCalculation as either hardwood or softwood. The script uses a simple list of gymnosperm genuses in Canada to identify the softwood species, and the rest is identified as hardwoods.

📋 REQUIREMENTS : You need Python installed on your computer. See https://www.python.org/downloads/ to install.

📦 INPUT : The script needs the file woodDensityDictionnary.json created by 5.WoodDensityBiomassDictionnary to retrieve the list of species of interest (all tree species of Canada, at least those associated with a Wood density value).

👉 HOW TO RUN :

- If on your own Windows computer :
	- Run the python scripts 1 in a powershell or command prompt using the "python" command (e.g. "python 1.createSpeciesTargetTypeDictionnary.py"). The results should be speciesTargetType.json.