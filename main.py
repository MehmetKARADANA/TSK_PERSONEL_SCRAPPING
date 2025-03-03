import subprocess
import sys
import time
from datetime import datetime
import logging
import os

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
        while True:
            # Process'lerin çalışır durumda olduğunu kontrol et
            if notification_process.poll() is not None:
                print("Notification service durdu, yeniden başlatılıyor...")
                notification_process = subprocess.Popen([sys.executable, 'notification_service.py'])
            
            if scraping_process.poll() is not None:
                print("Scraping service durdu, yeniden başlatılıyor...")
                scraping_process = subprocess.Popen([sys.executable, 'scrapping.py'])
            
            time.sleep(5)  # 5 saniye bekle
            
    except KeyboardInterrupt:
        print("\nProgramlar durduruluyor...")
        notification_process.terminate()
        scraping_process.terminate()
        print("Programlar durduruldu.")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    # Heroku'da worker'ı aktif tut
    try:
        run_services()
    except Exception as e:
        print(f"Ana program hatası: {e}")
        # Hata durumunda yeniden başlat
        time.sleep(10)
        os.execv(sys.executable, [sys.executable] + sys.argv) 