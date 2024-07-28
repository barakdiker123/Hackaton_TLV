from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# Load data and model
data = pd.read_csv('weather_commodity_prices.csv')
model = tf.keras.models.load_model('lstm_model_corn.h5')

models = {
    'corn': tf.keras.models.load_model('lstm_model_corn.h5'),
    'whitebeans': tf.keras.models.load_model('lstm_model_whitebeans.h5'),
    'cotton': tf.keras.models.load_model('lstm_model_cotton.h5'),
    'soybeans': tf.keras.models.load_model('lstm_model_soybeans.h5'),
}
# Normalize the data
features = ['temp', 'feelslike', 'humidity', 'precip', 'windspeed', 'windgust',
            'solarradiation', 'solarenergy', 'uvindex']
features1 = ['temp', 'feelslike', 'humidity', 'precip', 'windspeed', 'windgust',
            'solarradiation', 'solarenergy', 'uvindex', 'Price']
scaler = MinMaxScaler()
features = data[features].values
features_scaled = scaler.fit_transform(features)

last_price = list(data['Price'])[-1]

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/commodity/<commodity_name>')
def commodity_page(commodity_name):
    # if commodity_name not in models:
    #     return "Commodity model not found", 404

    fig_temp = px.line(data, x='datetime', y='temp', title='Temperature Over Time')
    fig_rain = px.line(data, x='datetime', y='precip', title='Rainfall Over Time')
    fig_humidity = px.line(data, x='datetime', y='humidity', title='Humidity Over Time')
    fig_price = px.line(data, x='datetime', y='Price', title=f'{commodity_name.capitalize()} Price Over Time')

    graph_temp = fig_temp.to_html(full_html=False)
    graph_rain = fig_rain.to_html(full_html=False)
    graph_humidity = fig_humidity.to_html(full_html=False)
    graph_price = fig_price.to_html(full_html=False)

    correlation_matrix = data[features1].corr().to_html()

    return render_template('commodity.html', commodity_name=commodity_name,
                           graph_temp=graph_temp, graph_rain=graph_rain,
                           graph_humidity=graph_humidity, graph_price=graph_price,
                           correlation_matrix=correlation_matrix)


@app.route('/commodity/<commodity_name>/predict', methods=['POST'])
def predict(commodity_name):
    if commodity_name not in models:
        return "Commodity model not found", 404
    # Extract all feature inputs from the form
    temp = float(request.form['temp'])
    feelslike = float(request.form['feelslike'])
    humidity = float(request.form['humidity'])
    precip = float(request.form['precip'])
    windspeed = float(request.form['windspeed'])
    windgust = float(request.form['windgust'])
    solarradiation = float(request.form['solarradiation'])
    solarenergy = float(request.form['solarenergy'])
    uvindex = float(request.form['uvindex'])

    # Prepare input data
    input_data = np.array(
        [[temp, feelslike, humidity, precip, windspeed, windgust, solarradiation, solarenergy, uvindex]])
    input_data_scaled = scaler.transform(input_data)
    input_data_scaled = np.reshape(input_data_scaled, (1, 1, 9))

    # Make prediction
    model = models[commodity_name]
    prediction = model.predict(input_data_scaled)[0][0] + last_price

    return f"Predicted Commodity Price: ${prediction:.2f}"


if __name__ == '__main__':
    app.run(debug=True)
