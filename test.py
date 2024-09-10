import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_general_table(soup, url):
    coaching_data = []

    # Find the table
    table = soup.find('table')
    if not table:
        print(f"No table found on page: {url}")
        return []

    # Find the headers
    header_row = table.find('thead').find_all('th') or table.find('thead').find_all('td')
    headers = [header.text.strip().lower() for header in header_row]
    print(f"Headers found: {headers} on page: {url}")

    # Create a mapping of column name to its index
    header_map = {
        'name': None,
        'title': None,
        'phone': None,
        'email address': None
    }

    for i, header in enumerate(headers):
        if 'name' in header:
            header_map['name'] = i
        elif 'title' in header:
            header_map['title'] = i
        elif 'phone' in header:
            header_map['phone'] = i
        elif 'email' in header:
            header_map['email address'] = i

    # Ensure we have found the necessary headers
    if None in header_map.values():
        print(f"Skipping table due to missing expected columns on page: {url}")
        return []

    # Extract data from rows in the <tbody>
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        # First check if the name is in <th>
        name_column = row.find('th')

        if name_column:
            # Case 1: Name in <th> and other data in <td>
            full_name = name_column.text.strip()
            title = row.find_all('td')[header_map['title'] - 1].text.strip() if len(row.find_all('td')) > header_map['title'] - 1 else "N/A"
            phone = row.find_all('td')[header_map['phone'] - 1].get_text(separator=' ').strip() if len(row.find_all('td')) > header_map['phone'] - 1 else "N/A"
            email_element = row.find_all('td')[header_map['email address'] - 1].find('a') if len(row.find_all('td')) > header_map['email address'] - 1 else None
            email = email_element['href'].replace('mailto:', '') if email_element else "N/A"
        else:
            # Case 2: All data including the name in <td>
            columns = row.find_all('td')
            if len(columns) > 0:
                title = columns[header_map['title']].text.strip() if header_map['title'] is not None and len(columns) > header_map['title'] else "N/A"
                full_name = columns[header_map['name']].text.strip() if header_map['name'] is not None and len(columns) > header_map['name'] else "N/A"
                phone = columns[header_map['phone']].get_text(separator=' ').strip() if header_map['phone'] is not None and len(columns) > header_map['phone'] else "N/A"
                email_element = columns[header_map['email address']].find('a') if header_map['email address'] is not None and len(columns) > header_map['email address'] else None
                email = email_element['href'].replace('mailto:', '') if email_element else "N/A"
            else:
                title = full_name = phone = email = "N/A"

        # Clean up phone number by removing duplicates
        phone = ' '.join(sorted(set(phone.split())))  # Split into parts, remove duplicates, and join again

        # Split name into first and last names
        name_parts = full_name.split()
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        coaching_data.append([title, first_name, last_name, phone, email])

    return coaching_data

def scrape_coaches_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return scrape_general_table(soup, url)
    else:
        print(f"Failed to load the page, status code: {response.status_code}")
        return []

urls = ['https://uabsports.com/sports/mens-soccer/coaches', 'https://nuhuskies.com/sports/mens-soccer/coaches', 'https://goterriers.com/sports/mens-soccer/coaches']
all_coaching_data = []

# Scrape each URL
for url in urls:
    coaching_data = scrape_coaches_page(url)
    if coaching_data:
        print(f"Data found on page: {url}")
    all_coaching_data.extend(coaching_data)

if all_coaching_data:
    df = pd.DataFrame(all_coaching_data, columns=["Title", "First Name", "Last Name", "Phone", "Email"])
    print(df)
else:
    print("No data was scraped.")

