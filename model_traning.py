import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Load data
data = pd.read_csv('weather_commodity_prices.csv')

features = ['temp', 'feelslike', 'humidity', 'precip', 'windspeed', 'windgust',
            'solarradiation', 'solarenergy', 'uvindex']

# Prepare features and target
features = data[features].values
target = data['Price'].values

# Normalize the data
scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)

# Prepare data for LSTM (reshape to 3D array)
X = []
y = []
time_steps = 10
for i in range(time_steps, len(features_scaled)):
    X.append(features_scaled[i-time_steps:i])
    y.append(target[i])
X, y = np.array(X), np.array(y)

# Split data into training and testing sets
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Build and train LSTM model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(LSTM(units=50))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=20, batch_size=32)

# Save the model
model.save('lstm_model_corn.h5')

# Make predictions and evaluate
y_pred = model.predict(X_test)
mse = np.mean((y_test - y_pred)**2)
print(f'Mean Squared Error: {mse}')
