import pandas as pd
import numpy as np

def filter_teams_games(dataframe: pd.DataFrame, team_name: str, include_opposition: bool= True) -> pd.DataFrame:
    if include_opposition:
        match_ids = dataframe[dataframe['team_name']==team_name]['matchID'].unique()
        team_df = dataframe[dataframe['matchID'].isin(match_ids)]
    else:
        team_df = dataframe[dataframe['team_name']==team_name]
    return team_df


def all_modes_agg(dataframe: pd.DataFrame, mode: str = 'all') -> pd.DataFrame:
    """
    Desc: Adds general variables to a table. These include:
        - kills per 10 mins
        - deaths per 10 mins
        - engagements per 10 mins (above two vars combined)
        - maps played
        - average kills per game
        Also, kd is re-calculated
        If mode == snd:
            - First engagement effectiveness (first kills / first deaths)
            - First bloods/ 10 minutes
        If mode == hardpoint:
            hill time per ten mins played
        If mode == control:
            captures/ten minutes
    Params:
        dataframe (pandas df):
        mode (string): The mode to get statistics for
    """
    # Convert gametime to a decimal
    dataframe  = dataframe.copy()
    dataframe['gametime'] = dataframe['gametime'].apply(lambda x: round((int(x.split(':')[0])*60 + int(x.split(':')[1]))/60), 2)
    if mode.lower() == 'hardpoint':
        dataframe = dataframe[dataframe['mode']=='Hardpoint']
    elif mode.lower() == 'snd':
        dataframe = dataframe[dataframe['mode']=='SearchandDestroy']
    elif mode.lower() == 'control':
        dataframe = dataframe[dataframe['mode']=='Control']
    df_numeric = dataframe.select_dtypes(include="number")
    df_numeric['player'] = dataframe['player']
    df_numeric = df_numeric.groupby('player').agg('sum')
    df_numeric['kd'] = df_numeric['kills']/df_numeric['deaths']
    df_numeric['kills per 10'] = (df_numeric['kills']/df_numeric['gametime'])*10
    df_numeric['deaths per 10'] = (df_numeric['deaths']/df_numeric['gametime'])*10
    df_numeric['engagements per 10'] = df_numeric['deaths per 10'] + df_numeric['kills per 10']
    if mode.lower() == 'snd':
        df_numeric['first_kill_effectiveness'] = df_numeric['first_kill']/df_numeric['first_death']
    elif mode.lower() == 'hardpoint':
        df_numeric['hill_time_per_10'] = (df_numeric['hill_time']/df_numeric['gametime'])*10

    return df_numeric

