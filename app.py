import os
import io
import pandas as pd
from dotenv import load_dotenv
import googleapiclient.discovery
import googleapiclient.http
from google.oauth2 import service_account
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
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
    
    # chronological limits for Date Picker
    min_date = df["Timestamp"].min().date()
    max_date = df["Timestamp"].max().date()

except Exception as e:
    print(f"[ERROR] Failed to load data during server initialization: {e}")
    unique_categories = []
    unique_trams = []
    min_date = None
    max_date = None

app = dash.Dash(__name__)
app.title = "FeedbackTrail Dashboard"

# Visual Layout with Active Controls and Graphs
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
        # 1. HEADER (with KPI value targets)
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
                # KPI Boxes
                html.Div(
                    style={"display": "flex", "gap": "15px"},
                    children=[
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "10px 20px", "border-radius": "4px", "background-color": "#FAFAFA", "text-align": "center", "min-width": "120px"},
                            children=[
                                html.Strong("Total Complaints", style={"color": "#333333"}), 
                                html.Div(id="total-complaints-val", style={"font-size": "20px", "font-weight": "bold", "color": "#F77C3F", "margin-top": "5px"})
                            ]
                        ),
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "10px 20px", "border-radius": "4px", "background-color": "#FAFAFA", "text-align": "center", "max-width": "200px"},
                            children=[
                                html.Strong("Top Category", style={"color": "#333333"}), 
                                html.Div(id="top-category-val", style={"font-size": "14px", "font-weight": "bold", "color": "#F77C3F", "margin-top": "5px", "white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"})
                            ]
                        ),
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "10px 20px", "border-radius": "4px", "background-color": "#FAFAFA", "text-align": "center", "min-width": "120px"},
                            children=[
                                html.Strong("Active Kiosks", style={"color": "#333333"}), 
                                html.Div(id="active-kiosks-val", style={"font-size": "20px", "font-weight": "bold", "color": "#F77C3F", "margin-top": "5px"})
                            ]
                        ),
                    ]
                )
            ]
        ),
        
        # MAIN GRID (Sidebar Controls + Graphs)
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
                        
                        # Date Range Picker
                        html.Div([
                            html.Label("Filter by Date Range:", style={"font-weight": "bold", "display": "block", "margin-bottom": "5px"}),
                            dcc.DatePickerRange(
                                id="date-picker-range",
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=max_date,
                                display_format="YYYY-MM-DD",
                                style={"width": "100%", "background-color": "#FFFFFF"}
                            )
                        ])
                    ]
                ),
                
                # RIGHT VISUALIZATIONS SECTION (Width: 75%)
                html.Div(
                    style={"flex": "3"},
                    children=[
                        # Upper Row: Two Plots (Side-by-Side)
                        html.Div(
                            style={"display": "flex", "gap": "20px", "margin-bottom": "20px"},
                            children=[
                                html.Div(
                                    style={"flex": "1", "border": "1px solid #CCCCCC", "padding": "20px", "background-color": "#FFFFFF", "border-radius": "5px", "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"},
                                    children=[
                                        html.H4("Complaint Intensity over Time", style={"margin-top": "0", "color": "#333333"}),
                                        dcc.Graph(id="time-series-chart", style={"height": "250px"})
                                    ]
                                ),
                                html.Div(
                                    style={"flex": "1", "border": "1px solid #CCCCCC", "padding": "20px", "background-color": "#FFFFFF", "border-radius": "5px", "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"},
                                    children=[
                                        html.H4("Complaints Distribution by Category", style={"margin-top": "0", "color": "#333333"}),
                                        dcc.Graph(id="category-chart", style={"height": "250px"})
                                    ]
                                ),
                            ]
                        ),
                        
                        # Lower Row: Map (Full Width)
                        html.Div(
                            style={"border": "1px solid #CCCCCC", "padding": "20px", "background-color": "#FFFFFF", "border-radius": "5px", "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)"},
                            children=[
                                html.H4("Casablanca Kiosk Hotspots Map", style={"margin-top": "0", "color": "#333333"}),
                                dcc.Graph(id="mapbox-map", style={"height": "400px"})
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# CALLBACK ENGINE
@app.callback(
    [
        Output("total-complaints-val", "children"),
        Output("top-category-val", "children"),
        Output("active-kiosks-val", "children"),
        Output("time-series-chart", "figure"),
        Output("category-chart", "figure"),
        Output("mapbox-map", "figure")
    ],
    [
        Input("category-dropdown", "value"),
        Input("tram-dropdown", "value"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date")
    ]
)
def update_dashboard(selected_categories, selected_trams, start_date, end_date):
    """
    Triggers dynamically whenever any filter is adjusted.
    Filters the Pandas dataframe and updates all KPI values & Plotly figures in real-time.
    """
    # local working copy of the master dataset
    filtered_df = df.copy()

    # Chronological Filtering
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["Timestamp"].dt.date >= pd.to_datetime(start_date).date()) &
            (filtered_df["Timestamp"].dt.date <= pd.to_datetime(end_date).date())
        ]

    # Category Filtering
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

    # Vehicle Filtering
    if selected_trams:
        filtered_df = filtered_df[filtered_df["Tram_ID"].isin(selected_trams)]

    # Recalculate KPIs
    total_count = len(filtered_df)
    top_cat = filtered_df["Category"].mode()[0] if not filtered_df.empty else "N/A"
    active_stations = filtered_df["Station_Name"].nunique() if not filtered_df.empty else 0

    # Rebuild Figure 1: Trends over Time
    if not filtered_df.empty:
        df_time = filtered_df.groupby(filtered_df["Timestamp"].dt.date).size().reset_index(name="Count")
        fig_line = px.line(df_time, x="Timestamp", y="Count", labels={"Timestamp": "Date", "Count": "Complaints"})
        fig_line.update_traces(line_color="#F77C3F", line_width=2.5)
    else:
        fig_line = px.line(title="No Data within selection")
        
    fig_line.update_layout(
        margin={"t": 30, "b": 10, "l": 10, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#EEEEEE"},
        xaxis={"gridcolor": "#EEEEEE"}
    )

    # Rebuild Figure 2: Category Distribution
    if not filtered_df.empty:
        df_cat_count = filtered_df["Category"].value_counts().reset_index(name="Count")
        fig_bar = px.bar(df_cat_count, x="Category", y="Count", labels={"Category": "Category", "Count": "Complaints"})
        fig_bar.update_traces(marker_color="#416FEC")
    else:
        fig_bar = px.bar(title="No Data within selection")
        
    fig_bar.update_layout(
        margin={"t": 30, "b": 10, "l": 10, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#EEEEEE"},
        xaxis={"tickangle": -45}
    )

    # Rebuild Figure 3: Mapbox Map
    if not filtered_df.empty:
        df_map_count = filtered_df.groupby(["Station_Name", "Latitude", "Longitude"]).size().reset_index(name="Count")
        fig_map = px.scatter_map(
            df_map_count, 
            lat="Latitude", 
            lon="Longitude", 
            size="Count", 
            color="Count",
            color_continuous_scale=px.colors.sequential.Oranges,
            size_max=35, 
            zoom=11.2, 
            map_style="carto-positron",
            hover_name="Station_Name",
            labels={"Count": "Complaints"}
        )
        fig_map.update_layout(
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            map_center={"lat": 33.57, "lon": -7.60}
        )
    else:
        # Fallback empty map centered on Casablanca
        fig_map = px.scatter_map(lat=[33.57], lon=[-7.60], zoom=11.2, map_style="carto-positron")
        fig_map.update_layout(
            margin={"t": 10, "b": 10, "l": 10, "r": 10}
        )

    return f"{total_count}", f"{top_cat}", f"{active_stations}", fig_line, fig_bar, fig_map

if __name__ == "__main__":
    app.run(debug=True)