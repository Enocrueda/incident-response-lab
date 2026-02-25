#!/usr/bin/env python3
"""
Auto Scanner for DVWA - Incident Response Lab
Author: Enoc Rueda
Description: Automates Nmap and Gobuster scans for web app analysis
"""

import subprocess
import sys
import os
from datetime import datetime

# Configuración
TARGET = "localhost"
URL = f"http://{TARGET}"
WORDLIST = "/usr/share/wordlists/dirb/common.txt"
SCAN_DIR = "../scans"

def print_banner():
    """Muestra banner del programa"""
    print("""
    ╔══════════════════════════════════════════╗
    ║     AUTO SCANNER - SOC Toolkit v1.0     ║
    ║     Author: Enoc Rueda                   ║
    ╚══════════════════════════════════════════╝
    """)

def run_nmap():
    """Ejecuta Nmap scan"""
    print("\n[1/3] 🔍 Escaneando puertos con Nmap...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{SCAN_DIR}/nmap/nmap_scan_{timestamp}.txt"
    
    cmd = ["nmap", "-sV", "-p-", TARGET, "-oN", output_file]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"    ✅ Nmap scan completado: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Error en Nmap: {e}")
        return False

def run_gobuster():
    """Execute Gobuster scan"""
    print("\n[2/3] 📁 Buscando directorios con Gobuster...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{SCAN_DIR}/gobuster/gobuster_scan_{timestamp}.txt"
    
    cmd = ["gobuster", "dir", "-u", URL, "-w", WORDLIST, "-o", output_file]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"    ✅ Gobuster scan completado: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Error en Gobuster: {e}")
        return False

def generate_report():
    """Genera reporte resumen"""
    print("\n[3/3] 📊 Generando reporte...")
    
    report_file = f"{SCAN_DIR}/scan_report.txt"
    
    with open(report_file, 'w') as f:
        f.write("AUTO SCANNER REPORT\n")
        f.write("="*50 + "\n")
        f.write(f"Fecha: {datetime.now()}\n")
        f.write(f"Objetivo: {URL}\n\n")
        
        f.write("ARCHIVOS GENERADOS:\n")
        if os.path.exists(f"{SCAN_DIR}/nmap"):
            f.write(f"  - Nmap scans: {len(os.listdir(f'{SCAN_DIR}/nmap'))} archivos\n")
        if os.path.exists(f"{SCAN_DIR}/gobuster"):
            f.write(f"  - Gobuster scans: {len(os.listdir(f'{SCAN_DIR}/gobuster'))} archivos\n")
    
    print(f"    ✅ Reporte guardado: {report_file}")

def main():

    print_banner()
    
    # Make directories if it already doesn't exist
    os.makedirs(f"{SCAN_DIR}/nmap", exist_ok=True)
    os.makedirs(f"{SCAN_DIR}/gobuster", exist_ok=True)
    
    nmap_ok = run_nmap()
    gobuster_ok = run_gobuster()
    
    if nmap_ok or gobuster_ok:
        generate_report()
        print("\n✅ Escaneo completado. Revisa la carpeta 'scans/'")
    else:
        print("\n❌ No se pudo completar ningún escaneo")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Escaneo interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
