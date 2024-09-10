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
    header_row = table.find('thead').find_all('th')
    headers = [header.text.strip().lower() for header in header_row]
    print(f"Headers found: {headers} on page: {url}")

    # Assign column indices based on the header
    try:
        name_index = headers.index('name') if 'name' in headers else None
        title_index = headers.index('title') if 'title' in headers else None
        phone_index = headers.index('phone') if 'phone' in headers else None
        email_index = headers.index('email address') if 'email address' in headers else None
    except ValueError:
        print(f"Skipping table due to missing expected columns on page: {url}")
        return []

    # Extract data from rows in the <tbody>
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        # Check if the name is stored in a <th> or <td> element
        name_column = row.find('th')

        if name_column:
            # Name in <th>
            full_name = name_column.text.strip()
            title = row.find_all('td')[0].text.strip() if len(row.find_all('td')) > 0 else "N/A"
            phone = row.find_all('td')[1].text.strip() if len(row.find_all('td')) > 1 else "N/A"
            email_element = row.find_all('td')[2].find('a') if len(row.find_all('td')) > 2 else None
            email = email_element['href'].replace('mailto:', '') if email_element else "N/A"
        else:
            # Everything in <td>
            columns = row.find_all('td')
            title = columns[0].text.strip() if len(columns) > 0 else "N/A"
            full_name = columns[1].text.strip() if len(columns) > 1 else "N/A"
            phone = columns[2].text.strip() if len(columns) > 2 else "N/A"
            email_element = columns[3].find('a') if len(columns) > 3 else None
            email = email_element['href'].replace('mailto:', '') if email_element else "N/A"

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

urls = ['https://uabsports.com/sports/mens-soccer/coaches', 'https://nuhuskies.com/sports/mens-soccer/coaches']
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
