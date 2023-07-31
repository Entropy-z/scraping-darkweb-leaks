import requests
import socks
import socket
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

tor_proxy = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

url = 'http://santat7kpllt6iyvqbr7q4amdv6dzrh6paatvyrzl7ry3zm72zigf4ad.onion'

cookies = {
    'grav-site-40d1b2d': 'el93igseph7rnrtp09qutvcbh3',
    'dcap': '37C8B2EB8AD8FD9CF3D51608F28316E9FDDBB3C94712F96F0883FFB7B86E64F1894E51D993E0904B20A7910475C3CF19C4B4BAFF3D40FA4F930139624B70DC621A93F2D8DAB4345724A408B084BC4E9A'
}

excluded_words = ["ARCHIVE", "ARCHIVE2", "HOME", "HOW TO DOWNLOAD", "ARCHIVE3", "ARCHIVE4", "ARCHIVE5"]

output_data = []

try:
    session = requests.Session()
    session.proxies.update(tor_proxy)

    socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 9050)
    socket.socket = socks.socksocket

    response = session.get(url, cookies=cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        menu_items = soup.find_all('a', class_='g-menu-item-container')

        output_urls = []

        for item in menu_items:
            title = item.find('span', class_='g-menu-item-title')
            link = item.get('href')
            if title and link:
                title_text = title.text.strip()

                if not any(word in title_text for word in excluded_words):
                    full_url = urljoin(url, link)
                    output_urls.append(full_url)

    for output_url in output_urls:
        response = session.get(output_url, cookies=cookies)
        if response.status_code == 200:
            output_soup = BeautifulSoup(response.text, 'html.parser')
            first_paragraph = output_soup.select_one('.g-content > p:nth-child(1)')
            if first_paragraph:
                info_text = first_paragraph.text.strip()

                name_match = re.search(r'Headquarters:\s(.+)', info_text)
                website_match = re.search(r'Website:\s(.+)', info_text)
                revenue_match = re.search(r'Revenue:\s(.+)', info_text)
                industry_match = re.search(r'Industry:\s(.+)', info_text)

                if name_match and website_match and revenue_match and industry_match:
                    website_full = website_match.group(1)
                    website_domain = website_full.split('.')[1].capitalize()

                    revenue = revenue_match.group(1)
                    industry = industry_match.group(1)

                    output_data.append({
                        'Name Company': website_domain,
                        'Website': website_full,
                        'Revenue': revenue,
                        'Industry': industry
                    })
                else:
                    print(f"Informações adicionais desnecessárias em {output_url}. Dados omitidos.")

except requests.exceptions.RequestException as e:
    print("Erro na requisição:", e)

df = pd.DataFrame(output_data)

output_file = 'data.csv'
df.to_csv(output_file, index=False)

print(f"Data saved to {output_file}")
