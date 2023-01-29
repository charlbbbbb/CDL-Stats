import pandas as pd

from cod_fandom_scraper import CodFandomPage

def create_match_id(map_info: pd.DataFrame, major: int, week: int) -> str:
    team1_abbrev = ''.join([i[0] for i in map_info['team1'][0].split()])
    team2_abbrev = ''.join([i[0] for i in map_info['team2'][0].split()])
    match_id = f"{team1_abbrev}{team2_abbrev}W{week}M{major}"
    return match_id

def long_format_to_pandas(page: CodFandomPage) -> pd.DataFrame:
    """
    Desc: This function formats a CodFandomPage object into a 
          dataframe so that the data can be easily read
    Params:
        page (CodFandomPage)
    Returns: Pandas df
    """
    total_df = None
    for match in page.matches:
        for map in match.all_maps:
            if map.map_info is not None and map.stats is not None:
                outer_frame = {'team1': [map.map_info['team1'][0]],
                                'team2': [map.map_info['team2'][0]],
                                'team1_score': [int(map.map_info['team2_score'][0])],
                                'team2_score': [int(map.map_info['team1_score'][0])],
                                'map': [map.map_info['map'][0]],
                                'time': [map.map_info['time'][0]],
                                'mode': [map.map_info['mode'][0]]}
            
                for player_num in range(8):
                    player_stats = map.stats.transpose().to_numpy()[:,player_num]
                    match_columns = map.stats.columns
                    for index, column in enumerate(match_columns):
                        outer_frame[f"{column}_{player_num+1}"] = [player_stats[index]]

                total_df = pd.concat([total_df, pd.DataFrame(outer_frame)])
    return total_df


def short_format_to_pandas(page: CodFandomPage, major: int, week:int ) -> pd.DataFrame:
    total_df = None
    for match in page.matches:
        for map in match.all_maps:
            if map.map_info is not None and map.stats is not None:
                #This could be functionalised but I cba :)
                #kd is being used to measure lengths as it is persistent in all dataframes and
                #looks better than writing df.columns.values[0]
                team_1_df = map.stats.iloc[0:4].copy().reset_index()
                team_1_df['team_name'] = [map.map_info['team1'][0] for i in range(len(team_1_df['kd']))]
                team_1_df['team_score'] = [map.map_info['team1_score'][0] for i in range(len(team_1_df['kd']))]

                team_2_df = map.stats.iloc[4:].copy().reset_index()
                team_2_df['team_name'] = [map.map_info['team2'][0] for i in range(len(team_2_df['kd']))]
                team_2_df['team_score'] = [map.map_info['team2_score'][0] for i in range(len(team_2_df['kd']))]
                
                if map.map_info['team1_score'][0] > map.map_info['team2_score'][0]:
                    team_1_df['outcome'] = ['winner' for i in range(len(team_1_df['kd']))]
                    team_2_df['outcome'] = ['loser' for i in range(len(team_2_df['kd']))]
                else:
                    team_2_df['outcome'] = ['winner' for i in range(len(team_2_df['kd']))]
                    team_1_df['outcome'] = ['loser' for i in range(len(team_1_df['kd']))]
                
                both_team_stats = pd.concat([team_1_df, team_2_df])
                both_team_stats['matchID'] = [create_match_id(map.map_info, major, week) for i in range(len(both_team_stats['kd']))]
                both_team_stats['map_winner'] = [map.map_info['map'][0] for i in range(len(both_team_stats['kd']))]
                both_team_stats['mode'] = [map.map_info['mode'][0].replace(' ', '') for i in range(len(both_team_stats['kd']))]
                both_team_stats['gametime'] = [map.map_info['time'][0] for i in range(len(both_team_stats['kd']))]
                both_team_stats['match_winner'] = [map.winner for i in range(len(both_team_stats['kd']))]
                total_df = pd.concat([total_df, both_team_stats])
    return total_df

            
            

            


    


def major_csv(major: int, week: int, format: str = 'long') -> None:
    cdf = CodFandomPage(major=major, week=week)
    cdf.parse_matches()
    if format.lower() == 'short':
        output_df = short_format_to_pandas(cdf, major, week)
    elif format.lower() == 'long':
        output_df = long_format_to_pandas(cdf)
    output_df.to_csv(f"data/major{major}_week{week}_{format}.csv", index=False)


major_csv(2, 1, 'short')




