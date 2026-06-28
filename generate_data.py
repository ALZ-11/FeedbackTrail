import csv
import random
from datetime import datetime, timedelta

# Define Casablanca stations with respective traffic weights
STATIONS = {
    "Abdelmoumen": {"lat": 33.5731, "lon": -7.6184, "weight": 0.35},
    "Casa Voyageurs": {"lat": 33.5898, "lon": -7.5898, "weight": 0.30},
    "Technopark": {"lat": 33.5350, "lon": -7.6322, "weight": 0.175},
    "Nations Unies": {"lat": 33.5956, "lon": -7.6186, "weight": 0.10},
    "Gare Casa Port": {"lat": 33.5992, "lon": -7.6125, "weight": 0.075}
}

# Load categories
try:
    with open("categories.txt", "r", encoding="utf-8") as f:
        CATEGORIES = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    CATEGORIES = [
        "Ponctualité et régularité",
        "Informations voyageur",
        "Equipements",
        "Tarification",
        "Comportement du personnel",
        "Sécurité et sûreté",
        "Informations insuffisantes",
        "Spam",
        "Comportement indésirable"
    ]

LANGUAGES = ["French", "Arabic", "English"]
LANG_WEIGHTS = [0.60, 0.35, 0.05]

TRAMS = [f"Tram{i:02d}" for i in range(1, 46)]

def generate_random_timestamp(start_date, end_date):
    """
    Generates a timestamp between start and end dates.
    Simulates Casablanca tram operating hours (06:00 to 23:30) and
    commute rush hour spikes (morning and evening).
    """
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    
    rand_roll = random.random()
    if rand_roll < 0.35:
        # Morning commute spike (07:30 to 09:30 -> 450 to 570 mins from midnight)
        minutes = random.randint(450, 570)
    elif rand_roll < 0.70:
        # Evening commute spike (17:00 to 19:30 -> 1020 to 1170 mins from midnight)
        minutes = random.randint(1020, 1170)
    else:
        # Other active operating hours
        active_ranges = [
            (360, 450),    # 06:00 - 07:30
            (570, 1020),   # 09:30 - 17:00
            (1170, 1410)   # 19:30 - 23:30
        ]
        chosen_range = random.choice(active_ranges)
        minutes = random.randint(chosen_range[0], chosen_range[1])
        
    hour = minutes // 60
    minute = minutes % 60
    second = random.randint(0, 59)
    
    target_date = start_date + timedelta(days=random_days)
    return datetime(target_date.year, target_date.month, target_date.day, hour, minute, second)

def select_weighted_station():
    """Selects a station based on predetermined busy-ness weights."""
    stations_list = list(STATIONS.keys())
    weights = [STATIONS[s]["weight"] for s in stations_list]
    return random.choices(stations_list, weights=weights, k=1)[0]

def main():
    # Simulated historical range (e.g., first 4 months of 2026)
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 5, 1)
    num_rows = 2000

    rows = []
    for _ in range(num_rows):
        timestamp = generate_random_timestamp(start_date, end_date)
        lang = random.choices(LANGUAGES, weights=LANG_WEIGHTS, k=1)[0]
        station_name = select_weighted_station()
        lat = STATIONS[station_name]["lat"]
        lon = STATIONS[station_name]["lon"]
        tram_id = random.choice(TRAMS)
        
        category = random.choice(CATEGORIES)
        
        # Injecting intentional anomalies for dashboard analytical discovery:
        # Tram12 has high rates of delays (50% override probability)
        if tram_id == "Tram12" and random.random() < 0.50:
            category = "Ponctualité et régularité"
        
        # Tram05 in the spring month of April (month 4) has elevated equipment complaints (60% override)
        if tram_id == "Tram05" and timestamp.month == 4 and random.random() < 0.60:
            category = "Equipements"

        # Under the original (legacy) vision, keep a clean placeholder for quick UI clicks
        complaint_text = "Choix direct de la catégorie"
        
        rows.append([
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            lang,
            category,
            tram_id,
            station_name,
            lat,
            lon,
            complaint_text
        ])
        
    # Sort the generated records chronologically to represent a true event log
    rows.sort(key=lambda x: x[0])
    
    # Write to CSV
    fieldnames = ["Timestamp", "Language", "Category", "Tram_ID", "Station_Name", "Latitude", "Longitude", "Complaint_Text"]
    
    with open("reclamations_history.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(rows)
        
    print(f"Successfully generated {num_rows} clean, simulated records in 'reclamations_history.csv'.")

if __name__ == "__main__":
    main()