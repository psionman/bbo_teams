import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from bbo_teams.models import Match


class BboPlayers:
    def __init__(self, page):
        self.page = page

    def add_players(self, match: Match):
        page = self.page
        page.get_by_text("People").first.click()
        for pair in [*match.our_pairs, *match.opps_pairs]:
            self._add_username(pair.player_a.username)
            self._add_username(pair.player_b.username)
        page.close()

    def _add_username(self, username: str) -> None:
        page = self.page
        page.get_by_role("textbox", name="Add Friend").click()
        page.get_by_role("textbox", name="Add Friend").fill(username)
        page.get_by_role("button", name="Add").click()
        print(f"Added {username}", flush=True)
        page.wait_for_timeout(100)

    def remove_players(self, match: Match) -> None:
        """Remove players from BBO."""
        usernames = [
            username
            for pair in [*match.our_pairs, *match.opps_pairs]
            for username in (pair.player_a.username, pair.player_b.username)
        ]
        self._open_people()
        for username in usernames:
            self._remove_username(username)

    def _open_people(self) -> None:
        """Open People and make sure the toggle is switched on."""
        page = self.page
        page.get_by_text("People").first.click()

        toggle = page.locator("ion-toggle")
        toggle.wait_for()
        if not toggle.evaluate("el => el.checked"):  # Click only if off
            toggle.click()
        page.wait_for_function(
            "() => document.querySelector('ion-toggle')?.checked",
            timeout=5000,
        )

    def _remove_username(self, username: str) -> None:
        """Unfollow one player, skipping anyone who isn't in the list."""
        page = self.page
        player = page.get_by_role(
            "button",
            name=re.compile(f"^{re.escape(username)}$", re.IGNORECASE),
        )
        try:
            player.wait_for(timeout=1000)
        except PlaywrightTimeoutError:
            print(f"Not in the list: {username}", flush=True)
            return
        print(f"Found player: {player}", flush=True)

        player.click(button="right")
        page.get_by_role("menuitem", name="Unfollow", exact=True).click()
        expect(player).to_have_count(0)  # Gone from the list
        print(f"Unfollowed {username}", flush=True)

    def list_people(self) -> list[str]:
        """Return the names in the People list, in the order shown."""
        page = self.page
        before = set(self._button_names())  # Lobby buttons, menus and so on

        self._open_people()
        page.wait_for_timeout(1000)  # Let the list render

        # Players are buttons too, so keep only the ones that are new
        names = [n for n in self._button_names() if n not in before]
        return list(dict.fromkeys(names))  # Remove duplicates, keep order

    def _button_names(self) -> list[str]:
        """Return the first line of every visible button's text."""
        texts = self.page.get_by_role("button").all_inner_texts()
        return [t.strip().split("\n")[0] for t in texts if t.strip()]
