# Telemetry Fetcher and Charging Dashboard (aka XPeng Mate)

A simple, containerized project that fetches telemetry data from the ABRP API, stores it in InfluxDB, and visualizes it with Grafana. 🚗🔋📊

---

## Why this project?

The reason for the project is to bypass some actual limitation offered by the XPeng application and the missing of the XPeng API in Europe (looking on Chinese search engine, it seems APIs exists in China).

The best way to recover all the data, and the "official" one proposed so far is to use [Enode](https://enode.com/) but to get access to production/real vehicle data you need to have the confirmation from the Enode sale.
It is a quite complicated process at this stage (I personnally still not have access to the APIs even after sever requests :() so I proposed a way to bypass this limitation using the ABRP "API", but for this you need to subscribe to the ABRP premium account.

---

## Architecture Overview

```mermaid
graph TD;
  API[ABRP API] -->|Fetch JSON| Fetcher[Telemetry Fetcher Python App]
  Fetcher -->|Write| InfluxDB
  InfluxDB -->|Visualize| Grafana
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Project Structure

```
/telemetry-project
|-- docker-compose.yml
|-- .env
|-- influxdb/
|   |-- config/
|-- grafana/
|   |-- provisioning/
|       |-- dashboards/
|           |-- *.json
|       |-- datasources/
|           |-- datasource.yml
|-- telemetry-fetcher/
|   |-- app/
|       |-- fetcher.py
|   |-- Dockerfile
|-- README.md
|-- images/
|   |-- logo/screenshots/...
```

---

## How to use it

### 1. Clone the repository

```bash
git clone https://github.com/mmornati/xpeng-mate.git
cd xpeng-mate
```

### 2. Configure the environment

Create a `.env` file based on the provided `sample.env`:

```dotenv
API_URL=https://api.iternio.com/1/session/get_tlm
API_KEY=your_api_key
SESSION_ID=your_seession_id
WAKEUP_VEHICLE_ID=your_vehicle_id

INFLUXDB_URL=http://influxdb:8086

INFLUXDB_USERNAME=myuser
INFLUXDB_PASSWORD=mypassword

INFLUXDB_TOKEN=my-token
INFLUXDB_BUCKET=my-bucket
INFLUXDB_ORG=my-org

GRAFANA_ADMIN_PASSWORD=admin

POLL_INTERVAL_SECONDS=120

# MQTT Settings
MQTT_BROKER=your-mqtt-broker
MQTT_PORT=1883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
MQTT_TOPIC_PREFIX=car/telemetry
```

#### 2.1 How to retrieve ABRP tokens
To get the `API_KEY`, `SESSION_ID` and the `WAKEUP_VEHICLE_ID` you can simply inspect a call made by your browser to the ABRP servers.
Just open on your browser the ABRP page and login, and look within the developer console the `get_tlm` call. In the Request preview (header and payload) you will have all the information to use to fill up the `.env` file.
 
![Developer Console](images/developer-console.png)

### 3. Start all containers

```bash
docker compose up --build
```

It will spin up:
- InfluxDB (to store telemetry)
- Grafana (to visualize)
- Python app (fetching telemetry at regular intervals)

### 4. Access the services

- **Grafana**: [http://localhost:3000](http://localhost:3000)  
  Login with the credentials set in your `.env` file.

- **InfluxDB**: [http://localhost:8086](http://localhost:8086)

---

## Dashboard Preview

![Charging Dashboard Preview Placeholder](images/dashboard-preview.png)

---

## Home Assistant
If you configure the MQTT Broker connection, some base information can then be retrieved in Home Assistant to build some specific boards and follow all the vehicle information.
Once the brower is configured, you need to configure some sensors in the `config.yaml` file based on what retrieved from the script topics.

```yaml
mqtt:
  sensor:
    - name: "Car SoC"
      state_topic: "car/telemetry/soc"
      unit_of_measurement: "%"
    - name: "Car Charging State"
      state_topic: "car/telemetry/is_charging"
    - name: "Car Latitude"
      state_topic: "car/telemetry/latitude"
    - name: "Car Longitude"
      state_topic: "car/telemetry/longitude"
    - name: "Vehicle Temperature"
      state_topic: "car/telemetry/vehicle_temp"
```

When everythin is ok, you will start receinving the information in HA and use it as you wish in script, boards, ...
![HA Developers data](images/home_assistant_sensors.png)


---

## Features

- Fetches telemetry data every X seconds.
- Automatically creates a dashboard to:
  - Display real-time GPS location.
  - Track charging sessions and locations.
  - Visualize state of charge (SoC) over time.
  - Analyze charging durations and energy metrics.
- Fully containerized and ready to deploy anywhere.

---

## Credits

- [A Better Route Planner (ABRP)](https://abetterrouteplanner.com/)
- [InfluxDB](https://www.influxdata.com/)
- [Grafana](https://grafana.com/)
- [Docker](https://www.docker.com/)

---

## License

Apache v2 License. See `LICENSE` for details.

---

> Made with ❤️ by EV Enthusiasts for EV Enthusiasts

