from bbo_teams.models import Match, Pair, Player
from bbo_teams.workbook import get_named_range_values


def get_match_data(path: str) -> Match:
    named_ranges = get_named_range_values(path)
    match = Match()
    named_ranges = get_named_range_values(path)

    match.club_name = named_ranges["club_name"]
    match.opponents_club_name = named_ranges["opposition_club"]
    match.match_date = named_ranges["match_date"]

    match.our_pairs = []
    match.opps_pairs = []
    for i in range(4):
        match.our_pairs.append(
            Pair(
                player_a=Player(
                    name=named_ranges["our_players"][i][0],
                    username=named_ranges["our_players"][i][1],
                ),
                player_b=Player(
                    name=named_ranges["our_players"][i][2],
                    username=named_ranges["our_players"][i][3],
                ),
            )
        )
        match.opps_pairs.append(
            Pair(
                player_a=Player(
                    name=named_ranges["opps_players"][i][0],
                    username=named_ranges["opps_players"][i][1],
                ),
                player_b=Player(
                    name=named_ranges["opps_players"][i][2],
                    username=named_ranges["opps_players"][i][3],
                ),
            )
        )

    return match
