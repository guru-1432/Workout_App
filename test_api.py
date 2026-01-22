import requests

try:
    r = requests.get('http://localhost:8000/api/history')
    print(r.status_code)
    data = r.json()
    if data and len(data) > 0:
        first_session = data[0]
        print("Session ID:", first_session.get('id'))
        if 'sets' in first_session:
            sets = first_session['sets']
            print("Sets count:", len(sets))
            if len(sets) > 0:
                first_set = sets[0]
                print("First Set Exercise:", first_set.get('exercise'))
        else:
            print("No sets found")
    else:
        print("No history found")
except Exception as e:
    print(e)
