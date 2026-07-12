import asyncio
import os
import re

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
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
        # use headless=False, slow_mo=400 to see the browser
        cls.browser = cls._loop.run_until_complete(cls.playwright.chromium.launch())
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

    def test_blank_modal(self):
        """Test the blank modal for creating a list."""
        self._run(self.page.get_by_role("button", name="TV Shows").click())
        self._run(
            self.page.locator("li").filter(has_text=re.compile(r"^Anime$")).click(),
        )
        self._run(self.page.get_by_placeholder("Search anime...").fill("perfect blue"))
        self._run(
            self.page.locator("form")
            .filter(has_text="Anime TV")
            .get_by_role("button")
            .first.click(),
        )
        self._run(
            self.page.locator(
                ".absolute > .relative > button:nth-child(2)"
            ).first.click(),
        )
        self._run(
            expect(self.page.locator("#lists-anime-437")).to_contain_text(
                "You haven't created any lists yet.",
            ),
        )

    def test_flow(self):
        """Test the flow of adding an item to a list and editing the list."""
        # Create list
        self._run(self.page.get_by_role("link", name="Lists").click())
        self._run(self.page.get_by_role("button", name="New List").click())
        self._run(expect(self.page.locator("h2")).to_contain_text("Create New List"))
        self._run(self.page.locator("#id_name").click())
        self._run(self.page.locator("#id_name").fill("test"))
        self._run(self.page.get_by_role("button", name="Create List").click())
        self._run(
            expect(
                self.page.locator("#lists-grid div")
                .filter(has_text="T 0 items")
                .nth(1),
            ).to_be_visible(),
        )

        # Add item to list
        self._run(self.page.get_by_role("button", name="TV Shows").click())
        self._run(
            self.page.locator("li").filter(has_text=re.compile(r"^Anime$")).click(),
        )
        self._run(self.page.get_by_placeholder("Search anime...").click())
        self._run(self.page.get_by_placeholder("Search anime...").fill("perfect blue"))
        self._run(
            self.page.locator("form")
            .filter(has_text="Anime TV")
            .get_by_role("button")
            .first.click(),
        )
        self._run(
            self.page.locator(
                ".absolute > .relative > button:nth-child(2)"
            ).first.click(),
        )
        self._run(
            expect(self.page.locator("#lists-anime-437")).to_contain_text(
                "Lists test Add",
            ),
        )
        self._run(self.page.get_by_role("button", name="Add", exact=True).click())
        self._run(
            expect(self.page.locator("#lists-anime-437")).to_contain_text("Remove"),
        )
        self._run(
            self.page.locator("#lists-anime-437").get_by_role("button").first.click()
        )

        # Edit list
        self._run(self.page.get_by_role("link", name="Lists").click())
        self._run(
            expect(
                self.page.locator("#lists-grid div").filter(has_text="T 1 item").nth(1),
            ).to_be_visible(),
        )
        self._run(self.page.get_by_role("button", name="Edit list").click())
        self._run(
            expect(self.page.locator("#lists-grid")).to_contain_text("Edit List"),
        )
        self._run(self.page.locator("#id_1_name").click())
        self._run(self.page.locator("#id_1_name").fill("test rename"))
        self._run(self.page.get_by_role("button", name="Save").click())
