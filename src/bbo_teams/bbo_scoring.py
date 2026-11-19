import re

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from bbo_teams.config import config
from bbo_teams.models import Match, WebSessionError

TWO_DAYS = 2 * 24 * 60 * 60


ROUND = re.compile(r"Round\s+(\d+)", re.IGNORECASE)


class BboScore:
    def __init__(self, page):
        self.page = page

    def scoring(self, match: Match):
        usernames = [
            match.our_pairs[0].player_a.username,
            match.our_pairs[-1].player_a.username,
        ]
        start_time = int(match.match_date.timestamp())
        end_time = start_time + TWO_DAYS

        page = self.page
        self._display_page(config.scoring_url)

        page.get_by_role("textbox", name="Username").fill(match.username)
        page.get_by_role("textbox", name="Password").fill(match.password)
        page.get_by_role("button", name="Login").click()

        scores = {}
        for section, username in enumerate(usernames):
            url = (
                f"{config.scoring_url}"
                f"?username={username}"
                f"&start_time={start_time}"
                f"&end_time={end_time}"
            )

            self._display_page(url)
            section_score = self._get_round_scores(match)
            scores[section + 1] = (
                section_score  # match named ranges in spreadsheet
            )
        return scores

    def _display_page(self, url: str) -> None:
        page = self.page
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_load_state("networkidle")
        except PlaywrightTimeoutError as error:
            self.close()
            raise WebSessionError(
                "Session did not load in time. Check your connection and "
                "try again."
            ) from error
        except PlaywrightError as error:
            self.close()
            raise WebSessionError(f"Could not reach {url}: {error}") from error

    def _get_round_scores(self, match: Match) -> dict[int, float | None]:
        """Return {round number: score} from the tourneySummary rows.

        `match_name` limits it to one match, e.g. "NBC vs Woodborough2".
        """
        match_name = f"{match.club_name} vs {match.opponents_club_name}"
        page = self.page
        page.locator("tr.tourneySummary").first.wait_for(timeout=15000)
        rows = page.locator("tr.tourneySummary").evaluate_all(
            """rows => rows.map(r => [
                r.querySelector('.tourneyName')?.innerText ?? '',
                r.querySelector('.tourneyScore')?.innerText ?? '',
            ])"""
        )

        scores: dict[int, float | None] = {}
        for name, score in rows:
            if match_name.lower() not in name.lower():
                continue
            found = ROUND.search(name)
            if not found:
                continue
            text = score.replace(
                "\xa0", ""
            ).strip()  # The cell can hold &nbsp;
            scores[int(found.group(1))] = int(float(text)) if text else 0
        return scores
