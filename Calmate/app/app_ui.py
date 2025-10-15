import tkinter as tk
from tkinter import ttk, messagebox
from addevent import get_events_for_day, get_free_slots, SCOPES
from gemini_helper import get_response
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import datetime


# ---------------- Google Calendar Setup ----------------
def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service


# ---------------- Tkinter Tooltip ----------------
class CreateToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            font=("Helvetica", 10),
        )
        label.pack(ipadx=5, ipady=3)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# ---------------- Tkinter Functions ----------------
def check_free_slots():
    service = get_calendar_service()
    date_str = date_entry.get()
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.")
        return

    events = get_events_for_day(service, date_str)
    free_slots_listbox.delete(0, tk.END)
    free_slots = get_free_slots(events)
    if not free_slots:
        messagebox.showinfo("No Free Slots", "No free slots available on this day.")
        return
    for idx, slot in enumerate(free_slots, 1):
        free_slots_listbox.insert(tk.END, f"{slot[0]} - {slot[1]}")
    root.free_slots = free_slots


def suggest_slots():
    event_title = event_entry.get()
    if not event_title:
        messagebox.showwarning("Input Needed", "Enter an event title first.")
        return
    try:
        duration = int(duration_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Duration", "Enter event duration in hours as a number.")
        return
    if not hasattr(root, "free_slots") or not root.free_slots:
        messagebox.showwarning("No Free Slots", "Check free slots first!")
        return

    # Format free_slots into numbered string for Gemini
    free_slots_text = ""
    for idx, slot in enumerate(root.free_slots, 1):
        free_slots_text += f"{idx}. {slot[0]} - {slot[1]}\n"

    suggested = get_response(event_title, free_slots_text, duration)
    suggested_listbox.delete(0, tk.END)
    for slot in suggested:
        suggested_listbox.insert(tk.END, f"{slot[0]} - {slot[1]}")
    root.suggested_slots = suggested


def schedule_event():
    try:
        selected_idx = suggested_listbox.curselection()[0]
        event_start, event_end = root.suggested_slots[selected_idx]
        event_title = event_entry.get()
        date_str = date_entry.get()
        service = get_calendar_service()
        start_dt = f"{date_str}T{event_start}:00-04:00"
        end_dt = f"{date_str}T{event_end}:00-04:00"
        event = {
            'summary': event_title,
            'start': {'dateTime': start_dt, 'timeZone': 'America/New_York'},
            'end': {'dateTime': end_dt, 'timeZone': 'America/New_York'},
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        messagebox.showinfo("Scheduled", f"✅ Event created: {created_event.get('htmlLink')}")
    except IndexError:
        messagebox.showwarning("No Selection", "Select a suggested slot first!")


# ---------------- Tkinter UI ----------------
root = tk.Tk()
root.title("Autoscheduler AI")
root.geometry("700x600")
root.config(bg="#f9fbfd")  # light cream/blue background


# Style
style = ttk.Style(root)
style.configure(
    "TButton",
    font=("Helvetica", 12),
    padding=6,
    relief="flat",
    borderwidth=0,
    background="#a7c7e7",  # pastel blue
    foreground="#000",
)
style.map("TButton",
          foreground=[('active', 'white')],
          background=[('active', '#5b8fc9')])  # slightly darker blue on hover


# Title
title_label = tk.Label(root, text="Autoscheduler AI", font=("Helvetica", 24, "bold"),
                       bg="#f9fbfd", fg="#2c3e50")
title_label.pack(pady=20)


# Input Frame Card
input_card = tk.Frame(root, bg="#d5e3f8", bd=2, relief="groove", padx=20, pady=20)
input_card.pack(pady=10, padx=20, fill="x")

tk.Label(input_card, text="Date (YYYY-MM-DD):", font=("Helvetica", 12),
         bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
date_entry = tk.Entry(input_card, font=("Helvetica", 12), width=20)
date_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_card, text="Event Title:", font=("Helvetica", 12),
         bg="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
event_entry = tk.Entry(input_card, font=("Helvetica", 12), width=25)
event_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_card, text="Duration (hours):", font=("Helvetica", 12),
         bg="#ffffff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
duration_entry = tk.Entry(input_card, font=("Helvetica", 12), width=5)
duration_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")


# Free Slots Card
free_card = tk.Frame(root, bg="#c7e0f7", bd=2, relief="groove", padx=10, pady=10)  # soft blue
free_card.pack(pady=10, padx=20, fill="x")
tk.Label(free_card, text="Free Slots:", font=("Helvetica", 12, "bold"), bg="#e3f2fd").pack(anchor="w")
free_slots_listbox = tk.Listbox(free_card, width=50, height=6, font=("Helvetica", 12),
                                bd=0, bg="#f7dff1")
free_slots_listbox.pack(pady=5, padx=5)
ttk.Button(free_card, text="Check Free Slots", command=check_free_slots).pack(pady=5)
CreateToolTip(free_card, "Click to fetch free slots from your Google Calendar")


# Suggested Slots Card
suggested_card = tk.Frame(root, bg="#c7e0f7", bd=2, relief="groove", padx=10, pady=10)  # very pale pastel blue
suggested_card.pack(pady=10, padx=20, fill="x")
tk.Label(suggested_card, text="AI Suggested Slots:", font=("Helvetica", 12, "bold"), bg="#f0f8ff").pack(anchor="w")
suggested_listbox = tk.Listbox(suggested_card, width=50, height=6, font=("Helvetica", 12),
                               bd=0, bg="#f7dff1")
suggested_listbox.pack(pady=5, padx=5)
ttk.Button(suggested_card, text="Suggest Slots", command=suggest_slots).pack(pady=5)
ttk.Button(suggested_card, text="Schedule Event", command=schedule_event).pack(pady=5)
CreateToolTip(suggested_card, "Select a slot and schedule your event")


root.mainloop()
