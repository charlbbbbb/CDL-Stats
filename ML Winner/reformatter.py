"""
The goal of this code is to convert each match into overall statistics for each team, 
and then combine these stats into one row with 'team1' and 'team2'. This should also contain the outcome of the match.
"""
import pandas as pd
import numpy as np

def declare_winner(df: pd.DataFrame) -> pd.DataFrame:
    df['map_winner'] = ["host" if a > b else "guest" for a, b in zip(df['matchGameResult.hostGameScore'], df['matchGameResult.guestGameScore'])]

    df['is_winner'] = ["Y" if a == b else "N" for a, b in zip(df['map_winner'], df['team_type'])]

    return df

def reshape_match(data): 
    data = declare_winner(data)
    grouping = {a: 'sum' for a in ['totalDamageDealt', 'totalKills', 'totalDeaths', 'totalFirstBloodKills', 'totalRotationKills', 'totalShotsHit', 'totalShotsFired']}
    grouping2 = {b: 'first' for b in ['team_type', 'matchGameResult.guestGameScore', 'matchGameResult.hostGameScore']}
    full_group = {**grouping , **grouping2}
    group = data.groupby(['gameMap', 'oppo_abbrev', 'abbrev', 'gameMode', 'map_winner', 'matchGame.matchId']).agg(full_group)

    group['rounds'] = group['matchGameResult.guestGameScore']+group['matchGameResult.hostGameScore']
    group['teamKd'] = group['totalKills']/group['totalDeaths']
    group['accuracy'] = group['totalShotsHit']/group['totalShotsFired']
    group['rotationalPercent'] = group['totalRotationKills']/group['totalKills']
    group['fbPerc'] = group['totalFirstBloodKills']/group['rounds']

    group.reset_index(inplace=True)
    group.drop(columns=['totalShotsHit', 'totalShotsFired', 'totalKills', 'totalDeaths', 'totalRotationKills', 'matchGameResult.hostGameScore', 
                        'matchGameResult.guestGameScore', 'totalFirstBloodKills', 'matchGame.matchId'], inplace=True)

    team1 = group[group['team_type']=='host'].copy()
    team1['host_abbrev'] = team1['abbrev']
    team1['guest_abbrev'] = team1['oppo_abbrev']

    team2 = group[group['team_type']=='guest'].copy()
    team2['guest_abbrev'] = team2['abbrev']
    team2['host_abbrev'] = team2['oppo_abbrev']

    t1 = {col: f"{col}_team1" for col in team1.columns}
    t2 = {col: f"{col}_team2" for col in team1.columns}
    team1.rename(columns=t1, inplace=True)
    team2.rename(columns=t2, inplace=True)

    merged = pd.merge(team1, team2, left_on=['host_abbrev_team1', 'guest_abbrev_team1', 'gameMap_team1', 'gameMode_team1'], 
            right_on=['host_abbrev_team2', 'guest_abbrev_team2', 'gameMap_team2', 'gameMode_team2'], how='left')

    needed = merged.drop(columns=['gameMap_team1', 'gameMap_team2', 'rounds_team1', 'rounds_team2', 'gameMode_team1',
                                'abbrev_team1', 'abbrev_team2', 'oppo_abbrev_team1', 'oppo_abbrev_team2',
                                'host_abbrev_team1', 'host_abbrev_team2', 'guest_abbrev_team1', 'guest_abbrev_team2', 'map_winner_team2'])

    needed.rename(columns={'map_winner_team1': 'winner',
                        'gameMode_team2': 'mode'}, inplace=True)

    needed['winner'] =  ['team1' if a == b else 'team2' for a, b in zip(needed['team_type_team1'], needed['winner'])] 
    needed.drop(columns=['team_type_team1', 'team_type_team2'], inplace=True)
    return needed