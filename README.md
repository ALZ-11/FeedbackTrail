# FeedbackTrail

A legacy Python-based complaint classification system prototype that integrates with AI APIs for intelligent classification and Google Drive for data storage.

## Features
- **Intelligent Classification**: Uses AI APIs to classify user complaints.
- **Google Drive Integration**: Automatically updates a centralized CSV tracking database.
- **Audio Recording**: Capture complaints via microphone and transcribe them using Google's Speech-to-Text.
- **Multi-language Support**: Interface and processing for Arabic, English, and French.

## Prerequisites
- Python 3.8+
- Active AI API Key
- Google Cloud Service Account credentials (JSON) with Drive API access.
- Google Drive file id

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ALZ-11/FeedbackTrail
   cd "FeedbackTrail"
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: You may need to install `pyaudio` manually depending on your OS).*

3. Set up environment variables:
   - Copy `.env.example` to `.env`.
   - Fill in your `OPENAI_API_KEY`, or set up any other AI API key.
   - Place your `credentials.json` in the project root or set `GOOGLE_APPLICATION_CREDENTIALS` in `.env`.
   - Fill in your `GOOGLE_DRIVE_FILE_ID` in `.env`.

## Usage
Run the main script:
```bash
python main.py
```

## Project Structure
- `main.py`: Primary application script.
- `categories.txt`: List of predefined complaint categories.
- `images/`: UI assets and icons.
- `credentials.json`: Service account keys.

