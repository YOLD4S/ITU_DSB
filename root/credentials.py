import os

from dotenv import dotenv_values

config = dotenv_values(".env")


URL_POST = config.get('URL_POST', 'https://obs.itu.edu.tr/api/ders-kayit/v21')
USERNAME = config.get('USERNAME')
PASSWORD = config.get('PASSWORD')
CRNS     = [crn.strip() for crn in config.get('CRNS', '').strip().split(',') if crn.strip()]
DROPS    = [crn.strip() for crn in config.get('DROPS', '').strip().split(',') if crn.strip()]
DATETIME = config.get('DATETIME')
EARLY = int(config.get('EARLY')) or 20
PING_URL = config.get('PING_URL')
SEND_EARLY = config.get('SEND_EARLY').strip().lower() == 'true'
TIME_INTERVAL = int(config.get('TIME_INTERVAL')) or 3
TRIAL_COUNT = int(config.get('TRIAL_COUNT')) or 2

if __name__ == "__main__":
    print(config)
    print(f"{URL_POST=}\n{USERNAME=}\n{PASSWORD=}\n{CRNS=}\n{DROPS=}\n{DATETIME=}\n{EARLY=}\n{PING_URL=}\n{SEND_EARLY=}\n{TIME_INTERVAL=}\n{TRIAL_COUNT=}")
