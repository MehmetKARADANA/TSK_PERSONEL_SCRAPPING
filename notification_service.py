import requests
from bs4 import BeautifulSoup
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

# Firebase kimlik bilgilerini yükle
cred = credentials.Certificate('C:\\Users\\Mehmet\\Desktop\\codes\\Python\\web_Scrapping\\tskpersonelteminapp-firebase-adminsdk-fbsvc-52be0ac8e1.json')
firebase_admin.initialize_app(cred)

# Firestore bağlantısı
db = firestore.client()
duyuru_collection = db.collection('duyurular')
temin_collection = db.collection('teminer')

# Gönderilen bildirimleri takip etmek için set
sent_notifications = set()

def send_notification(title, doc_id, type="duyuru"):
    """Yeni duyuru veya temin için bildirim gönder"""
    # Eğer bu bildirim daha önce gönderildiyse, tekrar gönderme
    if doc_id in sent_notifications:
        return
    
    notification_data = {
        "to": "",  # FCM topic veya token
        "title": f"Yeni {type.capitalize()}",
        "body": title
    }
    
    try:
        response = requests.post(
            'http://localhost:8080/api/fcm/broadcast',
            json=notification_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"Bildirim başarıyla gönderildi: {title}")
            # Başarılı bildirimi kaydet
            sent_notifications.add(doc_id)
        else:
            print(f"Bildirim gönderilemedi. Hata kodu: {response.status_code}")
            
    except Exception as e:
        print(f"Bildirim gönderirken hata oluştu: {e}")

# Firestore'da yeni duyuru dinleyicisi
def on_duyuru_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        # Sadece yeni eklenen duyurular için
        if change.type.name == 'ADDED':
            duyuru_data = change.document.to_dict()
            # Eğer bu yeni bir kayıt ise (created_at ile updated_at aynı ise)
            if duyuru_data.get('created_at') == duyuru_data.get('updated_at'):
                send_notification(duyuru_data.get('title', 'Yeni Duyuru'), change.document.id)

# Başlangıçta mevcut duyuruları kaydet
existing_duyurular = duyuru_collection.get()
for doc in existing_duyurular:
    sent_notifications.add(doc.id)

# Firestore'da yeni temin dinleyicisi
def on_temin_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            temin_data = change.document.to_dict()
            if temin_data.get('created_at') == temin_data.get('updated_at'):
                send_notification(temin_data.get('title', 'Yeni Temin'), change.document.id, "temin")

# Başlangıçta mevcut teminleri kaydet
existing_teminer = temin_collection.get()
for doc in existing_teminer:
    sent_notifications.add(doc.id)

# Duyuru ve temin koleksiyonlarını dinle
duyuru_watch = duyuru_collection.on_snapshot(on_duyuru_snapshot)
temin_watch = temin_collection.on_snapshot(on_temin_snapshot)

def run_notification_service():
    try:
        print("Notification service başlatıldı. Yeni duyurular ve teminler bekleniyor...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Servis durduruldu.")

# Scriptin çalışır durumda kalması için
try:
    run_notification_service()
except KeyboardInterrupt:
    print("Servis durduruldu.") 