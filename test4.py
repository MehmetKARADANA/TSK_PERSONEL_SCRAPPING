import requests
from bs4 import BeautifulSoup
import json
import sys

# Konsol çıktısı için UTF-8 encoding ayarla
sys.stdout.reconfigure(encoding='utf-8')

# Hedef URL
url = "https://personeltemin.msb.gov.tr/"

# HTTP isteği gönder
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_detail_content(detail_url):
    try:
        detail_response = requests.get(detail_url, headers=headers)
        # Response encoding'ini UTF-8 olarak ayarla
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
                        if div.find(text=lambda t: t and t.strip().startswith('1.')):
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

# Ana response için de encoding ayarla
response = requests.get(url, headers=headers)
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
                
                # Detay sayfasının içeriğini al
                detail_content = get_detail_content(full_detail_url) if full_detail_url else None
                
                teminler.append({
                    "title": title,
                    "date": date,
                    "detail_url": full_detail_url,
                    "detail_content": detail_content
                })
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
                
                # Detay sayfasının içeriğini al
                detail_content = get_detail_content(full_detail_url) if full_detail_url else None
                
                duyurular.append({
                    "title": title,
                    "date": date,
                    "detail_url": full_detail_url,
                    "detail_content": detail_content
                })
            except AttributeError:
                continue
    
    # Sonuçları yazdır
    result = {
        "teminler": teminler,
        "duyurular": duyurular
    }
    
    # JSON çıktısını UTF-8 ile yazdır
    print(json.dumps(result, indent=4, ensure_ascii=False, encoding='utf-8'))
else:
    print(f"HTTP Hatası: {response.status_code}")
