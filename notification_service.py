import requests
import json
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

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

def send_notification(title, doc_id, type="duyuru"):
    """Yeni duyuru veya temin için bildirim gönder"""
    if doc_id in sent_notifications:
        return
    
    notification_data = {
        "to": "",
        "title": f"Yeni {type.capitalize()}",
        "body": title
    }
    
    try:
        print("\n=== Bildirim Gönderiliyor ===")
        print(f"Veri: {notification_data}")
        
        # Session kullan ve IP adresi ile dene
        response = session.post(
            'http://localhost:8080/api/fcm/broadcast',  # Domain yerine IP kullan
            json=notification_data,  # json parametresi kullan
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        print(f"İstek durumu: {response.status_code}")
        print(f"Yanıt: {response.text}")
        
        if response.status_code == 200:
            print(f"Bildirim başarıyla gönderildi: {title}")
            sent_notifications.add(doc_id)
        else:
            print(f"Bildirim gönderilemedi. Hata kodu: {response.status_code}")
            
    except Exception as e:
        print(f"Bildirim gönderirken hata oluştu: {str(e)}")

def on_duyuru_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        # Sadece yeni eklenen duyurular için
        if change.type.name == 'ADDED':
            duyuru_data = change.document.to_dict()
            # Eğer bu yeni bir kayıt ise (created_at ile updated_at aynı ise)
            if duyuru_data.get('created_at') == duyuru_data.get('updated_at'):
                send_notification(duyuru_data.get('title', 'Yeni Duyuru'), change.document.id)

def on_temin_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            temin_data = change.document.to_dict()
            if temin_data.get('created_at') == temin_data.get('updated_at'):
                send_notification(temin_data.get('title', 'Yeni Temin'), change.document.id, "temin")

if __name__ == "__main__":
    # Başlangıçta mevcut duyuruları kaydet
    existing_duyurular = duyuru_collection.get()
    for doc in existing_duyurular:
        sent_notifications.add(doc.id)

    # Başlangıçta mevcut teminleri kaydet
    existing_teminler = temin_collection.get()
    for doc in existing_teminler:
        sent_notifications.add(doc.id)

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