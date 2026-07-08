
# CalMate
An AI-powered scheduling assistant that integrates with Google Calendar to automatically suggest optimal event times based on your calendar availability and personal preferences.

## What It Does

- Reads your Google Calendar via OAuth 2.0 to find free time slots for any given day
- Uses the Gemini API to intelligently rank and suggest the best 3 time slots based on your scheduling preferences (e.g., preferred time of day, avoiding back-to-back overload)
- Creates events directly in your Google Calendar with one click

## Tech Stack

- **Language:** Python 3
- **UI:** Tkinter
- **APIs:** Google Calendar API, Gemini API
- **Auth:** OAuth 2.0

## Setup

1. Clone the repo:
```bash
   git clone https://github.com/lavanyaashri/Calmate.git
   cd Calmate
```

2. Install dependencies:
```bash
   pip install -r requirements.txt
```

3. Create a `.env` file in the root folder with your Gemini API key:
   GEMINI_API_KEY=your_gemini_api_key_here
   
5. Download OAuth `credentials.json` from Google Cloud Console (enable the Google Calendar API) and place it in the `app/` folder.

6. Run the app:
```bash
   cd app
   python app_ui.py
```

## Project Structure
Calmate/

├── app/

│   ├── addevent.py       # Google Calendar integration

│   ├── app_ui.py         # Tkinter UI entry point

│   └── gemini_helper.py  # Gemini API prompt logic

├── requirements.txt

└── README.md

## Author

Lavanya Ashri
