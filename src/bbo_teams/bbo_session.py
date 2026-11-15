from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from bbo_teams.bbo_deal_files import BboDealFiles
from bbo_teams.bbo_login import BboLogin
from bbo_teams.bbo_players import BboPlayers
from bbo_teams.bbo_seat_teams import BboSeatTeams
from bbo_teams.models import Match

SESSION_FILE = Path("bbo_session.json")


class BboError(Exception):
    """A problem talking to BBO, with a message fit to show the user."""


class BboSession:
    """Own the browser so it stays open between button clicks."""

    def __init__(self, headless: bool = False) -> None:
        self._playwright = sync_playwright().start()
        self.logged_in = False
        self._browser = self._playwright.chromium.launch(headless=headless)
        try:
            self._context = self._browser.new_context(
                viewport={"width": 1700, "height": 900}
            )
            self.page = self._context.new_page()
        except PlaywrightError:
            self._playwright.stop()
            raise

        cdp = self._context.new_cdp_session(self.page)
        cdp.send("Emulation.setPageScaleFactor", {"pageScaleFactor": 0.75})
        self._context.storage_state(path=SESSION_FILE)

    def is_alive(self) -> bool:
        """True while the browser window is still open and responding."""
        try:
            self.page.evaluate("1")  # Raises if the window was closed
            return True
        except PlaywrightError:
            return False

    def close(self) -> None:
        """Close everything; safe to call more than once."""
        for step in (
            self._context.close,
            self._browser.close,
            self._playwright.stop,
        ):
            try:
                step()
            except PlaywrightError:
                pass  # Already closed, for example by you

    # =========================================================================
    # Login
    # =========================================================================

    def login(self, match: Match) -> None:
        if self.logged_in:
            return
        bbo_login = BboLogin(self.page)
        bbo_login.login(match)

    # =========================================================================
    # Seat teams methods
    # =========================================================================

    def seat_teams(self, match: Match):
        self.login(match)
        seat_teams = BboSeatTeams(self.page)
        seat_teams.seat_teams(match)

    # =========================================================================
    # Add players methods
    # =========================================================================

    def add_players(self, match: Match):
        self.login(match)
        bbo_players = BboPlayers(self.page)
        bbo_players.add_players(match)

    def remove_players(self, match: Match):
        self.login(match)
        bbo_players = BboPlayers(self.page)
        bbo_players.remove_players(match)

    # =========================================================================
    # Deal file upload methods
    # =========================================================================

    def upload_deal_files(self, match: Match) -> None:
        self.login(match)
        deal_files = BboDealFiles(self.page)
        deal_files.import_deal_files(match)


def get_session(existing_session: BboSession = None) -> BboSession:
    """Reuse the open session, or replace one you have closed."""
    session = existing_session
    if session is not None and not session.is_alive():
        session.close()  # Stops Playwright, so a new start() works
        session = None
    if session is None:
        session = BboSession()
    return session
