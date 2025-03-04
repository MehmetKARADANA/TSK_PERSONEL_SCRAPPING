import subprocess
import sys

def run_services():
    try:
        # Her iki servisi de ayrı process'lerde başlat
        notification = subprocess.Popen([sys.executable, 'notification_service.py'])
        scraping = subprocess.Popen([sys.executable, 'scraping_service.py'])
        
        # Process'leri bekle
        notification.wait()
        scraping.wait()
        
    except KeyboardInterrupt:
        print("\nProgramlar durduruluyor...")
        notification.terminate()
        scraping.terminate()
        print("Programlar durduruldu.")

if __name__ == "__main__":
    run_services() 