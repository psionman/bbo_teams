# To fix for windows

# Error: C:\Users\Jeff\AppData\Local\Jeff\psiutils\text\text.json not found

# File not found C:\Users\Jeff\AppData\Local\Jeff\psiutils\buttons\buttons.json


"""
Windows just File

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

list:
    just --list

run arg1="" arg2="" arg3="":
    uv run src/bbo_teams/main.py {{arg1}} {{arg2}} {{arg3}}
"""
# set up .env file

"""
in main.py remove


uv_python = os.getenv("UV_PYTHON")
if not uv_python:
    print(
        "Have you run export UV_PYTHON=/usr/bin/python3? - copied to clipboard"
    )
    clipboard.copy("export UV_PYTHON=/usr/bin/python3")

"""
