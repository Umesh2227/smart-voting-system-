"""
Quick dependency checker for running the project with system Python (no virtualenv).
Run: python check_deps.py
It will report missing packages and print a pip command to install them for the current user.
"""

required = ["flask", "pymysql", "pandas", "requests"]
missing = []
for pkg in required:
    try:
        __import__(pkg)
    except Exception:
        missing.append(pkg)

if not missing:
    print("All required packages are installed.")
else:
    print("Missing packages:", ", ".join(missing))
    cmd = "python -m pip install --user " + " ".join(missing)
    print("Install them with:")
    print(cmd)
