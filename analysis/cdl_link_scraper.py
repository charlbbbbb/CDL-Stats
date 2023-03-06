import requests
import re

def get_links(url):
    matches = []
    response = requests.get(url)
    for i in response.text.split():
        if  'match/' in i:
            matches.append(re.search('match/[0-9]+', i).group().split('/')[1])
    return matches

    
