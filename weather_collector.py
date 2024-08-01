import os
import requests
import psycopg2
from datetime import datetime
import time  # Import time module for sleep functionality

# Load database configuration from environment variables
db_config = {
    "host": "mypostgres",  # Use the container name as the host
    "port": 5432,
    "database": "mydatabase",
    "user": "myuser",
    "password": "password"
}

# Fetch and store weather data
def fetch_and_store_weather_data():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }

    response = requests.get(url, params=params)
    weather_data = response.json()

    # Connect to PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            time TIMESTAMP NOT NULL,
            temperature_2m FLOAT,
            relative_humidity_2m FLOAT,
            wind_speed_10m FLOAT
        );
    """)

    # Insert weather data into the table
    for i in range(len(weather_data['hourly']['time'])):
        time_stamp = datetime.fromisoformat(weather_data['hourly']['time'][i])
        temperature = weather_data['hourly']['temperature_2m'][i]
        humidity = weather_data['hourly']['relative_humidity_2m'][i]
        wind_speed = weather_data['hourly']['wind_speed_10m'][i]

        cursor.execute("""
            INSERT INTO weather_data (latitude, longitude, time, temperature_2m, relative_humidity_2m, wind_speed_10m)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (params['latitude'], params['longitude'], time_stamp, temperature, humidity, wind_speed))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    while True:  # Loop to run the script every 30 minutes
        fetch_and_store_weather_data()
        print("Weather data fetched and stored successfully.")
        time.sleep(1800)  # Sleep for 1800 seconds (30 minutes)

