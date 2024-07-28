import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration
WEATHER_API_KEY = 'bf8e819fd16676342cd47cd316734720'
ALPHA_VANTAGE_API_KEY = 'MGE99MOW7092UZEF' #'your_alpha_vantage_api_key'
CITY = 'Des Moines'
COMMODITY = 'BEANS'
DAYS = 90  # Adjusted to collect data for the last 90 days


# def get_coordinates(api_key, city):
#     url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={api_key}"
#     response = requests.get(url)
#     data = response.json()
#     if data:
#         return data[0]['lat'], data[0]['lon']
#     else:
#         raise Exception("City not found")
#
#
# def get_historical_weather(api_key, lat, lon, date):
#     timestamp = int(datetime.strptime(date, '%Y-%m-%d').timestamp())
#     url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine"
#     params = {
#         'lat': lat,
#         'lon': lon,
#         'dt': timestamp,
#         'appid': api_key,
#         'units': 'metric'
#     }
#     response = requests.get(url, params=params)
#     data = response.json()
#     if 'current' in data:
#         return {
#             'Date': date,
#             'Temperature': data['current']['temp'],
#             'Rainfall': data['current'].get('rain', {}).get('1h', 0)
#         }
#     else:
#         raise Exception(f"Error fetching data for {date}: {data}")
#
#
# def fetch_weather_for_date_range(api_key, city, days):
#     #lat, lon = get_coordinates(api_key, city)
#     lat = '41.5868'
#     lon = '-93.6250'
#     current_date = datetime.now() - timedelta(days=days) #datetime.strptime(datetime.now() - timedelta(days=days), '%Y-%m-%d')
#     end_date = datetime.now() #datetime.strptime(datetime.now(), '%Y-%m-%d')
#     weather_data = []
#
#     while current_date <= end_date:
#         date_str = current_date.strftime('%Y-%m-%d')
#         weather = get_historical_weather(api_key, lat, lon, date_str)
#         weather_data.append(weather)
#         current_date += timedelta(days=1)
#
#     return pd.DataFrame(weather_data)
# def fetch_weather_data(api_key, city, days):
#     latitude, longitude = get_coordinates(api_key, city)
#     weather_data = []
#     for day in range(days):
#         date = datetime.now() - timedelta(days=day)
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             weather_data.append({
#                 'Date': date.strftime('%Y-%m-%d'),
#                 'Temperature': data['main']['temp'],
#                 'Rainfall': data['rain'].get('1h', 0) if 'rain' in data else 0
#             })
#             time.sleep(1)  # Respect the rate limit
#     return pd.DataFrame(weather_data)


# Configuration
API_KEY = 'L2E7JU3H4842BTPYGHRV7VEDT'
#CITY = 'Des Moines, IA'


def fetch_historical_weather(api_key, city, days):
    # start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    # end_date = datetime.now().strftime('%Y-%m-%d')
    # url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{start_date}/{end_date}"
    # params = {
    #     'unitGroup': 'metric',
    #     'include': 'days',
    #     'key': api_key,
    #     'contentType': 'json'
    # }
    # response = requests.get(url, params=params)
    response = requests.get('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Des%2520Moines/2024-03-01/2024-07-26?elements=datetime%2CdatetimeEpoch%2Ctemp%2Ctempmax%2Ctempmin%2Cprecip%2Cwindspeed%2Cwindgust%2Cfeelslike%2Cfeelslikemax%2Cfeelslikemin%2Cpressure%2Cstations%2Cdegreedays%2Caccdegreedays&include=fcst%2Cobs%2Chistfcst%2Cstats&key=L2E7JU3H4842BTPYGHRV7VEDT&contentType=json')
    data = response.json()
    weather_data = []

    for day in data['days']:
        weather_data.append({
            'Date': day['datetime'],
            'Temperature': day['temp'],
            'Rainfall': day.get('precip', 0)
        })

    return pd.DataFrame(weather_data)

def fetch_commodity_price(api_key, commodity, days):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={commodity}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prices = []
        print(data)
        for date in sorted(data['Time Series (Daily)'].keys())[:days]:
            price = data['Time Series (Daily)'][date]['4. close']
            prices.append({
                'Date': date,
                'Price': float(price)
            })
        return pd.DataFrame(prices)
    else:
        raise Exception(f"Error fetching commodity prices: {response.status_code}")

# Collect data
# weather_df = fetch_historical_weather(API_KEY, CITY, DAYS)
# weather_df.to_csv(f'weather_{CITY}.csv')
commodity_df = fetch_commodity_price(ALPHA_VANTAGE_API_KEY, COMMODITY, DAYS)
commodity_df.to_csv(f'commedity_{COMMODITY}.csv')
#commodity_df = pd.read_csv(f'commedity_{COMMODITY}.csv')
weather_df = pd.read_csv('Saginaw.csv')
relevant_features = ['datetime', 'temp', 'feelslike', 'humidity', 'precip',
                     'windspeed', 'windgust', 'solarradiation', 'solarenergy',
                     'uvindex']

weather_df = weather_df[relevant_features]

commodity_df['Date'] = pd.to_datetime(commodity_df['Date'])
weather_df['Date'] = pd.to_datetime(weather_df['datetime'])

# Merge and save data
merged_df = pd.merge(weather_df, commodity_df, on='Date').drop('datetime', axis=1)
merged_df.to_csv('weather_commodity_prices_BEANS.csv', index=False)
print("Data collection completed and saved to 'weather_commodity_prices.csv'")
