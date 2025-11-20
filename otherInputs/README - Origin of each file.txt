1. probabilityMatrixCutsVersusStandType.csv

Created based by hand in Microsoft Excel. These probabilities are the combination of a first guesses from my own knowledge and readings about the use of cut types in forestry in Canada, and empirical probabilities generated with the scripts at scriptsToGenerateInputs/2.ProbabilityPrescriptionsMatrixFromQuebecData. I refined my first guesses with the empirical probabilities while still respecting the following rules I used for my first guesses :

- Clearcut is often used is Canada as it is the best option economically. As climate change pushed toward more deciduous species, it will keep being used to promote even-aged stands of coniferous species (which are the most diserable for the industry). However, it is particularly used in even-aged stands with shade-intolerant species.
- Shelterwood is much less used than clearcut, but is used when trying to regenerate shade-tolerant species. We also use it in shade-intolerant uneven-aged stands to promote shade tolerant species and an even-aged structure.
- Seed-tree is much less used than clearcuts, and is used to regenerate even-aged stands with shade-intolerant species. It's used in shade-tolerant stands to promote them back to shade-intolerant compositions, and a bit in uneven-aged stands to promote them back to even-aged structures.
- Selection cutting is used in uneven-aged stands only, and is more used in shade-tolerant stands; but can also be used in shade-intolerant stands sometimes.


2. shadeToleranceSpeciesCanada.json

Created using AI (a large language model or LLM). I asked a LLM to help me create a JSON file that would indicate the shade tolerance status (binary : tolerant or intolerant) of many tree species in Canada. I also asked the LLM to clearly indicate the source of information to decide the status of each species. I then personally fact-check every single species by looking at the source the LLM had given, and validating that it was coherent with the status chosen by the LLM.

The set of Canadian tree species considered in the .json file correspond to the list of species in a document of the National Forest Inventory of Canada (NFI) that I used to create the Merchantable Biomass Ratios (see scriptsToGenerateInputs/4.MerchantableBiomassDictionnary ; the file is online at the adress https://nfi.nfis.org/resources/biomass_models/appendix2_table6_tb.csv ). I could have done it for more tree species, but as the MHS-CBAU approach would ultimatly be limited to the species present in the document with the least amount of species (as we need one set of parameters per species), and because it takes quite a while to fact-check every entry.

The choice between tolerant/intolerant is sometimes murky, as many species have a shade tolerance that changes with age, or that is difficult to position compared to other species. But in the end, it's their reputation as tolerant or intolerant that matters, as this classification is used to reproduce the decisions of forest managers/engineers.