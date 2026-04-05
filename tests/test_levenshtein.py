# tests/test_levenshtein.py
import pandas as pd
from src.levenshtein import clean_company_name, clean_street_name

def test_clean_company_name():
    # Test standard suffix removal
    assert clean_company_name("TechCorp GmbH") == "techcorp"
    assert clean_company_name("Other Co KG") == "otherco"
    assert clean_company_name("Big Business AG") == "bigbusiness"
    
    # Test character removal (dots, spaces, asterisks)
    assert clean_company_name("A.B.C. mbH") == "abc"
    assert clean_company_name("My*Company") == "mycompany"
    
    # Test Null handling
    assert clean_company_name(pd.NA) == ""
    assert clean_company_name(None) == ""

def test_clean_street_name():
    # Test street suffix removal
    assert clean_street_name("Mainstrasse 12") == "main"
    assert clean_street_name("Hauptstraße") == "haupt"
    assert clean_street_name("Side weg 5") == "side"
    assert clean_street_name("Ringstr. 100") == "ring" # 'ring' AND 'str.' get removed
    
    # Test numeric removal
    assert clean_street_name("Avenue 12345") == "avenue"
    
    # Test Null handling
    assert clean_street_name(pd.NA) == ""
    assert clean_street_name(None) == ""
  
