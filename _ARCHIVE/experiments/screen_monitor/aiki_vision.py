#!/usr/bin/env python3
"""
AIKI Vision Monitor - Live Screen & Window Tracking
Kontinuerlig monitorering av skjerm og vinduer for AIKI-systemet
"""

import time
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image

# Config
SCREENSHOT_INTERVAL = 5  # sekunder mellom hver capture
SCREENSHOTS_DIR = Path.home() / "aiki" / "screen_monitor" / "screenshots"
WINDOW_LOG = Path.home() / "aiki" / "screen_monitor" / "window_activity.jsonl"
LATEST_SCREENSHOT = Path.home() / "aiki" / "screen_monitor" / "latest.png"
MAX_SCREENSHOTS = 100  # Behold kun siste 100 screenshots

# Opprett directories
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def get_active_window():
    """Hent informasjon om aktivt vindu (Wayland/X11)"""
    try:
        # Prøv Wayland først (GNOME)
        result = subprocess.run(
            ['gdbus', 'call', '--session', '--dest', 'org.gnome.Shell',
             '--object-path', '/org/gnome/Shell', '--method',
             'org.gnome.Shell.Eval', 'global.get_window_actors()[0].meta_window.get_wm_class()'],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            # Parse output
            output = result.stdout.strip()
            if "'" in output:
                return output.split("'")[1]
    except Exception:
        pass

    try:
        # Fallback: xdotool (X11)
        result = subprocess.run(
            ['xdotool', 'getactivewindow', 'getwindowname'],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return "Unknown"

def get_window_list():
    """Hent liste over alle åpne vinduer"""
    windows = []
    try:
        # GNOME/Wayland
        result = subprocess.run(
            ['wmctrl', '-l'],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        windows.append(parts[3])
    except Exception:
        pass

    return windows

def capture_screenshot():
    """Ta skjermbilde av hele skjermen"""
    timestamp = datetime.now()

    # Lagre som PNG
    filename = f"screen_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    filepath = SCREENSHOTS_DIR / filename

    screenshot_taken = False

    # Prøv ImageMagick import først (raskest og mest pålitelig)
    try:
        subprocess.run(
            ['import', '-window', 'root', str(filepath)],
            capture_output=True,
            timeout=5,
            check=True
        )
        screenshot_taken = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback: gnome-screenshot (system)
    if not screenshot_taken:
        try:
            subprocess.run(
                ['gnome-screenshot', '-f', str(filepath)],
                capture_output=True,
                timeout=5,
                check=True
            )
            screenshot_taken = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback: Flatpak GNOME Screenshot
    if not screenshot_taken:
        try:
            subprocess.run(
                ['flatpak', 'run', 'org.gnome.Screenshot', '-f', str(filepath)],
                capture_output=True,
                timeout=10,
                check=True
            )
            screenshot_taken = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

    if not screenshot_taken:
        print(f"⚠️  Screenshot feilet - ingen screenshot-verktøy tilgjengelig")
        return None, timestamp

    # Kopier til latest.png
    try:
        subprocess.run(['cp', str(filepath), str(LATEST_SCREENSHOT)], check=True)
    except subprocess.CalledProcessError:
        pass

    return str(filepath), timestamp

def cleanup_old_screenshots():
    """Slett gamle screenshots, behold kun siste MAX_SCREENSHOTS"""
    screenshots = sorted(SCREENSHOTS_DIR.glob("screen_*.png"))
    if len(screenshots) > MAX_SCREENSHOTS:
        for old_screenshot in screenshots[:-MAX_SCREENSHOTS]:
            old_screenshot.unlink()

def log_activity(screenshot_path, active_window, window_list):
    """Logg aktivitet til JSONL fil"""
    activity = {
        "timestamp": datetime.now().isoformat(),
        "screenshot": screenshot_path,
        "active_window": active_window,
        "open_windows": window_list,
        "window_count": len(window_list)
    }

    with open(WINDOW_LOG, 'a') as f:
        f.write(json.dumps(activity) + '\n')

def main():
    """Hovedloop for AIKI Vision Monitor"""
    print("🔴 AIKI Vision Monitor startet")
    print(f"📸 Screenshots lagres i: {SCREENSHOTS_DIR}")
    print(f"📝 Aktivitetslogg: {WINDOW_LOG}")
    print(f"⏱️  Intervall: {SCREENSHOT_INTERVAL} sekunder")
    print(f"👁️  Siste screenshot alltid tilgjengelig på: {LATEST_SCREENSHOT}")
    print("\nTrykk Ctrl+C for å stoppe\n")

    try:
        while True:
            # Hent info
            active_window = get_active_window()
            window_list = get_window_list()

            # Ta screenshot
            screenshot_path, timestamp = capture_screenshot()

            if screenshot_path is None:
                print(f"[{timestamp.strftime('%H:%M:%S')}] ⚠️  Screenshot feilet, prøver igjen...")
                time.sleep(SCREENSHOT_INTERVAL)
                continue

            # Logg aktivitet
            log_activity(screenshot_path, active_window, window_list)

            # Cleanup
            cleanup_old_screenshots()

            # Status output
            print(f"[{timestamp.strftime('%H:%M:%S')}] 📸 Screenshot tatt | "
                  f"🪟 Aktiv: {active_window[:50]} | "
                  f"Totalt: {len(window_list)} vinduer")

            # Vent til neste capture
            time.sleep(SCREENSHOT_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n🔴 AIKI Vision Monitor stoppet")

if __name__ == "__main__":
    main()
