import asyncio
import os
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from playwright.async_api import async_playwright, expect


class IntegrationTest(StaticLiveServerTestCase):
    """Integration tests for the application."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls._loop)
        cls.playwright = cls._loop.run_until_complete(
            async_playwright().start(),
        )
        # use headless=False, slow_mo=200 to see the browser
        cls.browser = cls._loop.run_until_complete(
            cls.playwright.chromium.launch(),
        )
        cls.page = cls._loop.run_until_complete(cls.browser.new_page())

    def _run(self, coro):
        """Run an async coroutine in the test's event loop."""
        return self._loop.run_until_complete(coro)

    def setUp(self):
        """Set up test data for CustomList model."""
        self.credentials = {"username": "test", "password": "12345"}
        self.user = get_user_model().objects.create_user(**self.credentials)
        self._run(self.page.goto(f"{self.live_server_url}/"))
        self._run(
            self.page.get_by_placeholder("Enter your username").fill(
                self.credentials["username"],
            ),
        )
        self._run(
            self.page.get_by_placeholder("Enter your password").fill(
                self.credentials["password"],
            ),
        )
        self._run(self.page.get_by_role("button", name="Sign in").click())

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class."""
        super().tearDownClass()
        cls._loop.run_until_complete(cls.browser.close())
        cls._loop.run_until_complete(cls.playwright.stop())
        cls._loop.close()

    def test_season_progress_edit(self):
        """Test the progress edit of a season."""
        self._run(
            self.page.get_by_placeholder("Search tv shows...").fill("breaking bad")
        )
        self._run(self.page.get_by_role("button").nth(1).click())
        self._run(expect(self.page.locator("h2")).to_contain_text("Search Results"))
        self._run(self.page.get_by_title("Breaking Bad", exact=True).click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Breaking Bad"))
        self._run(self.page.get_by_title("Season 1").click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Season 1"))
        self._run(self.page.locator(".p-2").first.click())
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text("Track Episode")
        )
        self._run(self.page.locator(".relative > .px-2").first.click())
        self._run(self.page.get_by_role("button", name="Fill in air date").click())
        self._run(self.page.get_by_role("button", name="Add watch").click())

        datetime_format = "%Y-%m-%d"

        # Episode 1 air date is 2008-01-20
        fixed_date = date(2008, 1, 20)

        self._run(
            expect(self.page.get_by_role("main")).to_contain_text(
                f"Last watched: {fixed_date.strftime(datetime_format)}",
            ),
        )
        self._run(self.page.get_by_role("link", name="Home").click())
        self._run(expect(self.page.get_by_text("Breaking Bad S1")).to_be_visible())
        self._run(
            self.page.locator("#media-grid-in-progress-season")
            .get_by_role("button")
            .nth(4)
            .click(),
        )
        self._run(self.page.get_by_title("Breaking Bad S1").click())

        today = timezone.localtime().strftime(datetime_format)
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text(
                f"Last watched: {today}",
            ),
        )

    def test_tv_completed(self):
        """Test the completed status of a TV show."""
        self._run(self.page.get_by_placeholder("Search tv shows...").click())
        self._run(
            self.page.get_by_placeholder("Search tv shows...").fill("breaking bad")
        )
        self._run(
            self.page.locator("form")
            .filter(has_text="TV Shows TV")
            .get_by_role("button")
            .first.click(),
        )
        self._run(expect(self.page.locator("h2")).to_contain_text("Search Results"))
        self._run(self.page.get_by_title("Breaking Bad", exact=True).click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Breaking Bad"))
        self._run(self.page.locator("button").filter(has_text="Add to tracker").click())
        self._run(expect(self.page.locator("#track-tv-1396")).to_contain_text("Score"))
        self._run(self.page.get_by_label("Status").select_option("Completed"))
        self._run(self.page.get_by_role("button", name="Add", exact=True).click())
        self._run(self.page.get_by_role("link", name="TV Shows").click())
        self._run(self.page.get_by_role("link", name="Table View").click())
        self._run(expect(self.page.locator("tbody")).to_contain_text("62"))

    def test_season_completed(self):
        """Test the completed status of a season."""
        self._run(
            self.page.get_by_placeholder("Search tv shows...").fill("breaking bad")
        )
        self._run(self.page.get_by_role("button").nth(1).click())
        self._run(expect(self.page.locator("h2")).to_contain_text("Search Results"))
        self._run(self.page.get_by_title("Breaking Bad", exact=True).click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Breaking Bad"))
        self._run(self.page.get_by_title("Season 1").click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Season 1"))
        self._run(self.page.get_by_role("button", name="Add to tracker").click())
        self._run(
            expect(self.page.locator("#track-season-1396-1")).to_contain_text("Score"),
        )
        self._run(self.page.get_by_role("button", name="Add", exact=True).click())
        self._run(self.page.get_by_role("link", name="TV Seasons").click())
        self._run(self.page.get_by_role("link", name="Table View").click())
        self._run(expect(self.page.locator("tbody")).to_contain_text("Completed"))
        self._run(expect(self.page.locator("tbody")).to_contain_text("7"))

    def test_tv_manual(self):
        """Test the manual creation of a TV show."""
        # Create TV show
        self._run(self.page.get_by_role("link", name="Create Custom").click())
        self._run(self.page.get_by_placeholder("Enter title").click())
        self._run(self.page.get_by_placeholder("Enter title").fill("Friends"))
        self._run(self.page.get_by_placeholder("Enter image URL").click())
        self._run(
            self.page.get_by_placeholder("Enter image URL").fill(
                "https://media.themoviedb.org/t/p/w300_and_h450_bestv2/2koX1xLkpTQM4IZebYvKysFW1Nh.jpg",
            ),
        )
        self._run(self.page.get_by_role("combobox").select_option("In progress"))
        self._run(self.page.get_by_role("button", name="Create Entry").click())
        self._run(
            expect(self.page.locator(".scheme-dark")).to_contain_text(
                "Friends added successfully.",
            ),
        )

        # Create season
        self._run(self.page.get_by_role("button", name="Season").click())
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text("Parent TV Show"),
        )
        self._run(self.page.get_by_placeholder("Search for a TV show...").click())
        self._run(self.page.get_by_placeholder("Search for a TV show...").type("fri"))
        self._run(
            expect(self.page.locator("#parent-tv-results")).to_contain_text("Friends"),
        )
        self._run(self.page.get_by_role("button", name="Friends").click())
        self._run(self.page.get_by_placeholder("Enter image URL").click())
        self._run(
            self.page.get_by_placeholder("Enter image URL").fill(
                "https://media.themoviedb.org/t/p/w130_and_h195_bestv2/odCW88Cq5hAF0ZFVOkeJmeQv1nV.jpg",
            ),
        )
        self._run(self.page.get_by_role("button", name="Create Entry").click())
        self._run(
            expect(self.page.locator("body")).to_contain_text(
                "Friends S1 added successfully.",
            ),
        )

        # Create episode
        self._run(self.page.get_by_role("button", name="Episode").click())
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text("Parent Season"),
        )
        self._run(self.page.get_by_placeholder("Search for a season...").click())
        self._run(self.page.get_by_placeholder("Search for a season...").type("frien"))
        self._run(
            expect(self.page.locator("#parent-season-results")).to_contain_text(
                "Friends - Season 1",
            ),
        )
        self._run(self.page.get_by_role("button", name="Friends - Season").click())
        self._run(self.page.get_by_placeholder("Enter image URL").click())
        self._run(
            self.page.get_by_placeholder("Enter image URL").fill(
                "https://media.themoviedb.org/t/p/w227_and_h127_bestv2/v6Elr1W2elOyGi1MClgV0mIBVHC.jpg",
            ),
        )
        self._run(self.page.locator('input[name="end_date"]').fill("2025-03-07"))
        self._run(self.page.get_by_role("button", name="Create Entry").click())
        self._run(
            expect(self.page.locator("body")).to_contain_text(
                "Friends S1E1 added successfully.",
            ),
        )

        # Check visibility
        self._run(self.page.get_by_role("link", name="TV Shows").click())
        self._run(self.page.get_by_role("link", name="Grid View").click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Friends"))
        self._run(self.page.get_by_role("link", name="TV Seasons").click())
        self._run(self.page.get_by_role("link", name="Grid View").click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Friends S1"))
        self._run(self.page.get_by_role("link", name="TV Shows").click())
        self._run(self.page.get_by_title("Friends").click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Friends"))
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Season 1"))
        self._run(self.page.get_by_title("Season 1").click())
        self._run(expect(self.page.get_by_role("main")).to_contain_text("Season 1"))
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text(
                "Episode 1 • Unknown air date",
            ),
        )

    def test_obfuscate_unseen_episodes_enabled(self):
        """Test that obfuscate_unseen_episodes setting is accessible and functional."""
        # Navigate to preferences
        self._run(self.page.get_by_role("link", name="Settings").click())
        self._run(self.page.get_by_role("link", name="Preferences").click())

        # Verify the obfuscate setting is visible
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text(
                "Obfuscate Unseen Episodes",
            ),
        )
        self._run(
            expect(self.page.get_by_role("main")).to_contain_text(
                "unseen episode images and descriptions will be blurred",
            ),
        )

        # Find and check the obfuscate checkbox by clicking the label
        # The checkbox is sr-only (hidden), so we need to click the label
        obfuscate_label = self.page.locator(
            'label:has(input[name="obfuscate_unseen_episodes"])',
        )
        self._run(obfuscate_label.click())

        # Save preferences
        self._run(self.page.get_by_role("button", name="Save Preferences").click())

        # Verify success message
        self._run(
            expect(self.page.locator(".scheme-dark")).to_contain_text(
                "Settings updated"
            ),
        )

        # Verify setting persisted
        self._run(self.page.get_by_role("link", name="Preferences").click())
        obfuscate_checkbox = self.page.locator(
            'input[name="obfuscate_unseen_episodes"]',
        )
        self._run(expect(obfuscate_checkbox).to_be_checked())

    def test_obfuscate_unseen_episodes_disabled(self):
        """Test toggling obfuscate_unseen_episodes setting off."""
        # Navigate to preferences
        self._run(self.page.get_by_role("link", name="Settings").click())
        self._run(self.page.get_by_role("link", name="Preferences").click())

        # Find the obfuscate checkbox
        obfuscate_checkbox = self.page.locator(
            'input[name="obfuscate_unseen_episodes"]',
        )
        if self._run(obfuscate_checkbox.is_checked()):
            # Click the label to uncheck (checkbox is sr-only, so click label)
            obfuscate_label = self.page.locator(
                'label:has(input[name="obfuscate_unseen_episodes"])',
            )
            self._run(obfuscate_label.click())

            # Save preferences
            self._run(self.page.get_by_role("button", name="Save Preferences").click())

            # Verify success message
            self._run(
                expect(self.page.locator(".scheme-dark")).to_contain_text(
                    "Settings updated",
                ),
            )

            # Verify setting persisted as unchecked
            self._run(self.page.get_by_role("link", name="Preferences").click())
            obfuscate_checkbox = self.page.locator(
                'input[name="obfuscate_unseen_episodes"]',
            )
            self._run(expect(obfuscate_checkbox).not_to_be_checked())
