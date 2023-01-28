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