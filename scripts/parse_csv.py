import csv
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

POSSIBLE_PATHS = [
    os.path.join(SCRIPT_DIR, '..', 'data', 'employers.csv'),
    os.path.join(SCRIPT_DIR, 'employers.csv'),
    os.path.join(SCRIPT_DIR, '..', 'employers.csv'),
    os.path.join(SCRIPT_DIR, 'data', 'employers.csv')
]

CSV_PATH = None
for path in POSSIBLE_PATHS:
    if os.path.exists(path) and os.path.getsize(path) > 0:
        CSV_PATH = path
        break

OUTPUT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'employers.json'))

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
    r'\bMaterials Sci & Engr\b': 'MSE',
    r'\bElectrical & Computer Engineering\b': 'ECE',
    r'\bBiomedical Engineering\b': 'Biomed',
    r'\bEnvironmental Engineering\b': 'Environ',
    r'\bGeotechnical Engineering\b': 'Geotech',
    r'\bStructural Engineering\b': 'Structural'
}

MAJORS_OVERRIDE_MAP = {
    "Ackerman-Estvold": "CE, CM",
    "Advanced Engineering and Environmental Services (AE2S)": "AE2S",
    "AKS Engineering & Forestry": "CE, CM, Engr, Environ, Forestry",
    "Allwest Testing & Engineering": "CE, Environ, Geotech",
    "Apex Companies / Forsgren": "CM, CE, Environ, Geo",
    "Applied Materials": "EE, ME, MSE, Physics, Chem",
    "Ardurra": "CE, CM, ME, Engr, EE, Environ",
    "Army Corps of Engineers - Hydropower Intern": "EE, ME",
    "ATS Inland NW": "ME, EE, CM, CSE",
    "Border States": "ME",
    "Brown and Caldwell": "CE, Environ, ME",
    "C3 Civil Engineering": "CE",
    "Chief Architect Software": "CS",
    "City of Boise": "CE",
    "Clark Pacific": "CE, Environ, ME",
    "Clenera": "ME, CM, EE",
    "CSHQA": "EE, ME",
    "Curtiss-Wright": "CS, CompE, EE, ME",
    "Cushing Terrell": "CE, EE, ME",
    "David Evans and Associates": "CE, CM, EE",
    "DC Engineering": "CE, CM, EE, ME, Structural",
    "DCI Engineers": "CE, Structural",
    "Electrical Consultants, Inc.": "CE, EE, ME",
    "EPC Services Company": "CE, EE, ME",
    "FOCUS Consulting": "CE",
    "Framatome Inc.": "EE, ME, MSE",
    "FTI - Engineering": "EE, ME, CM",
    "Gayle Manufacturing": "CM, CE, Engr",
    "GeoTek": "CE",
    "Gerding Builders": "CE, CM",
    "Granite Construction": "CM, CE",
    "Great West Engineering": "CE",
    "GSE Construction Company": "CM, CE, EE, ME",
    "Hamilton Construction": "CM, CE",
    "Harder Mechanical Contractors": "CM, ME",
    "Hargis Engineers": "ME, EE, Engr",
    "Harris": "EE, ME, CM",
    "HDR": "CE",
    "Hill & Peterson AFB Civilian Engineering": "CE, CS, Cyber, ECE, ME, MSE, Biomed, CM",
    "HMH Engineering": "CE",
    "Hoffman Construction": "CM",
    "Holland and Hart": "EE, patent law",
    "Horrocks": "CE",
    "Idaho National Laboratory": "All Engineering",
    "Idaho Power": "EE, ME, CE",
    "Idaho Transportation Department": "CE, CM",
    "Jacobs": "CE, EE, ME, MSE, Environ",
    "Janicki Industries": "ME, MSE, Engr",
    "Johnson Barrow": "ME",
    "J.F. Brennan Company": "CE, ME, Environ",
    "Keller Associates": "CE",
    "Kimley-Horn": "CE",
    "Kittelson & Associates": "CE",
    "KLA Corporation": "ECE, ME, MSE, CS, Physics, Chem",
    "KM Engineering": "CE",
    "KPFF Consulting Engineers": "CE",
    "Lumos & Associates": "CE",
    "Micron Technology": "CS, CSE, EE, MSE, ME, Physics",
    "Mission Critical Group": "ME, EE",
    "Mitsubishi Power Americas": "EE, ME, MSE",
    "Morrison-Maierle": "CE, ME",
    "Nasland Engineering": "CE",
    "Naval Nuclear Laboratory": "EE, ME, MSE",
    "NxEdge": "EE, ME, MSE",
    "NV5": "CE",
    "Perpetua Resources": "CE, Environ",
    "Plexus Corp.": "CompE, EE, ME",
    "Puget Sound Naval Shipyard": "CE, EE, ME",
    "Quality Electric": "CE, EE",
    "Quanta Infrastructure Solutions Group": "CM, CE",
    "RH2 Engineering": "CE, Environ",
    "RSCI": "CM, CE, ME",
    "RTM Engineering Consultants": "CE, EE, ME",
    "Schweitzer Engineering Laboratories (SEL)": "CS, CSE, EE",
    "Sletten Companies": "CM",
    "Southland Industries": "ME, CM",
    "SSOE Group": "CE, ME",
    "Stantec": "CE",
    "Tamarack Grove Engineering": "CE",
    "TD&H Engineering": "CE",
    "The Land Group": "CE",
    "Tokyo Electron (TEL)": "EE",
    "Trinity Consultants": "CE, Environ, ME",
    "U.S. Dept of State - Bureau of Diplomatic Security": "CS",
    "U.S. Navy - NUPOC": "EE, ME, MSE",
    "Ulteig": "CE, EE",
    "Vector Structural Engineering": "CE",
    "Visual Concepts": "CS, EE",
    "Washington State Dept of Transportation": "CM, CE",
    "Wright Brothers, The Building Company": "CM",
    "WSP": "CE, EE, ME"
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
    if not CSV_PATH:
        print("Error: Could not find 'employers.csv'.")
        return

    print(f"Reading from: {CSV_PATH}")
    employers_list = []

    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        try:
            headers = [h.strip() for h in next(reader)]
        except StopIteration:
            print(f"Error: '{CSV_PATH}' is empty.")
            return

        header_map = {h.lower(): i for i, h in enumerate(headers)}

        def get_val(row, target_names):
            for name in target_names:
                idx = header_map.get(name.lower())
                if idx is not None and idx < len(row):
                    val = row[idx].strip()
                    if val:
                        return val
            return ""

        for row in reader:
            if not row or not any(row):
                continue

            name = clean_val(get_val(row, ["Employer Name", "Employer", "Company Name", "Company", "Name"]))
            if not name and len(row) > 0:
                name = clean_val(row[0])

            if not name:
                continue

            # Look up major overrides first, otherwise search all major columns in order
            override = MAJORS_OVERRIDE_MAP.get(name)
            if not override:
                for k, v in MAJORS_OVERRIDE_MAP.items():
                    if k.lower() in name.lower() or name.lower() in k.lower():
                        override = v
                        break

            raw_majors = get_val(row, ["Combined Majors", "Majors", "Major Groups", "Hiring Majors"])
            hiring_majors = override if override else abbreviate_majors(raw_majors)

            employer_entry = {
                "employer_name": name,
                "employer_industry": clean_val(get_val(row, ["Employer Industry", "Industry"])),
                "website": clean_val(get_val(row, ["Website", "URL"])),
                "division": clean_val(get_val(row, ["Division"])),
                "employment_types": clean_val(get_val(row, ["Employment Types", "Employment Type"])),
                "hiring_majors": hiring_majors,
                "job_types": clean_val(get_val(row, ["Job Types", "Job Type"])),
                "school_years": clean_val(get_val(row, ["School Years", "School Year"])),
                "us_work_authorization_required": parse_bool(get_val(row, ["US work authorization required?", "US Work Auth Required"])),
                "accepts_opt_cpt": parse_bool(get_val(row, ["Accepts OPT/CPT candidates?", "Accepts OPT/CPT"])),
                "willing_to_sponsor": parse_bool(get_val(row, ["Willing to sponsor candidate?", "Willing To Sponsor"]))
            }
            employers_list.append(employer_entry)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(employers_list, f, indent=2)

    print(f"Success! Processed {len(employers_list)} employers -> saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    process_handshake_csv()