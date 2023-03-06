import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


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


def assign_extra_vars(df):
    df['map_winner'] = ["host" if a > b else "guest" for a, b in zip(df['matchGameResult.hostGameScore'], df['matchGameResult.guestGameScore'])]

    df['is_winner'] = ["Y" if a == b else "N" for a, b in zip(df['map_winner'], df['team_type'])]

    df['accuracy'] = [(a/+b)*100 for a, b in zip(df['totalShotsHit'], df['totalShotsFired'])]

    df['kills_untraded_perc'] = [(a/b)*100 if b > 0 else 0 for a, b in zip(df['untradedKills'], df['totalKills'])]

    df['deaths_traded_perc'] = [(a/b)*100  if b > 0 else 0 for a, b in zip(df['tradedDeaths'], df['totalDeaths'])]

    df['damage_per_kill'] = [round(a/b, 0) if b > 0 else 0 for a, b in zip(df['totalDamageDealt'], df['totalKills'])]
    return df

def cdl_untraded_kill_traded_deaths(df, host_name, guest_name, host_colour, guest_colour, save_name, x_size=7, y_size=8, save_location=None, legend_location="upper left",
                                    control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev'
        ]]
    df_refined = assign_extra_vars(df_refined)
    if not control:
        df_refined = df_refined[df_refined['gameMode'] != 'CDL Control']
    if not hardpoint:
        df_refined = df_refined[df_refined['gameMode'] != "CDL Hardpoint"]
    if not search:
        df_refined = df_refined[df_refined['gameMode'] != "CDL SnD"]
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"Untraded Deaths vs Untraded Kills % {host_name} vs {guest_name}")
    sns.scatterplot(data=df_refined, x='kills_untraded_perc', y='deaths_traded_perc', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['kills_untraded_perc'], df_refined['deaths_traded_perc'], df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);

    fig.savefig(f"{save_location if save_location else ''}/{save_name}.PNG")

def cdl_movement(df, host_name, guest_name, host_colour, guest_colour, save_name, x_size=7, y_size=8, save_location=None, legend_location="upper left",
                  control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev'
        ]]
    df_refined = assign_extra_vars(df_refined)
    if not control:
        df_refined = df_refined[df_refined['gameMode'] != 'CDL Control']
    if not hardpoint:
        df_refined = df_refined[df_refined['gameMode'] != "CDL Hardpoint"]
    if not search:
        df_refined = df_refined[df_refined['gameMode'] != "CDL SnD"]
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"Amount of Movement (Roughly) - {host_name} vs {guest_name}")
    sns.scatterplot(data=df_refined, x='percentTimeMoving', y='totalDistanceTraveled', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['percentTimeMoving'], df_refined['totalDistanceTraveled'], df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);

    fig.savefig(f"{save_location if save_location else ''}/{save_name}.PNG")

def damage_accuracy(df, host_name, guest_name, host_colour, guest_colour, save_name, x_size=7, y_size=8, save_location=None, legend_location="upper left",
                     control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev'
        ]]
    df_refined = assign_extra_vars(df_refined)
    if not control:
        df_refined = df_refined[df_refined['gameMode'] != 'CDL Control']
    if not hardpoint:
        df_refined = df_refined[df_refined['gameMode'] != "CDL Hardpoint"]
    if not search:
        df_refined = df_refined[df_refined['gameMode'] != "CDL SnD"]
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"Accuracy vs Damage per Kill - {host_name} vs {guest_name}")
    sns.scatterplot(data=df_refined, x='accuracy', y='damage_per_kill', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['accuracy'], df_refined['damage_per_kill'], df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);
    ax1.set_xlabel("Accuracy (%)")
    ax1.set_ylabel("Damage per Kill")

    fig.savefig(f"{save_location if save_location else ''}/{save_name}.PNG")


