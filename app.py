from flask import Flask, render_template_string, request
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone

app = Flask(__name__)

# Constants
SHIFT_OPTIONS = {
    "Shift 1 (12:30 PM - 10:00 PM)": {"start_hour": 12, "start_minute": 30},
    "Shift 2 (1:00 PM - 10:30 PM)": {"start_hour": 13, "start_minute": 0}
}
TOTAL_BREAK_MINUTES = 60

# HTML template (Bootstrap for style)
# ...existing code...
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Break Balance</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; padding-top: 50px; }
        .container { max-width: 450px; }
        .logo { width: 48px; margin-bottom: 10px; }
        .progress { height: 24px; }
        .footer { font-size: 0.9em; color: #888; margin-top: 30px; text-align: center; }
    </style>
</head>
<body>
<div class="container shadow p-4 rounded bg-white">
    <div class="text-center mb-3">
        <img src="https://cdn-icons-gif.flaticon.com/11186/11186847.gif" class="logo" alt="Break Balance">
        <h2 class="mb-1">Break Balance</h2>
        <div class="text-muted small mb-2">Check your break usage for today</div>
    </div>
    <div class="card mb-3">
        <div class="card-body">
            <form method="POST">
            <input type="hidden" name="timezone" id="timezone">
                <div class="mb-3">
                    <label class="form-label">Select Your Shift:</label>
                    <select name="shift" class="form-select" required>
                        {% for shift in shifts %}
                        <option value="{{ shift }}" {% if selected_shift == shift %}selected{% endif %}>{{ shift }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Worked Time <span data-bs-toggle="tooltip" title="Enter hours and minutes worked since shift start">(HH:MM)</span>:</label>
                    <input type="text" name="worked_time" class="form-control" placeholder="e.g. 04:50" required>
                </div>
                <button type="submit" class="btn btn-success w-100">Check Break</button>
            </form>
        </div>
    </div>
    {% if result %}
    <div class="card mt-3">
        <div class="card-body">
            <div class="alert alert-{{ 'success' if break_left >= 0 else 'danger' }} mb-3">
                {{ result }}
            </div>
            <div>
                <label class="form-label">Break Usage:</label>
                <div class="progress">
                    <div class="progress-bar {{ 'bg-success' if break_left >= 0 else 'bg-danger' }}" role="progressbar"
                        style="width: {{ (TOTAL_BREAK_MINUTES - break_left if break_left >= 0 else TOTAL_BREAK_MINUTES) / TOTAL_BREAK_MINUTES * 100 }}%"
                        aria-valuenow="{{ TOTAL_BREAK_MINUTES - break_left if break_left >= 0 else TOTAL_BREAK_MINUTES }}"
                        aria-valuemin="0" aria-valuemax="{{ TOTAL_BREAK_MINUTES }}">
                        {{ TOTAL_BREAK_MINUTES - break_left if break_left >= 0 else TOTAL_BREAK_MINUTES }} min
                    </div>
                </div>
                <div class="text-end small mt-1">Total allowed: {{ TOTAL_BREAK_MINUTES }} min</div>
            </div>
        </div>
    </div>
    {% endif %}
    <div class="footer">
        &copy; 2025 Break Balance | Made with ♥️ using Flask & Bootstrap
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    })
</script>
<script>
    // Set user's timezone in hidden input
    document.addEventListener("DOMContentLoaded", function() {
        var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.getElementById("timezone").value = tz;
    });

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    })
</script>
</body>
</html>
"""
# ...existing code...


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

            if now < shift_start:
                result = f"❌ Shift hasn't started yet (starts at {selected_shift[-14:]})."
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
            result = "⚠ Please enter worked time in HH:MM format (e.g., 04:50)"
            break_left = 0

    return render_template_string(HTML, shifts=SHIFT_OPTIONS.keys(), result=result, selected_shift=selected_shift, break_left=break_left, TOTAL_BREAK_MINUTES=TOTAL_BREAK_MINUTES, selected_tz=selected_tz)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
