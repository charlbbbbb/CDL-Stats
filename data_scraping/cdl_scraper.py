import requests
import pandas as pd
import os

def parse_player(data: pd.DataFrame, player_num: str, team_type: str, abbrev: str, team_abbrev: str, team_id: str) -> pd.DataFrame:
        """
        Desc: A function to parse each player from a map/series
        Params:
            data (df)
            player_num (str)
            team_type (str) - host or guest team
            abbrev (str) - the opposing teams abbreviation
            team_abbrev (str) - the player's teams abbreviation
        returns:
            full_team_map (df)
        """
        if not data.shape[1]:
            return pd.DataFrame()
        parsed_stats = pd.DataFrame(data['stats'][player_num], index=[0])
        parsed_stats["team_type"] = [team_type]
        parsed_stats["oppo_abbrev"]= [abbrev]
        parsed_stats["abbrev"]= [team_abbrev]
        parsed_stats['team_id'] = [team_id]
        full_team_map = data.merge(parsed_stats, on='id', how='inner').drop("stats", axis=1)
        return full_team_map


def parse_cdl_website(matchID, save: bool =True):

    url = 'https://cdl-other-services.abe-arsfutura.com/production/v2/content-types/match-detail/bltd79e337aca601012?options={"id":' + str(matchID) + '}'

    # Dummy headers must be created to simulate the CDL website
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
    complete_match_df = pd.DataFrame()
    host_abrv = response['data']['matchData']['matchExtended']['homeTeamCard']['abbreviation']
    guest_abrv = response['data']['matchData']['matchExtended']['awayTeamCard']['abbreviation']
    home_id = response['data']['matchData']['matchExtended']['homeTeamCard']['id']
    guest_id = response['data']['matchData']['matchExtended']['awayTeamCard']['id']
    for i in range(len(response['data']['matchData']['matchStats']['matches']['hostTeam'])):
        host_md = pd.DataFrame(response['data']['matchData']['matchStats']['matches']['hostTeam'][i])
        guest_md = pd.DataFrame(response['data']['matchData']['matchStats']['matches']['guestTeam'][i])
        for player in range(4):
            complete_match_df = pd.concat([complete_match_df, parse_player(host_md, player_num=player, team_type="host", abbrev=guest_abrv, team_abbrev=host_abrv, team_id = home_id)])
            complete_match_df = pd.concat([complete_match_df, parse_player(guest_md, player_num=player, team_type="guest",abbrev=host_abrv, team_abbrev=guest_abrv, team_id = guest_id)])
    match_info = pd.json_normalize(response['data']['matchData']['matchGamesExtended'])
    match_info.rename(columns={"matchGame.mode": "gameMode",
                                "matchGame.map": "gameMap"}, inplace=True)
    joined = complete_match_df.merge(match_info, how='left', on=["gameMode", "gameMap"])
    for i in response['data']['matchData']['matchExtended']['result']:
         joined[i] = response['data']['matchData']['matchExtended']['result'][i]
    if save:
        joined.to_csv(f"data/cdl_{matchID}.csv", index=False)
    return joined


df = pd.read_json('major_ids.json')
for i in df.keys():
    for j in df[i].keys():
        for id in df[i][j]:
            try:
                parse_cdl_website(int(id))
            except:
             pass

