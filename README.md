# Flask Guest Check-in


Instructions:


1. Install dependencies: `pip install -r requirements.txt`
2. Run locally: `python app.py` (app runs on port 10000 by default)
3. Upload or paste exactly 60 names. The app will produce assignments and QR codes under `static/qr_codes`.


Deploy on Render:


1. Push this repo to GitHub.
2. Create a new Web Service on Render, connect your repo, choose "Docker" environment.
3. Set the PORT environment variable (Render provides one automatically) — the Dockerfile uses `$PORT`.
4. Deploy.


Notes:
- For persistence across restarts add code to write `last_assignment.csv` when assignments are created.