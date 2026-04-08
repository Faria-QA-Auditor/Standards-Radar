import requests
import hashlib
import pandas as pd
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

# Configuración de archivos
INPUT_FILE = "standards_list.csv"
OUTPUT_FILE = "auditoria_beta_v1.csv"

def check_site(row):
    """
    Función que revisa un solo sitio y devuelve el diagnóstico detallado.
    """
    url = str(row['URL']).strip()
    # User-Agent para intentar "engañar" a los firewalls de los estados (como Kansas)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    
    try:
        # Timeout de 30 segundos para dar tiempo a sitios lentos (Tennessee/Arkansas)
        res = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        # 1. Diagnóstico de Errores HTTP (403, 404, 500, etc.)
        if res.status_code != 200:
            return {
                "Organization": row['Organization'],
                "Subject": row['Subject'],
                "Status": f"❌ Error {res.status_code}",
                "Check Date": datetime.now().strftime("%Y-%m-%d"),
                "Mapped Version": row['Mapped_Version'],
                "Hash": row.get('Hash'), # Mantenemos el último hash conocido
                "URL": url
            }

        # 2. Si el sitio responde bien (200 OK), calculamos el Fingerprint
        new_hash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
        old_hash = row.get('Hash')

        # 3. Comparación para detectar cambios (🚨)
        if pd.isna(old_hash) or old_hash == "" or str(old_hash).lower() == "none":
            status = "✔️ No changes"
        elif str(new_hash) != str(old_hash):
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
            "URL": url
        }

    # 4. Diagnóstico de errores de red (Timeouts y Conexión)
    except requests.exceptions.Timeout:
        error_msg = "❌ Timeout (Slow Site)"
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Connection Refused"
    except Exception as e:
        error_msg = "❌ Request Failed"

    return {
        "Organization": row['Organization'],
        "Subject": row['Subject'],
        "Status": error_msg,
        "Check Date": datetime.now().strftime("%Y-%m-%d"),
        "Mapped Version": row['Mapped_Version'],
        "Hash": row.get('Hash'),
        "URL": url
    }

def run_parallel_audit():
    # Verificamos que exista la lista maestra
    if not os.path.exists(INPUT_FILE):
        print(f"CRITICAL ERROR: {INPUT_FILE} not found.")
        return

    df
