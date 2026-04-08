import requests
import hashlib
import pandas as pd
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = "standards_list.csv"
OUTPUT_FILE = "auditoria_beta_v1.csv"

def check_site(row):
    url = str(row['URL']).strip()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        # Increased timeout and added user-agent to mimic a real browser
        res = requests.get(url, headers=headers, timeout=25, allow_redirects=True)
        
        # If the status code is not 200, we report the specific error
        if res.status_code != 200:
            return {
                "Organization": row['Organization'], "Subject": row['Subject'],
                "Status": f"❌ Error {res.status_code}", "Check Date": datetime.now().strftime("%Y-%m-%d"),
                "Mapped Version": row['Mapped_Version'], "Hash": row.get('Hash'), "URL": url
            }

        new_hash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
        old_hash = row.get('Hash')

        if pd.isna(old_hash) or old_hash == "" or str(old_hash).lower() == "none":
            status = "✔️ No changes"
        elif str(new_hash) != str(old_hash):
            status = "🚨 CHANGE DETECTED!"
        else:
            status = "✔️ No changes"

        return {
            "Organization": row['Organization'], "Subject": row['Subject'],
            "Status": status, "Check Date": datetime.now().strftime("%Y-%m-%d"),
            "Mapped Version": row['Mapped_Version'], "Hash": new_hash, "URL": url
        }

    except requests.exceptions.Timeout:
        error_msg = "❌ Timeout"
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Connection Refused"
    except Exception as e:
        error_msg = "❌ Request Failed"

    return {
        "Organization": row['Organization'], "Subject": row['Subject'],
        "Status": error_msg, "Check Date": datetime.now().strftime("%Y-%m-%d"),
        "Mapped Version": row['Mapped_Version'], "Hash": row.get('Hash'), "URL": url
    }

def run_parallel_audit():
    if not os.path.exists(INPUT_FILE): return
    df_list = pd.read_csv(INPUT_FILE)
    
    if os.path.exists(OUTPUT_FILE):
        df_prev = pd.read_csv(OUTPUT_FILE)
        # Keep the latest known hashes to compare in the next run
        df_to_check = pd.merge(df_list, df_prev[['Organization', 'Hash']], on='Organization', how='left')
    else:
        df_to_check = df_list

    with ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(check_site, df_to_check.to_dict('records')))
    
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    run_parallel_audit()
