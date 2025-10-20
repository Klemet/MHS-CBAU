✅ Goal of these scripts : To compute volume targets of wood harvested in a study landscape in Canada based on historical data from the past 20 years-ish. Also retrieves the area harvested for Commercial Thinning and Pre-Commertial Thinning, which area dealt with in area target instead of volume target in this Magic Harvest Scripting - Canadian Business As Usual (MHS-CBAU) method.

⚠ WARNING : These scripts use a lot of RAM, and it's better to run them on a computer with a lot of RAM or even on clusters of the Digital Research Alliance or Compute Canada (or any other supercomputing cluster). A job script file for the clusters of compute Canada is here.

⚠ WARNING : When downloading the input files on your computer with 1.downloadFiles_installPythonEnv.py, you might get errors because of your VPN. Try disconnecting from your VPN to try again if that happens.

📋 REQUIREMENTS : You need Python installed on your computer. See https://www.python.org/downloads/ to install.

👉 HOW TO RUN :

- First, create a shapefile containing your study landscape, and put it in /IntputData with the name study_landscape.shp (all files coming with the shapefile but with different extensions must have study_landscape as their name too). The script will detect it automatically. Your study landscape should be contained into a single Canadian province (and not accross two provinces or more); if that's not the case, you will get an error. If your study landscape is into several Canadian Provinces at once, either clip it, or cut it in half and run the scripts twice to get the estimates for each part the study landscape, and then sum the estimates together.

- If running the scripts pyon a Digital Research Alliance/Compute Canada cluster :
    - run 1.downloadFiles_installPythonEnv.py on your computer using Python, so as to download the input files on your computer.
	- Then, upload all of the files of the folder on the cluster.
	- Then, rename the words YOUR_CLUSTER_ACCOUNT_HERE and YOUR_EMAIL_HERE in the job script job_script_MHS-CBAU_VolumeTargetComputation.sh, and launch the script as a job using the "sbatch" command. Let the job run its course.
	- You should find the outputs in AnnualHarvestAnalysis_Output.txt in the main folder where the python scripts are. If you didn't, there has been an error; open the .out file corresponding to the job to see what happened.

- If on your own Windows computer :
	- Run the python scripts 1 and 2 in a powershell or command prompt using the "python" command (e.g. "python 1.downloadInputFiles.py").
	- Then, load the python environment in a terminal using .\PythonEnv\Scripts\Activate.ps1 if you are in a powershell on Windows, or .\PythonEnv\Scripts\activate.bat in a command prompt.
	- Run script 3 and 4 with the python environment loaded. You will need a lot of RAM for both, or a lot of space on a SSD so that windows can create a pagefile. but especially for 4.analyzeAnnualHarvest.py. When everything is done, you should find the outputs in AnnualHarvestAnalysis_Output.txt in the main folder where the python scripts are.