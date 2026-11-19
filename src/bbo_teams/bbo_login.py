import re

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from bbo_teams.config import config
from bbo_teams.models import Match, WebSessionError

COOKIE_BUTTON = re.compile(r"accept|agree|allow", re.IGNORECASE)
COOKIE_TIMEOUT = 1000


class BboLogin:
    def __init__(self, page):
        self.page = page

    def login(self, match: Match) -> None:
        page = self.page
        try:
            page.goto(
                config.login_url, wait_until="domcontentloaded", timeout=30000
            )
            page.locator("#username").wait_for(timeout=15000)
        except PlaywrightTimeoutError as error:
            self.close()
            raise WebSessionError(
                "BBO did not load in time. Check your connection and "
                "try again."
            ) from error
        except PlaywrightError as error:
            self.close()
            raise WebSessionError(f"Could not reach BBO: {error}") from error

        self._accept_cookies()

        self._enter_credentials(match.username, match.password)
        page.wait_for_url(lambda url: "/auth/login" not in url)
        page.add_style_tag(content="body { zoom: 75%; }")

        self._set_preferences()
        self.logged_in = True

    def _enter_credentials(self, username: str, password: str) -> None:
        page = self.page
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#password").press("Enter")

    def _accept_cookies(self) -> None:
        """Click the cookie consent button if one appears."""
        button = self.page.get_by_role("button", name=COOKIE_BUTTON).first
        try:
            button.click(timeout=COOKIE_TIMEOUT)
        except PlaywrightTimeoutError:
            pass  # No banner this time

    def _set_preferences(self) -> None:
        """Set the preferences for the user."""
        page = self.page
        page.get_by_text("Account").nth(2).click()
        page.get_by_role("tab", name="Settings").click()

        if config.disable_sound:
            page.locator("settings-list-item").filter(
                has_text="Sound effects on"
            ).locator("ion-toggle").click()

        if config.disable_vugraph:
            page.locator(
                "div:nth-child(6) > settings-list-item:nth-child(3) > "
                ".setting > .setting_line > .setting_toggle_button > "
                ".ng-untouched"
            ).click()
