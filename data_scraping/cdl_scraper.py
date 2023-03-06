import requests
import pandas as pd
import os

def parse_cdl_website(matchID, save=True):

    url = 'https://cdl-other-services.abe-arsfutura.com/production/v2/content-types/match-detail/bltd79e337aca601012?options={"id":' + str(matchID) + '}'

    cdl_headers = {
    "Host": "cdl-other-services.abe-arsfutura.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.5",
    "Referer": "https://www.callofdutyleague.com/",
    "x-origin": "callofdutyleague.com",
    "Origin": "https://www.callofdutyleague.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "TE": "trailers"}

    response = requests.get(url, headers=cdl_headers).json()

    def parse_player(data, player_num, team_type, abbrev):
        if not data.shape[1]:
            return pd.DataFrame()
        parsed_stats = pd.DataFrame(data['stats'][player_num], index=[0])
        parsed_stats["team_type"] = [team_type]
        parsed_stats["oppo_abbrev"]= [abbrev]
        full_team_map = data.merge(parsed_stats, on='id', how='inner').drop("stats", axis=1)
        return full_team_map


    complete_match_df = pd.DataFrame()

    host_abrv = response['data']['matchData']['matchExtended']['homeTeamCard']['abbreviation']
    guest_abrv = response['data']['matchData']['matchExtended']['awayTeamCard']['abbreviation']

    for i in range(len(response['data']['matchData']['matchStats']['matches']['hostTeam'])):
        host_md = pd.DataFrame(response['data']['matchData']['matchStats']['matches']['hostTeam'][i])
        guest_md = pd.DataFrame(response['data']['matchData']['matchStats']['matches']['guestTeam'][i])
        for player in range(4):
            complete_match_df = pd.concat([complete_match_df, parse_player(host_md, player_num=player, team_type="host", abbrev=guest_abrv)])
            complete_match_df = pd.concat([complete_match_df, parse_player(guest_md, player_num=player, team_type="guest", abbrev=host_abrv)])

    match_info = pd.json_normalize(response['data']['matchData']['matchGamesExtended'])
    match_info.rename(columns={"matchGame.mode": "gameMode",
                                "matchGame.map": "gameMap"}, inplace=True)
    joined = complete_match_df.merge(match_info, how='left', on=["gameMode", "gameMap"])


    if save:
        print(os.getcwd())
        joined.to_csv(f"data/cdl_{matchID}.csv", index=False)
    return joined

for i in range(8718, 8748):
    parse_cdl_website(i)