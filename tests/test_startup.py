"""Regression test for the Windows startup registry path."""

from smartclip import startup


def test_startup_registry_key_uses_windows_run_path():
    assert startup.KEY == r"Software\Microsoft\Windows\CurrentVersion\Run"
