import requests
from bs4 import BeautifulSoup


def main():
    jwt = get_jwt("", "")  # Your kepler username and password
    url_post = 'https://obs.itu.edu.tr/api/ders-kayit/v21'  # this endpoint can be changed every term
    crns = []    # Example: ['12345','34563','90075','123132'] (Maximum 10 crn)
    drops = []   # Example: ['12345','34563','90075','123132'] (Maximum 10 crn)

    response = requests.post(url_post,
                             headers={'Authorization': 'Bearer {}'.format(jwt)},
                             json={"ECRN": crns, "SCRN": drops})

    print(response.text)

    # Logs in with username and password, returns jwt token
def get_jwt(username, password):
    session = requests.Session()

    # Finds the url after some redirects
    first_url = 'https://obs.itu.edu.tr'
    response = session.get(first_url) # For hidden inputs
    login_url = response.url

    # Finds hidden inputs and adds them into the payload for login
    soup_login = BeautifulSoup(response.text, 'html.parser')
    login_tokens = soup_login.find_all('input')
    payload = {
        "ctl00$ContentPlaceHolder1$tbUserName": username,
        "ctl00$ContentPlaceHolder1$tbPassword": password
    }
    for token in login_tokens:
        if token.has_attr('value'):
            payload[token['name']] = token['value']

    # Logs in
    res_log = session.post(login_url, data=payload)

    # Gets the required cookie to get jwt
    cookie_jwt = res_log.history[-1].headers.get('Set-Cookie')
    headers_jwt = {
        'Cookie': cookie_jwt
    }
    # Gets jwt
    jwt = session.get('https://obs.itu.edu.tr/ogrenci/auth/jwt', headers=headers_jwt).text
    return jwt


if __name__ == "__main__":
    main()