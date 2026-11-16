# 👻 GhostType

> **Stealth hardware-level keystroke emulator with Anti-ZigZag indentation compensation.**  
> Effortlessly type AI-generated code directly into paste-restricted online contest platforms (IEEEXtreme, CS Academy, HackerRank, Codeforces, LeetCode, and Monaco/Ace editors).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

---

## ⚡ The Problem

Many competitive programming environments and contest editors disable clipboard paste events using browser JavaScript (`onpaste="return false;"` or `e.preventDefault()`). When using AI assistants (where officially permitted, such as IEEEXtreme), contestants are forced to either retype hundreds of lines manually or suffer severe formatting issues when naive typing scripts double-indent code into a chaotic "zig-zag" staircase pattern.

## 🎯 The Solution: GhostType

GhostType emulates **OS-level hardware keystrokes** (`pynput` / Windows `SendInput`). To the browser, it looks like you are physically typing on your keyboard.

### ✨ Key Features

- 🛡️ **Anti-ZigZag Indentation Engine**: Dynamically calculates the online IDE's auto-indentation and only sends the differential spaces (plus `Backspace` when un-indenting) so your code retains 100% clean formatting.
- ✂️ **Markdown & Tab Auto-Cleaner**: Automatically strips markdown code fences (````python````, ````cpp````) and expands tabs to standard 4-space indents.
- ⏱️ **Audio Countdown Cue**: Built-in 2–3 second audio beeps (*3... 2... 1... Go!*) giving you ample time to focus your target editor without looking away.
- 🛑 **Instant Killswitch**: Press **`ESC`** at any moment to immediately abort typing.
- 🖥️ **Dual Modes**:
  1. **GUI Mode**: Sleek dark-mode dashboard with always-on-top toggle, speed presets, and character/line counters.
  2. **Ghost Daemon (Quick Hotkey)**: Ultra-minimal background service. Copy code (`Ctrl+C`), click editor, press **`F8`**, and watch it type.

---

## 🚀 Quick Start

### Prerequisites
Make sure Python 3.8+ is installed on Windows. Install the required dependencies:
```bash
pip install pynput pyperclip
```

### Option A: Modern GUI App (`run_gui.bat`)
Double-click `run_gui.bat` or run:
```bash
python autotyper_gui.py
```
1. Paste or load code with **📋 Paste from Clipboard**.
2. Click **▶ START TYPING** (or press **`F8`**).
3. Switch to your contest editor during the 3-second audio countdown.
4. Press **`ESC`** at any time to abort.

### Option B: Quick Background Hotkey (`run_quick.bat`)
Double-click `run_quick.bat` or run:
```bash
python autotyper_quick.py
```
1. Keep the terminal running in the background.
2. In your AI chat / browser, copy code (`Ctrl + C`).
3. Click your cursor inside the contest code editor.
4. Press **`F8`** on your keyboard.
5. Listen for the 2 beeps, and the code will type out cleanly!

---

## ⚙️ Typing Speed Guidelines

| Preset | Delay per char | Speed | Best For |
|---|---|---|---|
| **Ultra** | 2 ms | ~500 chars/sec | Raw textareas, lightweight editors |
| **Fast (Recommended)** | 8 ms | ~125 chars/sec | Monaco, CS Academy, CodeMirror |
| **Medium** | 25 ms | ~40 chars/sec | Editors with heavy real-time linters |
| **Natural** | 50 ms | ~20 chars/sec | Simulating human typing cadence |

---

## 💡 Contest Editor Settings (Pro Tips)

Inside most contest web editors (e.g. CS Academy, Monaco, Ace):
1. Click the **Settings (⚙️ Gear icon)**.
2. Turn **OFF "Auto Indent"** and **"Auto Close Brackets"** if you want 100% literal typing.
3. *Alternative (DevTools)*: If browser DevTools are allowed, you can unblock paste events in 2 seconds via the Console:
   ```javascript
   window.addEventListener('paste', e => e.stopImmediatePropagation(), true);
   ```

---

## 📜 License
MIT License. Created for competitive programmers and developers.
