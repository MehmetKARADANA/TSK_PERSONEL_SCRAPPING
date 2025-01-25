import requests
from bs4 import BeautifulSoup
import json
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from pymongo import MongoClient
from datetime import datetime

# Konsol çıktısı için UTF-8 encoding ayarla
sys.stdout.reconfigure(encoding='utf-8')

# MongoDB Atlas bağlantısı
MONGO_URI = "mongodb+srv://mehmet34:mehmet175e@atlascluster.j3z8vqq.mongodb.net/?retryWrites=true&w=majority"

try:
    # Bağlantıyı test et
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("MongoDB'ye başarıyla bağlandı!")
    
    db = client['personeltemin']  # veritabanı adı
    temin_collection = db['teminler']  # teminler koleksiyonu
    duyuru_collection = db['duyurular']  # duyurular koleksiyonu
except Exception as e:
    print(f"MongoDB bağlantı hatası: {e}")
    exit(1)

# Hedef URL
url = "https://personeltemin.msb.gov.tr/"

# Retry stratejisi oluştur
retry_strategy = Retry(
    total=3,  # toplam deneme sayısı
    backoff_factor=1,  # her denemede beklenecek süre
    status_forcelist=[500, 502, 503, 504]  # hangi hatalarda tekrar denenecek
)

# Session oluştur ve retry stratejisini uygula
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# HTTP isteği gönder
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_detail_content(detail_url):
    try:
        # 3 saniye timeout ile istek at
        detail_response = session.get(detail_url, headers=headers, timeout=10)
        detail_response.encoding = 'utf-8'
        if detail_response.status_code == 200:
            detail_soup = BeautifulSoup(detail_response.text, "html.parser")
            content_text = None
            
            # Önce duyuru-container div'ini kontrol et
            content_div = detail_soup.find("div", class_="duyuru-container")
            if content_div:
                content_text = content_div.get_text(strip=True, separator='\n')
            else:
                # Container div'lerini bul
                containers = detail_soup.find_all("div", class_="container")
                for container in containers:
                    # İçinde metin olan div'leri bul
                    content_divs = container.find_all("div")
                    texts = []
                    for div in content_divs:
                        if div.find(string=lambda t: t and t.strip().startswith('1.')):
                            # İçeriği olan tüm div'leri topla
                            for content_div in div.parent.find_all("div"):
                                text = content_div.get_text(strip=True)
                                if text and not text.isspace():
                                    texts.append(text)
                            break
                    
                    if texts:
                        content_text = '\n'.join(texts)
                        break
            
            # HTML etiketlerini temizle ve düzgün format
            if content_text:
                content_text = content_text.replace('&nbsp;', ' ')
                content_text = content_text.replace('\n\n', '\n')
                content_text = content_text.replace('  ', ' ')
                return content_text
                
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

def check_duplicate(collection, title, url):
    """Veritabanında aynı başlık veya URL ile kayıt var mı kontrol et"""
    return collection.find_one({
        "$or": [
            {"title": title},
            {"detail_url": url}
        ]
    })

# Ana istek için de session kullan
try:
    response = session.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    # HTTP yanıtı kontrol et
    if response.status_code == 200:
        # Sayfanın HTML içeriğini al
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Teminler ve duyurular için ayrı listeler
        teminler = []
        duyurular = []
        
        # Teminleri al
        temin_div = soup.find("div", class_="tab-content active")
        if temin_div:
            temin_items = temin_div.find_all("div", class_="item cal")
            for item in temin_items:
                try:
                    title = item.find("h3").get_text(strip=True)
                    date = item.find("p", class_="date").get_text(strip=True)
                    detail_url = item.get("onclick").split("'")[1] if item.get("onclick") else None
                    full_detail_url = f"https://personeltemin.msb.gov.tr{detail_url}" if detail_url else None
                    
                    # Başlık veya URL ile kontrol et
                    existing_temin = check_duplicate(temin_collection, title, full_detail_url)
                    
                    if not existing_temin:
                        print(f"Yeni temin bulundu: {title}")
                        detail_content = get_detail_content(full_detail_url) if full_detail_url else None
                        temin_doc = {
                            "title": title,
                            "date": date,
                            "detail_url": full_detail_url,
                            "detail_content": detail_content,
                            "state": "active",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                        temin_collection.insert_one(temin_doc)
                        teminler.append(temin_doc)
                        print(f"Yeni temin eklendi: {title}")
                    else:
                        print(f"Bu temin zaten mevcut: {title}")
                        teminler.append(existing_temin)
                        
                except AttributeError:
                    continue
        
        # Duyuruları al
        duyuru_div = soup.find("div", class_="tab-content tab-cal-border-holder active")
        if duyuru_div:
            duyuru_items = duyuru_div.find_all("div", class_="item cal")
            for item in duyuru_items:
                try:
                    title = item.find("h3").get_text(strip=True)
                    date = item.find("div", class_="item--exp").find("p", class_="date").get_text(strip=True)
                    detail_url = item.get("onclick").split("'")[1] if item.get("onclick") else None
                    full_detail_url = f"https://personeltemin.msb.gov.tr{detail_url}" if detail_url else None
                    
                    # Başlık veya URL ile kontrol et
                    existing_duyuru = check_duplicate(duyuru_collection, title, full_detail_url)
                    
                    if not existing_duyuru:
                        print(f"Yeni duyuru bulundu: {title}")
                        detail_content = get_detail_content(full_detail_url) if full_detail_url else None
                        duyuru_doc = {
                            "title": title,
                            "date": date,
                            "detail_url": full_detail_url,
                            "detail_content": detail_content,
                            "state": "active",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                        duyuru_collection.insert_one(duyuru_doc)
                        duyurular.append(duyuru_doc)
                        print(f"Yeni duyuru eklendi: {title}")
                    else:
                        print(f"Bu duyuru zaten mevcut: {title}")
                        duyurular.append(existing_duyuru)
                        
                except AttributeError:
                    continue
        
        # Sonuçları yazdır
        if teminler or duyurular:
            print("\n=== MongoDB'ye Kaydedilen Veriler ===\n")
            
            if teminler:
                print(f"\nTeminler ({len(teminler)} adet):")
                for temin in teminler:
                    print(f"\nBaşlık: {temin['title']}")
                    print(f"Tarih: {temin['date']}")
                    print(f"Durum: {temin['state']}")
                    print(f"URL: {temin['detail_url']}")
                    print("-" * 50)
            
            if duyurular:
                print(f"\nDuyurular ({len(duyurular)} adet):")
                for duyuru in duyurular:
                    print(f"\nBaşlık: {duyuru['title']}")
                    print(f"Tarih: {duyuru['date']}")
                    print(f"Durum: {duyuru['state']}")
                    print(f"URL: {duyuru['detail_url']}")
                    print("-" * 50)
            
            # MongoDB'deki kayıt sayılarını kontrol et
            temin_count = temin_collection.count_documents({})
            duyuru_count = duyuru_collection.count_documents({})
            print(f"\nMongoDB'deki toplam kayıt sayıları:")
            print(f"Teminler: {temin_count}")
            print(f"Duyurular: {duyuru_count}")
        else:
            print("Hiç veri bulunamadı!")
    else:
        print(f"HTTP Hatası: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Bağlantı hatası: {e}")
