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

def get_outliers(data_1, data_2):
    d1_mean = data_1.mean()
    d2_mean = data_2.mean()
    d1_new = [round(a/b, 2) if b > 0 else 0 for a, b in zip(data_1, [d1_mean for i in range(data_1)])]
    d2_new = [round(a/b, 2) if b > 0 else 0 for a, b in zip(data_2, [d2_mean for i in range(data_2)])]
    score = [round((a+b)/2, 2) for a, b in zip(d1_new, d2_new)]
    return score
    

def assign_extra_vars(df):
    df['map_winner'] = ["host" if a > b else "guest" for a, b in zip(df['matchGameResult.hostGameScore'], df['matchGameResult.guestGameScore'])]

    df['is_winner'] = ["Y" if a == b else "N" for a, b in zip(df['map_winner'], df['team_type'])]

    df['accuracy'] = [(a/+b)*100 for a, b in zip(df['totalShotsHit'], df['totalShotsFired'])]

    df['kills_untraded_perc'] = [(a/b)*100 if b > 0 else 0 for a, b in zip(df['untradedKills'], df['totalKills'])]

    df['deaths_traded_perc'] = [(a/b)*100  if b > 0 else 0 for a, b in zip(df['tradedDeaths'], df['totalDeaths'])]

    df['damage_per_kill'] = [round(a/b, 0) if b > 0 else 0 for a, b in zip(df['totalDamageDealt'], df['totalKills'])]

    df['kd'] = [round((a/b), 2) if b > 0 else a for a, b in zip(df['totalKills'], df['totalDeaths'])]

    df['rot_kill_perc'] = [round((a/b)*100, 2) if b > 0 else 0 for a, b in zip(df['totalRotationKills'], df['totalKills'])]

    df['fb_perc'] = [round((a/b)*100, 2) if b > 0 else 0 for a, b in zip(df['totalFirstBloodKills'], df['totalKills'])]

    return df

def cdl_untraded_kill_traded_deaths(df, host_name, guest_name, host_colour, guest_colour, x_size=7, y_size=8, legend_location="upper left",
                                    control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev', 'totalFirstBloodKills'
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
    ax1.set_title(f"Traded Deaths % vs Untraded Kills % {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='kills_untraded_perc', y='deaths_traded_perc', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['kills_untraded_perc'], df_refined['deaths_traded_perc'], df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);


def cdl_movement(df, host_name, guest_name, host_colour, guest_colour, x_size=7, y_size=8, legend_location="upper left",
                  control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev','totalFirstBloodKills', 'abbrev'
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
    ax1.set_title(f"Amount of Movement (Roughly) - {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='percentTimeMoving', y='totalDistanceTraveled', hue='abbrev', ax=ax1, style='gameMode')
    for x, y, s, t, abb, score in zip(df_refined['percentTimeMoving'], df_refined['totalDistanceTraveled'], df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev'], 
                                      get_outliers(df['percentTimeMoving'], df_refined['totalDistanceTraveled'])):
        if score > 1.1 or score < 0.9:
            ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);


def cdl_damage_accuracy(df, host_name, guest_name, host_colour, guest_colour, save_name, x_size=7, y_size=8, save_location=None, legend_location="upper left",
                     control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev', 'totalFirstBloodKills'
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
    ax1.set_title(f"Accuracy vs Damage per Kill - {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='accuracy', y='damage_per_kill', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['accuracy'], df_refined['damage_per_kill'], df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);
    ax1.set_xlabel("Accuracy (%)")
    ax1.set_ylabel("Damage per Kill")



def cdl_kd_hill(df, host_name, guest_name, host_colour, guest_colour, x_size=7, y_size=8, legend_location="upper left"):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev',  'totalFirstBloodKills'
        ]]
    df_refined = assign_extra_vars(df_refined)
    df_refined = df_refined[df_refined["gameMode"]=="CDL Hardpoint"]
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"Hill Time vs KD - {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='kd', y='hillTime', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['kd'], df_refined['hillTime'], 
                                  df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.03, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);
    ax1.set_xlabel("KD")
    ax1.set_ylabel("Hill Time")


def cdl_rot_kills(df, host_name, guest_name, host_colour, guest_colour, x_size=7, y_size=8, legend_location="upper left"):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev', 'totalFirstBloodKills'
        ]]
    df_refined = assign_extra_vars(df_refined)
    df_refined = df_refined[df_refined["gameMode"]=="CDL Hardpoint"]
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"Hill Time vs Percent of Kills that are Rotational Kills - {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='rot_kill_perc', y='hillTime', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['rot_kill_perc'], df_refined['hillTime'], 
                                  df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);
    ax1.set_xlabel("% of kills that are rotational kills")
    ax1.set_ylabel("Hill Time")

def cdl_fb_perc(df, host_name, guest_name, host_colour, guest_colour, x_size=7, y_size=8, legend_location="upper left"):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev', 'totalFirstBloodKills', 'deadSilenceTime'
        ]]
    df_refined = assign_extra_vars(df_refined)
    df_refined = df_refined[df_refined["gameMode"]=="CDL SnD"]
    df_refined = df_refined[df_refined['totalKills'] > 5]
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"First Blood % vs KD (atleast 6 kills) - {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='fb_perc', y='kd', hue='gameMode', ax=ax1)
    for x, y, s, t, abb in zip(df_refined['fb_perc'], df_refined['kd'], 
                                  df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
        ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);
    ax1.set_xlabel("First Blood % (of players kills)")
    ax1.set_ylabel("KD")

def cdl_fair_fights(df, host_name, guest_name, host_colour, guest_colour, x_size=7, y_size=8, legend_location="upper left",
                    control=True, hardpoint=True, search=True):
    df_refined = df[['alias', 'gameMode', 'gameMap', 'totalDistanceTraveled', 'totalDamageDealt', 'totalShotsFired', 'totalShotsHit', 
        'totalAssists', 'totalDeaths', 'totalKills', 'hillTime', 'percentTimeMoving', 'lethalsUsed', 'tacticalsUsed',
        'tradedDeaths', 'tradedKills', 'untradedDeaths', 'untradedKills', 'team_type', 'totalRotationKills', 
        'matchGameResult.hostGameScore', 'matchGameResult.guestGameScore', 'oppo_abbrev', 'totalFirstBloodKills', 'deadSilenceTime',
        'totalInVictimFovKills'
        ]]
    df_refined = assign_extra_vars(df_refined)
    if not control:
        df_refined = df_refined[df_refined['gameMode'] != 'CDL Control']
    if not hardpoint:
        df_refined = df_refined[df_refined['gameMode'] != "CDL Hardpoint"]
    if not search:
        df_refined = df_refined[df_refined['gameMode'] != "CDL SnD"]
    df_refined.reset_index(inplace=True)
    df_refined['fair_fights'] = ((df_refined['totalInVictimFovKills']/df['totalKills'])*100).round(2)
    fig = plt.figure(figsize=(x_size, y_size))
    ax1 = fig.subplots()
    ax1.set_title(f"Fair Fight Wins - {host_name} {'vs' if guest_name != '' else ''} {guest_name}")
    sns.scatterplot(data=df_refined, x='totalKills', y='totalInVictimFovKills', ax=ax1, hue='fair_fights',cmap="coolwarm", )
    # for x, y, s, t, abb in zip(df_refined['totalKills'], df_refined['totalInVictimFovKills'], 
    #                               df_refined['alias'], df_refined['team_type'], df_refined['oppo_abbrev']):
    #     ax1.text(x+0.3, y, f"{s} ({abb})", alpha=0.6, color=(host_colour if t == 'host' else guest_colour))
    ax1.spines[['right', 'top']].set_visible(False)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc=legend_location);
    ax1.set_xlabel("Total Kills")
    ax1.set_ylabel("Total Kills in Victim FOV")
    