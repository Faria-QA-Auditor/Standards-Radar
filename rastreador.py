import requests
import hashlib
import pandas as pd
from datetime import datetime

# Official standards sites to monitor
SITES = {
    "New Jersey": "https://www.nj.gov/education/standards/",
    "Cambridge IGCSE": "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-upper-secondary/cambridge-igcse/subjects/",
    "AP": "https://apstudents.collegeboard.org/courses",
    "New York State": "https://www.nysed.gov/standards-instruction/nys-p-12-learning-standards-content-area",
    "California": "https://www.cde.ca.gov/be/st/ss/",
    "Connecticut": "https://portal.ct.gov/sde/ct-core-standards",
    "WIDA": "https://wida.wisc.edu/",
    "CCSS": "https://corestandards.org/",
    "ISTE": "https://iste.org/standards"
}

def run_audit():
    file_name = "auditoria_beta_v1.csv"
    
    # Try to load existing data for comparison
    try:
        df_old = pd.read_csv(file_name)
    except:
        df_old = pd.DataFrame()

    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    print("🚀 Starting audit...")

    for name, url in SITES.items():
        try:
            # Request site content
            res = requests.get(url, headers=headers, timeout=20)
            # Create a digital fingerprint (hash) of the content
            new_hash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
            
            # Logic to find the previous hash for this specific organization
            old_hash = None
            if not df_old.empty and name in df_old['Organization'].values:
                old_hash = df_old.loc[df_old['Organization'] == name, 'Hash'].values[0]
            
            # Compare hashes to detect changes
            if old_hash is None:
                status = "🆕 New URL / Initialized"
            elif new_hash != old_hash:
                status = "🚨 CHANGE DETECTED!"
            else:
                status = "✔️ No changes"
            
            results.append({
                "Organization": name, 
                "Status": status, 
                "Check Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "Hash": new_hash, 
                "URL": url
            })
            print(f"✅ {name}: {status}")

        except Exception as e:
            results.append({
                "Organization": name, 
                "Status": "❌ Connection Error", 
                "Check Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "Hash": None, 
                "URL": url
            })
            print(f"❌ {name}: Error occurred")

    # Save results to the CSV file
    df_final = pd.DataFrame(results)
    df_final.to_csv(file_name, index=False)
    print(f"\n📁 Audit complete. Results saved to {file_name}")

if __name__ == "__main__":
    run_audit()
