from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

from tools import remove_empty_strings, add_teams_to_frame, check_event_exists
from fandom_errors import MajorNotPlayedError

class CodFandomPage:
    """
    The CodFandomPage Class allows for pages to be parsed and analysed
    """
    def __init__(self, major: int = 1, week: int = 1) -> None:
        check_event_exists(major=major, week=week)
        """
        Params:
            major (int): The major number
            week (int): The week of that majors qualifiers
        Return: None
        """
        self.major = major
        self.week = week
        self.url = self.construct_link()
        self.soup = self.fetch_data()
        self.matches = None
    
        

    def construct_link(self):
        """
        Desc: Construct a link to fetch the data from
        """
        # TODO: Implement the changing of 'major 6' to 'champs' for the links
        if self.major > 6 or self.week > 3:
            raise Exception("Week or major number is larger than expected")
        if self.week == 1:
            return f"https://cod-esports.fandom.com/wiki/Call_of_Duty_League/2023_Season/Major_{self.major}/Qualifiers/Scoreboards"
        else:
            return f"https://cod-esports.fandom.com/wiki/Call_of_Duty_League/2023_Season/Major_{self.major}/Qualifiers/Scoreboards/Week_{self.week}"
    
    def fetch_data(self):
        """
        Desc: Send a request to the site for the data
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    
    def clean_data(self):
        """
        Clean the data fetched from the site
        """
        gl = self.soup.text.replace('\n', '#').split('[showhide]')[1:]
        matches = [[gl[i], gl[i+1], gl[i+2], gl[i+3], gl[i+4]] for i in range(0, len(gl), 5)] 
        for match_index, match in enumerate(matches, 0):
            for game_index, game in enumerate(match, 0):
                matches[match_index][game_index] = remove_empty_strings(re.split('[#&/]', game))
        return matches
    
    def parse_matches(self):
        """
        Turn each match into a Match Object
        """
        self.fetch_data()
        self.matches = [Match(match) for match in self.clean_data()]
        if self.matches == []:
            raise MajorNotPlayedError
    
    
class Match:
    """
    The Match object contains data regarding a CDL map (also known as a series)
    """
    def __init__(self, raw_map_data):
        self.map1 = Map(raw_map_data[0])
        self.map2 = Map(raw_map_data[1])
        self.map3 = Map(raw_map_data[2])
        self.map4 = Map(raw_map_data[3])
        self.map5 = Map(raw_map_data[4])
        self.all_maps = [self.map1, self.map2, self.map3, self.map4, self.map5]
        self.winner = self.count_maps([cur_map.winner for cur_map in self.all_maps if cur_map is not None])
    
    def count_maps(self, arr):
        """
        Count the number of maps won in a series/match to determine the overall winner
        """
        counts = {}
        for value in arr:
            if value:
                try:
                    counts[value] += 1
                except:
                    counts[value] = 1
        return max(counts)




class Map:
    """
    The Map object contains information for individual maps within a series
    """
    def __init__(self, map_data: list) -> None:
        self.gamemode = None
        self.winner = None
        self.loser = None
        self.stats = None
        self.map_info = None
        if map_data[1] == 'DNP':
            pass
        else:
            self.map_information = remove_empty_strings('::'.join(map_data).split('\u2060\u2060')[0].split('::')[:7])
            self.team1_stats =  remove_empty_strings('::'.join(map_data).split('\u2060\u2060')[1].split('::'))
            self.team2_stats =  remove_empty_strings('::'.join(map_data).split('\u2060\u2060')[2].split('::'))
            self.parse_map_info()
            self.gamemode = self.map_info['mode'][0]
            if self.gamemode == ' Search and Destroy':
                self.parse_snd()
            elif self.gamemode == ' Hardpoint':
                self.parse_hardpoint()
            elif self.gamemode == ' Control':
                self.parse_control()
        
    def parse_map_info(self):
        """
        Desc: Parse the map info
        Params: None
        Return: None
        Impact: Adds data to the objects map_info attribute
        """
        frame = {'team1':[self.map_information[0]],
                'team2':[self.map_information[3]],
                'team1_score':[self.map_information[1]],
                'team2_score':[self.map_information[2]],
                'map':[self.map_information[4].replace('Map:', '')],
                'time':[self.map_information[5]],
                'mode':[self.map_information[6].replace('Mode:', '')]}

        if int(self.map_information[1]) > int(self.map_information[2]):
            self.winner = self.map_information[0]
            self.loser = self.map_information[3]
        else:
            self.winner = self.map_information[3]
            self.winner = self.map_information[0]

        self.map_info = pd.DataFrame(frame)
        
    def parse_hardpoint(self):
        """
        Desc: Parse the data for a hardpoint map
        Params: None
        Returns: None
        Impact: Adds data to self.stats
        """
        self.team2_stats = self.team2_stats[:20]
        frame = {'player':[],
                'kills': [],
                'deaths': [],
                'kd': [],
                'hill_time':[]}
        
        add_teams_to_frame(self, frame=frame, index='player', start_value=0, seperator=5)
        add_teams_to_frame(self, frame=frame, index='kills', start_value=1, seperator=5)
        add_teams_to_frame(self, frame=frame, index='deaths', start_value=2, seperator=5)
        add_teams_to_frame(self, frame=frame, index='kd', start_value=3, seperator=5)
        add_teams_to_frame(self, frame=frame, index='hill_time', start_value=4, seperator=5)
        
        #Impute some missing data
        for value in frame:
            if len(frame[value]) < 8:
                for i in range(8-len(frame[value])):
                    frame[value].append(0)

        self.stats = pd.DataFrame(frame)
    
    def parse_snd(self):
        """
        Desc: Parse the data for an SnD map
        Params: None
        Returns: None
        Impact: Adds data to self.stats
        """
        self.team2_stats = self.team2_stats[:32]
        self.team1_stats = self.team1_stats
        frame = {'player':[],
                'kills': [],
                'deaths': [],
                'kd': [],
                'first_kill':[],
                'first_death':[],
                'plant':[],
                'defuse':[]}

        add_teams_to_frame(self, frame=frame, index='player', start_value=0, seperator=8)
        add_teams_to_frame(self, frame=frame, index='kills', start_value=1, seperator=8)
        add_teams_to_frame(self, frame=frame, index='deaths', start_value=2, seperator=8)
        add_teams_to_frame(self, frame=frame, index='kd', start_value=3, seperator=8)
        add_teams_to_frame(self, frame=frame, index='first_kill', start_value=4, seperator=8)
        add_teams_to_frame(self, frame=frame, index='first_death', start_value=5, seperator=8)
        add_teams_to_frame(self, frame=frame, index='plant', start_value=6, seperator=8)
        add_teams_to_frame(self, frame=frame, index='defuse', start_value=7, seperator=8)

        #Impute some missing data
        for value in frame:
            if len(frame[value]) < 8:
                for i in range(8-len(frame[value])):
                    frame[value].append(0)

        self.stats = pd.DataFrame(frame)
    
    def parse_control(self):
        """
        Desc: Parse the data for a control map
        Params: None
        Returns: None
        Impact: Adds data to self.stats
        """
        self.team2_stats = self.team2_stats[:20]
        frame = {'player':[],
                'kills': [],
                'deaths': [],
                'kd': [],
                'captures':[]}
        
        add_teams_to_frame(self, frame=frame, index='player', start_value=0, seperator=5)
        add_teams_to_frame(self, frame=frame, index='kills', start_value=1, seperator=5)
        add_teams_to_frame(self, frame=frame, index='deaths', start_value=2, seperator=5)
        add_teams_to_frame(self, frame=frame, index='kd', start_value=3, seperator=5)
        add_teams_to_frame(self, frame=frame, index='captures', start_value=4, seperator=5)

        #Impute some missing data
        for value in frame:
            if len(frame[value]) < 8:
                for i in range(8-len(frame[value])):
                    frame[value].append(0)
        
        self.stats = pd.DataFrame(frame)





