from __future__ import annotations

import threading
from datetime import datetime, timezone
from threading import Lock

from flask import Flask, jsonify, redirect, render_template, url_for

# Assuming validate.py is in the same directory.
# We import the validation functions and the slug cache to allow clearing it.
from validate import ALL_CHECKS, clear_caches

app = Flask(__name__)

# --- In-memory cache for validation results ---
validation_results = {
    "summary": {},
    "details": {},
    "last_run": None,
    "status": "Never run",  # Can be: Never run, Running, Finished
}
_RESULTS_LOCK = Lock()

def run_all_validations():
    """Runs all validation checks and updates the global results cache."""
    # Clear the file content cache from validate.py to ensure fresh data on each run
    clear_caches()

    summary = {}
    details = {}

    for name, func in ALL_CHECKS.items():
        try:
            if errors := func():
                summary[name] = "FAILED"
                details[name] = errors
            else:
                summary[name] = "PASSED"
        except Exception as e:
            summary[name] = "CRASHED"
            details[name] = [f"The check crashed with an unhandled exception: {e}"]

    with _RESULTS_LOCK:
        validation_results["summary"] = summary
        validation_results["details"] = details
        validation_results["last_run"] = datetime.now(timezone.utc)
        validation_results["status"] = "Finished"


@app.route("/")
def dashboard():
    """Renders the main dashboard page."""
    with _RESULTS_LOCK:
        # Pass a copy to the template to prevent race conditions during rendering
        current_results = validation_results.copy()
    return render_template("dashboard.html", results=current_results)


@app.route("/status")
def validation_status():
    """Returns the current validation status as JSON."""
    with _RESULTS_LOCK:
        status = validation_results["status"]
    return jsonify({"status": status})


@app.route("/run-validation")
def trigger_validation():
    """Triggers a new validation run in a background thread."""
    with _RESULTS_LOCK:
        if validation_results["status"] == "Running":
            # If a run is already in progress, do nothing and just redirect.
            return redirect(url_for("dashboard"))

        # Immediately update status to "Running" to prevent concurrent runs
        validation_results["status"] = "Running"
        validation_results["summary"] = {}  # Clear old results
        validation_results["details"] = {}

        # Run validation in a background thread to not block the request
        thread = threading.Thread(target=run_all_validations)
        # Daemon threads allow the main application to exit even if the thread is still running.
        thread.daemon = True
        thread.start()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    # For production, use a proper WSGI server like Gunicorn or Waitress.
    app.run(debug=True, port=5001)