import pandas as pd

# Path to your Thesaurus.txt file (from NCI EVS zip)
THESAURUS_PATH = "Thesaurus.txt"
OUTPUT_CSV = "ncit_oncology_drugs_regimens.csv"

# Define relevant semantic types and sources to include
RELEVANT_SEMANTIC_TYPES = {
    "Pharmacologic Substance",
    "Therapeutic or Preventive Procedure"
}

RELEVANT_SOURCES = {
    "HemOnc Regimen Terminology",
    "Multi-agent Therapeutic Regimens",
    "Pharmacotherapy Regimens"
}

# Load the file (no header, tab-delimited)
df = pd.read_csv(THESAURUS_PATH, sep="\t", header=None, dtype=str)
df.columns = [
    "Code", "URL", "Parent", "Preferred_Term", "Definition",
    "NCI_META", "Alt_Definition", "Semantic_Type", "Source"
]

# Filter by semantic type or source
df = df.fillna("")
df["Semantic_Set"] = df["Semantic_Type"].str.split("|")
df["Source_Set"] = df["Source"].str.split("|")

def is_relevant(row):
    return bool(set(row["Semantic_Set"]) & RELEVANT_SEMANTIC_TYPES) or \
           bool(set(row["Source_Set"]) & RELEVANT_SOURCES)

filtered_df = df[df.apply(is_relevant, axis=1)].copy()

# Synonyms will come from grouping by Code
# (there can be multiple rows per concept due to hierarchy or alt definitions)
synonym_map = {}
for code, group in filtered_df.groupby("Code"):
    synonyms = set()
    for pt in group["Preferred_Term"]:
        synonyms.update(pt.split("|"))
    synonym_map[code] = sorted(synonyms)

# Final deduplicated result
output_rows = []
for code, syn_list in synonym_map.items():
    preferred_term = syn_list[0]  # Use first synonym as preferred
    output_rows.append({
        "Code": code,
        "Preferred_Term": preferred_term,
        "Synonyms": "; ".join(syn_list)
    })

final_df = pd.DataFrame(output_rows)
final_df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Output written to {OUTPUT_CSV} with {len(final_df)} entries.")
