import os
#from dotenv import load_dotenv
import google.generativeai as genai


#load_dotenv()
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # load from .env

def get_response(event_title,free_time_slots,duration):
    genai.configure(api_key="enter you key")
    


    model = genai.GenerativeModel("gemini-2.5-flash")
    propmpt = f"""You are an AI scheduling assistant.

    I have an event titled "{event_title}" that lasts {duration} hours. 
    Here are the available time slots I can schedule it in:

    {free_time_slots}

    Please suggest up to 3 best time slots for this event based on optimal spacing and avoiding back-to-back overload. Make sure that the slots suggested are continuous. 
    Here are some of my preferences just for reference (you don't need to stick to it): 
    - I like to study in the evening/night
    - I like to schedule meetings in the evening
    - Night person → prefers events later in the day.
    - Day starts at 10:00 AM, ends at 1:00 AM.
    - Avoid back-to-back overload → Gemini should not suggest events right after another.

Prefer continuous blocks of time for events. If fewer than 3 valid options exist, return as many as possible.  
    Return your answer in the same numbered format as above, like:

    1. [slot]
    2. [slot]
    3. [slot]
    Don't output anything else other than the time slots.
    """
    response = model.generate_content(propmpt)

    text = response.text
    print(text)
    print("the text is over")

    parsed_slots = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            # Remove "1." or "2."
            _, times_str = line.split(".", 1)
            times_str = times_str.strip()
            # Handle multiple slots combined with "&"
            parts = times_str.split("&")
            for part in parts:
                start_end = part.strip().split(" - ")
                if len(start_end) == 2:
                    start, end = start_end
                    parsed_slots.append((start.strip(), end.strip()))
    return parsed_slots


