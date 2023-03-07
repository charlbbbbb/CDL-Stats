import pandas as pd

from fandom_errors import MajorDoesNotExistError

def remove_empty_strings(data):
    """
    Small function to remove empty strings from a list
    """
    return [i for i in data if i != '']

def add_teams_to_frame(map, frame: dict, index: str, start_value: int, seperator: int):
        """
        Function used to add information for both teams of a match to a map object
        """
        for i in range(start_value, len(map.team1_stats), seperator):
            frame[index].append(map.team1_stats[i])
        for i in range(start_value, len(map.team2_stats), seperator):
            frame[index].append(map.team2_stats[i])

def cast_column_to_float(df: pd.DataFrame, col_name: str):
    """
    Function to cast a dataframe column to float datatype
    This removes the need to type the below code repeatedly
    """
    df[col_name] = df[col_name].astype('float')
    return df

def check_event_exists(major:int, week: int) -> None:
    """
    A function to check the week and major inputs 
    to ensure that it is a valid event
    """
    # This function could return a a boolean value however the error message
    # can be included within this function to stop people from re-writing it
    # for every instance where a major and week combination is enetered 
    # --------------------------------------------------------------------------
    # The format for this dict is major: number of qualifying weeks in the major
    valid_events = {1: 2,
                    2: 3,
                    3: 3,
                    4: 3,
                    5: 3}
    try:
        valid_events[major]
        if week > 0 and week <= valid_events[major]:
            pass
        else:
            raise MajorDoesNotExistError
    except KeyError:
        raise MajorDoesNotExistError
    