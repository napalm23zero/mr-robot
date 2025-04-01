import pyautogui
import random
import time
import os
import threading
import math
from datetime import datetime
import keyboard  # only newbies uses a mouse

# ──────────────────────────────────────────────────────────────────────────────
#   _  _        _ __        _         ___  ____                    
#  | \| | __ _ | '_ \ __ _ | | _ __  |_  )|__ /  ___ ___  _ _  ___ 
#  | .  |/ _` || .__// _` || || '  \  / /  |_ \ |_ // -_)| '_|/ _ \
#  |_|\_|\__/_||_|   \__/_||_||_|_|_|/___||___/ /__|\___||_|  \___/
#
#  Made by: napalm23zero
#  Take a look at my playground: https://github.com/napalm23zero
#  Take a look at my other avater in a corporate work http://linkedin.com/in/dantas-rodrigo
#  Wanna talk? email me, like people used to to un the 90's rodrigo.dantas@hustletech.dev
#
# Who's the boss? -> Rodrigo Dantas
#
#  INSTALL FIRST:
#     - pip install pyautogui
#     - pip install keyboard
# ──────────────────────────────────────────────────────────────────────────────

# ───────────────────────────
#  YOU CONFIGURE, WE OBEY
# ───────────────────────────
DETECTION_THRESHOLD = 20                   # If you move the mouse too fast, we'll know
INACTIVITY_RESTART_TIME = 20               # Time (seconds) to chill before repeating
FOLDER_PATH = r"C:\Users\DarthVader\files" # Where your fake files live
FILE_EXTENSION = r".java"                  # We only mess with these
START_DELAY = 10                           # Seconds before the 1st wave of destruction

# Mouse movement config
MOUSE_MOVE_DURATION_MIN = 1
MOUSE_MOVE_DURATION_MAX = 1
REST_TIME_MIN = 0.5
REST_TIME_MAX = 2

# Typing config
TYPING_INTERVAL_MIN = 0.00         # Min typing speed in seconds
TYPING_INTERVAL_MAX = 0.02         # Max typing speed in seconds

# "Human error" config: chance to generate random typos while typing
TYPO_PROBABILITY = 0.03            # 3% chance of messing up
TYPO_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:,<.>/?\\|"

# Chance to pause typing after each file and do a figure-eight
INFINITY_MOVE_PROBABILITY = 0.3           # 30% chance
INFINITY_MOVE_DURATION = 30               # 30 seconds
INFINITY_MOVE_LOOPS = 2                   # Number of 'figure-8' loops during that duration
INFINITY_MOVE_RADIUS = 300                # Size of the loops

stop_event = threading.Event()
screen_width, screen_height = pyautogui.size()

def log(message):
    """Logs messages with timestamps, because every villain loves a monologue."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 {message}")

def read_and_cleanup_file(file_path):
    """
    Reads a file in binary mode, decodes as UTF-8 (replacing weird chars),
    and normalizes line endings to '\n'. Returns a list of lines.
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
    except Exception as e:
        log(f"⚠️ Error reading file {file_path}: {e}")
        return None

    # Decode as UTF-8, replacing problematic chars
    text = raw_data.decode('utf-8', 'replace')
    # Normalize line endings to '\n'
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    lines = text.split('\n')
    return lines

def type_with_typos_and_speed(char):
    """
    Potentially types a wrong character for comedic effect (typo),
    then backspaces it, then types the correct one.
    """
    if random.random() < TYPO_PROBABILITY and char != '\n':
        # Insert random wrong char
        wrong_char = random.choice(TYPO_CHARACTERS)
        pyautogui.write(wrong_char, interval=random.uniform(0.01, 0.05))

        # Wait as if we realized the mistake
        time.sleep(random.uniform(0.05, 0.3))

        # Press backspace to fix
        pyautogui.press('backspace')
        time.sleep(random.uniform(0.02, 0.1))

    # Now type the intended char at "human" speed
    pyautogui.write(char, interval=random.uniform(TYPING_INTERVAL_MIN, TYPING_INTERVAL_MAX))

def type_file_content(file_path):
    """
    Reads + cleans a file, then types it line-by-line:
      • For each line, we type characters with possible typos.
      • Press Enter at the end of each line.
    """
    lines = read_and_cleanup_file(file_path)
    if lines is None:
        return False  # Reading failed, skip

    log(f"📄 Gearing up to type: {file_path}")
    log(f"   Number of lines after cleanup: {len(lines)}")

    line_count = len(lines)
    for i, line in enumerate(lines, start=1):
        if stop_event.is_set():
            log("⏹️ Typing aborted mid-file because you got cold feet.")
            return False

        # Type each character in this line
        for char in line:
            if stop_event.is_set():
                return False
            type_with_typos_and_speed(char)

        # Press Enter to finish the line
        pyautogui.press('enter')
        log(f"   - Typed line {i}/{line_count}: '{line[:50]}'{'...' if len(line)>50 else ''}")
        time.sleep(random.uniform(0.02, 0.1))  # micro-pause

    log("🎉 Finished typing that entire file! On to the next bit of madness.")
    return True

def clear_editor():
    """Selects all in the editor (Ctrl + A) and Delete. Because we like a blank slate."""
    log("🧹 Clearing the editor now... (Ctrl + A, Delete)")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(random.uniform(0.2, 0.5))
    pyautogui.press('delete')
    time.sleep(random.uniform(0.5, 1))

def move_mouse_infinity(duration=30, loops=2, radius=300):
    """
    Moves the mouse in a smooth figure-eight pattern, centered on the screen.

    :param duration: total seconds to spend drawing the ∞ shape
    :param loops: how many times to trace a full figure-8
    :param radius: the 'size' of each loop
    """
    center_x = screen_width // 2
    center_y = screen_height // 2

    steps_per_loop = 200
    total_steps = steps_per_loop * loops

    log(f"✋ Starting figure-eight mouse movement for ~{duration}s, loops={loops}, radius={radius}.")

    start_time = time.time()
    for step in range(total_steps):
        if stop_event.is_set():
            return

        # Fraction of loop completed
        t = 2 * math.pi * (step % steps_per_loop) / steps_per_loop

        # Figure-eight param
        x_offset = math.sin(t) * radius
        y_offset = math.sin(t) * math.cos(t) * radius

        # Move to the new position
        pyautogui.moveTo(center_x + x_offset, center_y + y_offset)

        # If we've exceeded the intended duration, break
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break

        time.sleep(duration / total_steps)

    log("✋ Done with figure-eight mouse movement.")

def stop_script():
    """Stops the madness when 'Esc' is pressed. See you next time, boss."""
    log("🚫 'Esc' was pressed! Halting all chaos.")
    stop_event.set()
    time.sleep(1)
    log("🛑 All operations terminated gracefully. *sad robot noises*")

def process_files():
    """
    Finds all .java files in the folder, picks ONE at random, and types it.
    We'll also occasionally pause to do a figure-eight mouse move for ~30s.
    """
    log(f"🔍 Searching for files in: {FOLDER_PATH}")
    try:
        all_files = [
            f for f in os.listdir(FOLDER_PATH)
            if os.path.isfile(os.path.join(FOLDER_PATH, f))
            and f.lower().endswith(FILE_EXTENSION)
        ]
    except Exception as e:
        log(f"⚠️ Could not list files in {FOLDER_PATH}. Error: {e}")
        return False

    if not all_files:
        log(f"⚠️ No '{FILE_EXTENSION}' files found in {FOLDER_PATH}. Are we in the right lair?")
        return False

    # Instead of iterating over all files, pick just one random file
    file_name = random.choice(all_files)
    file_path = os.path.join(FOLDER_PATH, file_name)
    log(f"⌨️ Now targeting a single file: {file_name}")

    # Clear the editor first
    clear_editor()

    success = type_file_content(file_path)
    if not success:
        return False

    # Occasionally do a smooth figure-eight break after finishing
    if random.random() < INFINITY_MOVE_PROBABILITY and not stop_event.is_set():
        log("✋ Taking a short break for an infinity-shaped mouse move...")
        move_mouse_infinity(
            duration=INFINITY_MOVE_DURATION,
            loops=INFINITY_MOVE_LOOPS,
            radius=INFINITY_MOVE_RADIUS
        )

    # Wait a bit before the next "interaction" to look "human-ish"
    wait_time = random.uniform(2, 5)
    log(f"⏳ Done typing {file_name}. Resting for {wait_time:.2f}s before the next round.")
    time.sleep(wait_time)

    log("🎉 Finished typing one random file this round. A job well done!")
    return True

def main():
    """
    Launches the unstoppable loop:
      1. Waits START_DELAY seconds
      2. Clears stop_event
      3. Picks one .java file at random and types it
      4. Waits INACTIVITY_RESTART_TIME seconds
      5. Repeats forever (or until 'Esc' ends the party)
    """
    # Hook up 'esc' to stop everything
    keyboard.add_hotkey('esc', stop_script)

    while True:
        log(f"⏳ New mission begins in {START_DELAY}s. Grab coffee (or not)!")
        time.sleep(START_DELAY)

        stop_event.clear()

        # Process exactly ONE .java file
        try:
            process_files()
        except Exception as e:
            log(f"❌ Oops, an unhandled error occurred: {e}")

        if stop_event.is_set():
            log("⏹️ We were interrupted. Exiting main loop.")
            break

        log(f"🛑 Mission complete. Taking a {INACTIVITY_RESTART_TIME}s siesta. Then we do it all again!")
        time.sleep(INACTIVITY_RESTART_TIME)
        log("🔄 Alright, let's spin up a fresh round of chaos...")

if __name__ == "__main__":
    log("🚀 Script initiated! Prepare for unrelenting typed chaos.")
    main()
