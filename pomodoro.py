#!/usr/bin/env python3
"""A fully-featured Pomodoro timer CLI.

Features:
- Configurable work, short break, and long break durations
- Automatic cycle handling with long breaks after a number of pomodoros
- Interactive controls: pause/resume (p), skip (s), quit (q)

Usage:
    python pomodoro.py --work 25 --short-break 5 --long-break 15 --cycles 4

Press 'p' to pause/resume, 's' to skip the current session, 'q' to quit.
"""
from __future__ import annotations

import argparse
import threading
import time
from dataclasses import dataclass


@dataclass
class Config:
    work: int = 25 * 60
    short_break: int = 5 * 60
    long_break: int = 15 * 60
    cycles: int = 4


class PomodoroTimer:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.current_cycle = 0
        self.is_running = False
        self.is_paused = False
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()
        self._skip_event = threading.Event()

    def start(self) -> None:
        """Start the Pomodoro session."""
        self.is_running = True
        print(
            "Starting Pomodoro! Press 'p' to pause/resume, 's' to skip, 'q' to quit."
        )
        while self.is_running and self.current_cycle < self.config.cycles:
            if not self.run_session("Work", self.config.work):
                break
            self.current_cycle += 1
            if self.current_cycle % self.config.cycles == 0:
                if not self.run_session("Long Break", self.config.long_break):
                    break
            else:
                if not self.run_session("Short Break", self.config.short_break):
                    break
        if self.is_running:
            print("Pomodoro complete!")
        self.is_running = False

    def run_session(self, label: str, duration: int) -> bool:
        """Run an individual session. Returns False if aborted."""
        remaining = duration
        print(f"\nStarting {label} session ({duration // 60} min)")
        while remaining > 0 and self.is_running:
            self._pause_event.wait()
            if self._skip_event.is_set():
                self._skip_event.clear()
                print(f"Skipping {label} session.")
                return True
            mins, secs = divmod(remaining, 60)
            print(f"{label} {mins:02d}:{secs:02d}", end="\r")
            time.sleep(1)
            remaining -= 1
        if not self.is_running:
            return False
        print(f"{label} session ended!        ")
        print("\a", end="")  # Beep
        return True

    def pause(self) -> None:
        """Toggle pause state."""
        if self.is_paused:
            self.is_paused = False
            self._pause_event.set()
            print("Resumed.")
        else:
            self.is_paused = True
            self._pause_event.clear()
            print("Paused.")

    def stop(self) -> None:
        """Stop the timer."""
        self.is_running = False
        self._pause_event.set()
        self._stop_event.set()
        print("Stopped.")

    def skip(self) -> None:
        """Skip the current session."""
        self._skip_event.set()
        self._pause_event.set()
        self.is_paused = False


def input_listener(timer: PomodoroTimer) -> None:
    """Listen for keyboard commands."""
    while not timer._stop_event.is_set():
        try:
            cmd = input().strip().lower()
        except EOFError:
            timer.stop()
            break
        if cmd == "p":
            timer.pause()
        elif cmd == "s":
            timer.skip()
        elif cmd == "q":
            timer.stop()
            break


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="Pomodoro Timer")
    parser.add_argument("--work", type=int, default=25, help="Work duration in minutes")
    parser.add_argument(
        "--short-break", type=int, default=5, help="Short break duration in minutes"
    )
    parser.add_argument(
        "--long-break", type=int, default=15, help="Long break duration in minutes"
    )
    parser.add_argument(
        "--cycles", type=int, default=4, help="Number of work sessions before a long break"
    )
    args = parser.parse_args()
    return Config(
        work=args.work * 60,
        short_break=args.short_break * 60,
        long_break=args.long_break * 60,
        cycles=args.cycles,
    )


if __name__ == "__main__":
    config = parse_args()
    timer = PomodoroTimer(config)
    listener = threading.Thread(target=input_listener, args=(timer,), daemon=True)
    listener.start()
    timer.start()
    listener.join()
