import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'employers.csv')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'employers.json')

def clean_val(val):
    if not val:
        return ""
    return " ".join(str(val).strip().split())

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

            industry = clean_val(row.get("Industry", "")) or "Engineering & Tech"
            website = clean_val(row.get("Website", ""))
            job_types = clean_val(row.get("Job Types", "")) or clean_val(row.get("Employment Types", "")) or "General Hiring"

            majors = clean_val(row.get("Major Groups", "")) or clean_val(row.get("Majors", "")) or clean_val(row.get("Combined Majors", ""))
            if not majors:
                majors = "All Engineering Majors / Not Specified"

            raw_interviews = clean_val(row.get("Interviews ", "")).lower()
            on_campus_interviews = "Yes" if raw_interviews == "yes" else "No"

            employer_entry = {
                "name": name,
                "booth": "TBD",
                "industry": industry,
                "job_types": job_types,
                "majors": majors,
                "website": website,
                "on_campus_interviews": on_campus_interviews
            }
            employers_list.append(employer_entry)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(employers_list, f, indent=2)

    print(f"Success! Processed {len(employers_list)} employers into {OUTPUT_PATH}")

if __name__ == '__main__':
    process_handshake_csv()