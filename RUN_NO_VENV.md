Run the project without a virtual environment (Windows PowerShell)

This small helper file explains how to run the Smart Voting System using your system Python (no virtualenv).

1) Ensure Python and pip are on PATH:

```powershell
python --version
pip --version
```

2) Install required packages for the current user:

```powershell
pip install --user -r requirements.txt
```

3) Optionally run the dependency checker to verify:

```powershell
python check_deps.py
```

4) Start the app:

```powershell
python .\code\main.py
```

Or use the included helper script which installs packages for the current user and launches the app:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run_project.ps1
```

Notes:
- Installing with `--user` will place packages in your user site-packages; if you prefer a clean environment, use a virtualenv.
- Ensure your MySQL server is running and that the database `smart_voting_system` has been created and populated with `DATABASE/my_sql_dump.sql`.
- If you get import errors, ensure `pip` belongs to the same `python` by running `python -m pip --version` and install packages with `python -m pip install --user -r requirements.txt`.
