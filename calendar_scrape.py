from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import datetime

url = 'https://app.squarespacescheduling.com/schedule.php?action=showCalendar&fulldate=1&owner=26581810&template=monthly'
alert_months = []
alert_days = []
alert = False

with open('credentials.crd', 'r') as f:
    creds = f.read().splitlines()
    token = creds[0]
    user = creds[1]


today = datetime.date.today()
dates = []
for i in range(4):
    try:
        month = today.month + i
        year = today.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        date = datetime.date(year, month, 15)
        dates.append(date.strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"An error occurred: {e}")

for date_string in dates:

    post_fields = {'type': '34677534',
        'calendar': '6981298',
        'month': date_string,
        'timezone': 'Europe/London',
        'skip': 'true',
        'options[numDays]': '5',
        'ignoreAppointment': 'true',
        'appointmentType': '0',
        'calendarID': '0'
        }

    request = Request(url, urlencode(post_fields).encode())
    with urlopen(request) as response:
        html_doc = response.read().decode()

    soup = BeautifulSoup(html_doc, 'html.parser')
    # find all the tags that have the attribute data-testid="activeUpcomingCalendarDay"
    tags = soup.find_all(attrs={'data-testid': 'activeUpcomingCalendarDay'})
    for tag in tags:
        the_year, the_month, _ = map(int, date_string.split('-'))
        target_date = datetime.date(the_year, the_month, int(tag.text))
        if target_date.weekday() in (4, 5):
            alert = True
            alert_months.append(the_month)
            alert_days.append(tag.text)
for month in alert_months:
    month_name = datetime.datetime(2023, month, 1).strftime('%B')
    alert_months[alert_months.index(month)] = month_name

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if alert:
    alert_url = "https://api.pushover.net/1/messages.json"
    alert_post = {
        "token": token,
        "user": user,
        "message": "A weekend appointment has become available in " + str(alert_months),
        "device": "Chihiro",
        "sound": "persistent"
    }

    request = Request(alert_url, urlencode(alert_post).encode())
    with urlopen(request) as response:
        html_doc = response.read().decode()
    print("Alert!")
    with open("alert.txt", "a") as f:
        f.write(now + " " + html_doc + "\n")
else:
    print("No alert")
    with open("alert.txt", "a") as f:
        f.write(now + " " + "No alert" + "\n")
