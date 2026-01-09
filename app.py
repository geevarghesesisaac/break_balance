from flask import Flask, render_template, request
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone

app = Flask(__name__)

# Constants
SHIFT_OPTIONS = {
    "Shift 1 (9:00 AM - 6:00 PM)": {
        "start": (9, 0),
        "end": (18, 0),
        "break_minutes": 30
    },
    "Shift 2 (10:00 AM - 7:00 PM)": {
        "start": (10, 0),
        "end": (19, 0),
        "break_minutes": 30
    },
    "Shift 3 (12:30 PM - 10:00 PM)": {
        "start": (12, 30),
        "end": (22, 0),
        "break_minutes": 60
    },
    "Shift 4 (1:00 PM - 10:30 PM)": {
        "start": (13, 0),
        "end": (22, 30),
        "break_minutes": 60
    },
    "Shift 5 (2:30 PM - 12:00 AM)": {
        "start": (14, 30),
        "end": (0, 0),
        "break_minutes": 60,
        "overnight": True
    },
    "Shift 6 (4:30 PM - 2:00 AM)": {
        "start": (16, 30),
        "end": (2, 0),
        "break_minutes": 60,
        "overnight": True
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    break_left = None
    selected_shift = list(SHIFT_OPTIONS.keys())[0]
    break_minutes = SHIFT_OPTIONS[selected_shift]["break_minutes"]
    selected_tz = "Asia/Kolkata"

    if request.method == "POST":
        worked_time = request.form.get("worked_time", "").strip()
        selected_shift = request.form.get("shift")
        break_minutes = SHIFT_OPTIONS[selected_shift]["break_minutes"]
        selected_tz = request.form.get("timezone", "Asia/Kolkata")
        try:
            worked_hours, worked_minutes = map(int, worked_time.split(":"))
            worked_delta = timedelta(hours=worked_hours, minutes=worked_minutes)

            tz = pytz_timezone(selected_tz)
            now = datetime.now(tz)
            shift_time = SHIFT_OPTIONS[selected_shift]
            start_hour, start_minute = shift_time["start"]
            end_hour, end_minute = shift_time["end"]

            shift_start = now.replace(
                hour=start_hour,
                minute=start_minute,
                second=0,
                microsecond=0
            )

            shift_end = now.replace(
                hour=end_hour,
                minute=end_minute,
                second=0,
                microsecond=0
            )

            # Handle overnight shifts (Shift 5 & Shift 6)
            if shift_time.get("overnight"):
                if now.hour < start_hour:
                    shift_start -= timedelta(days=1)
                shift_end += timedelta(days=1)

            if now < shift_start:
                result = "⚠️ Selected shift has not started yet"
                break_left = break_minutes

            elif now > shift_end:
                result = "⚠️ Shift has already ended"
                break_left = 0


            else:
                elapsed_time = now - shift_start
                break_taken = elapsed_time - worked_delta
                break_taken_minutes = max(0, int(break_taken.total_seconds() // 60))
                break_left = break_minutes - break_taken_minutes


                if break_left >= 0:
                    result = f"✅ Break Taken: {break_taken_minutes} min | ✅ Break Left: {break_left} min"
                else:
                    result = f"❌ Break Taken: {break_taken_minutes} min | ❌ Overused by: {abs(break_left)} min"

        except ValueError:
            result = "Please enter worked time in HH:MM format (e.g., 04:50)"
            break_left = break_minutes

    # return render_template_string(HTML, shifts=SHIFT_OPTIONS.keys(), result=result, selected_shift=selected_shift, break_left=break_left, TOTAL_BREAK_MINUTES=TOTAL_BREAK_MINUTES, selected_tz=selected_tz)
    return render_template(
        "index.html",
        shifts=SHIFT_OPTIONS.keys(),
        result=result,
        selected_shift=selected_shift,
        break_left=break_left,
        break_minutes=break_minutes,
        selected_tz=selected_tz
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
