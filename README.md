# FeedbackTrail

FeedbackTrail is a legacy automated, client-to-cloud citizen feedback management prototype designed for smart city public transit systems. The system provides an automated pipeline from public terminal data entry to real-time administrative analytics using Casablanca's tramway network (*Casatramways*) as an operational baseline

## System Architecture

The application is structured into three decoupled pillars connected by a centralized cloud database:

```text
[Tkinter Panel Kiosk] ──(Logs real-time transit data)──► [Google Drive CSV]
                                                               │
[Analytical Dashboard] ◄──(Pulls & aggregates live data)───────┘
```

1. **Interactive Client Kiosk (`main.py`):**
   * Simulates stationary terminals deployed at tram stops.
   * Multi-language interface supporting **French, Arabic, and English** configurations.
   * **Voice Dictation:** Integrates Speech-to-Text recording and Google Speech Recognition to ensure accessibility for non-literate citizens.
   * **AI Classification:** Passes natural language input (text or transcribed voice) to the OpenAI API to categorize complaints into standardized categories in real-time.

2. **Cloud Database Pipeline (`Google Drive API`):**
   * Acts as a serverless, shared relational datastore.
   * Leverages a secure Google Service Account to download, append, and update a centralized CSV log in-memory.

3. **Operational Analytics Dashboard (`app.py`):**
   * A single-page, real-time web application built using **Dash** and **Plotly**.
   * **KPI Indicators:** Displays aggregated metrics including Total Complaints, Active Kiosks, and Top Complaint Category.
   * **Analytical Charts:** Features time-series charts showing Daily Complaint Intensity and vertical bar charts mapping Category Distribution.
   * **Casablanca Hotspot Map:** Plots geospatial density coordinates over Casablanca using Plotly's open-source maps. Bubbles scale in size and color based on localized complaint volume.
   * **Unified Callback Engine:** Sidebar dropdowns for Category, Tram ID, and Date Ranges instantly filter the dataset and animate all visuals in real-time.

---

## Simulated Database & Analytics (`generate_data.py`)

In order to demonstrate the dashboard's analytical capabilities without exposing sensitive production logs, the repository includes an offline data generator (`generate_data.py`). It populates the database with **2,000 historical records** designed to mirror actual transit operations:

* **Commute Spikes:** Timestamps are weighted to peak during morning (07:30–09:30) and evening (17:00–19:30) rush hours, and restricted strictly to active tramway operating hours (06:00 to 23:30).
* **Language Weights:** Distributed proportionally to reflect Casablanca's user demographics (60% French, 35% Arabic, 5% English).
* **Station Hotspots:** Distributes volume to create high-density intersections on the Mapbox map (Abdelmoumen and Casa Voyageurs representing high-traffic transfer hubs).
* **Pre-Planted Anomalies:** Injects specific vehicle and seasonal trends (e.g., elevated delay records on `Tram12` and a summer equipment stressor spike on `Tram05`) to test administrative drill-down filters.

---

## Prerequisites

To run this project locally, you will need:
* Python 3.8+
* An **OpenAI API Key** (configured for text classification).
* A **Google Cloud Service Account** credential file (`credentials.json`) with Google Drive API access enabled.
* A shared CSV file hosted on your Google Drive.

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ALZ-11/FeedbackTrail.git
   cd FeedbackTrail
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: `pyaudio` may require manual system-level installation depending on your operating system).*

3. **Configure Environment Variables:**
   * Copy the template environment file:
     ```bash
     cp .env.example .env
     ```
   * Open `.env` and fill in your `OPENAI_API_KEY`, your Google Drive `GOOGLE_DRIVE_FILE_ID`, and make sure your Service Account JSON file is saved as `credentials.json` in your root folder.

---

## Running the Application

### 1. Initialize the Database (Optional)
To populate your Google Drive CSV with the 2,000-row historical baseline:
```bash
python generate_data.py
```
*(Make sure to upload the resulting `reclamations_history.csv` to Google Drive and configure your `.env` with its File ID, sharing Editor access with your service account email).*

### 2. Launch the Kiosk Terminal
To run the terminal terminal and submit complaints:
```bash
python main.py
```

### 3. Launch the Operational Dashboard
To boot up the analytical server:
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:8050/`**