import os
import json
import requests
import pandas as pd

FAIR_ID = "66217"
API_URL = f"https://boisestate.joinhandshake.com/api/v1/career_fairs/{FAIR_ID}/employers.json"

# Grab cookie securely from the GitHub environment
COOKIE = os.getenv("HANDSHAKE_COOKIE", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cookie": COOKIE
}

def fetch_career_fair_data():
    session = requests.Session()
    session.headers.update(HEADERS)

    all_employers = []
    page = 1
    per_page = 50

    print(f"Fetching data from Handshake API for Fair #{FAIR_ID}...")

    while True:
        params = {"page": page, "per_page": per_page}
        response = session.get(API_URL, params=params)

        if response.status_code != 200:
            print(f"HTTP {response.status_code}: {response.text[:200]}")
            break

        data = response.json()
        employers = data.get("employers", data.get("data", []))
        if not employers:
            break

        for emp in employers:
            name = emp.get("name") or emp.get("employer", {}).get("name", "N/A")

            # Extract Majors
            majors_list = emp.get("accepted_majors", [])
            majors = ", ".join([m.get("name", str(m)) if isinstance(m, dict) else str(m) for m in majors_list])
            if not majors:
                majors = "All Majors / Not Specified"

            # Extract Job Types (Internship vs. Full-Time)
            job_types_list = emp.get("job_types", [])
            job_types = ", ".join([jt.get("name", str(jt)) if isinstance(jt, dict) else str(jt) for jt in job_types_list])
            if not job_types:
                job_types = "Not Specified"

            all_employers.append({
                "Employer": name,
                "Job Types Offered": job_types,
                "Accepted Majors": majors
            })

        print(f"Retrieved page {page} ({len(employers)} employers)")

        total_pages = data.get("total_pages", page)
        if page >= total_pages:
            break
        page += 1

    return all_employers

def create_interactive_html(records, filename="index.html"):
    json_data = json.dumps(records)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Boise State Career Fair Directory</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 25px; background: #f4f6f9; }}
            .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            h2 {{ color: #003366; margin-top: 0; }}
            table.dataTable {{ width: 100% !important; border-collapse: collapse; }}
            th {{ background: #003366; color: white; padding: 12px; font-weight: 600; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #eef2f5; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Boise State Career Fair Directory (Fair #66217)</h2>
            <p>Use the search box below to filter by <strong>Employer</strong>, <strong>Major</strong> (e.g., <em>Computer Science</em>), or <strong>Job Type</strong> (e.g., <em>Internship</em>).</p>
            <table id="employerTable" class="display" width="100%"></table>
        </div>

        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            const dataSet = {json_data};
            $(document).ready(function() {{
                $('#employerTable').DataTable({{
                    data: dataSet,
                    columns: [
                        {{ title: "Employer", data: "Employer" }},
                        {{ title: "Job Types Offered", data: "Job Types Offered" }},
                        {{ title: "Accepted Majors", data: "Accepted Majors" }}
                    ],
                    pageLength: 25,
                    responsive: true
                }});
            }});
        </script>
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    data = fetch_career_fair_data()
    if data:
        create_interactive_html(data)