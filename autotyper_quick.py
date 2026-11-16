"""
GhostType Quick - Background Hotkey Listener (Anti-ZigZag Edition)
Specially engineered for online coding contests (IEEEXtreme, CS Academy, HackerRank, Monaco).

Fixes the "Zig-Zag / Staircase" bug by compensating for the online editor's auto-indentation.

Workflow:
  1. Copy your code from Gemini / ChatGPT (Ctrl + C).
  2. Click your cursor inside the contest code editor.
  3. Press F8 on your keyboard.
  4. Wait 2 seconds (audio beeps will alert you).
  5. It types out the code with PERFECT indentation!
  6. Press ESC anytime to abort immediately.
"""

import time
import winsound
import threading
import pyperclip
from pynput.keyboard import Controller, Key, Listener

keyboard = Controller()
is_typing = False
stop_requested = False

# Configuration defaults
CHAR_DELAY = 0.008           # 8ms per character (fast & reliable)
COUNTDOWN_SECONDS = 2        # 2 seconds countdown before typing begins
ANTI_ZIGZAG_ENABLED = True   # Automatically compensates for editor auto-indentation
EXPAND_TABS = True           # Convert tabs to 4 spaces for uniform indentation
TAB_SIZE = 4

def play_tone(freq, dur_ms):
    try:
        winsound.Beep(freq, dur_ms)
    except Exception:
        pass

def clean_code_text(text):
    """Strips markdown fences and normalizes line endings and tabs."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # Strip markdown code blocks like ```python or ```cpp
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    processed = []
    for line in lines:
        if EXPAND_TABS:
            line = line.expandtabs(TAB_SIZE)
        processed.append(line)
        
    return processed

def type_worker(raw_text):
    global is_typing, stop_requested
    is_typing = True
    stop_requested = False

    print(f"\n[HOTKEY F8] Detected! Starting in {COUNTDOWN_SECONDS}s... Click your editor target!")
    
    # Countdown
    for i in range(COUNTDOWN_SECONDS, 0, -1):
        if stop_requested:
            print("[CANCELLED] Aborted by user.")
            is_typing = False
            return
        print(f" -> Typing in {i}...")
        play_tone(900, 100)
        time.sleep(0.9)

    if stop_requested:
        print("[CANCELLED] Aborted before typing.")
        is_typing = False
        return

    play_tone(1500, 150)
    print(" -> [TYPING NOW...] Anti-ZigZag Active. Press ESC to abort!")

    lines = clean_code_text(raw_text)
    total_lines = len(lines)
    start_time = time.time()
    chars_typed = 0

    editor_indent = 0 # Tracks the editor's cursor indentation column

    for idx, raw_line in enumerate(lines):
        if stop_requested:
            print(f"\n[STOPPED] Emergency stop triggered at line {idx+1}/{total_lines}.")
            play_tone(400, 250)
            is_typing = False
            return

        line = raw_line.rstrip()
        stripped = line.lstrip(" ")
        target_indent = len(line) - len(stripped)

        if idx == 0:
            # First line: type normally
            chars_to_type = line
            editor_indent = target_indent
        else:
            # Send Enter
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            time.sleep(CHAR_DELAY * 2.5)

            if ANTI_ZIGZAG_ENABLED:
                # Calculate what indentation the web editor automatically gave us
                prev_line = lines[idx - 1].rstrip()
                expected_indent = editor_indent
                
                # In Ace / Monaco: Enter auto-indents after colon or open brace
                if prev_line.endswith(":") or prev_line.endswith("{") or prev_line.endswith("("):
                    expected_indent += TAB_SIZE

                diff = target_indent - expected_indent

                if diff > 0:
                    # Editor gave too little indentation -> add remaining spaces
                    keyboard.type(" " * diff)
                    time.sleep(CHAR_DELAY)
                elif diff < 0:
                    # Editor gave too much indentation -> send backspaces to un-indent
                    num_backspaces = abs(diff)
                    for _ in range(num_backspaces):
                        if stop_requested:
                            is_typing = False
                            return
                        keyboard.press(Key.backspace)
                        keyboard.release(Key.backspace)
                        time.sleep(CHAR_DELAY * 0.8)

                chars_to_type = stripped
                editor_indent = target_indent
            else:
                chars_to_type = line

        # Type the line content character by character
        for char in chars_to_type:
            if stop_requested:
                print(f"\n[STOPPED] Emergency stop triggered!")
                play_tone(400, 250)
                is_typing = False
                return
            keyboard.type(char)
            time.sleep(CHAR_DELAY)
            chars_typed += 1

        pct = int(((idx + 1) / total_lines) * 100)
        print(f"\rTyping progress: {pct}% (Line {idx+1}/{total_lines})", end="", flush=True)

    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Finished typing {total_lines} lines ({chars_typed} chars) in {elapsed:.1f}s.")
    play_tone(1200, 100)
    play_tone(1600, 150)
    is_typing = False

def trigger_typing():
    global is_typing
    if is_typing:
        print("\n[BUSY] Already typing! Press ESC to stop current job.")
        return

    try:
        content = pyperclip.paste()
    except Exception as e:
        print(f"\n[ERROR] Could not read clipboard: {e}")
        return

    if not content or not content.strip():
        print("\n[WARNING] Clipboard is empty! Copy some code first (Ctrl + C).")
        play_tone(500, 150)
        return

    thread = threading.Thread(target=type_worker, args=(content,), daemon=True)
    thread.start()

def on_press(key):
    global stop_requested
    try:
        if key == Key.f8:
            trigger_typing()
        elif key == Key.esc:
            if is_typing:
                stop_requested = True
    except Exception:
        pass

def main():
    print("=" * 68)
    print("   👻 GhostType Quick (Anti-ZigZag Edition) - IEEEXtreme")
    print("=" * 68)
    print(" [FEATURES]")
    print("   ✔ Anti-ZigZag Active (Automatically compensates for auto-indent)")
    print("   ✔ Auto-strips markdown backticks (```python / ```cpp)")
    print("   ✔ Converts tabs to 4 spaces")
    print("-" * 68)
    print(" [HOTKEYS]")
    print("   • Press [ F8 ]  : Type current clipboard content")
    print("   • Press [ ESC ] : Emergency stop typing immediately")
    print("   • Press [Ctrl+C]: Quit this script")
    print("=" * 68)
    print("[LISTENING] Ready. Copy code from Gemini and press F8 in the editor...\n")

    listener = Listener(on_press=on_press)
    listener.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting AutoTyper Quick.")
        listener.stop()

if __name__ == "__main__":
    main()
