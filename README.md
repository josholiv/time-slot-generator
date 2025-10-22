# time-slot-generator
Script to generate a list of random time slots with custom settings and restrictions

## Features
Generates random time slots on weekdays between defined start and end times
Adjustable slot duration and start time increments
Set to skip entire days or specific time ranges, if needed
Set number of days from current date to start list, if needed

## Configuration
Set your desired settings in the Config class:
```
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
```
## Example output:
```
Settings:
- Time slots: 10
- Duration: 2h 30m
- Generate between 9:00 and 16:30
- Increment: 30m
- Start 7 days from today
- Avoid entire days: none
- Avoid specific times: Mon 9:00 – 10:30, Tue 14:00 – 15:30

Monday, October 27, from 12:00 PM – 2:30 PM   
Wednesday, October 29, from 2:00 PM – 4:30 PM 
Thursday, October 30, from 9:30 AM – 12:00 PM 
Friday, October 31, from 1:30 PM – 4:00 PM    
Monday, November 3, from 10:30 AM – 1:00 PM   
Wednesday, November 5, from 11:00 AM – 1:30 PM
Thursday, November 6, from 1:00 PM – 3:30 PM  
Friday, November 7, from 1:00 PM – 3:30 PM    
Monday, November 10, from 12:30 PM – 3:00 PM  
Tuesday, November 11, from 10:30 AM – 1:00 PM
```
## Usage
Run the script directly:
```
python time-slot-generator.py
```
The script prints the configuration and generated time slots in the console.

# time-slot-generator-gui
A GUI version of time-slot-generator, which also has some extra features: 
- Generate times for any day of the week, not just weekdays
- Specify the maximum number of slots to be generated per day
- Can simply copy the generated list and paste elsewhere

<img width="715" height="671" alt="image" src="https://github.com/user-attachments/assets/a0cb486f-cec1-4cb5-afc0-cd8358a13588" />

## Usage
Run the script directly:
```
python time-slot-generator-gui.py
```
