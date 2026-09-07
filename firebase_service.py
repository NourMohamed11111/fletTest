# firebase_service.py — talks to the real "maker-day-18" Realtime Database.
#
# Actual DB shape (from the console screenshot):
#   commands/
#       motor_dir:   "stop" | "forward" | "reverse"
#       motor_speed: 0-255            (PWM value, NOT a percentage)
#   events/
#       last_motion: "DETECTED" | "CLEAR" (or similar)
#   pump/
#       (structure not visible yet — collapsed in the screenshot)
#   sensors/
#       humidity:    number
#       light_pct:   number
#       temperature: number
#
# pip install pyrebase4

import pyrebase

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyD_iD1fVScQRbRwXdm4n-oGWybuS8gQsBA",
    "authDomain": "maker-day-18.firebaseapp.com",
    "databaseURL": "https://maker-day-18-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "maker-day-18",
    "storageBucket": "maker-day-18.firebasestorage.app",
    "messagingSenderId": "647559041884",
    "appId": "1:647559041884:web:66a6af9bd3e66ac64ca799",
}

_firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
db = _firebase.database()


def _make_merging_handler(on_change):
    """
    pyrebase's .stream() fires once per changed key, not once with the whole
    node every time. This keeps a local copy of the node and merges each
    event into it, so `on_change` always receives the full up-to-date dict.
    """
    state = {}

    def handler(message):
        path = message.get("path", "/")
        data = message.get("data")
        if path == "/":
            if isinstance(data, dict):
                state.clear()
                state.update(data)
        else:
            state[path.lstrip("/")] = data
        on_change(dict(state))

    return handler


def stream_sensors(on_change):
    """Streams /sensors — on_change(dict) gets humidity, light_pct, temperature."""
    return db.child("sensors").stream(_make_merging_handler(on_change))


def stream_events(on_change):
    """Streams /events — on_change(dict) gets last_motion."""
    return db.child("events").stream(_make_merging_handler(on_change))


def stream_pump(on_change):
    """Streams /pump raw, since its field names aren't confirmed yet."""
    return db.child("pump").stream(_make_merging_handler(on_change))


def send_motor_command(speed_pct: int, direction: str):
    """speed_pct is 0-100 from the UI slider; the ESP32 expects 0-255 PWM."""
    pwm = round(speed_pct * 255 / 100)
    db.child("commands").update({"motor_dir": direction, "motor_speed": pwm})
