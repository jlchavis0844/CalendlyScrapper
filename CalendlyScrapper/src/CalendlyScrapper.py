from datetime import datetime, timedelta  # for comparing time stamps
import json, requests, sys, os, csv, ctypes
from pytz import timezone
import pytz
from future.backports.test.pystone import FALSE



token = 'eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjI4NjM3NDg1LCJqdGkiOiJlM2JkZjkwNS02YzAxLTQ3NDgtOGIyNC0zZWMyYWIyZDUxMzciLCJ1c2VyX3V1aWQiOiJIQ0FHRENVRVZVR05HUFI1In0.TuM7yaVynzwuW0O8NiXTZlIQI9EoBXamF38Uvfhjr8s'
current_organization= 'https://api.calendly.com/organizations/AGEAFHCIH5WTSM67'
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path
pattern = '%Y-%m-%dT%H:%M:%SZ'
today_str = datetime.utcnow().strftime(pattern)
users = []
appointments = []

def load_users():
    global users
    url = 'https://api.calendly.com/organization_memberships'
    response = requests.get(url,
                            params={'organization' : current_organization},
                            headers={'Authorization':'Bearer {}'.format(token)})
    user_collection = response.json()['collection']
    #print(json.dumps(user_collection, indent=4))
    
    for user in user_collection:
        this_user = user['user']
        temp_user = {}
        temp_user['name'] = this_user['name']
        temp_user['uri'] = this_user['uri']
        users.append(temp_user)
    
    #print(json.dumps(users, indent = 4))
    
def get_user_name(uri):
    global users
    
    for user in users:
        if user['uri'] == uri:
            return user['name']
    
    return ''

def get_invitees(appt):
    invitees = []
    url = appt['uri'] + '/invitees'
    response = requests.get(url,
                            params={'organization' : current_organization},
                            headers={'Authorization':'Bearer {}'.format(token)})
    for invitee in response.json()['collection']:
        invitees.append(invitee)
    
    return invitees

file = open(path + '\\logs\\CalScraper' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("scraping appts started at " + time + '\t (' + today_str + ')')  # write to log

cnt = 0

load_users()

first_url = 'https://api.calendly.com/scheduled_events'
first_response = requests.get(first_url,
                        params = {'organization' : current_organization,
                                  'count' : 100,
                                  'status' : 'active',
                                  'sort': 'start_time:desc',
                                  'min_start_time' : today_str},
                        headers={'Authorization':'Bearer {}'.format(token)})

first_collection = first_response.json()['collection']
#print(json.dumps(first_collection, indent = 4))

print('going through ' + str(len(first_collection)) + ' appointments')
for appt in first_collection:
    temp_appt = appt
    temp_appt['invitees'] = get_invitees(appt)
    uri = appt['event_memberships'][0]['user']
    owner = get_user_name(uri)
    temp_appt['user'] = owner
    appointments.append(temp_appt)
    cnt = cnt + 1

print('Done with '+ str(cnt))

url = first_response.json()['pagination']['next_page']

while url is not None:
    url_parts = url.split('=')
    url = url_parts[len(url_parts)-1]
    
    response = requests.get(url,
                        params = {'organization' : current_organization,
                                  'count' : 100},
                        headers={'Authorization':'Bearer {}'.format(token)})

    collection = response.json()['collection']
    print('going through ' + str(len(collection)) + ' appointments')
    for appt in collection:
        temp_appt = appt
        temp_appt['invitees'] = get_invitees(appt)
        temp_appt['user'] = get_user_name(appt['event_memberships'][0]['user'])
        appointments.append(temp_appt)
        cnt = cnt + 1
    
    print('Done with '+ str(cnt))
    url = response.json()['pagination']['next_page']
    
#print(json.dumps(appointments, indent =4))
print('All Done, closing now ')
file.write(json.dumps(appointments, indent =4))
file.close()

