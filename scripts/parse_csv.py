import csv
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'employers.csv')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'employers.json')

MAJOR_ABBREVIATIONS = {
    r'\bCivil Engineering\b': 'CE',
    r'\bMechanical Engineering\b': 'ME',
    r'\bComputer Science\b': 'CS',
    r'\bElectrical Engineering\b': 'EE',
    r'\bEngineering Plus\b': 'E+',
    r'\bEngineering \+\b': 'E+',
    r'\bConstruction Management\b': 'CM',
    r'\bCivil/Environmental Engineering\b': 'CE/Env',
    r'\bConstruction Engineering\b': 'ConstE',
    r'\bGeneral Engineering\b': 'GenE',
    r'\bComputer Engineering\b': 'CompE',
    r'\bMaterials Science & Engr\b': 'MSE',
    r'\bMaterials Science & Engineering\b': 'MSE',
    r'\bMaterials Sci & Engr\b': 'MSE'
}

def clean_val(val):
    if val is None:
        return ""
    return " ".join(str(val).strip().split())

def abbreviate_majors(text):
    if not text:
        return ""
    cleaned = clean_val(text)
    for pattern, abbr in MAJOR_ABBREVIATIONS.items():
        cleaned = re.sub(pattern, abbr, cleaned, flags=re.IGNORECASE)
    return cleaned

def parse_bool(val):
    cleaned = clean_val(val).lower()
    if cleaned in ["true", "yes", "1"]:
        return True
    if cleaned in ["false", "no", "0"]:
        return False
    return val

def process_handshake_csv():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find '{CSV_PATH}'.")
        return

    employers_list = []

    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = clean_val(row.get("Employer Name", ""))
            if not name:
                continue

            employer_entry = {
                "employer_name": name,
                "employer_industry": clean_val(row.get("Employer Industry", "")),
                "website": clean_val(row.get("Website", "")),
                "division": clean_val(row.get("Division", "")),
                "employment_types": clean_val(row.get("Employment Types", "")),
                "major_groups": abbreviate_majors(row.get("Major Groups", "")),
                "combined_majors": abbreviate_majors(row.get("Combined Majors", "")),
                "job_types": clean_val(row.get("Job Types", "")),
                "school_years": clean_val(row.get("School Years", "")),
                "us_work_authorization_required": parse_bool(row.get("US work authorization required?", "")),
                "accepts_opt_cpt": parse_bool(row.get("Accepts OPT/CPT candidates?", "")),
                "willing_to_sponsor": parse_bool(row.get("Willing to sponsor candidate?", ""))
            }
            employers_list.append(employer_entry)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(employers_list, f, indent=2)

    print(f"Success! Processed {len(employers_list)} employers.")

if __name__ == '__main__':
    process_handshake_csv()