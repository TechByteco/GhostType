"""
AutoTyper Pro - Competitive Programming Keyboard Simulator (Anti-ZigZag Edition)
Designed for coding competitions (e.g., IEEEXtreme, CS Academy, HackerRank).
Features smart indentation compensation to completely eliminate staircase / zig-zag formatting.
"""

import sys
import time
import threading
import winsound
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import pyperclip
from pynput.keyboard import Controller, Key, Listener

class AutoTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("👻 GhostType Pro - Anti-ZigZag Edition")
        self.root.geometry("640x740")
        self.root.minsize(580, 620)
        self.root.configure(bg="#1e1e2e")

        self.keyboard = Controller()
        self.is_typing = False
        self.stop_requested = False
        self.typing_thread = None
        self.global_listener = None

        self._setup_style()
        self._build_ui()
        self._start_global_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.bg_dark = "#181825"
        self.card_bg = "#1e1e2e"
        self.accent = "#89b4fa"
        self.success = "#a6e3a1"
        self.danger = "#f38ba8"
        self.warning = "#f9e2af"
        self.text_color = "#cdd6f4"
        self.text_dim = "#9399b2"

        style.configure("TFrame", background=self.card_bg)
        style.configure("TLabel", background=self.card_bg, foreground=self.text_color, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.card_bg, foreground=self.accent, font=("Segoe UI", 14, "bold"))
        style.configure("Sub.TLabel", background=self.card_bg, foreground=self.text_dim, font=("Segoe UI", 9))

    def _build_ui(self):
        main_container = tk.Frame(self.root, bg=self.card_bg, padx=16, pady=12)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header Section
        header_frame = tk.Frame(main_container, bg=self.card_bg)
        header_frame.pack(fill=tk.X, pady=(0, 8))

        title_lbl = ttk.Label(header_frame, text="👻 GhostType Pro", style="Header.TLabel")
        title_lbl.pack(anchor=tk.W)

        sub_lbl = ttk.Label(
            header_frame, 
            text="Simulate realistic keystrokes • Anti-ZigZag active • Press F8 to start, ESC to abort",
            style="Sub.TLabel"
        )
        sub_lbl.pack(anchor=tk.W)

        # Toolbar Frame
        toolbar = tk.Frame(main_container, bg=self.card_bg)
        toolbar.pack(fill=tk.X, pady=(0, 8))

        btn_paste = tk.Button(
            toolbar, text="📋 Paste from Clipboard", command=self.load_from_clipboard,
            bg="#313244", fg=self.text_color, activebackground="#45475a", activeforeground="#ffffff",
            relief=tk.FLAT, padx=10, pady=5, font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        btn_paste.pack(side=tk.LEFT, padx=(0, 6))

        btn_clear = tk.Button(
            toolbar, text="🗑️ Clear Text", command=self.clear_text,
            bg="#313244", fg=self.danger, activebackground="#45475a", activeforeground="#ffffff",
            relief=tk.FLAT, padx=10, pady=5, font=("Segoe UI", 9), cursor="hand2"
        )
        btn_clear.pack(side=tk.LEFT, padx=(0, 6))

        btn_test = tk.Button(
            toolbar, text="📝 Test in Notepad", command=self.open_notepad_test,
            bg="#313244", fg=self.warning, activebackground="#45475a", activeforeground="#ffffff",
            relief=tk.FLAT, padx=10, pady=5, font=("Segoe UI", 9), cursor="hand2"
        )
        btn_test.pack(side=tk.LEFT)

        self.always_on_top_var = tk.BooleanVar(value=True)
        self.root.wm_attributes("-topmost", True)
        chk_top = tk.Checkbutton(
            toolbar, text="Always on Top", variable=self.always_on_top_var,
            command=self.toggle_always_on_top, bg=self.card_bg, fg=self.text_dim,
            selectcolor=self.bg_dark, activebackground=self.card_bg, activeforeground=self.text_color,
            font=("Segoe UI", 9)
        )
        chk_top.pack(side=tk.RIGHT)

        # Code Input Area
        input_frame = tk.Frame(main_container, bg=self.bg_dark, padx=1, pady=1)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.txt_code = scrolledtext.ScrolledText(
            input_frame, wrap=tk.NONE, font=("Consolas", 10),
            bg=self.bg_dark, fg="#f8f8f2", insertbackground="#ffffff",
            selectbackground="#585b70", selectforeground="#ffffff",
            relief=tk.FLAT, bd=6, undo=True
        )
        self.txt_code.pack(fill=tk.BOTH, expand=True)
        self.txt_code.bind("<KeyRelease>", self.update_char_stats)

        # Stats bar
        self.lbl_stats = ttk.Label(main_container, text="0 characters | 0 lines | Est. time: 0.0s", style="Sub.TLabel")
        self.lbl_stats.pack(anchor=tk.W, pady=(0, 8))

        # Configuration Box
        settings_frame = tk.LabelFrame(
            main_container, text=" Anti-ZigZag & Speed Settings ", bg=self.card_bg, fg=self.accent,
            font=("Segoe UI", 10, "bold"), padx=12, pady=8
        )
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        # Anti-ZigZag Feature Highlight
        anti_row = tk.Frame(settings_frame, bg=self.card_bg)
        anti_row.pack(fill=tk.X, pady=(0, 6))

        self.anti_zigzag_var = tk.BooleanVar(value=True)
        chk_zigzag = tk.Checkbutton(
            anti_row, text="🛡️ Anti-ZigZag Mode (Compensates for editor's auto-indent)", 
            variable=self.anti_zigzag_var, bg=self.card_bg, fg=self.success,
            selectcolor=self.bg_dark, activebackground=self.card_bg, activeforeground=self.success,
            font=("Segoe UI", 9, "bold")
        )
        chk_zigzag.pack(side=tk.LEFT)

        self.strip_md_var = tk.BooleanVar(value=True)
        chk_md = tk.Checkbutton(
            anti_row, text="✂️ Strip Markdown (```)", variable=self.strip_md_var,
            bg=self.card_bg, fg=self.text_color, selectcolor=self.bg_dark,
            activebackground=self.card_bg, activeforeground=self.text_color, font=("Segoe UI", 9)
        )
        chk_md.pack(side=tk.RIGHT)

        # Speed Presets
        speed_row = tk.Frame(settings_frame, bg=self.card_bg)
        speed_row.pack(fill=tk.X, pady=(2, 6))

        ttk.Label(speed_row, text="Speed:").pack(side=tk.LEFT, padx=(0, 8))

        self.speed_var = tk.StringVar(value="fast")
        speeds = [
            ("⚡ Ultra (2ms)", "ultra"),
            ("🚀 Fast (8ms - Recommended)", "fast"),
            ("⌨️ Medium (25ms)", "medium"),
            ("🐢 Natural (50ms)", "natural")
        ]
        for label, val in speeds:
            rb = tk.Radiobutton(
                speed_row, text=label, variable=self.speed_var, value=val,
                command=self.update_speed_selection, bg=self.card_bg, fg=self.text_color,
                selectcolor=self.bg_dark, activebackground=self.card_bg, activeforeground=self.text_color,
                font=("Segoe UI", 9)
            )
            rb.pack(side=tk.LEFT, padx=4)

        # Custom Delay & Countdown
        params_row = tk.Frame(settings_frame, bg=self.card_bg)
        params_row.pack(fill=tk.X, pady=(2, 2))

        ttk.Label(params_row, text="Countdown (sec):").pack(side=tk.LEFT, padx=(0, 6))
        self.countdown_spin = tk.Spinbox(
            params_row, from_=1, to=10, width=4, font=("Segoe UI", 9),
            bg=self.bg_dark, fg=self.text_color, insertbackground=self.text_color
        )
        self.countdown_spin.delete(0, tk.END)
        self.countdown_spin.insert(0, "3")
        self.countdown_spin.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(params_row, text="Char Delay (sec):").pack(side=tk.LEFT, padx=(0, 6))
        self.delay_entry = tk.Entry(
            params_row, width=8, font=("Segoe UI", 9),
            bg=self.bg_dark, fg=self.text_color, insertbackground=self.text_color
        )
        self.delay_entry.insert(0, "0.008")
        self.delay_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.delay_entry.bind("<KeyRelease>", lambda e: self.update_char_stats())

        self.beep_var = tk.BooleanVar(value=True)
        chk_beep = tk.Checkbutton(
            params_row, text="🔊 Audio Beeps", variable=self.beep_var,
            bg=self.card_bg, fg=self.text_color, selectcolor=self.bg_dark,
            activebackground=self.card_bg, activeforeground=self.text_color, font=("Segoe UI", 9)
        )
        chk_beep.pack(side=tk.LEFT)

        # Status & Progress Display
        status_box = tk.Frame(main_container, bg=self.bg_dark, padx=10, pady=6)
        status_box.pack(fill=tk.X, pady=(0, 8))

        self.lbl_status = tk.Label(
            status_box, text="● READY • Paste Gemini code and click 'Start Typing' or press F8",
            bg=self.bg_dark, fg=self.success, font=("Segoe UI", 10, "bold"), anchor="w"
        )
        self.lbl_status.pack(fill=tk.X)

        self.progress = ttk.Progressbar(main_container, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        # Main Action Buttons
        btn_frame = tk.Frame(main_container, bg=self.card_bg)
        btn_frame.pack(fill=tk.X)

        self.btn_start = tk.Button(
            btn_frame, text="▶ START TYPING (F8)", command=self.start_typing_flow,
            bg="#2e7d32", fg="#ffffff", activebackground="#388e3c", activeforeground="#ffffff",
            relief=tk.FLAT, pady=10, font=("Segoe UI", 11, "bold"), cursor="hand2"
        )
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.btn_stop = tk.Button(
            btn_frame, text="■ EMERGENCY STOP (ESC)", command=self.stop_typing,
            bg="#c62828", fg="#ffffff", activebackground="#d32f2f", activeforeground="#ffffff",
            relief=tk.FLAT, pady=10, font=("Segoe UI", 11, "bold"), cursor="hand2", state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def toggle_always_on_top(self):
        self.root.wm_attributes("-topmost", self.always_on_top_var.get())

    def update_speed_selection(self):
        val = self.speed_var.get()
        mapping = {
            "ultra": "0.002",
            "fast": "0.008",
            "medium": "0.025",
            "natural": "0.050"
        }
        if val in mapping:
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, mapping[val])
            self.update_char_stats()

    def clean_text_helper(self, text):
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if self.strip_md_var.get():
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
        processed = [line.expandtabs(4) for line in lines]
        return processed

    def load_from_clipboard(self):
        try:
            text = pyperclip.paste()
            if text:
                lines = self.clean_text_helper(text)
                clean_text = "\n".join(lines)
                self.txt_code.delete("1.0", tk.END)
                self.txt_code.insert("1.0", clean_text)
                self.update_char_stats()
                self.set_status(f"Loaded {len(clean_text)} characters from clipboard.", self.success)
            else:
                self.set_status("Clipboard is empty!", self.warning)
        except Exception as e:
            self.set_status(f"Failed to read clipboard: {e}", self.danger)

    def clear_text(self):
        self.txt_code.delete("1.0", tk.END)
        self.update_char_stats()
        self.set_status("Text cleared.", self.text_dim)

    def open_notepad_test(self):
        import subprocess
        try:
            subprocess.Popen(["notepad.exe"])
            self.set_status("Opened Notepad. Click inside Notepad and test typing!", self.warning)
        except Exception as e:
            self.set_status(f"Could not open Notepad: {e}", self.danger)

    def update_char_stats(self, event=None):
        raw_text = self.txt_code.get("1.0", tk.END)
        if raw_text.endswith("\n"):
            raw_text = raw_text[:-1]
        
        char_count = len(raw_text)
        line_count = len(raw_text.splitlines()) if char_count > 0 else 0

        try:
            delay = float(self.delay_entry.get())
        except ValueError:
            delay = 0.008

        est_time = char_count * delay
        self.lbl_stats.config(
            text=f"{char_count:,} characters | {line_count:,} lines | Est. time: {est_time:.1f}s"
        )

    def set_status(self, text, color=None):
        if color is None:
            color = self.text_color
        self.lbl_status.config(text=text, fg=color)

    def start_typing_flow(self):
        if self.is_typing:
            return

        text = self.txt_code.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]

        if not text.strip():
            clip = pyperclip.paste()
            if clip.strip():
                lines = self.clean_text_helper(clip)
                text = "\n".join(lines)
                self.txt_code.delete("1.0", tk.END)
                self.txt_code.insert("1.0", text)
                self.update_char_stats()
            else:
                messagebox.showwarning("No Text", "Please paste or enter code to type!")
                return

        try:
            countdown = int(self.countdown_spin.get())
        except ValueError:
            countdown = 3

        try:
            char_delay = float(self.delay_entry.get())
            if char_delay < 0.0001:
                char_delay = 0.0001
        except ValueError:
            char_delay = 0.008

        anti_zigzag = self.anti_zigzag_var.get()
        play_beeps = self.beep_var.get()

        self.is_typing = True
        self.stop_requested = False
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.progress["value"] = 0

        self.typing_thread = threading.Thread(
            target=self._run_typing_process,
            args=(text, countdown, char_delay, anti_zigzag, play_beeps),
            daemon=True
        )
        self.typing_thread.start()

    def _run_typing_process(self, text, countdown, char_delay, anti_zigzag, play_beeps):
        # 1. Countdown Phase
        for i in range(countdown, 0, -1):
            if self.stop_requested:
                self._finish_typing("Cancelled by user.", self.warning)
                return

            msg = f"⏳ STARTING IN {i}... Click inside contest editor now!"
            self.root.after(0, self.set_status, msg, self.warning)

            if play_beeps:
                try:
                    winsound.Beep(900, 120)
                except Exception:
                    pass
            time.sleep(0.9)

        if self.stop_requested:
            self._finish_typing("Cancelled before typing.", self.warning)
            return

        if play_beeps:
            try:
                winsound.Beep(1400, 180)
            except Exception:
                pass

        # 2. Text Preparation
        lines = self.clean_text_helper(text)
        total_lines = len(lines)
        self.root.after(0, self.progress.configure, {"maximum": total_lines})

        # 3. Anti-ZigZag Typing Loop
        start_time = time.time()
        chars_typed = 0
        editor_indent = 0

        for idx, raw_line in enumerate(lines):
            if self.stop_requested:
                self._finish_typing(f"🛑 STOPPED at line {idx+1}/{total_lines} (ESC pressed).", self.danger)
                return

            line = raw_line.rstrip()
            stripped = line.lstrip(" ")
            target_indent = len(line) - len(stripped)

            if idx == 0:
                chars_to_type = line
                editor_indent = target_indent
            else:
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
                time.sleep(char_delay * 2.5)

                if anti_zigzag:
                    prev_line = lines[idx - 1].rstrip()
                    expected_indent = editor_indent
                    if prev_line.endswith(":") or prev_line.endswith("{") or prev_line.endswith("("):
                        expected_indent += 4

                    diff = target_indent - expected_indent
                    if diff > 0:
                        self.keyboard.type(" " * diff)
                        time.sleep(char_delay)
                    elif diff < 0:
                        for _ in range(abs(diff)):
                            if self.stop_requested:
                                self._finish_typing("Stopped.", self.danger)
                                return
                            self.keyboard.press(Key.backspace)
                            self.keyboard.release(Key.backspace)
                            time.sleep(char_delay * 0.8)

                    chars_to_type = stripped
                    editor_indent = target_indent
                else:
                    chars_to_type = line

            for char in chars_to_type:
                if self.stop_requested:
                    self._finish_typing(f"🛑 STOPPED at line {idx+1}/{total_lines}.", self.danger)
                    return
                self.keyboard.type(char)
                time.sleep(char_delay)
                chars_typed += 1

            self.root.after(0, self.progress.configure, {"value": idx + 1})
            pct = int(((idx + 1) / total_lines) * 100)
            self.root.after(0, self.set_status, f"⌨️ Typing: {pct}% (Line {idx+1}/{total_lines})...", self.accent)

        elapsed = time.time() - start_time
        if play_beeps:
            try:
                winsound.Beep(1200, 100)
                winsound.Beep(1600, 150)
            except Exception:
                pass

        self._finish_typing(
            f"✅ COMPLETED! Typed {total_lines} lines cleanly in {elapsed:.1f}s.",
            self.success
        )

    def _finish_typing(self, message, color):
        self.is_typing = False
        self.stop_requested = False
        self.root.after(0, self.btn_start.configure, {"state": tk.NORMAL})
        self.root.after(0, self.btn_stop.configure, {"state": tk.DISABLED})
        self.root.after(0, self.set_status, message, color)

    def stop_typing(self):
        if self.is_typing:
            self.stop_requested = True
            try:
                winsound.Beep(400, 200)
            except Exception:
                pass
            self.set_status("Emergency Stop Requested! Aborting...", self.danger)

    def _start_global_hotkeys(self):
        def on_press(key):
            try:
                if key == Key.f8:
                    if not self.is_typing:
                        self.root.after(0, self.start_typing_flow)
                elif key == Key.esc:
                    if self.is_typing:
                        self.root.after(0, self.stop_typing)
            except Exception:
                pass

        self.global_listener = Listener(on_press=on_press)
        self.global_listener.daemon = True
        self.global_listener.start()

    def on_close(self):
        self.stop_typing()
        if self.global_listener and self.global_listener.is_alive():
            self.global_listener.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperApp(root)
    root.mainloop()
