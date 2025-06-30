from requests import get, post, Session
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ping3 import ping
from credentials import *
import re


def main():
    check_credentials()
    courses = course_names_by_crns()
    # Wait until 45 seconds left for the system to open
    start = time_resolver(DATETIME) - calc_delay()
    print(f"Waiting until {start}")
    wait_until(start - timedelta(seconds=45))
    # Prepare variables to avoid unnecessary waiting when the system is open
    jwt = get_jwt(USERNAME, PASSWORD)

    if start < datetime.now():
        start = datetime.now()
    wait_until(start)

    try_number = 1
    while True:
        response = post_kepler(jwt, CRNS, DROPS).json()
        print(f"🔁Attempt #{try_number}:")
        try_number += 1
        # print(response)
        for course in response['ecrnResultList']:
            if course['statusCode'] == 0:
                print(f"    ✅{courses[course['crn']]} was successfully registered.")
                CRNS.remove(course['crn'])
            else:
                print(f"    ❌{courses[course['crn']]} could not be registered.")
        if len(CRNS) == 0:
            print("All courses have been successfully registered. Wishing you a great semester!")
            break
        start += timedelta(seconds=TIME_INTERVAL)
        wait_until(start)
    return

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
        if datetime.now() >= target_time:
            break


def calc_delay():
    if SEND_EARLY:
        if PING_URL == "":
            print("You've not entered a valid URL. The request will not be sent earlier.(No need to worry if you don't even understand.")
            return timedelta(0)
        elif ping(PING_URL):
            latency = ping(PING_URL)
        else:
            print("The URL is not valid. The request will not be sent earlier.(No need to worry if you don't even understand.")
            return timedelta(0)
        for i in range(5):
            temp = ping(PING_URL)
            latency = min(latency, temp)
        return timedelta(milliseconds=latency-5)
    else:
        return timedelta(0)


def check_credentials():
    get_jwt(USERNAME, PASSWORD)
    if len(CRNS) > 10 or len(DROPS) > 10:
        raise SystemExit("Max 10 CRN is supported")


def course_names_by_crns():
    response = get('https://obs.itu.edu.tr/public/DersProgram/SearchBransKoduByProgramSeviye?programSeviyeTipiAnahtari=LS')
    branches = {}
    for i in response.json():
        branches[i['bransKoduId']] = i['dersBransKodu']
    courses = {}
    for id in branches:
        html = get('https://obs.itu.edu.tr/public/DersProgram/DersProgramSearch?programSeviyeTipiAnahtari=LS',
                            params={"dersBransKoduId": id}).text
        bs = BeautifulSoup(html, 'html.parser')
        rows = bs.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            courses[cols[0].text] = cols[1].text + ' ' + cols[2].text
    return courses


if __name__ == "__main__":
    main()