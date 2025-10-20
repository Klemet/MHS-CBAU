✅ Goal of these scripts : To produce a file that contains the probability that a forest cut of a certain type (the 4 types used are the ones used in the National Forestry Database) be of a certain size. This file will be used in the MHS-CBAU approach to choose the right size for a given cut when running LANDIS-II. The dataset used to compute these sizes is the Quebec Harvest dataset after 1976 (see https://www.donneesquebec.ca/recherche/dataset/recolte-et-reboisement). I only use Quebec data because this is the only dataset I have found that is available publicly and is complete enough amongst canadian provinces, and because there is not federal dataset of this type.

⚠ WARNING : When downloading the input files on your computer with 1.downloadFiles_installPythonEnv.py, you might get errors because of your VPN. Try disconnecting from your VPN to try again if that happens.

📋 REQUIREMENTS : You need Python installed on your computer. See https://www.python.org/downloads/ to install.

👉 HOW TO RUN :

- For windows :
	- Run the python scripts 1 and 2 in a powershell or command prompt using the "python" command (e.g. "python 1.downloadInputFiles.py").
	- Then, load the python environment in a terminal using .\PythonEnv\Scripts\Activate.ps1 if you are in a powershell on Windows, or .\PythonEnv\Scripts\activate.bat in a command prompt.
	- Run script 3 with the python environment loaded. When everything is done, you will find the file cut_size_distributions.json. The file associate two lists for each of the 4 cut types of the National Forestry Database of Canada (Clearcut; Shelterwood; Seed-Tree; Selection cut). The first list contains the upper bounds of 100 different bins, corresponding to cut sizes. Each bin is made to countain around 1% of the polygons. The second list contains the probability associated to each bin, computed from the frequency of polygons that are in this bin. This is the file that the magic harvest scripts of MHS-CBAU will use down the line. The script will also create several matplotlib graphs in png format showing the distribution of the cutsizes with a histogram and a KDE.