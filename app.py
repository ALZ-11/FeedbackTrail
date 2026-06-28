import os
import io
import pandas as pd
from dotenv import load_dotenv
import googleapiclient.discovery
import googleapiclient.http
from google.oauth2 import service_account
import dash
from dash import dcc, html
import plotly.express as px

load_dotenv()

def fetch_data_from_drive():
    """
    Authenticates with Google Drive and downloads the CSV database
    directly into a Pandas DataFrame.
    """
    print("Authenticating with Google Drive API...")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    file_id = os.getenv("GOOGLE_DRIVE_FILE_ID")

    if not credentials_path or not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
    if not file_id:
        raise ValueError("GOOGLE_DRIVE_FILE_ID is not set in your .env file.")

    # Authenticate using service account credentials
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

    print(f"Downloading database CSV (File ID: {file_id})...")
    request = drive_service.files().get_media(fileId=file_id)
    
    # In-memory download stream
    file_io = io.BytesIO()
    downloader = googleapiclient.http.MediaIoBaseDownload(file_io, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        
    file_io.seek(0)
    print("Download complete.")
    
    # Load stream directly into a Pandas DataFrame
    df = pd.read_csv(file_io, encoding="utf-8")
    return df

# Load initial data to populate visual components
try:
    df = fetch_data_from_drive()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    unique_categories = sorted(df["Category"].dropna().unique())
    unique_trams = sorted(df["Tram_ID"].dropna().unique())

    # Static KPI Calculations
    total_complaints = len(df)
    top_category = df["Category"].mode()[0] if not df.empty else "N/A"
    active_kiosks = df["Station_Name"].nunique() if not df.empty else 0

    # Figure 1: Daily Trend (Line Chart)
    df_time = df.groupby(df["Timestamp"].dt.date).size().reset_index(name="Count")
    fig_line = px.line(
        df_time, 
        x="Timestamp", 
        y="Count", 
        labels={"Timestamp": "Date", "Count": "Complaints"}
    )
    fig_line.update_traces(line_color="#F77C3F", line_width=2.5)
    fig_line.update_layout(
        margin={"t": 30, "b": 10, "l": 10, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#EEEEEE"},
        xaxis={"gridcolor": "#EEEEEE"}
    )

    # Figure 2: Category Distribution (Bar Chart)
    df_cat = df["Category"].value_counts().reset_index(name="Count")
    fig_bar = px.bar(
        df_cat, 
        x="Category", 
        y="Count",
        labels={"Category": "Category", "Count": "Complaints"}
    )
    fig_bar.update_traces(marker_color="#416FEC")
    fig_bar.update_layout(
        margin={"t": 30, "b": 10, "l": 10, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#EEEEEE"},
        xaxis={"tickangle": -45}
    )

    # Figure 3: Casablanca Spatial Heatmap (Mapbox)
    df_map = df.groupby(["Station_Name", "Latitude", "Longitude"]).size().reset_index(name="Count")
    fig_map = px.scatter_mapbox(
        df_map, 
        lat="Latitude", 
        lon="Longitude", 
        size="Count", 
        color="Count",
        color_continuous_scale=px.colors.sequential.Oranges,
        size_max=35, 
        zoom=11.2, 
        mapbox_style="carto-positron",
        hover_name="Station_Name",
        labels={"Count": "Complaints"}
    )
    fig_map.update_layout(
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        mapbox_center={"lat": 33.57, "lon": -7.60}
    )

except Exception as e:
    print(f"[ERROR] Failed to load data during server initialization: {e}")
    unique_categories = []
    unique_trams = []
    total_complaints = 0
    top_category = "N/A"
    active_kiosks = 0
    fig_line = {}
    fig_bar = {}
    fig_map = {}

app = dash.Dash(__name__)
app.title = "FeedbackTrail Dashboard"

# Style helper dictionary for control slider box
SKELETON_BOX = {
    "padding": "15px",
    "border": "1px dashed #999999",
    "text-align": "center",
    "color": "#999999",
    "border-radius": "3px",
    "background-color": "#FAFAFA"
}

# Define Visual Layout
app.layout = html.Div(
    style={
        "font-family": "Arial, sans-serif", 
        "max-width": "1600px", 
        "margin": "0 auto", 
        "padding": "20px", 
        "background-color": "#F4F4F4",
        "min-height": "100vh"
    },
    children=[
        # HEADER
        html.Div(
            style={
                "display": "flex", 
                "justify-content": "space-between", 
                "align-items": "center", 
                "border-bottom": "3px solid #F77C3F", 
                "padding-bottom": "15px", 
                "margin-bottom": "25px",
                "background-color": "#FFFFFF",
                "padding": "20px",
                "border-radius": "5px",
                "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"
            },
            children=[
                html.Div([
                    html.H1("FeedbackTrail Dashboard", style={"color": "#F77C3F", "margin": "0"}),
                    html.P("Real-time complaint monitoring & analytics", style={"margin": "5px 0 0 0", "color": "#666666"})
                ]),
                # Active KPI Boxes
                html.Div(
                    style={"display": "flex", "gap": "15px"},
                    children=[
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "10px 20px", "border-radius": "4px", "background-color": "#FAFAFA", "text-align": "center", "min-width": "120px"},
                            children=[
                                html.Strong("Total Complaints", style={"color": "#333333"}), 
                                html.Div(f"{total_complaints}", style={"font-size": "20px", "font-weight": "bold", "color": "#F77C3F", "margin-top": "5px"})
                            ]
                        ),
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "10px 20px", "border-radius": "4px", "background-color": "#FAFAFA", "text-align": "center", "max-width": "200px"},
                            children=[
                                html.Strong("Top Category", style={"color": "#333333"}), 
                                html.Div(f"{top_category}", style={"font-size": "15px", "font-weight": "bold", "color": "#F77C3F", "margin-top": "5px", "white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"})
                            ]
                        ),
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "10px 20px", "border-radius": "4px", "background-color": "#FAFAFA", "text-align": "center", "min-width": "120px"},
                            children=[
                                html.Strong("Active Kiosks", style={"color": "#333333"}), 
                                html.Div(f"{active_kiosks}", style={"font-size": "20px", "font-weight": "bold", "color": "#F77C3F", "margin-top": "5px"})
                            ]
                        ),
                    ]
                )
            ]
        ),
        
        # MAIN GRID (Sidebar Controls + Plots)
        html.Div(
            style={"display": "flex", "gap": "20px"},
            children=[
                # LEFT SIDEBAR / CONTROLS (Width: 25%)
                html.Div(
                    style={
                        "flex": "1", 
                        "min-width": "300px", 
                        "max-width": "400px", 
                        "border": "1px solid #CCCCCC", 
                        "padding": "20px", 
                        "background-color": "#FFFFFF", 
                        "border-radius": "5px", 
                        "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"
                    },
                    children=[
                        html.H3("Filters", style={"margin-top": "0", "color": "#333333", "border-bottom": "1px solid #EEEEEE", "padding-bottom": "10px"}),
                        
                        # Category Dropdown Filter
                        html.Div([
                            html.Label("Filter by Category:", style={"font-weight": "bold", "display": "block", "margin-bottom": "5px"}),
                            dcc.Dropdown(
                                id="category-dropdown",
                                options=[{"label": c, "value": c} for c in unique_categories],
                                multi=True,
                                placeholder="Select categories..."
                            )
                        ], style={"margin-bottom": "25px"}),
                        
                        # Tram ID Dropdown Filter
                        html.Div([
                            html.Label("Filter by Tram ID:", style={"font-weight": "bold", "display": "block", "margin-bottom": "5px"}),
                            dcc.Dropdown(
                                id="tram-dropdown",
                                options=[{"label": t, "value": t} for t in unique_trams],
                                multi=True,
                                placeholder="Select trams..."
                            )
                        ], style={"margin-bottom": "25px"}),
                        
                        # Date Range Slider Placeholder
                        html.Div([
                            html.Label("Filter by Date Range:", style={"font-weight": "bold", "display": "block", "margin-bottom": "5px"}),
                            html.Div("Date Range Slider Placeholder", style=SKELETON_BOX)
                        ])
                    ]
                ),
                
                # RIGHT VISUALIZATIONS SECTION (Width: 75%)
                html.Div(
                    style={"flex": "3"},
                    children=[
                        # Upper Row: Two Plots
                        html.Div(
                            style={"display": "flex", "gap": "20px", "margin-bottom": "20px"},
                            children=[
                                html.Div(
                                    style={"flex": "1", "border": "1px solid #CCCCCC", "padding": "20px", "background-color": "#FFFFFF", "border-radius": "5px", "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"},
                                    children=[
                                        html.H4("Complaint Intensity over Time", style={"margin-top": "0", "color": "#333333"}),
                                        dcc.Graph(id="time-series-chart", figure=fig_line, style={"height": "250px"})
                                    ]
                                ),
                                html.Div(
                                    style={"flex": "1", "border": "1px solid #CCCCCC", "padding": "20px", "background-color": "#FFFFFF", "border-radius": "5px", "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"},
                                    children=[
                                        html.H4("Complaints Distribution by Category", style={"margin-top": "0", "color": "#333333"}),
                                        dcc.Graph(id="category-chart", figure=fig_bar, style={"height": "250px"})
                                    ]
                                ),
                            ]
                        ),
                        
                        # Lower Row: Map (Full Width)
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "20px", "background-color": "#FFFFFF", "border-radius": "5px", "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"},
                            children=[
                                html.H4("Casablanca Kiosk Hotspots Map", style={"margin-top": "0", "color": "#333333"}),
                                dcc.Graph(id="mapbox-map", figure=fig_map, style={"height": "400px"})
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)