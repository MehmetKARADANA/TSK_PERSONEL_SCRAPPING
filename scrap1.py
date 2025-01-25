import requests
from bs4 import BeautifulSoup

# URL of the announcements page
url = 'https://personeltemin.msb.gov.tr/Anasayfa/Duyurular'

# Send a GET request to fetch the page content
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the announcement containers (adjust this based on actual structure)
announcement_items = soup.find_all('div', class_='announcement-item')  # Modify if needed

# Extract the title, date, and URL of each announcement
announcements = []
for item in announcement_items:
    # Extract title
    link = item.find('a', class_='btn-icon')  # Adjust the class if needed
    title = link.get('title', 'No title') if link else 'No title'
    url = link.get('href') if link else 'No URL'

    # Extract date (Assuming date is within a span or div, modify the selector as needed)
    date_tag = item.find('span', class_='announcement-date')  # Modify this part based on the actual HTML
    date = date_tag.get_text(strip=True) if date_tag else 'No date'

    # Add to the announcements list
    announcements.append({'title': title, 'url': url, 'date': date})

# Print the announcements
for announcement in announcements:
    print(f"Title: {announcement['title']}")
    print(f"URL: {announcement['url']}")
    print(f"Date: {announcement['date']}")
    print('-' * 50)
