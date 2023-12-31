"""
Implements the class responsible for pretty printing to scores.json

Status: Working
"""

from json import dumps
from re import compile as recompile


class ScoresEncoder:
    """
    Class to allow for pretty printing of scores.json.
    Puts the list of bomb cords on its own line.

    Could probably be improved to more dynamic,
    since currently you need to be very careful when changing the data in scores.json.
    """

    @classmethod
    def default(cls, obj):
        """The function that should be called to utilize the encoder."""
        new_str = dumps(obj, indent=4)
        new_str = cls._postProcess(new_str)
        return new_str

    @staticmethod
    def _postProcess(json_str: str):
        """
        Takes the string and does the main part of the formatting.
        Making sure the cord list is all on one line.
        """
        # These regexes could be a problem if you ever
        # decide to save other data in a list in a list.
        # could be addressed by perhaps checking
        # if what comes after is a cord aka. [[int, int]]
        open_pattern = recompile(r"\s*\[\s*\[")
        close_pattern = recompile(r"\]\s*\]")

        open_matches = open_pattern.finditer(json_str)
        close_matches = close_pattern.finditer(json_str)

        new_str = ""
        end = 0  # here to allow for last_end to be assigned
        while True:
            try:
                last_end = end
                start = next(open_matches).start()
                end = next(close_matches).end()
            except StopIteration:
                break

            sub_str = json_str[start:end]

            sub_str = sub_str.replace("\n", "")
            sub_str = sub_str.replace(" ", "")

            sub_str = " " + sub_str  # puts list on new line and indents it

            new_str += json_str[last_end:start] + sub_str
        new_str += json_str[last_end:]
        return new_str
