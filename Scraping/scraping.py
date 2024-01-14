import requests
from bs4 import BeautifulSoup
import re

def scrape_weather_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # テーブルから気温と気圧のデータを取得
    data_rows = soup.find_all('tr', class_='mtx')
    
    temperature_data = []
    pressure_data = []

    for row in data_rows:
        columns = row.find_all('td')
        if len(columns) >= 11:
            date = columns[0].text.strip()
            temperature = columns[10].text.strip() + "℃"  
            pressure = columns[1].text.strip() + " hPa" 
            temperature_data.append((date, temperature))
            pressure_data.append((date, pressure))

    return temperature_data, pressure_data

# URLとデータを取得
url1 = 'https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=44&block_no=47662&year=2023&month=12&day=&view=a2'
url2 = 'https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=51&block_no=47636&year=2024&month=01&day=06&view=a1'

temperature_data1, pressure_data1 = scrape_weather_data(url1)
temperature_data2, pressure_data2 = scrape_weather_data(url2)

# データを出力する関数
def print_data(data, label):
    print(f"{label}:")
    for date, value in data:
        print(f"{date}: {value}")

# 出力
print_data(temperature_data1, "1つ目のURLの気温")
print_data(pressure_data1, "1つ目のURLの気圧")
print_data(temperature_data2, "2つ目のURLの気温")
print_data(pressure_data2, "2つ目のURLの気圧")


import sqlite3


# データベースを作成する関数
def create_database():
    conn = sqlite3.connect('weather_data.db')
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

    conn.commit()
    conn.close()

# データをデータベースに挿入する関数
def insert_data_into_database(data, table_name):
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()

    cursor.executemany(f'INSERT OR IGNORE INTO {table_name} VALUES (?, ?)', data)

    conn.commit()
    conn.close()

# データベースを作成
create_database()

# スクレイピングしたデータを挿入する（scrape_weather_data 関数は別途定義する必要があります）
# 1つ目のURLからデータを取得
url1 = 'https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=44&block_no=47662&year=2023&month=12&day=&view=a2'
temperature_data1, pressure_data1 = scrape_weather_data(url1)

# 2つ目のURLからデータを取得
url2 = 'https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=51&block_no=47636&year=2024&month=01&day=06&view=a1'
temperature_data2, pressure_data2 = scrape_weather_data(url2)

# データベースにデータを挿入
insert_data_into_database(temperature_data1, 'temperature')
insert_data_into_database(pressure_data1, 'pressure')
insert_data_into_database(temperature_data2, 'temperature')
insert_data_into_database(pressure_data2, 'pressure')


import sqlite3

def read_data_from_database(table_name):
    # SQLiteデータベースに接続
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()

    # データの取得
    cursor.execute(f'SELECT * FROM {table_name}')
    data = cursor.fetchall()

    # データベースをクローズ
    conn.close()

    return data

# データベースから気温データを取得して表示
temperature_data = read_data_from_database('temperature')
print("気温データ:")
for row in temperature_data:
    print(row)

# データベースから気圧データを取得して表示
pressure_data = read_data_from_database('pressure')
print("\n気圧データ:")
for row in pressure_data:
    print(row)
