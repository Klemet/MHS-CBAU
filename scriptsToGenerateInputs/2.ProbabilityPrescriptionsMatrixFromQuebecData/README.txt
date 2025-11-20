✅ Goal of these scripts : To compute a matrix of frequency of use of different forest cuts (clearcuts; shelterwood; seed tree; and selection cutting, as used in the datasets of the National Forestry Database of Canada) accross different 4 different stand types (even-aged/shade tolerant; even-aged/shade intolerant; uneven-aged/shade tolerant; uneven-aged/shade intolerant) based on data of Quebec. These frequencies are expressed in relative terms (e.g. 80% of the surface of even-aged/shade tolerant stands is harvested with clearcutting, 0.1% with selection cutting, etc.), but can be used as a guide to derive the probabilities of applying a given prescription to a given type of stand. These probabilities are necessary for the MHS-CBAU approach. Here, the frequencies are computed based on two Quebec datasets : the 5th provincial forest inventory (see https://www.donneesquebec.ca/recherche/fr/dataset/resultats-d-inventaire-et-carte-ecoforestiere) and the harvest dataset (see https://www.donneesquebec.ca/recherche/dataset/recolte-et-reboisement). The harvest dataset in particular is quite unique as it is very detailed and publicly available, which does not seem to be the case for other provinces. Ideally, we should get these probabilities for each province; but I haven't been able to get the same datasets for other provinces, and no federal dataset seem to exist.

⚠ WARNING : I do not recommand to use the frequencies that get out of these script directly as probabilities of applying a given prescription for a given stand. They should be used as an additional information for your decision, but should not be taken litteraly. This is because there is a temporal mismatch beween most of the harvest data and the forest inventory data; the forest inventory data is most often more recent than the harvest data. The assumption here is that the forest types (even-aged, uneven-aged, dominated by shade-tolerant or intolerant species) do not change too fast with time, as to the mismatch should not have too much impacts on the results. But it is still there. Another issue comes from determining if a stand is even-aged, uneven-aged, shade-tolerant or intolerant. This is especially touchy for shade-tolerance, as it is not a binary measure at the species level, and even less at the stand level. I use some pretty simple criterias here.

⚠ WARNING : These scripts use a lot of RAM, and it's better to run them on a computer with a lot of RAM or even on clusters of the Digital Research Alliance or Compute Canada (or any other supercomputing cluster). A job script file for the clusters of compute Canada is here.

⚠ WARNING : The input data is fairly large (around 14Gb), and need to be un-zipped. This means you will need around 30Gb of free space on your computer to use these scripts. The scripts will also create a large temporary file that can weight around 20Gb when running. It's much better to run these scripts on Digital Research Alliance's or Compute Canada's clusters.

⚠ WARNING : When downloading the input files on your computer with 1.downloadFiles_installPythonEnv.py, you might get errors because of your VPN. Try disconnecting from your VPN to try again if that happens.

📋 REQUIREMENTS : You need Python installed on your computer. See https://www.python.org/downloads/ to install.

📦 INPUTS : The script uses two .gdb spatial dataset for Quebec (that are downloaded with 1.downloadInputFiles.py), but it also uses two .JSON file that I've created manually. These JSON files contains information about the shade tolerance of all tree species in Quebec that can be found in the 5th provincial forest inventory data (with URL for sources about their tolerance status), and the keys to reclassifies the forest operations coded in the harvest data (there are a lot of them) into the 4 categories used in the National Forestry Database of Canada (which we're using for the rest of the MHS-CBAU approach). This second JSON about forest operation has been done by hand and arbitrarely, by interpreting the different foresty operations based on my own knowledge of them.

👉 HOW TO RUN :


- If running the scripts pyon a Digital Research Alliance/Compute Canada cluster :
    - run 1.downloadFiles_installPythonEnv.py on your computer using Python, so as to download the input files on your computer.
	- Then, upload all of the files of the folder on the cluster.
	- Then, rename the words YOUR_CLUSTER_ACCOUNT_HERE and YOUR_EMAIL_HERE in the job script job_script_MHS-CBAU_VolumeTargetComputation.sh, and launch the script as a job using the "sbatch" command. Let the job run its course.
	- You should find two output files : forest_cut_matrix.csv contains a matrix of frequency (per hectare of stands of a given forest type) for 4 cut categories of the National Forestry Database of Canada; but it also contains stands of unknown types, and a "others" section for all forest operations that were not cuts, or where unknown. Each number in this matrix is the percentage of surface in each category for all of the forest operation polygons in the harvest dataset. The file forest_cut_matrix_probabilities.csv removes the "others" or "unknown" categories, and expresses percentages for each given stand type (i.e. all percentage for a stand type/column are equal to 1). This second file is probably the one you will want.

- If on your own Windows computer :
	- Run the python scripts 1 and 2 in a powershell or command prompt using the "python" command (e.g. "python 1.downloadInputFiles.py").
	- Then, load the python environment in a terminal using .\PythonEnv\Scripts\Activate.ps1 if you are in a powershell on Windows, or .\PythonEnv\Scripts\activate.bat in a command prompt.
	- Run script 3. You will need a lot of RAM for it, or a lot of space on a SSD so that windows can create a pagefile. When everything is done, you should find two output files : forest_cut_matrix.csv contains a matrix of frequency (per hectare of stands of a given forest type) for 4 cut categories of the National Forestry Database of Canada; but it also contains stands of unknown types, and a "others" section for all forest operations that were not cuts, or where unknown. Each number in this matrix is the percentage of surface in each category for all of the forest operation polygons in the harvest dataset. The file forest_cut_matrix_probabilities.csv removes the "others" or "unknown" categories, and expresses percentages for each given stand type (i.e. all percentage for a stand type/column are equal to 1). This second file is probably the one you will want.
	
	
📊 RESULTS

Here is the resulting matrix (you should normally obtain the same) in forest_cut_matrix_probabilities.csv :

CUTTYPE						Even/Tol		Uneven/Tol		Even/Intol		Uneven/Intol
Clearcut					0.9085			0.3044			0.9277			0.7244
Seed Tree					0.0135			0.043			0.0097			0.0256
Selection Cutting			0.0702			0.6408			0.0584			0.2436
Shelterwood					0.0078			0.0118			0.0042			0.0064