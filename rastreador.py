import requests
import hashlib
import pandas as pd
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = "standards_list.csv"
OUTPUT_FILE = "auditoria_beta_v1.csv"

def check_site(row):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # We fetch the site content
        res = requests.get(row['URL'], headers=headers, timeout=25)
        new_hash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
        
        # Determine status by comparing with previous hash (if exists)
        old_hash = row.get('Hash')
        if pd.isna(old_hash) or old_hash == "":
            status = "✔️ No changes"
        elif new_hash != old_hash:
            status = "🚨 CHANGE DETECTED!"
        else:
            status = "✔️ No changes"

        return {
            "Organization": row['Organization'],
            "Subject": row['Subject'],
            "Status": status,
            "Check Date": datetime.now().strftime("%Y-%m-%d"),
            "Mapped Version": row['Mapped_Version'],
            "Hash": new_hash,
            "URL": row['URL']
        }
    except Exception as e:
        return {
            "Organization": row['Organization'], "Subject": row['Subject'],
            "Status": "❌ Error", "Check Date": datetime.now().strftime("%Y-%m-%d"),
            "Mapped Version": row['Mapped_Version'], "Hash": None, "URL": row['URL']
        }

def run_parallel_audit():
    # If the audit output already exists, we use it to keep previous hashes
    if os.path.exists(OUTPUT_FILE):
        df_master = pd.read_csv(OUTPUT_FILE)
        df_list = pd.read_csv(INPUT_FILE)
        # Merge to keep hashes from previous runs
        df_to_check = pd.merge(df_list, df_master[['Organization', 'Hash']], on='Organization', how='left')
    else:
        df_to_check = pd.read_csv(INPUT_FILE)

    # High-speed processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_site, df_to_check.to_dict('records')))
    
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    run_parallel_audit()
