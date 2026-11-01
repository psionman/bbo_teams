import re
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, expect, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from bbo_teams import logger
from bbo_teams.config import config
from bbo_teams.models import Match, Team

LOGIN_URL = "https://www.bridgebase.com/v3/auth/login"
SESSION_FILE = Path("bbo_session.json")


STARTS_PATTERN = re.compile(
    r"Starts:\s*(\w{3}, \d{1,2} \w{3} \d{4}, \d{1,2}:\d{2})"
)

COOKIE_BUTTON = re.compile(r"accept|agree|allow", re.IGNORECASE)
COOKIE_TIMEOUT = 1000
SEATS = ("north", "east", "south", "west")

DEFAULT_NAME = "Untitled folder"
ROWS = ".listItem"
NAMES = f"{ROWS} p"
ADD = 'img[src="assets/icons/add.svg"]'
EDIT = 'img[src$="edit.svg"]'
DONE = 'img[src$="done.svg"]'
MODAL = "modal-content"
FIXED_FOLDER = "My favorite hands"
UPLOADED_TO = re.compile(r"uploaded into folder:(.+?) for username")


TAG_INPUT_JS = """([value, tag]) => {
    const box = [...document.querySelectorAll('input')]
        .find(e => e.value === value);
    if (box) box.setAttribute('data-target', tag);
    return !!box;
}"""


def upload_deal_files(self, match: Match) -> None:
    self.login(match)
    page = self.page

    page.get_by_text("Account").nth(2).click()
    page.get_by_text("Deal archive").click()

    try:
        page.get_by_text(FIXED_FOLDER, exact=True).wait_for(timeout=20000)
    except PlaywrightTimeoutError as error:
        raise BboError("The deal archive did not load.") from error

    for deal_file in match.deal_files:
        self._create_named_folder(deal_file)
        self._import_lin_file(deal_file)


def _exact(text: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*{re.escape(text)}\s*$")


def _first_difference(before: list[str], after: list[str]) -> int:
    for index, name in enumerate(after):
        if index >= len(before) or before[index] != name:
            return index
    return len(after) - 1


def accept_cookies(page: Page) -> None:
    """Click the cookie consent button if one appears."""
    button = page.get_by_role("button", name=COOKIE_BUTTON).first
    try:
        button.click(timeout=COOKIE_TIMEOUT)
    except PlaywrightTimeoutError:
        pass  # No banner this time


class BboError(Exception):
    """A problem talking to BBO, with a message fit to show the user."""


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

    def login(self, match: Match) -> None:
        page = self.page
        try:
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            page.locator("#username").wait_for(timeout=15000)
        except PlaywrightTimeoutError as error:
            self.close()
            raise BboError(
                "BBO did not load in time. Check your connection and "
                "try again."
            ) from error
        except PlaywrightError as error:
            self.close()
            raise BboError(f"Could not reach BBO: {error}") from error

        accept_cookies(page)

        self._enter_credentials(match.username, match.password)
        page.wait_for_url(lambda url: "/auth/login" not in url)
        page.add_style_tag(content="body { zoom: 75%; }")
        self._context.storage_state(path=SESSION_FILE)

    def _enter_credentials(self, username: str, password: str) -> None:
        page = self.page
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#password").press("Enter")

    def seat_teams(self, match: Match):
        self.login(match)
        page = self.page

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

    def add_players(self, match: Match):
        self.login(match)
        page = self.page
        page.get_by_text("People").first.click()
        for pair in [*match.our_pairs, *match.opps_pairs]:
            self._add_username(pair.player_a.username)
            self._add_username(pair.player_b.username)

    def _add_username(self, username: str) -> None:
        page = self.page
        page.get_by_role("textbox", name="Add Friend").click()
        page.get_by_role("textbox", name="Add Friend").fill(username)
        page.get_by_role("button", name="Add").click()

    # =========================================================================
    # Deal file upload methods
    # =========================================================================

    def upload_deal_files(self, match: Match) -> None:
        """Import each .lin file into a folder named after it."""
        self.login(match)
        self._open_deal_archive()
        for deal_file in match.deal_files:
            self._import_into_new_folder(deal_file)
        self.page.wait_for_timeout(500)
        self.page.close()

    def _open_deal_archive(self) -> None:
        """Open the archive and press "+" so the folder list appears."""
        page = self.page
        page.locator("tab-bar-button:visible").filter(
            has_text="Account"
        ).click()

        tab = page.get_by_role("tab", name="Deal archive")
        arrow = page.locator(".mat-mdc-tab-header-pagination-after")
        for _ in range(4):  # The tab strip scrolls sideways
            try:
                tab.click(timeout=2000)
                break
            except PlaywrightTimeoutError:
                arrow.click(timeout=2000)
        else:
            raise BboError("Could not open the Deal archive tab.")
        expect(tab).to_have_attribute("aria-selected", "true")
        page.get_by_role("heading", name="SELECT FOLDER").wait_for(
            timeout=20000
        )

        page.locator(ADD).first.click()
        expect(self._default_rows().first).to_be_visible(timeout=20000)

    def _default_rows(self) -> Locator:
        return self.page.locator(ROWS).filter(has_text=DEFAULT_NAME)

    def _import_into_new_folder(self, deal_file: str) -> None:
        page = self.page
        rows = self._default_rows()
        if rows.count() == 0:
            page.locator(ADD).first.click()
            expect(rows.first).to_be_visible()

        # Click a default-named folder, as you do by hand
        folder_name = rows.first.locator("p").inner_text().strip()
        rows.first.locator("p").click()

        button = page.get_by_role("button", name="Import LIN file")
        expect(button).to_be_enabled(timeout=10000)
        button.click()

        uploaded_to = self._upload(deal_file)
        if uploaded_to == deal_file:
            return  # BBO made the folder from the folder-name box
        if uploaded_to != folder_name:
            raise BboError(
                f"Import went to {uploaded_to!r}, not {folder_name!r}."
            )
        self._rename_default_folder(folder_name, deal_file)

    def _upload(self, deal_file: str) -> str:
        """Upload the .lin file; return the folder BBO says it used."""
        page = self.page
        frame = page.locator(f"{MODAL} iframe").content_frame
        file_input = frame.locator('input[name="srcfile"]')
        file_input.wait_for(timeout=10000)

        # With nothing selected the form has a folder-name box; use it
        title = frame.locator('input[name="title"]')
        if title.count():
            title.fill(deal_file)

        file_input.set_input_files(
            Path(config.deal_directory, f"{deal_file}.lin")
        )
        frame.locator('input[name="Import"]').evaluate("el => el.click()")

        body = frame.locator("body")
        try:
            expect(body).to_contain_text(
                "uploaded into folder:", timeout=30000
            )
        except AssertionError as error:
            raise BboError(
                f"No upload confirmation:\n{body.inner_text()[:300]}"
            ) from error
        result = body.inner_text()

        page.get_by_role("button", name="Close", description="Close").click()
        expect(page.locator(MODAL)).to_have_count(0)

        found = UPLOADED_TO.search(result)
        if not found:
            raise BboError(f"Could not read BBO's reply:\n{result[:300]}")
        return found.group(1).strip()

    def _rename_default_folder(self, default_name: str, name: str) -> None:
        """Rename the first default-named folder to `name`."""
        page = self.page
        self._default_rows().first.locator(EDIT).click()

        page.wait_for_function(
            TAG_INPUT_JS, arg=[default_name, "folder-name"], timeout=5000
        )
        box = page.locator('[data-target="folder-name"]')
        box.fill(name)
        expect(box).to_have_value(name)
        box.evaluate("el => el.removeAttribute('data-target')")
        page.locator(DONE).click()

        expect(
            page.locator(NAMES).filter(has_text=_exact(name))
        ).to_have_count(1)
