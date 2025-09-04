# Pomodoro Timer

This repository contains a command-line Pomodoro timer.

## Features
- Configurable work, short break, and long break durations
- Automatic handling of work/break cycles with long breaks after a set number of sessions
- Interactive controls: pause/resume (`p`), skip (`s`), quit (`q`)

## Usage
```bash
python pomodoro.py --work 25 --short-break 5 --long-break 15 --cycles 4
```
During execution, type `p` to pause/resume, `s` to skip the current session, or `q` to quit the timer.
