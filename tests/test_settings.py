# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime  # type: ignore
from unittesting import DeferrableTestCase  # type: ignore
from os import path
from typing import List, Tuple, Dict, Generator
try:
    from lib import settings, entities
except ImportError:
    # If we're running these tests in UnitTesting, then we need to use
    # The package name - Tab Filter - so let's grab import lib and try again.
    from importlib import import_module
    settings = import_module(".core.settings", "Tab Filter")
    entities = import_module(".core.entities", "Tab Filter")

ShowCaptionsTabSetting = settings.ShowCaptionsTabSetting
IncludePathTabSetting = settings.IncludePathTabSetting
Tab = entities.Tab

DEFAULT_SETINGS: Dict[str, bool] = {
    "show_captions": True,
    "include_path": False,
    "preview_tab": False
}


class ShowCaptionsTabSettingTestCase(DeferrableTestCase):
    """Tests the Show Captions Tab Settings."""

    settings: sublime.Settings

    def setUp(self) -> None:
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        for setting in DEFAULT_SETINGS:
            self.settings.set(setting, DEFAULT_SETINGS[setting])

        # Close any existing views so as to avoid polluting the results.
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.window().run_command("close_file")

    def tearDown(self) -> None:
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.set_scratch(True)
            view.window().run_command("close_file")

    def test_setting_disabled(self) -> None:
        """Tests with the setting disabled."""
        self.settings.set("show_captions", False)
        setting: ShowCaptionsTabSetting = ShowCaptionsTabSetting(self.settings)
        scratch_view: sublime.View = sublime.active_window().new_file()
        tabs: List[Tab] = [Tab(scratch_view)]

        self.assertFalse(setting.is_enabled())
        self.assertListEqual(tabs, setting.apply(tabs))
        self.assertListEqual([], tabs[0].get_captions())

    def test_current_file(self) -> Generator[int, None, None]:
        """Tests the setting with captions disabled."""
        setting: ShowCaptionsTabSetting = ShowCaptionsTabSetting(self.settings)

        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )
        bar_fixture: str = path.normpath(
            path.join(dir, "./fixtures/bar.txt")
        )

        foo_view: sublime.View = sublime.active_window().open_file(foo_fixture)
        bar_view: sublime.View = sublime.active_window().open_file(bar_fixture)

        data_set: Tuple[Tuple[List[Tab], List[List[str]], sublime.View], ...]

        data_set = (
            ([Tab(foo_view), Tab(bar_view)], [['Current File'], []], foo_view),
            ([Tab(foo_view), Tab(bar_view)], [[], ['Current File']], bar_view),
        )

        yield 100

        for (tabs, captions, view) in data_set:
            with self.subTest(tabs=tabs, captions=view, view=view):
                view.window().focus_view(view)
                self.assertTrue(setting.is_enabled())
                self.assertListEqual(tabs, setting.apply(tabs))
                actual = []
                for tab in tabs:
                    actual.append(tab.get_captions())
                self.assertListEqual(captions, actual)

    def test_unsaved_file(self) -> None:
        """Tests detecting unsaved files."""
        setting: ShowCaptionsTabSetting = ShowCaptionsTabSetting(self.settings)
        scratch_view: sublime.View = sublime.active_window().new_file()
        tabs: List[Tab] = [Tab(scratch_view)]

        self.assertTrue(setting.is_enabled())
        self.assertListEqual(tabs, setting.apply(tabs))
        self.assertListEqual(
            ["Current File", "Unsaved File"],
            tabs[0].get_captions()
        )

    def test_unsaved_changes(self) -> Generator[int, None, None]:
        """Tests detecting unsaved changes."""
        setting: ShowCaptionsTabSetting = ShowCaptionsTabSetting(self.settings)

        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        foo_view: sublime.View = sublime.active_window().open_file(foo_fixture)

        sublime.set_timeout(
            lambda: foo_view.run_command("insert", {"characters": "foo"}),
            100
        )

        yield 100

        tabs: List[Tab] = [Tab(foo_view)]

        self.assertTrue(setting.is_enabled())
        self.assertListEqual(tabs, setting.apply(tabs))
        self.assertListEqual(
            ["Current File", "Unsaved Changes"],
            tabs[0].get_captions()
        )

    def test_read_only(self) -> None:
        """Tests detecting read only views."""
        setting: ShowCaptionsTabSetting = ShowCaptionsTabSetting(self.settings)
        scratch_view: sublime.View = sublime.active_window().new_file()
        scratch_view.set_read_only(True)
        tabs: List[Tab] = [Tab(scratch_view)]

        self.assertTrue(setting.is_enabled())
        self.assertListEqual(tabs, setting.apply(tabs))
        self.assertListEqual(
            ["Current File", "Unsaved File", "Read Only"],
            tabs[0].get_captions()
        )


class IncludePathTabSettingTestCase(DeferrableTestCase):
    """Tests the Include path Tab Settings."""

    settings: sublime.Settings

    def setUp(self) -> None:
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        for setting in DEFAULT_SETINGS:
            self.settings.set(setting, DEFAULT_SETINGS[setting])

        # Close any existing views so as to avoid polluting the results.
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.window().run_command("close_file")

    def tearDown(self) -> None:
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.set_scratch(True)
            view.window().run_command("close_file")

    def test_setting_disabled(self) -> Generator[int, None, None]:
        """Tests with the setting disabled."""
        self.settings.set("include_path", False)
        setting: IncludePathTabSetting = IncludePathTabSetting(self.settings)

        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        expected = path.basename(foo_fixture)

        foo_view: sublime.View = sublime.active_window().open_file(foo_fixture)
        tabs: List[Tab] = [Tab(foo_view)]

        yield 100

        self.assertFalse(setting.is_enabled())
        self.assertListEqual(tabs, setting.apply(tabs))
        self.assertEqual(expected, tabs[0].get_title())
        self.assertEqual(foo_fixture, tabs[0].get_subtitle())

    def test_with_file_view(self) -> Generator[int, None, None]:
        """Tests with the setting disabled."""
        self.settings.set("include_path", True)
        setting: IncludePathTabSetting = IncludePathTabSetting(self.settings)

        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        foo_view: sublime.View = sublime.active_window().open_file(foo_fixture)
        tabs: List[Tab] = [Tab(foo_view)]

        yield 100

        self.assertTrue(setting.is_enabled())
        self.assertListEqual(tabs, setting.apply(tabs))
        self.assertEqual(foo_fixture, tabs[0].get_title())
        self.assertEqual(foo_fixture, tabs[0].get_subtitle())
