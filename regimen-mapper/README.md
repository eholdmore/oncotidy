# Regimen Mapper
Turn messy free-text chemotherapy regimen data into tidy lists of **NCI Preferred Drug Names**.

## Description
Designed to work with **OncDRS** ```TREATMENT_PLAN``` tables (or similar), this tool parses free-text chemotherapy plan entries and maps them to standardized terms using the NCI Thesaurus.

It supports:

- Synonym expansion (e.g., “Taxotere” → “Docetaxel”)

- Regimen-level recognition (e.g., “Docetaxel/Cyclophosphamide” → "Docetaxel, Cyclophosphamide")

- Fuzzy matching

- Token-based pre-processing for speed and accuracy :rocket:

- Batch processing large datasets

## **Requirements**
These are lightweight, well-supported libraries:

- ```pandas``` – data loading and wrangling

- ```rapidfuzz``` – fast fuzzy matching

- ```tqdm``` – progress bar for longer-running operations

If you also want to keep compatibility with older ```fuzzywuzzy``` code, add:
```
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.12.2  # Optional speed boost for fuzzywuzzy
```
But for speed and better licensing, ```rapidfuzz``` is preferred.

## General Workflow
1. **Prepare input files:**

- Place your ```TREATMENT_PLAN.txt``` (pipe-delimited) file in the ```data/``` directory.

- Download the latest NCI Thesaurus tab-delimited flat file ZIP from [here](https://evs.nci.nih.gov/evs-download/thesaurus-downloads) and place it in the same ```data/``` folder.

2. **Set up the Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Generate the drug synonym lookup table:**
```bash
python create_drug_thesaurus.py
```

4. **Run the mapper:**
```bash
python get_drug_names.py
```

This will produce a CSV file with the following columns:

- ```DFCI_MRN```

- ```TPLAN_START_DT```

- ```STD_CHEMO_PLAN``` (original messy field)

- ```Standardized_Drugs``` (cleaned and matched NCI preferred names)

- ```Line_Number``` (if treatment line identification is included)

## Example Input
```TREATMENT_PLAN.txt```
```
DFCI_MRN|TPLAN_START_DT|STD_CHEMO_PLAN
######|2023-05-01|Docetaxel/Cyclophosphamide
######|2023-07-15|Nivolumab 3Mg/Kg/Ipilimumab 1Mg/Kg X4, Nivolumab 480 Mg Q4Wks
```

## Example Output
```standardized_treatment_output.csv```
```
DFCI_MRN,TPLAN_START_DT,STD_CHEMO_PLAN,Standardized_Drugs,Line_Number
######,2023-05-01,Docetaxel/Cyclophosphamide,cyclophosphamide, docetaxel,1
######,2023-07-15,Nivolumab 3Mg/Kg/Ipilimumab 1Mg/Kg X4, Nivolumab 480 Mg Q4Wks,ipilimumab, nivolumab,1
```

## Requirements
All dependencies are listed in ```requirements.txt```, but core packages include:

- ```pandas```

- ```rapidfuzz```

- ```tqdm```

- ```python-Levenshtein``` (optional but speeds things up if using ```fuzzywuzzy``` fallback)

## :inbox_tray: **Contact**
For questions or suggestions, feel free to reach out to [ericah@ds.dfci.harvard.edu].
