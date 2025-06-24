# This endpoint can be changed every term but not recommended to make change on if you are not sure what you are doing
URL_POST = 'https://obs.itu.edu.tr/api/ders-kayit/v21'

# Your login credentials to kepler.itu
USERNAME = ''
PASSWORD = ''

# Example: ['12345','34563','90075','123132'] (Maximum 10 crn)
CRNS     = []
DROPS    = []

# Example format: "15/03/2035 15.00.00" which means 15th March 2035, at 3 pm.
# The program will most likely raise an error if the input is entered in an incorrect format
DATETIME = "24/06/2025  16.00.00"

# If you have a stable internet connection, it's recommended to change SEND_EARLY to True and
# enter a URL which has low latency to ITU servers.
# This way the automation will decide how earlier to send the request
# Otherwise the duration that the request is sent earlier will be EARLY(in milliseconds)
EARLY = 0
PING_URL = ""
SEND_EARLY = False
