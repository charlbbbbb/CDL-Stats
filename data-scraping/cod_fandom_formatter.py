import pandas as pd

from cod_fandom_scraper import CodFandomPage

def format_to_pandas(page: CodFandomPage) -> pd.DataFrame:
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

def major_csv(major: int, week: int):
    cdf = CodFandomPage(major=major, week=week)
    cdf.parse_matches()
    outputted_df = format_to_pandas(cdf)
    outputted_df.to_csv(f"data\major{major}_week{week}.csv", index=False)



