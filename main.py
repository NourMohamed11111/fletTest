# main.py — IoT Dashboard as a phone-native-feeling app (Flet)
#
# Desktop preview:  python main.py
# Android build:    flet build apk        (produces build/apk/app-release.apk)
# iOS build:        flet build ipa
#
# The old version streamed the whole page as one long web-style column.
# This version gives it real mobile-app structure instead:
#   - a top AppBar (like a native title bar)
#   - a bottom NavigationBar to switch screens (Dashboard / Control)
#   - page.adaptive=True so controls render as Material on Android and
#     Cupertino-style on iOS automatically
#   - SafeArea so content doesn't sit under phone notches/status bars

import threading
import flet as ft
from firebase_service import stream_sensors, stream_events, stream_pump, send_motor_command

# ---- shared UI refs, filled in once the page is built ----
temp_text = hum_text = light_text = motion_text = pump_text = None
speed_slider = None


CARD_BGCOLOR = "#0Fffffff"     # white @ ~6% opacity, as an #aarrggbb hex literal
CARD_BORDER_COLOR = "#1Affffff"  # white @ ~10% opacity


def sensor_card(label: str, value_ctrl: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column([ft.Text(label, size=12, color=ft.Colors.WHITE54), value_ctrl], spacing=6),
        padding=16,
        bgcolor=CARD_BGCOLOR,
        border_radius=14,
        border=ft.Border.all(1, CARD_BORDER_COLOR),
        expand=True,
    )


def build_dashboard_view() -> ft.Control:
    global temp_text, hum_text, light_text, motion_text, pump_text
    temp_text = ft.Text("-- °C", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)
    hum_text = ft.Text("-- %", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)
    light_text = ft.Text("-- %", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_300)
    motion_text = ft.Text("--", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70)
    pump_text = ft.Text("--", size=14, color=ft.Colors.WHITE60)

    return ft.Column(
        [
            ft.ResponsiveRow(
                [
                    ft.Container(sensor_card("Temperature", temp_text), col=6),
                    ft.Container(sensor_card("Humidity", hum_text), col=6),
                ],
                spacing=12,
                run_spacing=12,
            ),
            ft.ResponsiveRow(
                [
                    ft.Container(sensor_card("Light Level", light_text), col=6),
                    ft.Container(sensor_card("Motion", motion_text), col=6),
                ],
                spacing=12,
                run_spacing=12,
            ),
            ft.Container(
                content=ft.Column(
                    [ft.Text("Pump (raw — confirm fields once expanded)", size=12, color=ft.Colors.WHITE54), pump_text],
                    spacing=6,
                ),
                padding=16,
                bgcolor=CARD_BGCOLOR,
                border_radius=14,
                border=ft.Border.all(1, CARD_BORDER_COLOR),
            ),
        ],
        spacing=12,
    )


def build_control_view(page: ft.Page) -> ft.Control:
    global speed_slider
    speed_slider = ft.Slider(min=0, max=100, value=50, divisions=20, label="{value}%", active_color=ft.Colors.BLUE_400)

    def send(direction: str):
        speed = 0 if direction == "stop" else int(speed_slider.value)
        send_motor_command(speed, direction)
        page.show_dialog(ft.SnackBar(ft.Text(f"Sent: {direction} @ {speed}%")))

    return ft.Column(
        [
            ft.Text("Motor Control", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Speed", size=13, color=ft.Colors.WHITE70),
            speed_slider,
            ft.Row(
                [
                    ft.ElevatedButton("Forward", icon=ft.Icons.ARROW_UPWARD, bgcolor=ft.Colors.BLUE_700,
                                       on_click=lambda e: send("forward"), expand=True),
                    ft.ElevatedButton("Stop", icon=ft.Icons.STOP, bgcolor=ft.Colors.RED_700,
                                       on_click=lambda e: send("stop"), expand=True),
                    ft.ElevatedButton("Reverse", icon=ft.Icons.ARROW_DOWNWARD, bgcolor=ft.Colors.BLUE_700,
                                       on_click=lambda e: send("reverse"), expand=True),
                ],
                spacing=8,
            ),
        ],
        spacing=16,
    )


def main(page: ft.Page):
    page.title = "IoT Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F1117"
    page.adaptive = True  # native-feeling controls per platform
    page.padding = 0

    dashboard_view = build_dashboard_view()
    control_view = build_control_view(page)
    body = ft.Container(content=dashboard_view, padding=16, expand=True)

    def on_nav_change(e):
        body.content = dashboard_view if e.control.selected_index == 0 else control_view
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text("IoT Dashboard"),
        center_title=False,
        bgcolor="#0Affffff",  # white @ ~4% opacity
    )
    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationBarDestination(icon=ft.Icons.TUNE_OUTLINED, selected_icon=ft.Icons.TUNE, label="Control"),
        ],
    )

    page.add(ft.SafeArea(body, expand=True))

    # -------- live Firebase updates --------
    def on_sensors(data: dict):
        if "temperature" in data:
            temp_text.value = f"{data['temperature']:.1f} °C"
        if "humidity" in data:
            hum_text.value = f"{data['humidity']:.1f} %"
        if "light_pct" in data:
            light_text.value = f"{data['light_pct']} %"
        page.update()

    def on_events(data: dict):
        motion = data.get("last_motion")
        if motion is not None:
            is_detected = str(motion).upper() == "DETECTED"
            motion_text.value = "🔴 Motion!" if is_detected else "🟢 Clear"
            motion_text.color = ft.Colors.RED if is_detected else ft.Colors.GREEN
            page.update()

    def on_pump(data: dict):
        pump_text.value = str(data) if data else "no data yet"
        page.update()

    threading.Thread(target=lambda: stream_sensors(on_sensors), daemon=True).start()
    threading.Thread(target=lambda: stream_events(on_events), daemon=True).start()
    threading.Thread(target=lambda: stream_pump(on_pump), daemon=True).start()


ft.run(main)