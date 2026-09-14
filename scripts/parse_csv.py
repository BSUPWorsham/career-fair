import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'employers.csv')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'employers.json')

def clean_val(val):
    if val is None:
        return ""
    cleaned = " ".join(str(val).strip().split())
    return cleaned

def parse_bool(val):
    cleaned = clean_val(val).lower()
    if cleaned in ["true", "yes", "1"]:
        return True
    if cleaned in ["false", "no", "0"]:
        return False
    return val  # Return cleaned string if value is missing or non-boolean

def process_handshake_csv():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find '{CSV_PATH}'. Place your CSV in the data/ directory.")
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
                "jobs_on_handshake": clean_val(row.get("Jobs on Handshake", "")),
                "job_titles": clean_val(row.get("Job Titles", "")),
                "majors": clean_val(row.get("Majors", "")),
                "major_groups": clean_val(row.get("Major Groups", "")),
                "combined_majors": clean_val(row.get("Combined Majors", "")),
                "job_types": clean_val(row.get("Job Types", "")),
                "school_years": clean_val(row.get("School Years", "")),
                "us_work_authorization_required": parse_bool(row.get("US work authorization required?", "")),
                "accepts_opt_cpt": parse_bool(row.get("Accepts OPT/CPT candidates?", "")),
                "willing_to_sponsor": parse_bool(row.get("Willing to sponsor candidate?", ""))
            }
            employers_list.append(employer_entry)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(employers_list, f, indent=2)

    print(f"Success! Processed {len(employers_list)} employers into {OUTPUT_PATH}")

if __name__ == '__main__':
    process_handshake_csv()