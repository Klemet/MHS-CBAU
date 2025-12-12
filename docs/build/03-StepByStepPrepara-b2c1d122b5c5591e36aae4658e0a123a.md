# Step-by-step preparations of the input files for MHS-CBAU

**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)\

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

Now that we have seen how MHS-CBAU works, here is a step-by-step on how to generate and prepare all of the files for your simulation.

**Again, this is not a step-by-step of how the scripts work**; we’ve seen that in the previous section.

Here, we’re talking about what you need to do, in practice, to generate all of the files and get them ready so that you can use MHS-CBAU in your study landscape.


## About this step-by-step

```{image} ./images/Slide25.jpg
:width: 100%
:align: center
```

This step by step is written in the README of the Github repository of MHS-CBAU.

All of the files discussed here in the step-by-step are also in the Github repository of MHS-CBAU.

There is only one step in the step by step that is more complicated because it requires a lot of RAM : it's generating the wood volume and area targets for your area. It's because it uses a lot of high-resolution maps from federal datasets. But it comes with a way to run it on the computing cluster of Compute Canada/Digital Research Alliance of Canada.

We will talk here about a lot of different files here : don't panic. My advice : don't try to remember everything. Today, it's about understanding the methodology and having an idea of what you will have to do to follow the steps. 

Here are the steps, one by one :

```{image} ./images/Slide26.jpg
:width: 100%
:align: center
```

MHS-CBAU requires that you install several extensions of LANDIS-II :  ([Biomass Harvest](https://github.com/LANDIS-II-Foundation/Extension-Biomass-Harvest), [Magic Harvest](https://github.com/Klemet/LANDIS-II-Magic-Harvest) and [Output Biomass Community](https://github.com/LANDIS-II-Foundation/Extension-Output-Biomass-Community).

See the Biomass Harvest repository and the Magic Harvest repository and Output Biomasss Community for the installers. The [dockerized versions of LANDIS-II](https://github.com/LANDIS-II-Foundation/Tool-Docker-Apptainer) already contain both extensions.

:::{tip} LANDIS-II v7, or LANDIS-II v8 ?
MHS-CBAU should normally work with both LANDIS-II v7 and LANDIS-II v8 currently, as these three extensions functions in exactly the same way in the case of MHS-CBAU. 
:::

```{image} ./images/Slide27.jpg
:width: 100%
:align: center
```

Installing Python : Python is programming langage that can be used either as programs, scripts or interpreted through a console (like R). All of the scripts present in this repository are in Python. You will need it to run certain scripts that will generate the inputs for your study area, but also for the scripts that will run during your LANDIS-II simulation. But you need to make sure that you have some of the Python packages installed to run the scripts.

If you have never used Python before and don't plan to use it for something else than MHS-CBAU, here is the quick way to get things ready.
- Go on https://www.python.org/downloads/, download and install the latest version of Python.
- Create a virtual environment containing the packages necessary for MHS-CBAU scripts to run :
- Use `python -m venv PythonEnv` in any terminal to create the virtual environment in the folder PythonEnv where your terminal is currently pointing at.
- Use the one of the following commands to activate the virtual environment in your OS and terminal of choice :
    - `source PythonEnv/bin/activate` if you're on Linux/MacOS/using Git-bash
    - `PythonEnv\Scripts\activate.bat` if you're using a command prompt on Windows
    - `PythonEnv\Scripts\Activate.ps1` if you're using a Powershell prompt on Windows
- Install the packages needed for MHS-CBAU with `pip install numpy pandas rasterio tqdm`

You will need to activate this environment before launching your LANDIS-II simulations in the future so that the MHS-CBAU scripts can run during the simulation (see the activation command that fits your OS or command prompt you will use to run LANDIS-II as written above). Note that you can move or copy/paste the `PythonEnv` folder containing the virtual environment you have just created in another folder of your computer to put it closer to your LANDIS-II simulation files.

If you are using a Dockerized version of LANDIS-II, you can easily install Python and these 4 packages in the base environment of your docker image (no need to create a virtual environment), which will make the packages available to the MHS-CBAU scripts. Here are the commands needed :

```shell
RUN apt-get install -y \
python3 \
python-is-python3 \
pip

RUN pip install numpy pandas rasterio tqdm
```

```{image} ./images/Slide28.jpg
:width: 100%
:align: center
```

Creating the management areas and stands maps : These maps should be the same as the ones demanded by the Biomass Harvest extention. The way to make these will be unique to your study area, and will most likely easy to create using the finer-scale data (often forest polygons) that you will have used to create the initial conditions of your landscape.

The management area map should be of the same size and resolution as all of your other LANDIS-II maps for your study landscape. Pixels should contain a value that corresponds to the management area they are in. It's most likely that one of the values you will use will correspond to protected areas (areas without harvesting). Keep that value noted for later. In MHS-CBAU, we only distinguish between protected and non-protected areas; but you can customize the scripts for more nuance or for zoning.

The stand map should also be of the same size and resolution as all of your other LANDIS-II maps for your study landscape. Pixels should contain either 0 (inactive cell), or a number corresponding to the unique identifier of a stand. Therefore, all pixels with the same value will be considered to be in the same cell. However, all of the pixels of a given stands should be in one management area, and not two. You will get errors from the Biomass Harvest extension if you don't respect this rule. You will most likely create this map using forest polygons used for your initial conditions. 

```{image} ./images/Slide29.jpg
:width: 100%
:align: center
```

Converting your species name to the NFI terminology : This is to save you time, as the scripts and ready-made parameters in this repository use this format. If you don't use this format, you will have to edit some files down the road to avoid errors.

The format used by the NFI is described in [this document](https://nfi.nfis.org/resources/general/3-TreeSpeciesList-Version4.5.pdf
), and is as follow : `XXXX.YYY`, with `XXXX` being the first four letters of the Genus in capsize letters (e.g. `ABIE` for *Abies*) and `YYY` being the first three letters of the species name (e.g. `BAL` for *Balsamea*). This gives you `ABIE.BAL` for *Abies balsamea*, `PICE.MAR` for *Picea mariana*, etc.

You will find all of the codes for almost all species in Canada in [the document](https://nfi.nfis.org/resources/general/3-TreeSpeciesList-Version4.5.pdf
).

:::{warning} If you choose not to use this formatting
If you don't use this formatting, you will have to edit the name of the species in these 4 files further down the line : `merchantableBiomassRatiosDictionnary.json`; `shadeToleranceSpeciesCanada.json`; `speciesTargetType.json`; `woodDensityDictionnary.json`. See bellow for information about how these files are generated. **You will have to make sure that all of the species you simulate in LANDIS-II have their names present in these files**.
:::

```{image} ./images/Slide30.jpg
:width: 100%
:align: center
```

Defining the commercial species in your landscape : These commercial species will be the ones that will be planted in some cases after a clearcut in the MHS-CBAU algorithm. These species must be the most interesting species commercially for forest industries.

For example : in Quebec, these would mostly be white spruce and black spruce (PICE.MAR and PICE.GLA according to the format of the NFI; see above).

```{image} ./images/Slide31.jpg
:width: 100%
:align: center
```

Deciding a gross volume reduction factor : LANDIS-II computes the aboveground biomass of the age cohorts (in weight of biomass). In contrast, MHS-CBAU works by estimating the merchantable volume of the age cohort from the above ground biomass. It compares these merchantable volume to "merchantable volume targets" for the timestep, which are based on reported harvested volumes in Canada (from the National Forestry Database of Canada).

MHS-CBAU converts the aboveground biomass of LANDIS-II to merchantable volume so using three conversion factors : a ratio of merchantable versus total aboveground biomass; the wood density of the species; and a further reduction factor that accounts for wood that is, in the end, not used by the industry because of defects or other reasons. While the merchantable biomass ratios and wood density will be automatically generated by the scripts of the repository (see below), you can adjust this reduction factor yourself.

I recommend using a reduction factor of 7% (0.07) based on the data we have from Quebec on this gross-to-net reduction (see [here](https://diffusion.mern.gouv.qc.ca/public/DGAB/Registre_public/07_Donnees_forestieres/2023-2028/01_Unites_d'amenagement/TB06_matrice_repartition_reduction-produits-essence_2023-2028.xlsx)). You can also change this ratio by species.

```{image} ./images/Slide32.jpg
:width: 100%
:align: center
```

Creating a shapefile defining the extent of your study landscape : You can use [QGIS](https://qgis.org/) to do this. As much as possible, be certain that this extent is the same extent as the raster maps you are using in LANDIS-II.

```{image} ./images/Slide33.jpg
:width: 100%
:align: center
```

Running the script to compute the harvesting targets in your area : The scripts are located in `scriptsToGenerateInputs/1.VolumeAndAreaTargetsCalculation`.

You will find a README.txt file containing all of the instructions you will need to run the scripts.

I will describe the methodology of this script quickly here :

```{image} ./images/Slide34.jpg
:width: 100%
:align: center
```

The scripts use three federal datasets : CanLAD (which are 30x30m raster maps showing the forest disturbances detected from satellite every year throughout all of Canada); the NFI biomass rasters (250x250m raster maps showing the variation of biomass through all of Canada for 2001 and 2011); and the National Forestry Database (dataframes containing the reported values of harvested wood volume for softwoods and hardwoods in all provinces in Canada throughout different years).

Also, the script needs to know where your study landscape is, so you have to provide your study landscape in shapefile format.

```{image} ./images/Slide35.jpg
:width: 100%
:align: center
```

What the script is going to do is use these datasets to estimate the volume of hardwood and softwood trees harvested year by year in your study landscape.

To do this, it's going to get the value harvested in the province where your landscape is for the year; then, it's going to combine information from CanLAD and from the NFI biomass rasters to estimate the amount of biomass of hardwoods and softwoods harvested in your study area versus the one harvested in the province.

The script will then do a ratio of the volume harvested in the whole province versus the one in your study landscape; for example, 17% of the biomass harvested in Ontario in 2018 might have been harvested in your study landscape. The script will then multiply this ratio with the volumes harvested in the entire province, which then gives us a pretty good estimate of the volume harvested in your study landscape.

```{image} ./images/Slide36.jpg
:width: 100%
:align: center
```

The script will then derive this estimate for the year 2000 to the year 2020, every year; and then do an average across all years.

This average for each of the wood category we use (softwood and hardwoods) then becomes the wood targets for your landscape.

Note that we're talking about merchantable wood volume, meaning woods harvested in the province and then used by sawmills and factories, because that's the one reported in the National Forestry Database.

```{image} ./images/Slide37.jpg
:width: 100%
:align: center
```

As you can see, this is not a perfect method because of several caveats :
- CanLAD does not always detect cuts (especially partial cuts)
- the NFI biomass rasters are only for 2001 and 2011, even though we want to look at other years than these two, which will result in a temporal mismatch
- ideally, a biomass ratio should not be translated directly into a volume ratio, because the relation of biomass to volume can change depending of the species you're talking about.

But after a lot of researching, thinking and testing, this is the best compromise I found to allow you to derive these volume targets easily. Using federal datasets allow us to derive data for all of Canada easily, with a replicable and scripted methodology. And through testing, I've seen that the numbers obtained with this methodology were quite similar to those I got with previous attempts during my PhD thesis and my post-doc work that used more complicated and precise methods.

Why does it matter so much that we get the right volume targets ? Because it's going to influence harvesting in your landscape very heavily; 20% bigger targets means 20% more cuts in your landscape ! 

:::{note} What should be the timeframe of the Business as Usual here ?
When we define a Business as Usual scenario for a given landscape, we have to define what time period do we mean for the "as usual". Is it the last 5 years ? The last 10 years ? The last 20 years ? 30 years ? etc.

Thing is, Canadian forest management has changed in the past 30 years. Through social pressure and economic crisis, the wood volume harvested in the different provinces have Canada have really changed through time.

Based on the data available and on my own knowledge of these changes, the year 2000 to 2020 represents a pretty good fit. Harvesting in Canada was higher between 2000-2005 than it is today (it dropped at around 2008), but as the legacy of this more intense harvesting is still here, and because there's always a risk that we come back to these levels in the future, I'd say that this is a pretty good "Business As Usual" timeframe for Canada.
:::

```{image} ./images/Slide38.jpg
:width: 100%
:align: center
```

For the area targets for non-commercial prescriptions : the same script takes care of it, and the approach is similar – except we multiply the ratios computed between the whole province and the study landscape with the area harvesting with thinning. This gives us an estimate of the area harvested with thinning in the study landscape for each year, which we can average.

The scripts will output a file named `annualHarvestTargets.json`. Here is what it will look like. Keep this file at hand. Also keep in mind the units used in it : the main MHS-CBAU python script is adapted to used these units.

```{image} ./images/Slide39.jpg
:width: 100%
:align: center
```

Generating the merchantable ratios and ecozones map : The scripts are located in `scriptsToGenerateInputs/4.MerchantableBiomassDictionnary`. You will find a README.txt file containing all of the instructions you will need to run the scripts.

```{image} ./images/Slide40.jpg
:width: 100%
:align: center
```

To be quick : these ratios are gathered from tree biomass models used in the National Forest Inventory of Canada. These models are statistical models that can estimate the relative biomass of different part of the tree : Trunk, bark, branches and leaves. By looking at the trunk only, we get the merchantable part of the tree. These statistical models have parameters that change for each province and ecozone of Canada; sometimes, the parameters are not available for a certain species in a certain place for Canada (not enough real-life measures to make the parameters). In that case, the parameters are substituted for another ecozone/province nearby. 

The scripts will output two files you need to keep at hand : `EcozonesRaster.tif`, and `merchantableBiomassRatiosDictionnary.json`.

:::{danger} Avoiding the confusiong between *ecozones* (Canada) and *ecoregions* (LANDIS-II)
*Ecozones* are a classification system used by the different canadian agencies. They represent biomes : Thundra, Mixed forest, etc.

They should not be confused with the term *ecoregions*, which is a term used in LANDIS-II to define, inside the model, regions or pixels where the physical conditions (climate, slope, aspect, soils, etc.) are considered homogenous. So here, I’m talking about ecozones, the system used by the Canadian government – because the ratios we get here are defined per province and per ecozone. 
:::

The ecozone raster (`EcozonesRaster.tif`) contains a special ecozone ID representing a combo of ecozone/province so that we can get the right ratio for your species depending on where it is in Canada. The ecozone raster is made to have the same size as the other raster maps of your LANDIS-II simulation to make things easier. Again, don’t confuse it with your “Ecoregion raster”, which is a raster needed by your LANDIS-II simulation. I’m sorry that the terms are confusing.

:::{note} What about climate change ?
As climate change comes, the position of the ecozones of Canada (as defined by the canadian government) might change with time. Deciduous forests will climb up north, etc. 

However, we don’t deal with this change in position in MHS-CBAU. The ecozone rasters created here is made using the official files showing the position of ecozones in Canada today.

Apparently, while we know that ecozones will change in the future because of climate change, we don’t really have models to have predictions of their evolution as of today.

As such, we keep things static in MHS-CBAU. This might be a limitation that you might want to highlight in your papers if you use MHS-CBAU; although it will only concern these biomass ratios we used to compute merchantable volume from aboveground biomass.
:::

```{image} ./images/Slide41.jpg
:width: 100%
:align: center
```

Preparing the Output Biomass Community parameter file : The Output Biomass Community extension is vital to making the scripts of MHS-CBAU work. This extension outputs two files at each time step - a csv file and a raster file - which contain the composition of your LANDIS-II landscape in the same format as the initial condition raster and csv/text file you use to initialize LANDIS-II.

The MHS-CBAU script will read these file in order to get the current state of the landscape at each time step.At the time of writing this, Output Biomass Community doesn't have any parameter except from the timestep at which it runs. Therefore, just write a text file with the following :

Replace `X` with the timestep you are using for Magic Harvest and Biomass Harvest (**it must be the same timestep**).

The output files of Output Biomass Community are very large, but the MHS-CBAU script has some lines to remove these files once the timestep is over. You can edit the parameter DELETE_COMMUNITIES_FILES in `MHS-CBAU_MainScript.py` to change this.

**Be certain to write in your LANDIS-II scenario file that your scenario should use Output Biomass Community**.












## Thinking about what you can do with Magic Harvest

The three exercices that I propose here will not ask you to code in any programming langage.

What I'm going to do is ask you to write step-by-step algorithms in plain english about what a possible script used with Magic Harvest (whatever the programming langage you choose down the road) will be used for different use case.

In that way, when you'll try to use Magic Harvest for your own research, I hope that you'll have a general idea of what you'll want to do with it. The implementation of your algorithm in a programming - the coding part - is not necesseraly the most complex thing to do, especially with the new AI tools that are accessible today.

## Example of an algorithm in plain english

![](./images/Slide28.jpg)</br>

Here is an example of the kind of algorithm I propose that you'll write in the following exercises, in plain english. 

Here, we'll simply write the algorithm for a script that will do the following :

We want to do repeated partial cutting every 30 years for 90 years, and simple clearcutting in a landscape : So here, what we want to do is to harvest a certain percentage of the target with partial cutting, which demands that when we select a stand for harvesting with partial cutting, we have to come back every 30 years to harvest it until we reach 90 years, and then we stop coming back. 

Here is the resulting algorithm in plain english to write a script that will do this with Magic Harvest :

- Read the state of the landscape and put it in variables
- Define or read target of hectares to harvest with partial cutting and clear cutting
- Read a file containing information about stands that have been registered with repeated partial cutting and put it in a variable
- For each stand registered for repeated partial cutting :
	- Check if this year should be a year where the given stand is harvested with partial cutting (period of 30 years)
		- If it is the case, write the code corresponding to partial cutting in the management map for all of the pixels of the stand, and then record the - next time that the stand should be harvested in the variable
	- If not, do nothing.
	- Check if the stand has reached its last partial cutting (90 years are done)
		- If so, remove the stand from the variable
- Check if we need to add new stands to list of regular partial cutting reach the % of hectare harvested each year with partial cutting
	- If that's the case, rank the stands in the landscape based on their biomass.
	- Then, select stands starting with those with a lot of biomass until we reach the target. Add each of these stands to the list of repeated partial-  cutting.
- Then, look at all of the stands in the landscape and rank them by biomass
	- For each stand, looking at those with the most biomass first, register them for harvesting with clearcutting in the management map for all of the-  pixels of the stand
	- Stop when we have reached the target of hectares to harvest with clearcutting
- Export the management map and edit the parameter files of B. Harvest.


## First exercise - Salvage logging

```{exercise}
:label: exercise-1

![](./images/Slide30.jpg)</br>

Let's start simple : we're going to do salvage logging. 

We want that when a fire happens in the landscape, B. Harvest will go and harvest 70% all stands impacted by the fire (remember that a stand is a group of pixels in LANDIS-II). The prescription we will used called "salvage logging" will be pre-defined in the B. Harvest parameter text file, so we do not need to create it in the script. The rest of the harvesting for the current timestep will be left to B. Harvest to decide; so here, we do not take complete control.

Basically, that means that we are going to take the fire map created by one of the fire extensions of LANDIS-II; the management area map of B. Harvest; and we're going to merge the two to create a new management area corresponding to the fire. Then, we'll have to make sure that B. Harvest will harvest 70% of the surfaced of this new management area with the salvage logging prescription.

```

````{solution} exercise-1
:label: my-solution-exercise-1
:class: dropdown

Here is the resulting algorithm in plain english to write a script that will do this with Magic Harvest.

The solution here is relatively simple, because we're letting Biomass Harvest take a lot of decisions.

![](./images/Slide31.jpg)</br>

- Read latest fire map

- Edit the management area map to create a new one on the disturbance

- Edit the biomass harvest parameter file to make sure it will read the new map and edit its implementation table to add a new line to harvest 70% of the stands or of the surface of the new management area

````

## Second exercise - Clearcutting, Partial cutting and protected areas

```{exercise}
:label: exercise-2

![](./images/Slide32.jpg)</br>

We want to harvest with clearcutting and partial cutting until we reach a target of biomass. Not a target of surface, but a target of biomass. So here, we're taking complete control of what pixels and stands we will harvest, and we will make all of the decision to choose them. But we will stop when we have reached enough biomass harvest - something that B. Harvest cannot do, because B. Harvest cannot use biomass targets, only surface ! We will harvest 70% of the target of biomass with clearcutting, and then 30% with partial cutting. We will prioritize stands with the most biomass in them, but we will avoid stands located in protected areas.

So, we're going to read the stands in the landscapes; define a biomass target (it doesn't matter the number, just know that we have one); we're going to rank the stands, and then select stands with clearcutting or partial cutting until 70% of the biomass target is harvested with clearcutting, and 30% with partial cutting. And of course, we'll be mindful of the protected areas.

This one is going to be much more complex since we're taking complete control of what pixels will be harvested exactly. Take your time; you will surely encounter problems as you go forwards, for which you will have to go back and edit the beginning of your algorithm to get things ready for the rest.
```

````{solution} exercise-2
:label: my-solution-exercise-2
:class: dropdown

- Read the position of the stands and their composition in terms of vegetation/age cohorts and their biomass
- Read the location of protected areas, and create an object that defines if a stand is in a protected area or not
- Read or define in the script how clearcutting and partial cutting are done so that we can estimate the biomass harvested when we apply it to a - stand
- Prepare an empty management map filled with zeroes
- Define the overall biomass target
- Harvest 70% with clearcutting :
	- Rank the stand in the landscape based on their biomass
	- Create a list of stands harvested with clearcutting
	- Add stands to the clearcutting list one by one in ranking order
		- Check everytime if a stand is in a protected area. If it is not, then do not add it to the list
		- Estimate the biomass that will be harvested with the clearcutting in each given stand, and compute a sum
			- When the sum reaches 70% of the biomass target, stop the loop.
- Harvest 30% with partial cutting :
	- Same thing as with clearcutting : Rank stands according to biomass, add them to the list if they are not in a protected area or already - - - harvested by clearcutting. Compute the biomass that will be harvested by partial cutting everytime we add a stand to the list, and compute the - sum. When sum reaches 30% of the biomass target, stop the loop.
- For both the clearcutting and partial cutting list, look at each stand in both list
	- For each pixels of the stand, write the code corresponding to either clearcutting or partial cutting in the pixels of the management map
- Export the management map as a raster map
- Edit the biomass harvest parameter file to make sure it will read the new management map as both its management area raster and stand raster, and edit its implementation table to add two new lines to harvest 100% of the pixels corresponding to the code of clearcutting and partial - cutting with the respective prescription.
````

## Third exercise - Clearcutting and complex planting of rare species

```{exercise}
:label: exercise-3

![](./images/Slide34.jpg)</br>

We want to harvest a biomass target with clearcutting like we did before. But in a random 20% of the stands that we will harvest with clearcutting, we will do enrichment planting and add 2 rare species in the stand. We will add distribute these 2 rare species randomly in the cells of the stand, 1 species per cell. These rare species will be chosen based on the composition of the cell : we have a table giving us the priority for planting each of them. But if the rare species is already in the stand, then we will not plant it and choose another of lower priority. We will just do clearcutting to keep things simple, and nothing else. No partial cutting this time. No protected areas either.

So, like before, we would look at the stands in the landscape, take a biomass target, rank the stands, select stands for harvest with clearcutting until we reach the biomass target; then, we will select 20% of all stands harvested randomly, select 2 rare species to plant, and plant these species randomly in the stand, with one species planted by pixel. And so, we are going to need special prescription of clearcutting + planting because remember : B. Harvest can only do one type of planting by prescription. B. Harvest cannot vary the planting or do conditional planting for one prescription. So here, we have to prepare this for B.Harvest so that they know what to do.

This is basically what I've done in a recent paper (see [Hardy et al. 2025](https://dx.plos.org/10.1371/journal.pone.0326627)), albeit a little different.
```

````{solution} exercise-3
:label: my-solution-exercise-3
:class: dropdown

![](./images/Slide36.jpg)</br>

- Read the position of the stands and their composition in terms of vegetation/age cohorts and their biomass
- Read the location of protected areas, and create an object that defines if a stand is in a protected area or not
- Read or define in the script how clearcutting is done so that we can estimate the biomass harvested when we apply it to a stand
- Prepare an empty management map filled with zeroes
- Prepare an object to record new clearcutting prescription with different types of planting following the clearcut.
- Define the overall biomass target
- Select the stands to harvest :
	- Rank all of the stands in the landscape according to their biomass.
	- We add the stands one by one in their ranking order to the list of stands harvested with clearcutting for the timestep.
		- For each stand, we compute the biomass that clearcutting will harvest and we compute the sum.
	- We stop when we have reached the biomass target.
- We select 20% of stands randomly in the list of stand harvested with clearcutting.
	- For the 80% not selected, we input the code for simple clearcutting (without planting) in the empty management map.
	- For the 20% selected for planting, we look at stands one by one.
		- We select the 2 species to plant by looking at the composition of the stand and our priority list for planting.
		- Once the 2 species are selected, we check if clearcutting prescription with a planting of one of these 2 species already exist in our object to - record new planting prescriptions.
			- If it exist, we simply get the code for the two prescriptions that will plant these two species.
			- If it doesn't exist, we create them and generate new codes for them.
		- We then distribute the codes for the 2 planting prescriptions randomly in the cells of the stand in the management map, trying to have a 50/50 - ratio between the number of pixels with the first planting prescription and the second.
- Export the management map as a raster map
- Edit the biomass harvest parameter file to make sure it will read the new management map as both its management area raster and stand raster, - and edit its implementation table to add two new lines to harvest 100% of the pixels corresponding to the code of clearcutting and partial cutting with the respective prescription.
````