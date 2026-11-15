import re
import time
from pathlib import Path

from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from bbo_teams.config import config
from bbo_teams.models import Match

DEFAULT_NAME = "Untitled folder"
ROWS = ".listItem"
NAMES = f"{ROWS} p"
ADD = 'img[src="assets/icons/add.svg"]'
EDIT = 'img[src$="edit.svg"]'
DONE = 'img[src$="done.svg"]'
MODAL = "modal-content"
FIXED_FOLDER = "My favorite hands"
UPLOADED_TO = re.compile(r"uploaded into folder:(.+?) for username")
DELETE = 'img[src$="delete.svg"]'

TAG_INPUT_JS = """([value, tag]) => {
    const box = [...document.querySelectorAll('input')]
        .find(e => e.value === value);
    if (box) box.setAttribute('data-target', tag);
    return !!box;
}"""


def _exact(text: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*{re.escape(text)}\s*$")


class BboError(Exception):
    """A problem talking to BBO, with a message fit to show the user."""


class BboDealFiles:
    def __init__(self, page: Page) -> None:
        self.page = page

    def import_deal_files(self, match: Match) -> None:
        """Import each .lin file into a folder named after it."""
        self.login(match)
        self._open_deal_archive()

        existing = set(self._settled_folder_names())
        for deal_file in match.deal_files:
            if deal_file in existing:
                print(
                    f"Skipping {deal_file}: folder already exists", flush=True
                )
                continue
            self._import_into_new_folder(deal_file)
            existing.add(deal_file)
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

    def _folder_names(self) -> list[str]:
        return [n.strip() for n in self.page.locator(NAMES).all_inner_texts()]

    def _settled_folder_names(self, stable_ms: int = 1000) -> list[str]:
        """Return folder names once the list has stopped changing."""
        last = self._folder_names()
        stable_since = time.monotonic()
        deadline = stable_since + 10
        while time.monotonic() < deadline:
            self.page.wait_for_timeout(100)
            current = self._folder_names()
            if current != last:
                last, stable_since = current, time.monotonic()
            elif (time.monotonic() - stable_since) * 1000 >= stable_ms:
                break
        return last

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

        # At least one folder has the new name (an older one may exist too)
        expect(
            page.locator(NAMES).filter(has_text=_exact(name)).first
        ).to_be_visible()

    def remove_deal_files(self, match: Match) -> None:
        """Remove deal files from BBO."""
        self.login(match)
        self._open_deal_archive()

        folder_names = match.deal_files.copy()
        folder_names.append(DEFAULT_NAME)
        self._delete_deal_folders(folder_names, dry_run=False)

    def _delete_deal_folders(
        self, names: list[str], dry_run: bool = True
    ) -> None:
        """Delete every folder whose name is in `names`.

        With dry_run=True (the default) nothing is deleted; it only
        reports what would be.
        """
        existing = self._settled_folder_names()

        for name in names:
            if name == FIXED_FOLDER:
                print(f"Refusing to delete {name!r}", flush=True)
                continue
            found = existing.count(name)
            if found == 0:
                print(f"Not found: {name}", flush=True)
                continue
            if dry_run:
                print(f"Would delete {found} x {name}", flush=True)
                continue
            deleted = self._delete_folder(name)
            print(f"Deleted {deleted} x {name}", flush=True)

    def _delete_folder(self, name: str) -> int:
        """Delete every folder called `name`; return how many went."""
        page = self.page
        rows = page.locator(ROWS).filter(has_text=_exact(name))
        deleted = 0

        while rows.count() and deleted < 20:  # Cap guards against a loop
            before = rows.count()
            rows.first.locator(DELETE).click()

            # BBO asks for confirmation
            page.get_by_role("button", name="Yes", exact=True).click()

            # Wait until the row has really gone before looking again
            expect(rows).to_have_count(before - 1)
            deleted += 1
        return deleted
