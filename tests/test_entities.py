# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime  # type: ignore
from os import path
from unittest import TestCase
from typing import List, Tuple, Optional
try:
    from lib import entities
except ImportError:
    # If we're running these tests in UnitTesting, then we need to use
    # The package name - Tab Filter - so let's grab import lib and try again.
    from importlib import import_module
    entities = import_module(".lib.entities", "Tab Filter")

Tab = entities.Tab


class TabTestCase(TestCase):
    """Tests the tab entity works as expected."""

    def setUp(self) -> None:
        # Close any existing views so as to avoid polluting the results.
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.window().run_command("close_file")

    def tearDown(self) -> None:
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.set_scratch(True)
            view.window().run_command("close_file")

    def test_initialisation(self) -> None:
        """Test initialising a Tab."""
        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )
        scratch_view: sublime.View = sublime.active_window().new_file()
        file_view: sublime.View = sublime.active_window().open_file(fixture)

        dataset: Tuple[Tuple[sublime.View, str, bool, Optional[str]], ...] = (
            (scratch_view, "untitled", False, None),
            (file_view, path.basename(fixture), True, path.dirname(fixture))
        )

        for (view, name, is_file, pathname) in dataset:
            with self.subTest(
                view=view,
                name=name,
                is_file=is_file,
                pathname=pathname
            ):
                entity: Tab = Tab(view)
                self.assertEquals(name, entity.get_title())
                self.assertEquals(bool(is_file), entity.is_file_view())
                self.assertEquals(pathname, entity.get_path())

    def test_get_title(self) -> None:
        """Tests getting the title of the Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertEquals("untitled", entity.get_title())

    def test_get_subtitle(self) -> None:
        """Tests getting the subtitle of the Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertEquals("untitled", entity.get_subtitle())

    def test_set_title(self) -> None:
        """Tests setting the title of the Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertEquals("untitled", entity.get_title())
        entity.set_title("foo")
        self.assertEquals("foo", entity.get_title())

    def test_set_subtitle(self) -> None:
        """Tests setting the subtitle of the Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertEquals("untitled", entity.get_subtitle())
        entity.set_subtitle("foo")
        self.assertEquals("foo", entity.get_subtitle())

    def test_is_file_view(self) -> None:
        """Tests checking whether the Tab's view is a file or not."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertEquals(False, entity.is_file_view())

        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        file_view: sublime.View = sublime.active_window().open_file(fixture)

        entity = Tab(file_view)
        self.assertEquals(True, entity.is_file_view())

    def test_get_path(self) -> None:
        """Tests getting the path for a Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertEquals(None, entity.get_path())

        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        file_view: sublime.View = sublime.active_window().open_file(fixture)

        entity = Tab(file_view)
        expected: str = path.dirname(fixture)
        self.assertEquals(expected, entity.get_path())

    def test_get_view(self) -> None:
        """Tests getting the underlying view for a Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        self.assertIs(scratch_view, entity.get_view())

    def test_add_caption(self) -> None:
        """Test adding captions to a Tab."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        # Ensure we start with no captions.
        self.assertListEqual([], entity.get_captions())

        entity.add_caption("bar")

        # Ensure a regular caption can be added.
        self.assertListEqual(["bar"], entity.get_captions())

        entity.add_caption("baz")

        # Ensure additional captions can be added.
        self.assertListEqual(["bar", "baz"], entity.get_captions())

        second_scratch_view: sublime.View = sublime.active_window().new_file()

        entity = Tab(second_scratch_view)

        entity.add_caption(123)  # type: ignore

        # Ensure captions are stringified
        self.assertListEqual(["123"], entity.get_captions())

    def test_get_captions(self) -> None:
        """Tests getting the captions for a Tab"""
        scratch_view: sublime.View = sublime.active_window().new_file()
        entity: Tab = Tab(scratch_view)

        self.assertListEqual([], entity.get_captions())
        entity.add_caption("test")
        self.assertListEqual(["test"], entity.get_captions())

    def test_get_details_caption_configuration(self) -> None:
        """Test getting details for a Tab with various caption settings."""
        scratch_view: sublime.View = sublime.active_window().new_file()

        entity: Tab = Tab(scratch_view)

        details: List[str] = entity.get_details()

        # Without captions at all.
        self.assertListEqual(["untitled", "untitled"], details)

        details = entity.get_details()

        # With empty captions.
        self.assertListEqual(["untitled", "untitled"], details)

        entity.add_caption("bar")

        # With bespoke captions.
        details = entity.get_details()

        self.assertListEqual(["untitled", "untitled", "bar"], details)

        entity.add_caption("baz")

        details = entity.get_details()

        self.assertListEqual(["untitled", "untitled", "bar, baz"], details)
