# Customization of MHS-CBAU

**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

So now, you know how MHS-CBAU works. You know how to set it up. We're going to talk briefly about customizing the scripts to implement more complex forms of forest management (e.g. TRIAD zoning, etc.) so that you can test their effect compared to the Business as Usual implemented by default in the scripts of MHS-CBAU.


## Requirements

```{image} ./images/Slide44.jpg
:width: 100%
:align: center
```

Customizing will require more patience than setting up MHS-CBAU.

You will have to learn a bit of Python to code (you can also use AI models to help you, but be careful about understanding what you do !); you will have to at least read the scripts one time by yourself; and you will also have to test things.

Luckily, Python makes this easier by being an interpreted language, and the scripts of MHS-CBAU contains a "debug mode" made especially so that you can test the scripts ! That’s what we’re going to check out quickly.

```{image} ./images/Slide45.jpg
:width: 100%
:align: center
```

To use the “DEBUG mode” of MHS-CBAU, you should first run a LANDIS-II simulation for your landscape WITHOUT MHS-CBAU, just to generate some outputs; especially, you need the outputs of the Output Biomass Community files which contain the state of the landscape. You will use these to load the state of the landscape in the Python script, and so that you can then test out the rest of your script. So the goal of debug mode is to run the Python script on a snapshot of your landscape, even if this snapshot comes from an incomplete simulation (since MHS-CBAU will not be activated in this simulation).

Then, you just have to enable debug mode in the main MHS-CBAU script (`MHS-CBAU_MainScript.py`) by turning `DEBUG_MODE_ENABLED` to `True`, and filling out the line with `os.chdir` to point to the folder where the output files are. See the comments in the script for more.

Then, you can use Spyder – a free and open source software which is the equivalent of RStudio, but for Python – to run the script line by line, or section by section, allowing you to test it and debug it.


```{image} ./images/Slide46.jpg
:width: 100%
:align: center
```

The interface of Spyder is extremely similar to R Studio : your script on the left, and a terminal to the right to see what happens when you run sections of the script, or just a single line. Spyder can be downloaded on the spyder website. It will create its own virtual environment; but by going into "Consoles", you can create a new terminal from a Python virtual environment or a Anaconda virtual environment. So you can easily create an environment with the 4 packages necessary for MHS-CBAU, and then open a terminal from this environment.

From then on, you can run the code line by line, or section by section (`Shift` + `Enter` to run a code section in Spyder, which are defined by the caracters `#%%`). You can look at what the terminal writes; you can look at the variables in the variable explorer on the right; and you also have a profiler (see "Run" and then "Profile file" or "Profile cell" or "Profile line") to help you see what sections of the scripts take time to run, etc. Spyder is entirely free, open-source and super useful. It will help you a lot to do what you want to do if you have to customize MHS-CBAU.

```{image} ./images/Slide47.jpg
:width: 100%
:align: center
```

An example for implementing zoning : we want to harvest a different volume of wood in different zones in the landscape. Or maybe we want to have a different prescription regime for each zone ? 

First, we need to identify where management areas are registered in the script : it's in `standManagementUnitDict`, a dictionnary that register the management area of each stand in the landscape.

Then, we need to modify the Inputs section to read a python dictionary in JSON format that will contain one target per management area ID; or several dictionaries of prescription probabilities so that different prescriptions are chosen in different zones (see file `probabilityMatrixCutsVersusStandType`).

Finally, we need to do a "for" loop around the different ID of your management areas : the loop will do the same 3 steps (repeated prescriptions, new commercial prescriptions, non commercial prescriptions), but will do it differently for each zone (by using different wood targets for each zone, or by using different prescription probabilities for each zone)

```{image} ./images/Slide48.jpg
:width: 100%
:align: center
```

Another example with suggestions to implement the functional complex network (see [this article](https://doi.org/10.1186/s40663-019-0166-2) for more information).

- Add a new section (and most likely a new function) where we use the dictionnaries containing the location of the stands (`standCoordinatesDict`), the one containing the neighbor of each stand (`standNeighboursDict`), and the one containing the composition of each stand (`standCompositionDict`) to create a functional complex network.
- We then can compute the functional diversity of each stand with their composition (`standCompositionDict`), and then make a network with the position of the stands (`standCoordinatesDict` and `standNeighboursDict`)
- Finally, we can then write a new algorithm of selection of prescription for each stand, etc.

```{image} ./images/Slide49.jpg
:width: 100%
:align: center
```

- And that's it ! Here is what you might want to do following this workshop :

- When you will want to include harvesting in your LANDIS-II simulation, check [the repository of MHS-CBAU](https://github.com/Klemet/MHS-CBAU) for the step-by-step checklist to prepare all of the files for a Business As Usual scenario

- Test your Business As Usual scenario, see if the impact harvesting have on your outputs, etc. Debug if necessary.

- Then, once ready, you can customize the script to do some new management scenarios.

The content of this presentation (including the script of what I’ve said) is online !




![](./images/Slide37.jpg)</br>

Thank you for taking the time to learn to use Magic Harvest ! I hope it'll be as useful to you as it was to me.

You might think that this workshop is strangely detailed and complete for such a small extension of a single Forest Landscape Model. Truth is, I had a lot of colleagues and people in the LANDIS-II community asking me about Magic Harvest; and so, I decided to make sure that everybody had a good ressource to learn how to use it in the future.

As forest ecologists, we are now in great demand to investigate the long-term and large scale effect of forest management. Forest industries, governments and the public at large are desperate to find new ways to do forestry without compromising the health, integrity and complexity of forests.

While I do believe that there will be no miracles coming out of this research, and that our societies will most likely need to tune down our level of ressource consumption if we really want to help forest survivre the 21st century (and those that will come after), simulations can still clarifiy a lot of thing on these issues.

Magic Harvest offers you the capability of making complex management strategies in a completely flexible way while profiting from the amazing power of the LANDIS-II model. It basically allows you to couple a complex forest management model with a complex Forest landscape model. In my own experience, this is still really new, and very exciting for many people.

The sky is the limit : you might make management decisions based on complex algorithms that you will have created, or you might even use external models used in forestry (e.g. Woodstock) to do the decisions and import them back into LANDIS-II.

The main difficulty of Magic Harvest is not necesseraly to use it, but to use it in conjonction with the rest of LANDIS-II; because all of the other extensions of LANDIS-II need calibrating and parametrizing and all ! LANDIS-II is an awesome model, but it does take time and patience to get it in your mind and have a good view of what's going on. Luckily, it's often simpler to understand than other models thanks to its modular nature and its spatially explicit representation of things, which makes it easier to visualize in your mind. But once you'll get it, you will be a forest ecologist in very high demand. Congratulations for your perseverance !

One last word : I can answer some questions at clem.hardy@pm.me, but my time these days is quite limited. Still, feel free to send me a message !

Good luck simulating forests,


*Clément*




