from dataclasses import dataclass


@dataclass
class Player:
    name: str = ""
    username: str = ""


@dataclass
class Pair:
    north_south: Player
    east_west: Player


@dataclass
class Match:
    club_name: str = ""
    opponents_club_name: str = ""
    match_date: str = ""
    our_players: list[Pair] = None
    opps_players: list[Pair] = None
