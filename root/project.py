from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ping3 import ping
from credentials import *
import re, time, requests, tls_client


error_messages = {
    "VAL01": "{} could not be taken. Result code: 'VAL01'",
    "VAL02": "{} could not be taken. You are not in an active course enrollment period.",
    "VAL03": "{} could not be taken again because it was taken this semester.",
    "VAL04": "{} could not be taken because it was not included in the lesson plan.",
    "VAL05": "{} cannot be added as maximum number of credits allowed for this term is exceeded.",
    "VAL06": "{} cannot be added as the enrollment limit has been reached and there is no quota left.",
    "VAL07": "{} cannot be re-added because this course has been completed before with an AA grade.",
    "VAL08": "{} could not be taken because your program is not among the programs that can take this course.",
    "VAL09": "{} cannot be added due to a time conflict with another course.",
    "VAL10": "No action has been taken because you are not registered to the course {} this semester.",
    "VAL11": "{} cannot not be added as its prerequisites are not met.",
    "VAL12": "{} is not offered in the respective semester.",
    "VAL13": "{} has been temporarily disabled.",
    "VAL14": "{} could not be taken. System is temporarily disabled.",
    "VAL15": "You can send maximum 12 CRN parameters.",
    "VAL16": "You currently have an ongoing transaction, try again later.",
    "VAL17": "{} could not be taken. Due to maintenance work, the system is temporarily unavailable.",
    "VAL18": "{} could not be taken. Result code: 'VAL18'",
    "VAL19": "{}  could not be taken because it is an undergraduate course.",
}


def main():
    session = tls_client.Session()
    print("Checking username and password...")
    print("Verified successfully." if check_credentials() else "Please check your credentials.")

    print("Starting...")
    courses = course_names_by_crns()

    start = time_resolver(DATETIME) - calc_delay()
    if start > datetime.now():
        print(f"Waiting until {start}")

    # Wait until 1 minute left for the system to open
    wait_until(start - timedelta(minutes=1))
    # Prepare variables to avoid unnecessary waiting when the system is open
    jwt = get_jwt(USERNAME, PASSWORD)

    try_number = 1
    retry_number = 1
    while True:
        try:
            response = post_kepler(session, jwt, CRNS, DROPS).json()
            print(f"\n🔁 Attempt #{try_number}:")
            try_number += 1
            for course in response["ecrnResultList"]:
                if course["statusCode"] == 0:
                    print(
                        f"  ✅ {course['crn']} was successfully registered.(In attempt #{try_number})"
                    )
                    CRNS.remove(course["crn"])
                else:
                    print(
                        "  ❌ "
                        + error_messages[course["resultCode"]].format(
                            courses[course["crn"]] + " with CRN: " + course["crn"]
                        )
                    )
                    if course["resultCode"] in {"VAL15", "VAL16"}:
                        break
            if len(CRNS) == 0:
                print(
                    "\n  ☑️ All courses have been successfully registered. Wishing you a great semester!"
                )
                return
            time.sleep(TIME_INTERVAL)
        except KeyboardInterrupt:
            print("Program terminated.")
            exit(0)
        except:
            try:
                jwt = get_jwt(USERNAME, PASSWORD)
            except:
                for i in range(5):
                    print(
                        f"\r- Failed to get jwt. Please check your network connection. Retrying in {5 - i} seconds...(Attempt #{retry_number})",
                        end="",
                    )
                    time.sleep(1)
                retry_number += 1


# Adding the required auth token, posts the request to take or drop lectures
def post_kepler(session, jwt, crns, drops):
    response = session.post(
        URL_POST,
        headers={"Authorization": "Bearer {}".format(jwt)},
        json={"ECRN": crns, "SCRN": drops}
    )
    return response


# Logs in with username and password, returns jwt token
def get_jwt(username, password):
    session = requests.Session()
    # Finds the required url after some redirects
    response = session.get("https://obs.itu.edu.tr", timeout=2)  # For hidden inputs
    login_url = response.url

    # Finds hidden inputs and adds them into the payload for login
    soup_login = BeautifulSoup(response.text, "html.parser")
    login_tokens = soup_login.find_all("input")

    payload = {}
    # Fills the payload
    for token in login_tokens:
        match_username = re.search(r".*username.*", token["id"], re.IGNORECASE)
        match_password = re.search(r".*password.*", token["id"], re.IGNORECASE)
        if match_username:
            payload[token["name"]] = username
        elif match_password:
            payload[token["name"]] = password
        elif token.has_attr("value"):
            payload[token["name"]] = token["value"]
    # Logs in
    res_log = session.post(login_url, data=payload)
    # Checks if the user is redirected meaning that the credentials are valid
    if not res_log.history:
        raise SystemExit("Please check your login credentials")
    # Gets the required cookie to get jwt
    cookie_jwt = res_log.history[-1].headers.get("Set-Cookie")
    headers_jwt = {"Cookie": cookie_jwt}
    # Gets jwt
    jwt = requests.get("https://obs.itu.edu.tr/ogrenci/auth/jwt", headers=headers_jwt).text
    session.get("https://girisv3.itu.edu.tr/logout.aspx")
    return jwt


def time_resolver(date_time):
    matches = re.search(
        r"(\d{2})/(\d{2})/(\d{4}) *(\d{2})\.(\d{2})\.(\d{2})", date_time
    )
    if not matches:
        raise SystemExit("Please check your date and time format")

    day = int(matches.group(1))
    month = int(matches.group(2))
    year = int(matches.group(3))
    hour = int(matches.group(4))
    minute = int(matches.group(5))
    second = int(matches.group(6))

    if (
        0 <= day <= 31
        or 0 <= month <= 12
        or 0 <= hour <= 24
        or 0 <= minute <= 59
        or 0 <= second <= 59
    ):
        pass
    else:
        raise SystemExit("Please check your date and time")
    return datetime(year, month, day, hour, minute, second)


def wait_until(target_time):
    while True:
        if datetime.now() >= target_time:
            break


def calc_delay():
    if SEND_EARLY:
        if PING_URL == "":
            print(
                "You've not entered a valid URL. The request will not be sent earlier.(No need to worry if you don't even understand."
            )
            return timedelta(EARLY)
        elif ping(PING_URL):
            latency = ping(PING_URL)
        else:
            print(
                "The URL is not valid. The request will not be sent earlier.(No need to worry if you don't even understand."
            )
            return timedelta(EARLY)
        for i in range(5):
            temp = ping(PING_URL)
            if abs(latency - temp) > 5:
                print(
                    "Your network is not stable. The request will not be sent earlier.(No need to worry if you don't even understand."
                )
            else:
                latency = min(latency, temp)
        return timedelta(milliseconds=latency - 5)
    else:
        return timedelta(0)


def check_credentials():
    try:
        get_jwt(USERNAME, PASSWORD)
        return True
    except:
        return False


def course_names_by_crns():
    response = requests.get(
        "https://obs.itu.edu.tr/public/DersProgram/SearchBransKoduByProgramSeviye?programSeviyeTipiAnahtari=LS"
    )
    branches = {}
    for i in response.json():
        branches[i["bransKoduId"]] = i["dersBransKodu"]
    courses = {}
    for id in branches:
        html = requests.get(
            "https://obs.itu.edu.tr/public/DersProgram/DersProgramSearch?programSeviyeTipiAnahtari=LS",
            params={"dersBransKoduId": id},
        ).text
        bs = BeautifulSoup(html, "html.parser")
        rows = bs.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            courses[cols[0].text] = cols[1].text + " " + cols[2].text
    return courses


if __name__ == "__main__":
    main()
