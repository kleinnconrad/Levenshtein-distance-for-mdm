# Databricks notebook source
# MAGIC %pip install Levenshtein

import pandas as pd
import re
import Levenshtein

import os

# 1. Load data
# Try to resolve path relative to script directory (for local execution)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'test_addresses.csv')
    df_records = pd.read_csv(data_path)
except NameError:
    # If __file__ is not defined (e.g., inside a Databricks Notebook environment)
    # Databricks allows relative paths from the notebook's location.
    data_path = '../data/test_addresses.csv'
    df_records = pd.read_csv(data_path)

# Ensure zip_code is treated as string for blocking
df_records['zip_code'] = df_records['zip_code'].astype(str)

# 2. Define data cleaning functions
def clean_company_name(name):
    """
    Cleans and standardizes a company name.

    Removes common legal entity suffixes, punctuation, and converts to lowercase.

    Args:
        name (str): The original company name.

    Returns:
        str: The standardized company name.
    """
    if pd.isna(name):
        return ""
    name = str(name).lower()
    name = re.sub(r'gmbh|kg|ag|mbh|str\.', '', name)
    name = re.sub(r'[\.\s\*]', '', name)
    return name

def clean_street_name(street):
    """
    Cleans and standardizes a street name.

    Removes common street suffixes, numbers, punctuation, and converts to lowercase.

    Args:
        street (str): The original street name.

    Returns:
        str: The standardized street name.
    """
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
    """
    Calculates the Levenshtein similarity score for company and street names.

    Args:
        row (pd.Series): A row from the merged DataFrame containing _x and _y suffixes.

    Returns:
        pd.Series: A series containing the name and street similarity scores as percentages.
    """
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

print(f"Total duplicate pairs found: {len(final_output)}")
print("\nSample Duplicate Pairs:")
print(final_output.head(20))

# 9. Save to Databricks Delta Table
try:
    # The 'spark' session is automatically available in a Databricks notebook environment
    spark_df = spark.createDataFrame(final_output)
    spark_df.write.mode("overwrite").saveAsTable("workspace.default.address_duplicates")
    print("\nSuccessfully saved results to Delta table: workspace.default.address_duplicates")
except NameError:
    print("\nLocal execution detected ('spark' session not found). Results were not saved to a Delta table.")
