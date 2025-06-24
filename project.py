from traceback import print_tb

from requests import get, post, Session
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ping3 import ping
from credentials import *
import re, sys


def main():
    check_credentials()

    # Wait until 45 seconds left for the system to open
    start = time_resolver(DATETIME)
    print(f"Waiting until {start}")
    wait_until(start - timedelta(seconds=45))
    # Prepare variables to avoid unnecessary waiting when the system is open
    jwt = get_jwt(USERNAME, PASSWORD)
    delay = calc_delay()

    wait_until(start - delay)
    response = post_kepler(jwt, CRNS, DROPS)
    print(response.text)
    print(f"{delay}")


# Adding the required auth token, posts the request to take or drop lectures
def post_kepler(jwt, crns, drops):
    response = post(URL_POST,
                    headers={'Authorization': 'Bearer {}'.format(jwt)},
                    json={"ECRN": crns, "SCRN": drops})
    return response

# Logs in with username and password, returns jwt token
def get_jwt(username, password):
    session = Session()

    # Finds the required url after some redirects
    response = session.get('https://obs.itu.edu.tr') # For hidden inputs
    login_url = response.url

    # Finds hidden inputs and adds them into the payload for login
    soup_login = BeautifulSoup(response.text, 'html.parser')
    login_tokens = soup_login.find_all('input')

    payload = {}
    # Fills the payload
    for token in login_tokens:
        match_username = re.search(r".*username.*", token['id'], re.IGNORECASE)
        match_password = re.search(r".*password.*", token['id'], re.IGNORECASE)
        if match_username:
            payload[token['name']] = username
        elif match_password:
            payload[token['name']] = password
        elif token.has_attr('value'):
            payload[token['name']] = token['value']
    # Logs in
    res_log = session.post(login_url, data=payload)
    # Checks if the user is redirected meaning that the credentials are valid
    if not res_log.history:
        raise SystemExit('Please check your login credentials')
    # Gets the required cookie to get jwt
    cookie_jwt = res_log.history[-1].headers.get('Set-Cookie')
    headers_jwt = {
        'Cookie': cookie_jwt
    }
    # Gets jwt
    jwt = session.get('https://obs.itu.edu.tr/ogrenci/auth/jwt', headers=headers_jwt).text
    return jwt


def time_resolver(date_time):
    matches = re.search(r"(\d{2})/(\d{2})/(\d{4}) *(\d{2})\.(\d{2})\.(\d{2})", date_time)
    if not matches:
        raise SystemExit('Please check your date and time format')

    day = int(matches.group(1))
    month = int(matches.group(2))
    year = int(matches.group(3))
    hour = int(matches.group(4))
    minute = int(matches.group(5))
    second = int(matches.group(6))

    if 0 <= day <= 30\
        or 0 <= month <= 12\
        or 0 <= hour <= 24\
        or 0 <= minute <= 59\
        or 0 <= second <= 59:
        pass
    else:
        raise SystemExit('Please check your date and time')
    return datetime(year, month, day, hour, minute, second)


def wait_until(target_time):
    while True:
        now = datetime.now()
        if now >= target_time:
            break


def calc_delay():
    if not SEND_EARLY:
        return timedelta(milliseconds=EARLY)

    if ping(PING_URL):
        latency = ping(PING_URL)
    else:
        raise SystemExit("Please check PING_URL or if you don't have a valid URL, change SEND_EARLY to False")
    for i in range(5):
        temp = ping(PING_URL)
        latency = max(latency, temp)
    return timedelta(milliseconds=latency+10)


def check_credentials():
    calc_delay()  # To precheck if the url is valid(pingable)
    get_jwt(USERNAME, PASSWORD)
    if len(CRNS) > 10 or len(DROPS) > 10:
        raise SystemExit("Max 10 CRN is supported")


if __name__ == "__main__":
    main()