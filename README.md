# ITU_DSB

ITU OBS Auto Registration Bot
=============================

ITU_DSB is a Python-based automation tool that helps Istanbul Technical University (ITU) students automatically register for courses the moment the registration system opens on OBS (https://obs.itu.edu.tr). By submitting pre-defined CRNs exactly on time, it increases the chances of successful enrollment in high-demand courses.

Technologies Used
-----------------
- Python
  - requests – For handling HTTP(S) requests
  - BeautifulSoup – For parsing HTML during login and course name scraping
  - datetime – For precise timing and delay handling
  - ping3 – For latency-based request optimization
  - re – For regex-based HTML parsing and input flexibility

Features
--------
- Precise Timing: Automatically waits until the exact second specified in your configuration and triggers course registration at that moment.
- JWT Authentication: Logs in with your OBS credentials, securely obtains a JWT token, and logs out immediately to prevent redundant sessions.
- Readable Errors: Maps raw server result codes (e.g., VAL01, VAL06) to detailed, human-readable error messages.
- Course Name Matching: Fetches course names from the official course schedule page based on CRNs, making error logs more understandable.
- Latency-Aware Requests: Optionally pings the OBS server to adjust the request time for optimal delivery based on network conditions.
- Persistent Retry Logic: In case of connection failures (e.g., internet cut off), the bot automatically retries without requiring you to restart the program manually.
- Smart Filtering: If one common reason (like VAL15 or VAL16) is blocking all course attempts, the bot avoids spamming the same error message repeatedly.
- CRN Cleanup: Once a course is successfully added, its CRN is removed from the list to avoid duplicate requests.
- Consistent Loop Timing: Instead of sleeping for a fixed duration after each request, the script shifts the next attempt’s target time, ensuring execution aligns precisely with real-time (e.g., always every 3 seconds from launch).
- Regex Flexibility: Uses regex within get_jwt() to locate username and password fields dynamically, supporting future OBS UI changes.
- Time Input Parsing: The time_resolver() function applies regex to tolerate minor input format mistakes, improving user experience.

Installation
------------
Make sure you have Python installed on your system
Option 1: Clone the repository
    git clone https://github.com/YOLD4S/ITU_DSB.git
    cd ITU_DSB
    pip install -r requirements.txt

Option 2: Manual Installation
    Download the zip file from this link: https://github.com/YOLD4S/ITU_DSB/archive/refs/heads/main.zip
    Install it manually without changing the structure
    Install the required modules by running this in your terminal:
      pip install -r requirements.txt

*Note: Standard Python libraries such as datetime, re, and time are already built-in.*

Configuration
-------------
Edit the file `root/credentials.py` with your personalized data:

USERNAME = "your_obs_username"
PASSWORD = "your_obs_password"
CRNS = ["12345", "23456"]        # CRNs of the courses to register
DROPS = []                       # CRNs of courses to drop (optional)
URL_POST = "https://obs.itu.edu.tr/ogrenci/ogrsis/ders-kayit"
DATETIME = "17/06/2025 09.00.00" # Format: DD/MM/YYYY HH.MM.SS
TIME_INTERVAL = 3                # Time between each retry
SEND_EARLY = True                # Whether to send early based on ping
EARLY = 0.8                      # Offset in seconds if SEND_EARLY is True
PING_URL = "obs.itu.edu.tr"      # Used for latency measurement. If can't take response latency will be assumed to be 0. Yo can give another ip from Istanbul.

Running
-------
To run the bot, simply execute:

    python project.py

If a course is successfully registered:

    ✅ The course BLG223 Data Structures(Example) was successfully registered. (In attempt #3)

If there’s an error:

    ❌ MAT101E Mathematics I with CRN: 12345 could not be taken. <Failure explanation>'

Notes & Limitations
-------------------
- If OBS login flow changes, the script may require updates (especially get_jwt() or scraping logic).
- Aggressive request loops may lead to temporary session blocks or login throttling by the university’s server.
- Your credentials.py file contains sensitive data — keep it private and do not upload it publicly.


Enjoy seamless registration and never miss a course again with ITU_DSB! 🚀
