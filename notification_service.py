import requests
import json
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

#Bu kodalr vps sunucularında çalışıyor ve logları txt dosyalarında tutuluyor.

# Konsol çıktısı için UTF-8 encoding ayarla
sys.stdout.reconfigure(encoding='utf-8')

# Firebase'i başlat
cred = credentials.Certificate('./tskpersonelteminapp-firebase-adminsdk-fbsvc-52be0ac8e1.json')
firebase_admin.initialize_app(cred)

# Firestore client'ı oluştur
db = firestore.client()
duyuru_collection = db.collection('duyurular')
temin_collection = db.collection('teminler')

# Session ayarları
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Gönderilen bildirimleri takip etmek için set
sent_notifications = set()

def send_notification(title, doc_id, notification_type="duyuru"):
    print("send_notification")
    notification_data = {
        "to": "",
        "title": f"Yeni {notification_type} yayınlandı!",
        "body": title,
        "doc_id": doc_id
    }

    try:
        print(f"Notification verisi: {notification_data}")
        response = session.post(
            'http://vmi2491623.contaboserver.net:8080/api/fcm/broadcast',
            json=notification_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"İstek durumu: {response.status_code}")
        if response.status_code == 200:
            print("Bildirim başarıyla gönderildi.")
        else:
            print(f"Bildirim gönderilemedi, hata kodu: {response.status_code}")
            print(f"Hata mesajı: {response.text}")
    except Exception as e:
        print(f"Bildirim gönderme sırasında hata: {str(e)}")

def on_duyuru_snapshot(doc_snapshot, changes, read_time):
    print("Duyuru Snapshot dinleniyor...")
    for change in changes:
        if change.type.name == 'ADDED':
            duyuru_data = change.document.to_dict()
            print(f"Yeni duyuru: {duyuru_data.get('title', 'Yeni Duyuru')}")
            
            # Timestamp kontrolü - sadece saniye kısmını karşılaştır
            created_at = duyuru_data.get('created_at').strftime('%Y-%m-%d %H:%M:%S')
            updated_at = duyuru_data.get('updated_at').strftime('%Y-%m-%d %H:%M:%S')
            print(f"Created: {created_at}, Updated: {updated_at}")
            
            # Microsaniye olmadan karşılaştır
            if created_at == updated_at:
                print("Yeni duyuru, bildirim gönderiliyor...")
                send_notification(duyuru_data.get('title', 'Yeni Duyuru'), change.document.id)
            else:
                print("Güncelleme, bildirim gönderilmiyor")

def on_temin_snapshot(doc_snapshot, changes, read_time):
    print("Temin Snapshot dinleniyor...")
    for change in changes:
        if change.type.name == 'ADDED':
            temin_data = change.document.to_dict()
            print(f"Yeni temin: {temin_data.get('title', 'Yeni Temin')}")
            
            # Timestamp kontrolü
            created_at = temin_data.get('created_at')
            updated_at = temin_data.get('updated_at')
            print(f"Created: {created_at}, Updated: {updated_at}")
            
            if created_at == updated_at:
                print("Yeni temin, bildirim gönderiliyor...")
                send_notification(temin_data.get('title', 'Yeni Temin'), change.document.id, "temin")
            else:
                print("Güncelleme, bildirim gönderilmiyor")

if __name__ == "__main__":
    # Duyuru ve temin koleksiyonlarını dinle
    duyuru_watch = duyuru_collection.on_snapshot(on_duyuru_snapshot)
    temin_watch = temin_collection.on_snapshot(on_temin_snapshot)
    
    try:
        print("Notification service başlatıldı.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        firebase_admin.delete_app(firebase_admin.get_app())
        print("Servis durduruldu.") 