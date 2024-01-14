import requests
from bs4 import BeautifulSoup
import sqlite3
import csv
import re
from datetime import datetime

# スクレイピング機能
def scrape_weather_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーをチェック
    except requests.RequestException as e:
        print(f"Error during requests to {url} : {e}")
        return [], []

    soup = BeautifulSoup(response.text, 'html.parser')
    data_rows = soup.find_all('tr', class_='mtx')
    
    temperature_data = []
    pressure_data = []

    for row in data_rows:
        columns = row.find_all('td')
        if len(columns) >= 11:
            # 日付フォーマットを YYYY-MM-DD 形式に変更する場合はここを修正
            # 例: date = datetime.strptime(columns[0].text.strip(), '%Y/%m/%d').strftime('%Y-%m-%d')
            date = columns[0].text.strip()
            temperature = columns[10].text.strip() + "℃"  
            pressure = columns[1].text.strip() + " hPa" 
            temperature_data.append((date, temperature))
            pressure_data.append((date, pressure))

    return temperature_data, pressure_data

# データベース関連の機能
def create_database():
    with sqlite3.connect('weather_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature (
                date TEXT PRIMARY KEY,
                temperature TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pressure (
                date TEXT PRIMARY KEY,
                pressure TEXT
            )
        ''')

def insert_data_into_database(data, table_name):
    with sqlite3.connect('weather_data.db') as conn:
        cursor = conn.cursor()
        cursor.executemany(f'INSERT OR IGNORE INTO {table_name} VALUES (?, ?)', data)

def read_data_from_database(table_name):
    with sqlite3.connect('weather_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        return cursor.fetchall()

# CSV出力機能
def save_data_to_csv(data, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Value'])  # CSVのヘッダー
            writer.writerows(data)
    except IOError as e:
        print(f"IOError while writing to {filename}: {e}")

# メインプログラム
def main():
    create_database()

    # 1つ目のURLからデータを取得
    url1 = 'https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=44&block_no=47662&year=2023&month=12&day=&view=a2'
    temperature_data1, pressure_data1 = scrape_weather_data(url1)
    insert_data_into_database(temperature_data1, 'temperature')
    insert_data_into_database(pressure_data1, 'pressure')

    # 2つ目のURLからデータを取得
    url2 = 'https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=51&block_no=47636&year=2024&month=01&day=06&view=a1'
    temperature_data2, pressure_data2 = scrape_weather_data(url2)
    insert_data_into_database(temperature_data2, 'temperature')
    insert_data_into_database(pressure_data2, 'pressure')

    # データベースからデータを取得してCSVファイルに保存
    temperature_data = read_data_from_database('temperature')
    pressure_data = read_data_from_database('pressure')
    save_data_to_csv(temperature_data, 'temperature_data.csv')
    save_data_to_csv(pressure_data, 'pressure_data.csv')

if __name__ == "__main__":
    main()
