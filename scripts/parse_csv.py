import csv
import json
import os

# Set up paths relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'employers.csv')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'employers.json')

def clean_val(val):
    """Strips extra quotes, whitespace, and formatting anomalies."""
    if not val:
        return ""
    return " ".join(str(val).strip().split())

def process_handshake_csv():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find '{CSV_PATH}'. Place your CSV in the data/ directory.")
        return

    employer_map = {}

    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Check approval status
            status = clean_val(row.get("Registrations Status", "")).lower()
            if status and status != "approved":
                continue

            # Target exact column names from your CSV
            name = clean_val(row.get("Employers Name", ""))
            majors = clean_val(row.get("Major Names", ""))
            job_title = clean_val(row.get("Job Registrations Title", ""))

            if not name:
                continue

            # Fallback for empty majors
            if not majors:
                majors = "All Engineering Majors / Not Specified"

            # If employer was already added (multi-job row), aggregate job titles
            if name in employer_map:
                if job_title and job_title not in employer_map[name]["job_types"]:
                    if employer_map[name]["job_types"] == "General Hiring":
                        employer_map[name]["job_types"] = job_title
                    else:
                        employer_map[name]["job_types"] += f", {job_title}"
            else:
                employer_map[name] = {
                    "name": name,
                    "booth": "Assigned at Event",
                    "industry": "Engineering & Tech",
                    "majors": majors,
                    "job_types": job_title if job_title else "General Hiring",
                    "website": ""
                }

    employers_list = list(employer_map.values())

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(employers_list, f, indent=2)

    print(f"Success! Processed {len(employers_list)} unique approved employers into {OUTPUT_PATH}")

if __name__ == '__main__':
    process_handshake_csv()