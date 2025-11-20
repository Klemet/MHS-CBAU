#!/bin/bash
#SBATCH --account=YOUR_CLUSTER_ACCOUNT_HERE
#SBATCH --mail-user=YOUR_EMAIL_HERE
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL
#SBATCH --time=02-00:00 # time (DD-HH:MM)
#SBATCH --ntasks=1 # number of MPI processes
#SBATCH --mem=80GB
#SBATCH --cpus-per-task=1
#SBATCH --job-name=MHS-CBAU_CutProbabilityMatrix
#SBATCH --output=%x-%j.out

# Loading packages
module load python
module load arrow

# Switching to SLURM temp folder for faster computing
startingFolder=$(pwd)
cp -r $startingFolder/. $SLURM_TMPDIR
cd $SLURM_TMPDIR/

# Creating Python virtual environment
virtualenv --no-download PythonEnv
source PythonEnv/bin/activate
pip install --no-index --upgrade pip
pip install --no-index pandas numpy fiona geopandas shapely pyogrio tqdm pyarrow

# Launching the scripts
python -u 3.ComputeFrequencyCutsPerForestTypeMatrix.py

# Disabling and delting python environment
deactivate
rm -r PythonEnv

# Copying the files back to where we started
cp -r $SLURM_TMPDIR/. $startingFolder

echo Job is over !