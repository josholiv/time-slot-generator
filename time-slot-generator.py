from datetime import datetime, timedelta
import random

# ======================
# === CONFIGURATION ===
# ======================

# Settings
class Config:
    NUM_SLOTS = 10
    SLOT_DURATION = timedelta(hours=2, minutes=30)
    START_TIME = 9       # e.g., 9 = 9:00 AM, 9.5 = 9:30 AM
    END_TIME = 16.5        #e.g., 16.5 = 4:30 PM
    TIME_INCREMENT_MINUTES = 30  # increments for start times
    DAYS_FROM_TODAY = 7

    # Restrictions
    AVOID_DAYS = []  # 0=Mon ... 6=Sun
    # Format: {weekday_int: [(start_hour, end_hour), ...]}
    AVOID_TIMES = {
        0: [(9.0, 10.5)],
        1: [(14.0, 15.5)],
    }

# ======================
# === HELPER FUNCTIONS ===
# ======================

def overlaps_avoid_time(weekday, start_hour, end_hour, avoid_times):
    """Check if a slot overlaps with any restricted times for a given weekday."""
    if weekday not in avoid_times:
        return False
    for a_start, a_end in avoid_times[weekday]:
        if (start_hour < a_end) and (end_hour > a_start):
            return True
    return False

def format_hour(hour_float):
    """Convert decimal hour to HH:MM string."""
    hour = int(hour_float)
    minute = int((hour_float % 1) * 60)
    return f"{hour}:{minute:02d}"

def format_slot(date_obj, start_dt, end_dt):
    """Format a single time slot for printing."""
    date_str = date_obj.strftime("%A, %B %d").replace(" 0", " ")
    time_range = f"{start_dt.strftime('%I:%M %p').lstrip('0')} – {end_dt.strftime('%I:%M %p').lstrip('0')}"
    return f"{date_str}, from {time_range}"

# ======================
# === SLOT GENERATION ===
# ======================

def generate_time_slots(config: Config):
    """Generate a list of random time slots respecting restrictions."""
    slots = []
    start_date = (datetime.today() + timedelta(days=config.DAYS_FROM_TODAY)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    current_date = start_date
    weekdays = [0, 1, 2, 3, 4]  # Mon-Fri

    # Build valid start times in increments
    increment_hours = config.TIME_INCREMENT_MINUTES / 60
    valid_start_times = []
    t = config.START_TIME
    while t <= config.END_TIME - config.SLOT_DURATION.total_seconds()/3600:
        valid_start_times.append(t)
        t += increment_hours

    # Generate slots
    while len(slots) < config.NUM_SLOTS:
        if current_date.weekday() in weekdays and current_date.weekday() not in config.AVOID_DAYS:
            start_hour = random.choice(valid_start_times)
            end_hour = start_hour + config.SLOT_DURATION.total_seconds()/3600
            if overlaps_avoid_time(current_date.weekday(), start_hour, end_hour, config.AVOID_TIMES):
                current_date += timedelta(days=1)
                continue

            start_dt = current_date.replace(
                hour=int(start_hour),
                minute=int((start_hour % 1) * 60),
                second=0
            )
            end_dt = start_dt + config.SLOT_DURATION
            slots.append((current_date, start_dt, end_dt))

        current_date += timedelta(days=1)

    return slots[:config.NUM_SLOTS]

# ======================
# === PRINT FUNCTIONS ===
# ======================

def print_settings(config: Config):
    """Print configuration settings nicely."""
    total_seconds = int(config.SLOT_DURATION.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    days_in_future = config.DAYS_FROM_TODAY

    weekday_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    avoid_days_str = ", ".join([weekday_names[d] for d in config.AVOID_DAYS]) if config.AVOID_DAYS else "none"

    avoid_times_list = []
    for day, times in config.AVOID_TIMES.items():
        for start, end in times:
            avoid_times_list.append(f"{weekday_names[day]} {format_hour(start)} – {format_hour(end)}")
    avoid_times_str = ", ".join(avoid_times_list) if avoid_times_list else "none"

    print(f"\nRandomly generated time slots!\n"
          f"\nSettings:\n"
          f"- Time slots: {config.NUM_SLOTS}\n"
          f"- Duration: {hours}h {minutes}m\n"
          f"- Generate between {format_hour(config.START_TIME)} and {format_hour(config.END_TIME)}\n"
          f"- Increment: {config.TIME_INCREMENT_MINUTES}m\n"
          f"- Start {days_in_future} days from today\n"
          f"- Avoid entire days: {avoid_days_str}\n"
          f"- Avoid specific times: {avoid_times_str}\n")

def print_slots(slots):
    """Print the generated time slots without numbering."""
    for s in slots:
        print(f"{format_slot(*s)}")

# ======================
# === MAIN EXECUTION ===
# ======================

def main():
    config = Config()
    print_settings(config)
    slots = generate_time_slots(config)
    print_slots(slots)

if __name__ == "__main__":
    main()
