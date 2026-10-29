from dataclasses import dataclass


@dataclass
class Player:
    name: str = ""
    username: str = ""


@dataclass
class Pair:
    player_a: Player
    player_b: Player


@dataclass
class Match:
    club_name: str = ""
    opponents_club_name: str = ""
    match_date: str = ""
    our_pairs: list[Pair] = None
    opps_pairs: list[Pair] = None
    deal_files: list[str] = None
