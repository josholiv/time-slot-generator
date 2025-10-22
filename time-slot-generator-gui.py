"""
Time Slot Generator GUI
-----------------------
Generates randomized, non-overlapping time slots within a date and time range.

Features:
- Specify number of time slots, duration, start and end times, increments, and start date.
- Optionally avoid specific days or time ranges.
- Specify maximum number of slots allowed per day.
- Outputs formatted list of time slots in chronological order.

Author: Josh Olivier
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import random

# ======================
# === CONFIGURATION ===
# ======================

class Config:
    """Holds user-defined settings for time slot generation."""

    NUM_SLOTS: int = 10
    SLOT_DURATION: timedelta = timedelta(hours=2, minutes=30)
    START_TIME: float = 9
    END_TIME: float = 16.5
    TIME_INCREMENT_MINUTES: int = 30
    DAYS_FROM_TODAY: int = 7
    AVOID_DAYS: list[int] = []
    AVOID_TIMES: dict[int, list[tuple[float, float]]] = {}
    SLOTS_PER_DAY: int = 1  # number of slots allowed per day


# ======================
# === HELPER FUNCTIONS ===
# ======================


def parse_time_hhmm(time_str: str) -> float:
    """Convert 'HH:MM' to float hours (e.g., '09:30' → 9.5)."""
    try:
        hour, minute = map(int, time_str.split(":"))
        return hour + minute / 60
    except ValueError:
        raise ValueError("Time must be in HH:MM format, e.g., 09:30")


def format_hour_24(hour_float: float) -> str:
    """Convert float hours to 'HH:MM'."""
    hour = int(hour_float)
    minute = int((hour_float % 1) * 60)
    return f"{hour:02d}:{minute:02d}"


def format_slot_custom(date_obj: datetime, start_dt: datetime, end_dt: datetime) -> str:
    """Format a slot with readable date/time strings."""
    date_str = date_obj.strftime("%A, %B %d").replace(" 0", " ")
    start_str = start_dt.strftime("%I:%M %p").lstrip("0")
    end_str = end_dt.strftime("%I:%M %p").lstrip("0")
    return f"{date_str}, from {start_str} – {end_str}"


def overlaps_avoid_time(weekday: int, start_hour: float, end_hour: float, avoid_times: dict) -> bool:
    """Check if a time range overlaps any avoided period."""
    if weekday not in avoid_times:
        return False
    for a_start, a_end in avoid_times[weekday]:
        if (start_hour < a_end) and (end_hour > a_start):
            return True
    return False


# ======================
# === CORE LOGIC ===
# ======================


def generate_time_slots(config: Config) -> list:
    """Generate random, non-overlapping time slots based on configuration."""
    slots = []
    start_date = (datetime.today() + timedelta(days=config.DAYS_FROM_TODAY)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    current_date = start_date
    days = list(range(7))

    increment_hours = config.TIME_INCREMENT_MINUTES / 60
    valid_start_times = [
        t
        for t in frange(
            config.START_TIME,
            config.END_TIME - config.SLOT_DURATION.total_seconds() / 3600,
            increment_hours,
        )
    ]

    while len(slots) < config.NUM_SLOTS:
        if current_date.weekday() in days and current_date.weekday() not in config.AVOID_DAYS:
            daily_slots = []
            attempts = 0
            while len(daily_slots) < config.SLOTS_PER_DAY and attempts < 50:
                start_hour = random.choice(valid_start_times)
                end_hour = start_hour + config.SLOT_DURATION.total_seconds() / 3600

                if overlaps_avoid_time(current_date.weekday(), start_hour, end_hour, config.AVOID_TIMES):
                    attempts += 1
                    continue

                # Prevent overlap within the same day
                if any(
                    not (end_hour <= s_dt.hour + s_dt.minute / 60 or start_hour >= e_dt.hour + e_dt.minute / 60)
                    for _, s_dt, e_dt in daily_slots
                ):
                    attempts += 1
                    continue

                start_dt = current_date.replace(
                    hour=int(start_hour),
                    minute=int((start_hour % 1) * 60),
                    second=0,
                )
                end_dt = start_dt + config.SLOT_DURATION
                daily_slots.append((current_date, start_dt, end_dt))
                attempts += 1

            daily_slots.sort(key=lambda x: x[1])
            slots.extend(daily_slots)

        current_date += timedelta(days=1)
        if current_date - start_date > timedelta(days=90):  # safety limit
            break

    slots.sort(key=lambda x: x[1])
    return slots[: config.NUM_SLOTS]


def frange(start: float, stop: float, step: float):
    """Generate a range of floats."""
    while start <= stop:
        yield round(start, 2)
        start += step


# ======================
# === GUI LOGIC ===
# ======================


def generate_slots():
    """Collect input values, generate slots, and display results."""
    try:
        cfg = Config()
        cfg.NUM_SLOTS = int(num_slots.get())
        cfg.SLOT_DURATION = timedelta(hours=float(duration.get()))
        cfg.START_TIME = parse_time_hhmm(start_time.get())
        cfg.END_TIME = parse_time_hhmm(end_time.get())
        cfg.TIME_INCREMENT_MINUTES = int(increment.get())
        cfg.DAYS_FROM_TODAY = int(days_ahead.get())
        cfg.SLOTS_PER_DAY = int(slots_per_day.get())

        cfg.AVOID_DAYS = [i for i, v in enumerate(avoid_day_vars) if v.get() == 1]
        cfg.AVOID_TIMES = {}

        for entry in avoid_times_listbox.get(0, tk.END):
            day, start_end = entry.split(" ", 1)
            start_str, end_str = start_end.split(" – ")
            day_idx = days.index(day)
            cfg.AVOID_TIMES.setdefault(day_idx, []).append(
                (parse_time_hhmm(start_str), parse_time_hhmm(end_str))
            )

        slots = generate_time_slots(cfg)
        output_box.delete("1.0", tk.END)
        for s in slots:
            output_box.insert(tk.END, f"{format_slot_custom(*s)}\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def add_avoid_time():
    """Add an avoid time range to the listbox."""
    day = day_dropdown.get()
    try:
        start_h = parse_time_hhmm(start_time_entry.get())
        end_h = parse_time_hhmm(end_time_entry.get())
    except ValueError as ve:
        messagebox.showerror("Invalid input", str(ve))
        return

    avoid_times_listbox.insert(
        tk.END, f"{day} {format_hour_24(start_h)} – {format_hour_24(end_h)}"
    )
    start_time_entry.delete(0, tk.END)
    end_time_entry.delete(0, tk.END)


def remove_selected_avoid_time():
    """Remove the selected avoid time from the listbox."""
    for i in reversed(avoid_times_listbox.curselection()):
        avoid_times_listbox.delete(i)


# ======================
# === GUI SETUP ===
# ======================


def main():
    """Initialize and run the Tkinter GUI."""
    global num_slots, duration, start_time, end_time, increment, days_ahead
    global slots_per_day, avoid_day_vars, avoid_times_listbox
    global day_dropdown, start_time_entry, end_time_entry, output_box, days

    root = tk.Tk()
    root.title("Random Time Slot Generator")
    root.geometry("720x760")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=15)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Number of slots:").grid(column=0, row=0, sticky="w")
    num_slots = ttk.Entry(frm)
    num_slots.insert(0, "10")
    num_slots.grid(column=1, row=0, pady=2)

    ttk.Label(frm, text="Duration (hours):").grid(column=0, row=1, sticky="w")
    duration = ttk.Entry(frm)
    duration.insert(0, "2.5")
    duration.grid(column=1, row=1, pady=2)

    ttk.Label(frm, text="Start time (HH:MM):").grid(column=0, row=2, sticky="w")
    start_time = ttk.Entry(frm)
    start_time.insert(0, "09:00")
    start_time.grid(column=1, row=2, pady=2)

    ttk.Label(frm, text="End time (HH:MM):").grid(column=0, row=3, sticky="w")
    end_time = ttk.Entry(frm)
    end_time.insert(0, "16:30")
    end_time.grid(column=1, row=3, pady=2)

    ttk.Label(frm, text="Increment (minutes):").grid(column=0, row=4, sticky="w")
    increment = ttk.Entry(frm)
    increment.insert(0, "30")
    increment.grid(column=1, row=4, pady=2)

    ttk.Label(frm, text="Days from today to start:").grid(column=0, row=5, sticky="w")
    days_ahead = ttk.Entry(frm)
    days_ahead.insert(0, "7")
    days_ahead.grid(column=1, row=5, pady=2)

    ttk.Label(frm, text="Max slots per day").grid(column=0, row=6, sticky="w")
    slots_per_day = ttk.Entry(frm)
    slots_per_day.insert(0, "1")
    slots_per_day.grid(column=1, row=6, pady=2)

    ttk.Label(frm, text="Avoid days:").grid(column=0, row=7, sticky="w")
    avoid_days_frame = ttk.Frame(frm)
    avoid_days_frame.grid(column=1, row=7, sticky="w", pady=2)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    avoid_day_vars = [tk.IntVar() for _ in days]

    for i, day in enumerate(days):
        if day in ["Sat", "Sun"]:
            avoid_day_vars[i].set(1)
        ttk.Checkbutton(avoid_days_frame, text=day, variable=avoid_day_vars[i]).grid(
            column=i, row=0, padx=3, sticky="w"
        )

    ttk.Label(frm, text="Avoid specific times:").grid(column=0, row=8, sticky="w")
    avoid_times_frame = ttk.Frame(frm)
    avoid_times_frame.grid(column=0, row=9, columnspan=7, sticky="w", pady=(5, 0))

    day_dropdown = ttk.Combobox(avoid_times_frame, values=days, state="readonly", width=5)
    day_dropdown.set("Mon")
    day_dropdown.grid(column=0, row=0, padx=(0, 5))

    ttk.Label(avoid_times_frame, text="Start (HH:MM):").grid(column=1, row=0, padx=(5, 2))
    start_time_entry = ttk.Entry(avoid_times_frame, width=6)
    start_time_entry.grid(column=2, row=0, padx=(0, 10))

    ttk.Label(avoid_times_frame, text="End (HH:MM):").grid(column=3, row=0, padx=(5, 2))
    end_time_entry = ttk.Entry(avoid_times_frame, width=6)
    end_time_entry.grid(column=4, row=0, padx=(0, 10))

    ttk.Button(avoid_times_frame, text="Add Time", command=add_avoid_time).grid(column=5, row=0, padx=5)
    ttk.Button(avoid_times_frame, text="Remove Selected", command=remove_selected_avoid_time).grid(column=6, row=0, padx=5)

    avoid_times_listbox = tk.Listbox(frm, width=100, height=5)
    avoid_times_listbox.grid(column=0, row=10, columnspan=7, pady=5, sticky="w")

    ttk.Button(frm, text="Generate", command=generate_slots).grid(column=0, row=11, columnspan=7, pady=10)

    output_box = tk.Text(frm, width=80, height=12)
    output_box.grid(column=0, row=12, columnspan=7, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()