import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

# Sayfa URL'si
url = "https://personeltemin.msb.gov.tr"

# Web sayfasını kazıma fonksiyonu
def scrape_data():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Güncel teminler
    teminler = []
    temin_div = soup.find('div', {'class': 'col-md-6 home-tabs main-tab-left'})
    temin_items = temin_div.find_all('div', class_='item cal')
    for item in temin_items:
        title = item.find('h3').text.strip()
        description = item.find('p').text.strip()
        date = item.find('p', class_='date').text.strip()
        link = item.a['href'] if item.a else ''
        teminler.append({
            'title': title,
            'description': description,
            'date': date,
            'link': f"https://personeltemin.msb.gov.tr{link}"
        })

    # Güncel duyurular
    duyurular = []
    duyuru_div = soup.find('div', {'class': 'col-md-6 home-tabs main-tab-right'})
    duyuru_items = duyuru_div.find_all('div', class_='item cal')
    for item in duyuru_items:
        title = item.find('h3').text.strip()
        date = item.find('p', class_='date').text.strip()
        link = item.a['href'] if item.a else ''
        duyurular.append({
            'title': title,
            'date': date,
            'link': f"https://personeltemin.msb.gov.tr{link}"
        })

    return {'teminler': teminler, 'duyurular': duyurular}

# API route
@app.route('/api/data', methods=['GET'])
def get_data():
    data = scrape_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
