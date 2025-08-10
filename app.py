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
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Break Balance</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; padding-top: 50px; }
        .container { max-width: 450px; }
        .logo { width: 48px; margin-bottom: 10px; border-radius: 50%; }
        .progress { height: 24px; }
        .progress-bar { transition: width 1s cubic-bezier(.4,0,.2,1); }
        .footer { font-size: 0.9em; color: #888; margin-top: 30px; text-align: center; }
        body.dark-mode {
            background: #181a1b !important;
            color: #f8f9fa !important;
        }
        body.dark-mode .container {
            background: #23272b !important;
            color: #f8f9fa !important;
        }
        body.dark-mode .card {
            background: #23272b !important;
            color: #f8f9fa !important;
        }
        body.dark-mode .form-control,
        body.dark-mode .form-select {
            background: #181a1b !important;
            color: #f8f9fa !important;
            border-color: #444 !important;
        }
        body.dark-mode .footer {
            color: #aaa !important;
        }
        body.dark-mode .text-muted {
            color: #b0b0b0 !important;
        }
        body.dark-mode .form-text {
            color: #b0b0b0 !important;
        }
        .btn-check-break {
            background: #1976d2 !important;      /* Blue */
            border-color: #1976d2 !important;
            color: #fff !important;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
            transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
        }
        .btn-check-break:hover, .btn-check-break:focus {
            background: #1565c0 !important;      /* Darker blue on hover */
            border-color: #1565c0 !important;
            box-shadow: 0 4px 16px rgba(25, 118, 210, 0.18);
            transform: translateY(-2px) scale(1.03);
        }
        body.dark-mode .btn-check-break {
            background: #1565c0 !important;
            border-color: #1565c0 !important;
            color: #fff !important;
        }
        body.dark-mode .btn-check-break:hover, body.dark-mode .btn-check-break:focus {
            background: #1976d2 !important;
            border-color: #1976d2 !important;
        }
    </style>
</head>
<body>
<div class="container shadow p-4 rounded bg-white">
    <div class="text-center mb-3">
        <img src="https://cdn-icons-gif.flaticon.com/11186/11186847.gif" class="logo" alt="Break Balance">
        <h2 class="mb-1">Break Balance</h2>
        <div class="text-muted small mb-2">Healthy Breaks, Productive You...</div>
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
                <button type="submit" class="btn btn-check-break w-100">Check Break</button>
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
                        <div class="progress-bar progress-bar-striped progress-bar-animated {{ 'bg-success' if break_left >= 0 else 'bg-danger' }}" role="progressbar"
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
<!-- Theme Toggle Button -->
<button id="theme-toggle" aria-label="Toggle theme"
    style="position:fixed;bottom:30px;right:30px;z-index:100;width:45px;height:45px;border-radius:50%;border:1px solid #222;background:#f8f9fa;color:#222;display:grid;place-items:center;">
    <!-- Sun Icon -->
    <svg id="sun-icon" xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="none" viewBox="0 0 30 30">
        <circle cx="15" cy="15" r="6" stroke="currentColor" stroke-width="2"/>
        <path d="M15 1.25V3.75M15 26.25V28.75M5.27 5.27L7.05 7.05M22.95 22.95L24.72 24.72M1.25 15H3.75M26.25 15H28.75M5.27 24.72L7.05 22.95M22.95 7.05L24.72 5.27" stroke="currentColor" stroke-width="2"/>
    </svg>
    <!-- Moon Icon (hidden by default) -->
    <svg id="moon-icon" xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 26 26" style="display:none;">
        <path d="M22.08 13.45c-.17 1.79-.84 3.5-1.94 4.92-1.1 1.42-2.58 2.5-4.27 3.11-1.69.61-3.52.73-5.27.32-1.75-.41-3.36-1.29-4.61-2.56-1.25-1.27-2.13-2.88-2.52-4.64-.39-1.76-.27-3.59.34-5.28.61-1.69 1.7-3.17 3.12-4.27C8.29 3.99 9.99 3.32 11.79 3.16c-1.05 1.42-1.56 3.19-1.43 4.98.13 1.79.89 3.45 2.14 4.7 1.25 1.25 2.91 2.01 4.7 2.14 1.79.13 3.56-.38 4.98-1.43z" stroke="currentColor" stroke-width="2"/>
    </svg>
</button>
<script>
document.getElementById('theme-toggle').onclick = function() {
    document.body.classList.toggle('dark-mode');
    // Toggle icons
    let sun = document.getElementById('sun-icon');
    let moon = document.getElementById('moon-icon');
    if(document.body.classList.contains('dark-mode')) {
        sun.style.display = 'none';
        moon.style.display = 'block';
    } else {
        sun.style.display = 'block';
        moon.style.display = 'none';
    }
};
</script>
<script>
    // Save selected shift to cookie on change
    document.addEventListener("DOMContentLoaded", function() {
        var shiftSelect = document.querySelector('select[name="shift"]');
        if (shiftSelect) {
            // Restore from cookie
            var lastShift = document.cookie.replace(/(?:(?:^|.*;\s*)selected_shift\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            if (lastShift) {
                for (var i = 0; i < shiftSelect.options.length; i++) {
                    if (shiftSelect.options[i].value === lastShift) {
                        shiftSelect.selectedIndex = i;
                        break;
                    }
                }
            }
            // Save to cookie on change
            shiftSelect.onchange = function() {
                document.cookie = "selected_shift=" + encodeURIComponent(this.value) + ";path=/";
            };
        }
    });
</script>
</body>
</html>
"""


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
