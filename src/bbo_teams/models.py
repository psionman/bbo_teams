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
class Team:
    north: str
    south: str
    east: str
    west: str


@dataclass
class Match:
    club_name: str = ""
    opponents_club_name: str = ""
    match_date: str = ""
    our_pairs: list[Pair] = None
    opps_pairs: list[Pair] = None
    round: int = 0
    section: int = 0
    deal_files: list[str] = None
    our_teams: Team = None
    opps_teams: Team = None
    boards_per_round = "6"

    @property
    def title(self) -> str:
        return (
            f"{self.club_name} vs {self.opponents_club_name} - "
            f"Round {self.round} - Section {self.section}"
        )

    @property
    def description(self) -> str:
        return "+private+ +slow+"


# Seat plans for opponents
# Key: (round, section)
# Value: [opponent_pair_1, opponent_pair_2]
OPPS_SEAT_PLANS = {
    0: {
        0: [1, 0],
        1: [3, 2],
    },
    1: {
        0: [0, 1],
        1: [2, 3],
    },
    2: {
        0: [3, 2],
        1: [1, 0],
    },
    3: {
        0: [2, 3],
        1: [0, 1],
    },
}
