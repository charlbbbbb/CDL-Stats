import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import re


def read_number_range(start: int, end: int) -> pd.DataFrame:
    not_exist = []
    dataframes = []
    for i in range(start, end+1):
        try:
            dataframes.append(pd.read_csv(f"../data/cdl_{i}.csv"))
        except FileNotFoundError:
            not_exist.append(i)
    print(f"The following match IDs do not exist {not_exist}")
    df = pd.concat(dataframes)
    return df


def generate_outlier_score(column1, column2, method: str):
    col1_scores = (np.array([abs(round(a/b, 2)-1) if b > 0 else 0 for a, b in\
                         zip(column1, [column1.mean() if method.lower=='mean' else column1.median() for i in column1])]))
    col2_scores = (np.array([abs(round(a/b, 2)-1) if b > 0 else 0 for a, b in\
                         zip(column2, [column2.mean() if method.lower=='mean' else column2.median() for i in column2])]))
    
    return (col1_scores+col2_scores)/2


def declare_winner(df: pd.DataFrame) -> pd.DataFrame:
    df['map_winner'] = ["host" if a > b else "guest" for a, b in zip(df['matchGameResult.hostGameScore'], df['matchGameResult.guestGameScore'])]

    df['is_winner'] = ["Y" if a == b else "N" for a, b in zip(df['map_winner'], df['team_type'])]

    return df


def compare_stats(df: pd.DataFrame, col1:str , col2: str, title: str = None,
                   sens=None, hue_by="abbrev", gamemode=None, team=None,
                     size=(10, 10), show_winner=False, grid=True,
                     legend=True, outlier_method='mean', map=None,
                     pal=None, x_gap=0, hidden_spines=None, show_event=False):
    
    df = declare_winner(df)

    fig = plt.figure(figsize=size)
    ax1 = fig.subplots(ncols=1)

    if gamemode:
        df = df[df['gameMode'].isin([gamemode] if type(gamemode) == str else gamemode)]
    
    if team:
        df = df[df['abbrev'].isin([team] if type(team) == str else team)]
    
    if map:
        df = df[df['gameMap'].isin([map] if type(map) == str else map)]


    chosen_style = None
    if show_winner:
        chosen_style = 'is_winner'
    if show_event:
        chosen_style = 'event'
    sns.scatterplot(df, x=col1, y=col2, hue=hue_by, style=chosen_style, ax=ax1, 
                    palette = pal if pal else sns.color_palette("tab10"))
    ax1.set_title(title if title else f"{col1} vs {col2}")

    if grid:
        ax1.grid(True, alpha=0.4)

    if sens:
        outlier_scores = generate_outlier_score(df[col1], df[col2], outlier_method)
        for x, y, s, op, score in zip(df[col1], df[col2], df['alias'], df['oppo_abbrev'], outlier_scores):
            if score > sens:
                ax1.text(x+x_gap, y, f"{s} ({op})", color='black', alpha=0.65)

    if legend:
        ax1.legend(bbox_to_anchor=(-0.1, 1))
    
    if hidden_spines:
        ax1.spines[hidden_spines].set_visible(False)
    
    return fig


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


def get_matches(url):
    response = requests.get(url, headers=cdl_headers).text
    match_ids = []
    matches = re.findall('"match":{"id":[0-9]+', response)
    second_matches = re.findall('match/[0-9]+', response)
    second_matches = [i.split('/')[-1] for i in second_matches]
    matches.extend(second_matches)
    for match in matches:
        match_ids.append(match.split(':')[-1])
    return match_ids

def read_in_list(ids):
    frames = []
    for idd in ids:
        frames.append(pd.read_csv(f'../data/cdl_{idd}.csv'))
    return pd.concat(frames)

        
    



    

