# Databricks notebook source
"""
Generates synthetic address data for testing the Levenshtein string matching pipeline.
"""
import pandas as pd
import random
import uuid
import pathlib

# Set random seed for reproducibility
random.seed(42)

def generate_noise(text: str, noise_level: float = 0.1) -> str:
    """Introduces random typos (insertions, deletions, substitutions) to a string."""
    if not text:
        return text
    
    chars = list(text)
    num_errors = int(len(chars) * noise_level)
    
    for _ in range(num_errors):
        error_type = random.choice(['insert', 'delete', 'substitute'])
        idx = random.randint(0, len(chars) - 1)
        
        if error_type == 'insert':
            chars.insert(idx, random.choice('abcdefghijklmnopqrstuvwxyz'))
        elif error_type == 'delete' and len(chars) > 1:
            chars.pop(idx)
        elif error_type == 'substitute':
            chars[idx] = random.choice('abcdefghijklmnopqrstuvwxyz')
            
    return "".join(chars)

def generate_test_data(num_rows: int = 500) -> pd.DataFrame:
    """Generates synthetic address data."""
    systems = ['CRM', 'ERP', 'WEB', 'LEGACY']
    
    base_companies = [
        "TechCorp", "DataSystems", "GlobalTrade", "FutureVision", "AlphaAnalytics",
        "BetaBuilders", "GammaGroup", "DeltaDynamics", "EpsilonEngineering", "ZetaZone",
        "CloudInnovations", "SmartSolutions", "CyberNet", "PrimeLogistics", "ApexIndustries"
    ]
    company_suffixes = ["GmbH", "KG", "AG", "Inc", "LLC", "Ltd", "Corp"]
    
    base_streets = [
        "Main", "Broadway", "Market", "Oak", "Maple", "Pine", "Cedar", "Elm",
        "Washington", "Lake", "Hill", "Park", "River", "Forest", "Sunset"
    ]
    street_suffixes = ["strasse", "straße", "weg", "gasse", "ring", "str.", " avenue", " blvd"]
    
    data = []
    
    # We want a mix of clean records, slight duplicates, and distinct records
    target_unique_entities = num_rows // 2  # Each entity might have a duplicate
    
    for i in range(target_unique_entities):
        company_base = random.choice(base_companies) + str(random.randint(1, 100))
        suffix = random.choice(company_suffixes)
        company_name = f"{company_base} {suffix}"
        
        street_base = random.choice(base_streets)
        st_suffix = random.choice(street_suffixes)
        street_num = random.randint(1, 999)
        street_name = f"{street_base}{st_suffix} {street_num}"
        
        zip_code = str(random.randint(10000, 99999))
        
        # Original record
        data.append({
            'system_id': random.choice(systems),
            'record_id': str(uuid.uuid4())[:8],
            'company_name': company_name,
            'street_name': street_name,
            'zip_code': zip_code
        })
        
        # Duplicate record with noise (50% chance)
        if random.random() < 0.5:
            noisy_company = generate_noise(company_base) + " " + random.choice(company_suffixes)
            noisy_street = generate_noise(street_base) + random.choice(street_suffixes) + f" {street_num}"
            
            data.append({
                'system_id': random.choice(systems),
                'record_id': str(uuid.uuid4())[:8],
                'company_name': noisy_company,
                'street_name': noisy_street,
                'zip_code': zip_code  # keep zip_code same to test blocking
            })
            
    # Pad to exact num_rows if needed
    while len(data) < num_rows:
        data.append({
            'system_id': random.choice(systems),
            'record_id': str(uuid.uuid4())[:8],
            'company_name': "Extra Corp GmbH",
            'street_name': "Extra str. 123",
            'zip_code': str(random.randint(10000, 99999))
        })
        
    # Trim if we overshot slightly
    data = data[:num_rows]
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_test_data(500)
    
    # Determine output path
    try:
        script_dir = pathlib.Path(__file__).parent.resolve()
        project_root = script_dir.parent
        data_dir = project_root / "data"
    except NameError:
        # If __file__ is not defined (e.g., inside a Databricks Notebook environment)
        # Databricks allows relative paths from the notebook's location.
        data_dir = pathlib.Path('../data')
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = data_dir / "test_addresses.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} rows of test data at {output_path}")
