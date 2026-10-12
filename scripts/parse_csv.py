import csv
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# Look next to this script first, then one folder up, so it works either way.
SEARCH_DIRS = [SCRIPT_DIR, PARENT_DIR]

EMPLOYERS_NAMES = ['employers.csv', os.path.join('data', 'employers.csv')]
JOBS_NAMES = ['jobs.csv', 'Final_updated active jobs with majors fall 2026.csv',
              os.path.join('data', 'jobs.csv')]


def find_file(names):
    for d in SEARCH_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p) and os.path.getsize(p) > 0:
                return p
    return None


def find_output_dir():
    """Put employers.json next to index.html so the page can fetch it."""
    for d in SEARCH_DIRS:
        if os.path.exists(os.path.join(d, 'index.html')):
            return d
    return SCRIPT_DIR


EMPLOYERS_PATH = find_file(EMPLOYERS_NAMES)
JOBS_PATH = find_file(JOBS_NAMES)
OUTPUT_PATH = os.path.join(find_output_dir(), 'employers.json')

# Order matters: longer / more specific names must come before names they contain.
MAJOR_ABBREVIATIONS = [
    (r'\bElectrical\s*&\s*Computer Engineering\b', 'ECE'),
    (r'\bCivil/Environmental Engineering\b', 'CE/Env'),
    (r'\bMaterials Science\s*&\s*Engineering\b', 'MSE'),
    (r'\bMaterials Science\s*&\s*Engr\b', 'MSE'),
    (r'\bMaterials Sci\s*&\s*Engr\b', 'MSE'),
    (r'\bCivil Engineering\b', 'CE'),
    (r'\bMechanical Engineering\b', 'ME'),
    (r'\bComputer Science\b', 'CS'),
    (r'\bElectrical Engineering\b', 'EE'),
    (r'\bEngineering Plus\b', 'E+'),
    (r'\bEngineering\s*\+', 'E+'),
    (r'\bConstruction Management\b', 'CM'),
    (r'\bConstruction Engineering\b', 'ConstE'),
    (r'\bGeneral Engineering\b', 'GenE'),
    (r'\bComputer Engineering\b', 'CompE'),
    (r'\bBiomedical Engineering\b', 'Biomed'),
    (r'\bEnvironmental Engineering\b', 'Environ'),
    (r'\bGeotechnical Engineering\b', 'Geotech'),
    (r'\bStructural Engineering\b', 'Structural'),
]

# NOTE: the old "Advanced Engineering and Environmental Services (AE2S)": "AE2S"
# entry was removed. It set that company's majors to the text "AE2S". Add the real
# majors back here if you know them; otherwise the CSV's majors are used.
MAJORS_OVERRIDE_MAP = {
    "Ackerman-Estvold": "CE, CM",
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
    "WSP": "CE, EE, ME",
}

STOP_WORDS = {'inc', 'llc', 'corp', 'corporation', 'co', 'company', 'the', 'ltd'}


def clean_val(val):
    if val is None:
        return ""
    s = str(val).replace('\r', ' ').replace('\n', ' ').strip()
    return " ".join(s.split())


def norm(s):
    """Lowercase, drop punctuation and filler words so 'Harris, Inc.' == 'harris'."""
    s = re.sub(r'[^a-z0-9 ]', ' ', s.lower())
    return ' '.join(w for w in s.split() if w not in STOP_WORDS)


def open_csv(path):
    """Open as UTF-8; fall back to Windows-1252 for CSVs saved by older Excel."""
    try:
        f = open(path, mode='r', encoding='utf-8-sig', newline='')
        f.read()
        f.seek(0)
        return f
    except UnicodeDecodeError:
        return open(path, mode='r', encoding='cp1252', newline='')


def lookup(table, key, label):
    """Exact normalized match first. Otherwise allow a match only when one name
    starts with the other at a word boundary (e.g. 'harris' vs 'harris corporation').
    Fuzzy matches are printed so you can verify them."""
    if key in table:
        return table[key]
    for k, v in table.items():
        if key.startswith(k + ' ') or k.startswith(key + ' '):
            print(f"  [fuzzy {label}] '{key}' ~ '{k}'")
            return v
    return None


OVERRIDES = {norm(k): v for k, v in MAJORS_OVERRIDE_MAP.items()}


def abbreviate_majors(text):
    if not text:
        return ""
    cleaned = clean_val(text)
    for pattern, abbr in MAJOR_ABBREVIATIONS:
        cleaned = re.sub(pattern, abbr, cleaned, flags=re.IGNORECASE)
    return cleaned


def parse_bool(val):
    cleaned = clean_val(val).lower()
    if cleaned in ("true", "yes", "1"):
        return True
    if cleaned in ("false", "no", "0"):
        return False
    return clean_val(val)


def process_csvs():
    if not EMPLOYERS_PATH:
        print("Error: could not find employers.csv (looked next to this script and one folder up).")
        return

    # Job IDs keyed by normalized employer name
    company_job_ids = {}
    if JOBS_PATH:
        print(f"Reading jobs from: {JOBS_PATH}")
        with open_csv(JOBS_PATH) as f:
            for row in csv.DictReader(f):
                emp = norm(clean_val(row.get("Employer", "")))
                jid = clean_val(row.get("Job ID", ""))
                if emp and jid:
                    company_job_ids.setdefault(emp, set()).add(jid)
    else:
        print("Note: no jobs CSV found; job IDs will come from employers.csv if present.")

    print(f"Reading employers from: {EMPLOYERS_PATH}")
    employers_list = []
    missing_override = []

    with open_csv(EMPLOYERS_PATH) as f:
        reader = csv.reader(f)
        try:
            headers = [h.strip() for h in next(reader)]
        except StopIteration:
            print("Error: employers.csv is empty.")
            return

        header_map = {h.lower(): i for i, h in enumerate(headers)}

        def get_val(row, names):
            for name in names:
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
            if not name:
                name = clean_val(row[0])
            if not name:
                continue

            key = norm(name)

            matched = lookup(company_job_ids, key, "jobs")
            if matched:
                jobs_str = ", ".join(sorted(matched))
            else:
                jobs_str = clean_val(get_val(row, ["Jobs on Handshake", "Job IDs", "Listings"]))

            override = lookup(OVERRIDES, key, "majors")
            if override:
                hiring_majors = override
            else:
                missing_override.append(name)
                hiring_majors = abbreviate_majors(
                    get_val(row, ["Combined Majors", "Majors", "Major Groups", "Hiring Majors"]))

            employers_list.append({
                "employer_name": name,
                "employer_industry": clean_val(get_val(row, ["Employer Industry", "Industry"])),
                "website": clean_val(get_val(row, ["Website", "URL"])),
                "jobs_on_handshake": jobs_str,
                "employment_types": clean_val(get_val(row, ["Employment Types", "Employment Type"])),
                "hiring_majors": hiring_majors,
                "job_types": clean_val(get_val(row, ["Job Types", "Job Type"])),
                "school_years": clean_val(get_val(row, ["School Years", "School Year"])),
                "us_work_authorization_required": parse_bool(get_val(row, ["US work authorization required?", "US Work Auth Required"])),
                "accepts_opt_cpt": parse_bool(get_val(row, ["Accepts OPT/CPT candidates?", "Accepts OPT/CPT"])),
                "willing_to_sponsor": parse_bool(get_val(row, ["Willing to sponsor candidate?", "Willing To Sponsor"])),
            })

    employers_list.sort(key=lambda e: e["employer_name"].lower())

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(employers_list, f, ensure_ascii=False, indent=2)

    if missing_override:
        print(f"\n{len(missing_override)} employers had no majors override (used CSV majors):")
        for n in missing_override:
            print(f"  - {n}")

    print(f"\nSuccess! {len(employers_list)} employers -> {OUTPUT_PATH}")


if __name__ == '__main__':
    process_csvs()