from datetime import date, datetime
from pathlib import Path

from bbo_teams.config import config
from bbo_teams.models import Match, Pair, Player
from bbo_teams.workbook import get_named_range_values


def get_match_data(path: str) -> Match:
    named_ranges = get_named_range_values(path)
    match = Match()
    named_ranges = get_named_range_values(path)

    match.club_name = named_ranges["club_name"]
    match.opponents_club_name = named_ranges["opposition_club"]
    match.match_date = _parse_date(named_ranges["match_date"])
    match.deal_files = [deal[0] for deal in named_ranges["deal_files"]]
    bbo_logins = named_ranges["bbo_logins"]

    match.bbo_usernames = []
    match.bbo_passwords = []
    match.bbo_usernames.append(bbo_logins[0][0])
    match.bbo_passwords.append(bbo_logins[0][1])
    if bbo_logins[1][0] and bbo_logins[1][1]:
        match.bbo_usernames.append(bbo_logins[1][0])
        match.bbo_passwords.append(bbo_logins[1][1])
    else:
        match.bbo_usernames.append(bbo_logins[0][0])
        match.bbo_passwords.append(bbo_logins[0][1])

    match.our_pairs = _get_pairs(named_ranges["our_players"])
    match.opps_pairs = _get_pairs(named_ranges["opps_players"])

    errors = _validate_data(match)
    return match, errors


def _get_pairs(players: list[tuple[str, str]]) -> list[Pair]:
    pairs = []
    for i in range(0, len(players)):
        pairs.append(
            Pair(
                player_a=Player(
                    name=players[i][0] or "",
                    username=players[i][1],
                ),
                player_b=Player(
                    name=players[i][2] or "",
                    username=players[i][3],
                ),
            )
        )
    return pairs


def _parse_date(text: str, fmt: str = "%d %B %Y") -> date | None:
    """Return the date, or None if text isn't a valid date in this format."""
    if isinstance(text, date):
        return text
    try:
        return datetime.strptime(text.strip(), fmt).date()
    except ValueError:
        return None


def _validate_data(match: Match) -> list[str]:
    errors = []
    if not match.club_name:
        errors.append("Club name is required")
    if not match.opponents_club_name:
        errors.append("Opponents club name is required")
    if not match.match_date:
        errors.append("Match date invalid or missing")

    if not match.bbo_usernames[0]:
        errors.append("BBO username missing")
    if not match.bbo_passwords[0]:
        errors.append("BBO password missing")

    errors.extend(_validate_players(match.our_pairs, "Our"))
    errors.extend(_validate_players(match.opps_pairs, "Opponents"))

    for deal_file in match.deal_files:
        file_path = Path(config.deal_directory, f"{deal_file}.lin")
        if not file_path.exists():
            errors.append(f"Deal file {deal_file} not found")
    return errors


def _validate_players(pairs: list[Pair], team: str) -> list[str]:
    errors = []
    if len(pairs) < 4:
        errors.append(f"{team} pairs are required (at least 4)")
    else:
        for i, pair in enumerate(pairs):
            if not pair.player_a.username:
                errors.append(
                    f"{team} pair {i + 1} player A username is required"
                )
            if not pair.player_b.username:
                errors.append(
                    f"{team} pair {i + 1} player B username is required"
                )
    return errors
