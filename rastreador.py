import requests
import hashlib
import pandas as pd
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = "standards_list.csv"
OUTPUT_FILE = "auditoria_beta_v1.csv"

def check_site(row):
    # Limpieza profunda de la URL
    url = str(row.get('URL', '')).strip()
    if not url or url.lower() == 'nan':
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        if res.status_code != 200:
            status = f"❌ Error {res.status_code}"
            new_hash = row.get('Hash')
        else:
            new_hash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
            old_hash = row.get('Hash')
            
            if pd.isna(old_hash) or old_hash == "" or str(old_hash).lower() == "none":
                status = "✔️ No changes"
            elif str(new_hash) != str(old_hash):
                status = "🚨 CHANGE DETECTED!"
            else:
                status = "✔️ No changes"

        return {
            "Organization": row.get('Organization', 'Unknown'),
            "Subject": row.get('Subject', 'General'),
            "Status": status,
            "Check Date": datetime.now().strftime("%Y-%m-%d"),
            "Mapped Version": row.get('Mapped_Version', 'N/A'),
            "Hash": new_hash,
            "URL": url
        }

    except Exception as e:
        # Capturamos el tipo de error para el reporte
        error_type = type(e).__name__
        return {
            "Organization": row.get('Organization', 'Unknown'),
            "Subject": row.get('Subject', 'General'),
            "Status": f"❌ {error_type}",
            "Check Date": datetime.now().strftime("%Y-%m-%d"),
            "Mapped Version": row.get('Mapped_Version', 'N/A'),
            "Hash": row.get('Hash'),
            "URL": url
        }

def run_parallel_audit():
    if not os.path.exists(INPUT_FILE):
        print("Input file missing")
        return

    # Cargamos y limpiamos el CSV de entrada
    df_list = pd.read_csv(INPUT_FILE)
    df_list.columns = df_list.columns.str.strip() # Borra espacios en nombres de columnas
    
    if os.path.exists(OUTPUT_FILE):
        df_prev = pd.read_csv(OUTPUT_FILE)
        df_prev.columns = df_prev.columns.str.strip()
        # Mantenemos los hashes previos
        df_to_check = pd.merge(df_list, df_prev[['Organization', 'Hash']], on='Organization', how='left')
    else:
        df_to_check = df_list

    # Ejecución en paralelo
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_site, df_to_check.to_dict('records')))
    
    # Filtramos resultados nulos y guardamos
    final_results = [r for r in results if r is not None]
    pd.DataFrame(final_results).to_csv(OUTPUT_FILE, index=False)
    print("Audit finished successfully.")

if __name__ == "__main__":
    run_parallel_audit()
