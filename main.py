import subprocess
import sys
import time
from datetime import datetime
import logging

# Logging seviyesini ayarla
logging.basicConfig(level=logging.ERROR)

def run_services():
    try:
        # Her iki servisi de ayrı process'lerde başlat
        notification_process = subprocess.Popen([sys.executable, 'notification_service.py'])
        print("Notification service başlatıldı.")
        
        scraping_process = subprocess.Popen([sys.executable, 'scrapping.py'])
        print("Scraping service başlatıldı.")
        
        # Her iki process'i de bekle
        notification_process.wait()
        scraping_process.wait()
        
    except KeyboardInterrupt:
        print("\nProgramlar durduruluyor...")
        notification_process.terminate()
        scraping_process.terminate()
        print("Programlar durduruldu.")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    run_services() 