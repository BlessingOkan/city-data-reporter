
import os
import csv
import requests
import json

CSV_FILE = "city_data.csv"
CSV_HEADERS = ["City", "Country", "Temperature (C)", "Humidity (%)", "Description"]

def get_api_key():
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        raise RuntimeError("API key not found. Did you run export OWM_API_KEY='your-key'?")
    return api_key

def prompt_city():
    while True:
        city = input("Enter a city name (or type 'report' to view saved data): ").strip()
        if city:
            return city
        print("City name cannot be empty.")

def fetch_weather(city, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code == 404:
        raise RuntimeError(f"City '{city}' not found.")
    if resp.status_code == 401:
        raise RuntimeError("Invalid API key.")
    if not resp.ok:
        raise RuntimeError(f"API error: {resp.status_code}")

    return resp.json()

def parse_weather(data):
    return (
        data["name"],
        data["sys"]["country"],
        float(data["main"]["temp"]),
        int(data["main"]["humidity"]),
        data["weather"][0]["description"]
    )

def save_to_csv(row):
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def read_csv_report():
    if not os.path.exists(CSV_FILE):
        return "No CSV file yet."
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return "CSV file has no data yet."
    report = [f"Total cities: {len(rows)}"]
    for r in rows:
        report.append(f"- {r['City']} → {r['Temperature (C)']}°C")
    return "\n".join(report)

def main():
    api_key = get_api_key()
    city = prompt_city()

    if city.lower() == "report":
        print(read_csv_report())
        return

    try:
        data = fetch_weather(city, api_key)
        row = parse_weather(data)
    except Exception as e:
        print("Error:", e)
        return

    print(f"\n{row[0]}, {row[1]} — {row[2]:.1f}°C, {row[3]}% humidity, {row[4].capitalize()}")
    save_to_csv(row)
    print(f"Saved to {CSV_FILE}. Run again and type 'report' to view summary.")

if __name__ == "__main__":
    main()

