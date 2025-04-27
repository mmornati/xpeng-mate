import requests
import time
from influxdb_client import InfluxDBClient, Point, WriteOptions
import os


API_URL = os.getenv("API_URL", "https://api.iternio.com/1/session/get_tlm")  # default fallback if needed
API_KEY = os.getenv("API_KEY")
SESSION_ID = os.getenv("SESSION_ID")
WAKEUP_VEHICLE_ID = int(os.getenv("WAKEUP_VEHICLE_ID"))

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 10))

if not all([API_KEY, SESSION_ID, WAKEUP_VEHICLE_ID, INFLUXDB_TOKEN]):
    raise ValueError("Missing required environment variables!")



# === HEADERS ===
HEADERS = {
    "accept": "*/*",
    "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": f"APIKEY {API_KEY}",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://abetterrouteplanner.com",
    "pragma": "no-cache",
    "referer": "https://abetterrouteplanner.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

# === Functions ===

def fetch_data():
    payload = {
        "session_id": SESSION_ID,
        "wakeup_vehicle_id": WAKEUP_VEHICLE_ID
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def write_to_influxdb(client, measurement_name, data):
    write_api = client.write_api(write_options=WriteOptions(batch_size=1))

    if data.get("status") != "ok":
        print("API response not OK, skipping...")
        return

    for vehicle_data in data.get("result", []):
        vehicle_id = vehicle_data.get("vehicle_id")
        car_model = vehicle_data.get("car_model")
        owner_name = vehicle_data.get("owner_name")
        tlm = vehicle_data.get("tlm", {})

        if not tlm:
            print(f"No telemetry for vehicle_id {vehicle_id}")
            continue

        point = Point(measurement_name)

        # === Add tags (indexed metadata) ===
        point.tag("vehicle_id", vehicle_id)
        point.tag("car_model", car_model)
        point.tag("owner_name", owner_name)

        # === Add telemetry fields ===
        fields_to_store = {
            "latitude": tlm.get("lat"),
            "longitude": tlm.get("lon"),
            "soc": tlm.get("soc"),
            "speed_is_gps": tlm.get("speed_is_gps"),
            "is_charging": tlm.get("is_charging"),
            "is_dcfc": tlm.get("is_dcfc"),
            "elevation": tlm.get("elevation"),
            "traffic_speed": tlm.get("traffic_speed"),
            "road_speed": tlm.get("road_speed"),
            "accel": tlm.get("accel"),
            "vehicle_temp": tlm.get("vehicle_temp"),
        }

        # Weather info (if available)
        location = tlm.get("location", {})
        weather = location.get("weather", {})
        fields_to_store.update({
            "weather_temp": weather.get("temp"),
            "weather_pressure": weather.get("pressure"),
            "weather_humidity": weather.get("humidity"),
            "weather_wind_speed": weather.get("wind_speed"),
            "weather_wind_dir": weather.get("wind_dir"),
        })

        for field_name, value in fields_to_store.items():
            if value is not None:
                point.field(field_name, value)

        # Use the telemetry timestamp (if available) for better time precision
        utc_timestamp = tlm.get("utc")
        if utc_timestamp:
            point.time(int(utc_timestamp) * 1_000_000_000)  # nanoseconds

        # Write to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def main():
    influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

    while True:
        try:
            data = fetch_data()
            print(f"Fetched data: {data}")
            write_to_influxdb(influx_client, "telemetry", data)
        except Exception as e:
            print(f"Error occurred: {e}")
        
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()