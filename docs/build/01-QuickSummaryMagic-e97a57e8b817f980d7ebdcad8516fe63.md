# A very short summary of Magic Harvest

**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)\

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

:::{note} This is only a summary !
The content of this section is a very short summary of the [Magic Harvest Workshop](https://klemet.github.io/Workshop-MagicHarvest/). If you wanna learn more about Magic Harvest and its subtilities, I advise that you take a look at it.
:::


## A metaphor : Magic and B. Harvest

```{image} ./images/Slide10.jpg
:width: 100%
:align: center
```

Magic Harvest is a LANDIS-II extension. It's one of the three necessary to use MHS-CBAU (see previous slides). It's the one that really allows MHS-CBAU to exist, as it allows the user to run scripts or programs during the simulation to make management decisions.

It works in tandem with the Biomass Harvest extension of LANDIS-II. As a metaphor : Biomass harvest is like a forester. It has the tools to harvest trees (can harvest trees in LANDIS-II), and can do some management decisions too (but the algorithm is simple and limited). He can work solo !

In contrast, Magic Harvest is a forest engineer. Their main skill is making decisions; they have not tools to cut trees ! (The code of Magic Harvest cannot remove trees in LANDIS-II). So, Magic Harvest has to work in tandem with Biomass Harvest and cannot work solo. When they work in tandem, Magic Harvest can make the management decisions (where and how to harvest at this timestep), and Biomass Harvest will do the actual harvesting (removing trees in the internal variables of LANDIS-II).


## Controlling Biomass Harvest with Magic Harvest and a Python script

```{image} ./images/Slide11.jpg
:width: 100%
:align: center
```

As detailed in the [Magic Harvest Workshop](https://klemet.github.io/Workshop-MagicHarvest/), Magic Harvest can work in tandem with Biomass Harvest with different degrees of control. As Biomass Harvest still has a decision algorithm implemented, Magic Harvest can make some of the decisions, or ALL of the decisions concerning harvesting at the time step.

Here, in MHS-CBAU, we use Magic Harvest in a "total control" mode. This is how it works, as a summary (more information are [in the workshop](https://klemet.github.io/Workshop-MagicHarvest/)) : 
- At every timestep, Magic Harvest runs BEFORE Biomass Harvest.
- When it runs, it will call a custom command (for example : run a given Python script).
- The command/script will make all of the management decisions, and return a management map of the same dimension as the landscape.
- In this management map, we find pixels filled with a code corresponding to a given management prescription (e.g. clearcutting).
- We will also return an edited version of the parameter text file of Biomass Harvest, which can contain additional prescriptions (e.g. prescriptions with a certain form a planting), and an edited harvest implementation table (that tells Biomass Harvest to harvest 100% of all pixels with a given code in the management map with the prescription associated with the code).
- Then, Magic Harvest will make Biomass Harvest re-load its internal parameters using this management map and edited parameter text file for Biomass Harvest. This will override the decision algorithm of Biomass Harvest, which will harvest the pixels on the landscape exactly as Magic Harvest planned it. 