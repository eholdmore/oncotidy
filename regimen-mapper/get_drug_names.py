import pandas as pd
from rapidfuzz import fuzz, process
import re
from tqdm import tqdm 

# Load treatment data and drug thesaurus
treatment_path = "TREATMENT_PLAN.txt"
drug_list_path = "ncit_oncology_drugs_regimens.csv"

treatment_df = pd.read_csv(treatment_path, sep="|", dtype=str, encoding='ISO-8859-1')
drug_df = pd.read_csv(drug_list_path)

# Tokenization + cleaning
def normalize(text):
    text = re.sub(r'[^a-zA-Z0-9\s/+.()-]', '', str(text)).lower()
    tokens = re.split(r'[\s/+,.-]+', text)
    return " ".join(sorted(set(tokens)))

# Pre-tokenize synonym list
syn_to_pref = {}
normalized_synonyms = []

for _, row in drug_df.iterrows():
    preferred = row["Preferred_Term"].strip().lower()
    synonyms = [s.strip().lower() for s in str(row["Synonyms"]).split(";")]
    
    for syn in synonyms + [preferred]:
        norm_syn = normalize(syn)
        syn_to_pref[norm_syn] = preferred
        normalized_synonyms.append(norm_syn)

# Matching function
def match_drugs(text, threshold=85):
    norm_text = normalize(text)
    matches = process.extract(norm_text, normalized_synonyms, scorer=fuzz.token_sort_ratio, score_cutoff=threshold, limit=10)
    
    matched_pref_terms = {syn_to_pref[match[0]] for match in matches}
    return ", ".join(sorted(matched_pref_terms)) if matched_pref_terms else None

tqdm.pandas()
treatment_df["Standardized_Drugs"] = treatment_df["STD_CHEMO_PLAN"].progress_apply(match_drugs)

# Detect line changes
# Ensure sorting before detecting line changes
treatment_df["TPLAN_START_DT"] = pd.to_datetime(treatment_df["TPLAN_START_DT"], errors='coerce')
treatment_df = treatment_df.sort_values(by=["DFCI_MRN", "TPLAN_START_DT"])

# Assign line numbers by patient, incrementing when the drug regimen changes
def assign_line_numbers(group):
    line = 1
    last_drugs = None
    lines = []
    for drugs in group["Standardized_Drugs"]:
        if pd.isna(drugs) or drugs != last_drugs:
            line += 1 if last_drugs is not None else 0
            last_drugs = drugs
        lines.append(f"Line {line}")
    return lines

treatment_df["Line_Number"] = treatment_df.groupby("DFCI_MRN", group_keys=False).apply(assign_line_numbers)

# Step 5: Output final CSV
output_df = treatment_df[["DFCI_MRN", "TPLAN_START_DT", "STD_CHEMO_PLAN", "Standardized_Drugs", "Line_Number"]]
output_df.to_csv("standardized_treatments_with_lines.csv", index=False)
print("✅ Output saved to 'standardized_treatments_with_lines.csv'")


