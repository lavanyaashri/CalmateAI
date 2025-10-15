from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gemini_helper import get_response




# If modifying events, use this scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_events_for_day(service, date_str):
    """
    Fetch events for a given date (YYYY-MM-DD) and return them as a list of dicts.
    """
    start_of_day = f"{date_str}T00:00:00-04:00"  # Adjust timezone as needed
    end_of_day = f"{date_str}T23:59:59-04:00"

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

def get_free_slots(events, work_start="10:00", work_end="23:59", slot_duration=60):
    """
    Divide free time into 1-hour slots (or slot_duration minutes) between work_start and work_end.
    """
    free_slots = []
    
    work_start_dt = datetime.datetime.strptime(work_start, "%H:%M")
    work_end_dt = datetime.datetime.strptime(work_end, "%H:%M")
    
    if not events:
        current = work_start_dt
        while current + datetime.timedelta(minutes=slot_duration) <= work_end_dt:
            end_time = current + datetime.timedelta(minutes=slot_duration)
            free_slots.append((current.strftime("%H:%M"), end_time.strftime("%H:%M")))
            current = end_time
        return free_slots
    
    # Convert events to datetime ranges
    event_times = []
    for e in events:
        start_str = e['start'].get('dateTime', e['start'].get('date'))[11:16]
        end_str = e['end'].get('dateTime', e['end'].get('date'))[11:16]
        event_times.append((
            datetime.datetime.strptime(start_str, "%H:%M"),
            datetime.datetime.strptime(end_str, "%H:%M")
        ))
    
    event_times.sort(key=lambda x: x[0])
    
    current = work_start_dt
    for start, end in event_times:
        while current + datetime.timedelta(minutes=slot_duration) <= start:
            slot_end = current + datetime.timedelta(minutes=slot_duration)
            free_slots.append((current.strftime("%H:%M"), slot_end.strftime("%H:%M")))
            current = slot_end
        if current < end:
            current = end
    
    # Free time after last event
    while current + datetime.timedelta(minutes=slot_duration) <= work_end_dt:
        slot_end = current + datetime.timedelta(minutes=slot_duration)
        free_slots.append((current.strftime("%H:%M"), slot_end.strftime("%H:%M")))
        current = slot_end
    
    return free_slots

def main():
    creds = None
    # token.json stores your access/refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save creds for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Ask user for the date to check
    event_date = input("Which day do you want to check? (YYYY-MM-DD): ")

    # Fetch and show existing events
    events = get_events_for_day(service, event_date)
    if not events:
        print("\nNo events scheduled for this day!")
    else:
        print("\nYour schedule for the day:")
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date'))
            end = e['end'].get('dateTime', e['end'].get('date'))
            print(f"{start[11:16]} - {end[11:16]}: {e.get('summary', 'No Title')}")

    # Show free 1-hour slots
    free_slots_list= ''
    free_slots = get_free_slots(events)
    if not free_slots:
        
        return
    else:
        
        for idx, slot in enumerate(free_slots, 1):
            free_slots_list += (f"{idx}. {slot[0]} - {slot[1]}")

        # Let user pick a slot
        

    # Ask for event title
    event_title = input("\nEvent title: ")
    duration= int(input("Enter hours: "))
    suggested_response = get_response(event_title, free_slots_list, duration)

    # Show suggested slots
    print("\nHere are the suggested slots:")
    for idx, slot in enumerate(suggested_response, 1):
        print(f"{idx}. {slot[0]} - {slot[1]}")

    # Let user pick one
    chosen_option = int(input("\nEnter the number of the slot you want to schedule: "))
    event_start, event_end = suggested_response[chosen_option - 1]
    print(f"Selected time slot: {event_start} - {event_end}")

    # Format datetime strings
    start_dt = f"{event_date}T{event_start}:00-04:00"
    end_dt = f"{event_date}T{event_end}:00-04:00"

    # Create the event
    event = {
        'summary': event_title,
        'start': {'dateTime': start_dt, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_dt, 'timeZone': 'America/New_York'},
    }

    # Insert into Google Calendar
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"\n✅ Event created: {created_event.get('htmlLink')}")



if __name__ == '__main__':
    main()


