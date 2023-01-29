class MajorNotPlayedError(Exception):
    """
    An error for when the inputted event is yet to be played
    """
    def __init__(self) -> None:
        super().__init__("The major and week combination is valid but is yet to be played/have data uploaded\n")

class MajorDoesNotExistError(Exception):
    """
    An error for when the inputted event does not exist
    """
    def __init__(self) -> None:
        super().__init__("Please enter a valid major/week combination\n")