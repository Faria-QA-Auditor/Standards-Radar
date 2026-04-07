import requests
import hashlib
import pandas as pd
from datetime import datetime
import os

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
    
    # Si el archivo no existe, lo creamos vacío con columnas
    if not os.path.exists(file_name):
        df_old = pd.DataFrame(columns=['Organization', 'Status', 'Check Date', 'Hash', 'URL'])
    else:
        df_old = pd.read_csv(file_name)

    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for name, url in SITES.items():
        try:
            res = requests.get(url, headers=headers, timeout=20)
            new_hash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
            
            old_hash = None
            if not df_old.empty and name in df_old['Organization'].values:
                old_hash = df_old.loc[df_old['Organization'] == name, 'Hash'].values[0]
            
            status = "🚨 CHANGE DETECTED!" if old_hash and new_hash != old_hash else "✔️ No changes"
            
            results.append({
                "Organization": name, 
                "Status": status, 
                "Check Date": datetime.now().strftime("%Y-%m-%d"), 
                "Hash": new_hash, 
                "URL": url
            })
        except Exception as e:
            results.append({
                "Organization": name, "Status": "❌ Error", 
                "Check Date": datetime.now().strftime("%Y-%m-%d"), 
                "Hash": None, "URL": url
            })

    pd.DataFrame(results).to_csv(file_name, index=False)

if __name__ == "__main__":
    run_audit()
