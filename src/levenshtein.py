# Databricks notebook source

import pandas as pd
import re
import Levenshtein

# 1. Load your dummy data (using the exact fields defined here)
data = {
    'system_id': ['S1', 'S2', 'S3'],
    'record_id': ['R1', 'R2', 'R3'],
    'company_name': ['TechCorp GmbH', 'TechCorp', 'Other Co KG'],
    'street_name': ['Mainstrasse 12', 'Main str. 12', 'Side weg 5'],
    'zip_code': ['12345', '12345', '54321']
}
df_records = pd.DataFrame(data)

# 2. Define data cleaning functions
def clean_company_name(name):
    if pd.isna(name):
        return ""
    name = str(name).lower()
    name = re.sub(r'gmbh|kg|ag|mbh|str\.', '', name)
    name = re.sub(r'[\.\s\*]', '', name)
    return name

def clean_street_name(street):
    if pd.isna(street):
        return ""
    street = str(street).lower()
    street = re.sub(r'strasse|straße|weg|gasse|ring|str\.', '', street)
    street = re.sub(r'[\.\s0-9]', '', street)
    return street

# 3. Apply cleaning
df_records['clean_name'] = df_records['company_name'].apply(clean_company_name)
df_records['clean_street'] = df_records['street_name'].apply(clean_street_name)

# 4. Self-Join on zip_code
merged_df = pd.merge(df_records, df_records, on='zip_code', suffixes=('_x', '_y'))

# 5. Filter out self-matches
merged_df = merged_df[merged_df['record_id_x'] != merged_df['record_id_y']]

# 6. Calculate Edit Distance Similarity
def calculate_similarity(row):
    name_sim = Levenshtein.ratio(row['clean_name_x'], row['clean_name_y']) * 100
    street_sim = Levenshtein.ratio(row['clean_street_x'], row['clean_street_y']) * 100
    return pd.Series({'name_sim': name_sim, 'street_sim': street_sim})

sim_scores = merged_df.apply(calculate_similarity, axis=1)
merged_df = pd.concat([merged_df, sim_scores], axis=1)

# 7. Apply the 90% threshold filter
duplicates_df = merged_df[
    (merged_df['name_sim'] >= 90) & 
    (merged_df['street_sim'] >= 90)
]

# 8. Select the final fields using ONLY the _x and _y variations of your input columns
final_output = duplicates_df[[
    'system_id_x', 
    'record_id_x', 
    'record_id_y', 
    'system_id_y'
]].drop_duplicates()

print(final_output)
