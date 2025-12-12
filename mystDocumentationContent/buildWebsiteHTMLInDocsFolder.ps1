# To use this script, you need to install myst on a Python environment accessible from the powershell you will be using.
# See https://mystmd.org/guide/installing
# Simplest : Download Python from the main Python website, and install Myst with pip install mystmd.
# If using anaconda : install Myst in a conda environment from which you will launch the script.

# Set the BASE_URL environment variable to a placeholder address
# If you wanna test the site locally first : use "file://PATH_TO_DOCS_FOLDER_ON_YOUR_COMPUTER".
$env:BASE_URL = "https://klemet.github.io/MHS-CBAU"

# Build the HTML files
myst build --html

# Define the source and destination directories
$sourceDir = "_build/html"
$destDir = "../docs"

# Delete the destination directory if it exists
Write-Host "Removing $destDir if it exists."
if (Test-Path -Path $destDir) {
    Remove-Item -Path $destDir -Recurse -Force
}

# Create the destination directory
Write-Host "Creating $destDir."
New-Item -ItemType Directory -Path $destDir

# Copy all files and subdirectories from the source directory to the destination directory
Write-Host "Copying build files in $destDir."
Copy-Item -Path $sourceDir\* -Destination $destDir -Recurse

# Create an empty .nojekyll file in the docs folder
Write-Host "Creating .nojekyll file for github."
New-Item -ItemType File -Path "$destDir\.nojekyll" -Force

# Remove build folder
Write-Host "Removing _build folder."
if (Test-Path -Path "_build") {
    Remove-Item -Path "_build" -Recurse -Force
}

# Output a message indicating the operation is complete
Write-Host "All files and subdirectories have been successfully moved to the $destDir folder."
