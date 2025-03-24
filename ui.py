import customtkinter as ctk
from PIL import Image
import os
import json
import schedule
import threading
import time
import re
from tkinter import messagebox

class StardewNotifierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Stardew Notifier ✨")
        self.geometry("550x500")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.asset_path = os.path.join(os.path.dirname(__file__), 'assets')
        self.bg_image = ctk.CTkImage(Image.open(os.path.join(self.asset_path, "spring_bg.png")), size=(550, 500))
        self.mascot_image = ctk.CTkImage(Image.open(os.path.join(self.asset_path, "junimo.png")), size=(80, 80))

        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.mascot_label = ctk.CTkLabel(self, image=self.mascot_image, text="")
        self.mascot_label.place(x=30, y=30)

        self.reminder_frame = ctk.CTkScrollableFrame(self, width=500, height=250)
        self.reminder_frame.place(relx=0.5, rely=0.55, anchor="center")

        self.add_button = ctk.CTkButton(self, text="+ Add Reminder", command=self.add_reminder_entry)
        self.add_button.place(relx=0.5, rely=0.88, anchor="center")

        self.save_button = ctk.CTkButton(self, text="Save All Reminders", command=self.save_reminders)
        self.save_button.place(relx=0.5, rely=0.94, anchor="center")

        self.entries = []
        self.load_reminders()
        self.start_scheduler_thread()

    def add_reminder_entry(self, time_value="", message=""):
        time_entry = ctk.CTkEntry(self.reminder_frame, placeholder_text="HH:MM", width=80)
        time_entry.insert(0, time_value)
        message_entry = ctk.CTkEntry(self.reminder_frame, placeholder_text="Reminder message...", width=300)
        message_entry.insert(0, message)
        delete_button = ctk.CTkButton(self.reminder_frame, text="🗑", width=40, command=lambda: self.delete_reminder_entry(row))

        row = len(self.entries)
        time_entry.grid(row=row, column=0, padx=5, pady=5)
        message_entry.grid(row=row, column=1, padx=5, pady=5)
        delete_button.grid(row=row, column=2, padx=5, pady=5)

        self.entries.append((time_entry, message_entry, delete_button))

    def delete_reminder_entry(self, index):
        if 0 <= index < len(self.entries):
            time_entry, message_entry, delete_button = self.entries[index]
            time_entry.destroy()
            message_entry.destroy()
            delete_button.destroy()
            self.entries.pop(index)
            self.refresh_reminder_grid()

    def refresh_reminder_grid(self):
        for idx, (time_entry, message_entry, delete_button) in enumerate(self.entries):
            time_entry.grid(row=idx, column=0, padx=5, pady=5)
            message_entry.grid(row=idx, column=1, padx=5, pady=5)
            delete_button.configure(command=lambda i=idx: self.delete_reminder_entry(i))
            delete_button.grid(row=idx, column=2, padx=5, pady=5)

    def validate_and_format_time(self, time_str):
        match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
        if not match:
            return None
        hour, minute = match.groups()
        try:
            hour = int(hour)
            minute = int(minute)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        except:
            return None
        return None

    def save_reminders(self):
        reminders = []
        for time_entry, message_entry, _ in self.entries:
            time_text = time_entry.get()
            message_text = message_entry.get()
            formatted_time = self.validate_and_format_time(time_text)

            if not formatted_time:
                messagebox.showerror("Invalid Time Format", f"'{time_text}' is not a valid time. Please use HH:MM (24-hour).")
                return

            if formatted_time and message_text:
                reminders.append({"time": formatted_time, "message": message_text})

        with open("config.json", "w") as f:
            json.dump(reminders, f)

        print("Reminders saved! ❤️")
        self.schedule_all_reminders(reminders)

    def load_reminders(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    reminders = json.load(f)
                    for reminder in reminders:
                        self.add_reminder_entry(reminder["time"], reminder["message"])
                    self.schedule_all_reminders(reminders)
                    print("Reminders loaded.")
            except Exception as e:
                print(f"Error loading reminders: {e}")

    def schedule_all_reminders(self, reminders):
        schedule.clear()
        for reminder in reminders:
            schedule.every().day.at(reminder["time"]).do(self.send_notification, reminder["message"])

    def send_notification(self, message):
        try:
            from plyer import notification
            notification.notify(
                title="Stardew Notifier",
                message=message,
                timeout=5
            )
        except ImportError:
            print("Plyer not installed. Cannot send notification.")

    def start_scheduler_thread(self):
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        t = threading.Thread(target=run_scheduler, daemon=True)
        t.start()
