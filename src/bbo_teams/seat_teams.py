import re
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from bbo_teams import logger
from bbo_teams.models import Match, Team

LOGIN_URL = "https://www.bridgebase.com/v3/auth/login"
SESSION_FILE = Path("bbo_session.json")


STARTS_PATTERN = re.compile(
    r"Starts:\s*(\w{3}, \d{1,2} \w{3} \d{4}, \d{1,2}:\d{2})"
)

COOKIE_BUTTON = re.compile(r"accept|agree|allow", re.IGNORECASE)
COOKIE_TIMEOUT = 1000
SEATS = ("north", "east", "south", "west")


def accept_cookies(page: Page) -> None:
    """Click the cookie consent button if one appears."""
    button = page.get_by_role("button", name=COOKIE_BUTTON).first
    try:
        button.click(timeout=COOKIE_TIMEOUT)
    except PlaywrightTimeoutError:
        pass  # No banner this time


class BboSession:
    """Own the browser so it stays open between button clicks."""

    def __init__(self, headless: bool = False) -> None:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        try:
            self._context = self._browser.new_context(
                viewport={"width": 1700, "height": 900}
            )
        except Exception as e:
            logger.error(f"Failed to create browser context: {e}")
            raise
        self.page: Page = self._context.new_page()
        # Set Chromium page zoom to 75%
        cdp = self._context.new_cdp_session(self.page)
        cdp.send("Emulation.setPageScaleFactor", {"pageScaleFactor": 0.75})

    def login(self, username: str, password: str) -> None:
        page = self.page
        page.goto(LOGIN_URL)
        accept_cookies(page)
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#password").press("Enter")
        page.wait_for_url(lambda url: "/auth/login" not in url)
        page.add_style_tag(content="body { zoom: 75%; }")
        self._context.storage_state(path=SESSION_FILE)

    def seat_teams(self, match: Match):
        page = self.page
        print(page)

        page.get_by_role("button", name="Team Matches").click()
        page.get_by_role("button", name="Create Team Match").click()
        popup = page.locator("team-match-properties-popup")
        print(type(popup))

        self._complete_identity(popup, match)
        self._complete_options(page, popup, match)
        self._complete_seats(popup, match)

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

    def print_tags(self):
        page = self.page
        page.wait_for_timeout(2000)
        page.screenshot(path="after_click.png")

        tags = page.evaluate(
            """() => [...new Set(
                [...document.querySelectorAll('*')]
                    .map(e => e.tagName.toLowerCase())
                    .filter(t => t.includes('-'))
            )]"""
        )
        Path("tags.txt").write_text("\n".join(sorted(tags)))
        Path("page.html").write_text(page.content())
        print("done", flush=True)
