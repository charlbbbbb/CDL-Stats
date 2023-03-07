import configparser

def read_config() -> configparser.ConfigParser:
    """
    Reads the config file into configparser.ConfigParser object
    """
    conf = configparser.ConfigParser()
    conf.read('config.ini')
    return conf

config = read_config()
DATA_SAVE_LOCATION = config['SAVE SETTINGS']['data_location']