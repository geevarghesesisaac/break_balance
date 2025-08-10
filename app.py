from flask import Flask, render_template, request
import datetime
import os

app = Flask(__name__)

TOTAL_BREAK_MINUTES = 60

SHIFT_OPTIONS = {
    "Shift 1 (12:30 PM - 10:00 PM)": {"start_hour": 12, "start_minute": 30},
    "Shift 2 (1:00 PM - 10:30 PM)": {"start_hour": 13, "start_minute": 0}
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        worked_time = request.form.get("worked_time", "").strip()
        shift_name = request.form.get("shift", list(SHIFT_OPTIONS.keys())[0])

        try:
            worked_hours, worked_minutes = map(int, worked_time.split(":"))
            worked_delta = datetime.timedelta(hours=worked_hours, minutes=worked_minutes)

            now = datetime.datetime.now()
            shift_time = SHIFT_OPTIONS[shift_name]
            shift_start = now.replace(hour=shift_time["start_hour"], minute=shift_time["start_minute"], second=0, microsecond=0)

            if now < shift_start:
                result = f"❌ Shift hasn't started yet ({shift_name})."
            else:
                elapsed_time = now - shift_start
                break_taken = elapsed_time - worked_delta
                break_taken_minutes = int(break_taken.total_seconds() // 60)
                break_left = TOTAL_BREAK_MINUTES - break_taken_minutes

                if break_left >= 0:
                    result = f"✅ Break Taken: {break_taken_minutes} min | Break Left: {break_left} min"
                else:
                    result = f"❌ Break Taken: {break_taken_minutes} min | Overused by: {abs(break_left)} min"
        except ValueError:
            result = "❌ Please enter worked time in HH:MM format."

    return render_template("index.html", shifts=SHIFT_OPTIONS.keys(), result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
