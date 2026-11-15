from playwright.sync_api import Locator, Page, expect

from bbo_teams.models import Match, Team

SEATS = ("north", "east", "south", "west")


class BboSeatTeams:
    def __init__(self, page):
        self.page = page
        pass

    def seat_teams(self, match: Match):
        self.login(match)
        page = self.page

        self._open_team_matches()
        page.get_by_role(
            "button", name="Create Team Match", exact=True
        ).click()
        popup = page.locator("team-match-properties-popup")

        self._complete_identity(popup, match)
        self._complete_options(page, popup, match)
        self._complete_seats(popup, match)

    def _open_team_matches(self) -> None:
        """Get to the Team Matches screen from wherever the session is."""
        page = self.page
        create = page.get_by_role(
            "button", name="Create Team Match", exact=True
        )
        if create.is_visible():
            return  # Already on the Team Matches screen

        lobby_button = page.get_by_role(
            "button", name="Team Matches", exact=True
        )
        if not lobby_button.is_visible():
            page.get_by_role(
                "button", name="Lobby"
            ).click()  # The →Lobby button
        lobby_button.click()
        expect(create).to_be_visible()

    def _complete_identity(self, popup: Locator, match: Match):
        popup.get_by_role("textbox").first.wait_for()
        popup.get_by_role("tab", name="Identification").click()
        popup.get_by_label("Title").fill(match.title)
        popup.get_by_label("Description").fill(match.description_text)
        popup.get_by_role("textbox", name="Team 1").fill(match.club_name)
        popup.get_by_role("textbox", name="Team 2").fill(
            match.opponents_club_name
        )

    def _complete_options(self, page: Page, popup: Locator, match: Match):

        popup.get_by_role("tab", name="Options").click()
        popup.get_by_role("radio", name="IMPs").check()
        popup.get_by_role("spinbutton", name="Number of Boards").fill(
            match.boards_per_round
        )

        popup.get_by_role(
            "checkbox", name="Allow kibitzers", exact=True
        ).uncheck()
        popup.get_by_role(
            "checkbox", name="Allow kibitzers to chat with players"
        ).uncheck()
        popup.get_by_role("checkbox", name="Allow Undos").uncheck()
        popup.get_by_role("checkbox", name="Barometer scoring").uncheck()

        popup.get_by_role("radio", name="Use saved deals").click()
        popup.get_by_role("button", name="Select folder").click()

        hand_popup = page.locator("hand-folder-select-popup")
        hand_popup.wait_for()

        # If deal file misspelled can be handled manually
        hand_popup.get_by_text(match.deal_file).click()
        hand_popup.get_by_role("button", name="Select", exact=True).click()
        hand_popup.locator("#modal-content-1").get_by_role(
            "button", name="Close"
        )

    def _fill_seats(self, popup: Locator, team: Team, group: int) -> None:
        """Fill one team's four seats; group 0 is the first set shown."""
        for seat in SEATS:
            popup.get_by_placeholder(seat.title(), exact=True).nth(group).fill(
                getattr(team, seat)
            )

    def _complete_seats(self, popup: Locator, match: Match) -> None:
        popup.get_by_role("tab", name="Reserve seats").click()
        self._fill_seats(popup, match.our_team, group=0)
        self._fill_seats(popup, match.opps_team, group=1)
