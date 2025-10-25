from flask import Flask, render_template, request
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone

app = Flask(__name__)

# Constants
SHIFT_OPTIONS = {
    "Shift 1 (12:30 PM - 10:00 PM)": {"start_hour": 12, "start_minute": 30},
    "Shift 2 (1:00 PM - 10:30 PM)": {"start_hour": 13, "start_minute": 0},
    "Shift 3 (4:30 PM - 2:00 AM)": {"start_hour": 16, "start_minute": 30, "overnight": True}
}
TOTAL_BREAK_MINUTES = 60

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    break_left = None
    selected_shift = list(SHIFT_OPTIONS.keys())[0]
    selected_tz = "Asia/Kolkata"

    if request.method == "POST":
        worked_time = request.form.get("worked_time", "").strip()
        selected_shift = request.form.get("shift")
        selected_tz = request.form.get("timezone", "Asia/Kolkata")
        try:
            worked_hours, worked_minutes = map(int, worked_time.split(":"))
            worked_delta = timedelta(hours=worked_hours, minutes=worked_minutes)

            tz = pytz_timezone(selected_tz)
            now = datetime.now(tz)
            shift_time = SHIFT_OPTIONS[selected_shift]
            shift_start = now.replace(
                hour=shift_time["start_hour"],
                minute=shift_time["start_minute"],
                second=0,
                microsecond=0
            )

            # Handle overnight shift (e.g., Shift 3 goes past midnight)
            if "overnight" in shift_time and shift_time["overnight"]:
                if now.hour < shift_time["start_hour"]:
                    shift_start -= timedelta(days=1)

            if now < shift_start:
                result = f"⚠️ Selected shift hasn't started yet!"
                break_left = 0
            else:
                elapsed_time = now - shift_start
                break_taken = elapsed_time - worked_delta
                break_taken_minutes = int(break_taken.total_seconds() // 60)
                break_left = TOTAL_BREAK_MINUTES - break_taken_minutes

                if break_left >= 0:
                    result = f"✅ Break Taken: {break_taken_minutes} min | ✅ Break Left: {break_left} min"
                else:
                    result = f"❌ Break Taken: {break_taken_minutes} min | ❌ Overused by: {abs(break_left)} min"

        except ValueError:
            result = "Please enter worked time in HH:MM format (e.g., 04:50)"
            break_left = 0

    # return render_template_string(HTML, shifts=SHIFT_OPTIONS.keys(), result=result, selected_shift=selected_shift, break_left=break_left, TOTAL_BREAK_MINUTES=TOTAL_BREAK_MINUTES, selected_tz=selected_tz)
    return render_template(
        "index.html",
        shifts=SHIFT_OPTIONS.keys(),
        result=result,
        selected_shift=selected_shift,
        break_left=break_left,
        TOTAL_BREAK_MINUTES=TOTAL_BREAK_MINUTES,
        selected_tz=selected_tz
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
