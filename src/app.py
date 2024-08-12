import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

def obtener_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el HTML: {e}")
        return None

def extraer_datos(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')  # Encuentra la primera tabla relevante
    rows = table.find_all('tr')[1:]  # Omitir el encabezado

    all_data = []
    for row in rows:
        cells = row.find_all('td')
        date = cells[0].get_text(strip=True)
        value = cells[1].get_text(strip=True)
        all_data.append([date, value])

    df = pd.DataFrame(all_data, columns=['Date', 'Value'])
    return df[:50]  # Filtra las primeras 50 filas

def procesar_datos(df):
    df['Value'] = df['Value'].replace('[\$,B,M]', '', regex=True).astype(float)
    df['Value'] = df.apply(lambda x: x['Value'] * 1000 if 'B' in x['Value'] else x['Value'], axis=1)
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')
    return df

def almacenar_en_sqlite(df, db_name="Tesla.db"):
    with sqlite3.connect(db_name) as conn:
        df.to_sql('Ingresos', conn, if_exists='replace', index=False)

def main():
    url = 'https://ycharts.com/companies/TSLA/revenues'
    html = obtener_html(url)

    if html:
        df = extraer_datos(html)
        df_procesado = procesar_datos(df)
        almacenar_en_sqlite(df_procesado)

        with sqlite3.connect("Tesla.db") as conn:
            cursor = conn.cursor()
            for row in cursor.execute("SELECT * FROM Ingresos"):
                print(row)

if __name__ == "__main__":
    main()
