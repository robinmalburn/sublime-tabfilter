# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime
from unittesting import DeferrableTestCase
from os import path
from unittest.mock import patch
from typing import List, Dict, Generator
try:
    import tabfilter
except ImportError:
    # If we're running these tests in UnitTesting, then we need to use
    # The package name - Tab Filter - so let's grab import lib and try again.
    from importlib import import_module
    tabfilter = import_module(".tabfilter", "Tab Filter")

TabFilterCommand = tabfilter.TabFilterCommand

DEFAULT_SETINGS: Dict[str, bool] = {
    "show_captions": True,
    "include_path": False,
    "preview_tab": False
}


class TabFilterCommandTestCase(DeferrableTestCase):
    """Tests the tab filter command works as expected."""

    views: List[sublime.View] = []
    settings: sublime.Settings

    def setUp(self) -> None:
        self.views = []
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        for setting in DEFAULT_SETINGS:
            self.settings.set(setting, DEFAULT_SETINGS[setting])

        # Close any existing views so as to avoid polluting the results.
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.window().run_command("close_file")

    def tearDown(self) -> None:
        for view in self.views:
            view.set_scratch(True)
            view.window().focus_view(view)
            view.window().run_command("close_file")

    def test_run_with_no_files(self) -> None:
        """Tests running with a single file."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            mock_panel.assert_called_once_with([], cmd._on_done)

    def test_run_with_scratch_and_captions(self) -> None:
        """Test running with a scratch buffer and captions enabled."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.new_file()
            view.set_scratch(True)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            expected: List[str] = [
                "untitled",
                "untitled",
                "Current File, Unsaved File"
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_scratch_and_path(self) -> None:
        """Test running with a scratch buffer and path enabled to ensure
        the setting results in no change to output."""
        self.settings.set("include_path", True)
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.new_file()
            view.set_scratch(True)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            expected: List[str] = [
                "untitled",
                "untitled",
                "Current File, Unsaved File"
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_scratch_and_read_only(self) -> None:
        """Test running with a scratch buffer and read only caption."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.new_file()
            view.set_scratch(True)
            view.set_read_only(True)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            expected: List[str] = [
                "untitled",
                "untitled",
                "Current File, Unsaved File, Read Only"
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_scratch_and_no_captions(self) -> None:
        """Test running with a scratch buffer and captions disabled."""
        self.settings.set("show_captions", False)
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.new_file()
            view.set_scratch(True)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            expected: List[str] = ["untitled", "untitled"]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_file_and_captions(self) -> Generator[int, None, None]:
        """Test running with a file and captions enabled."""
        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.open_file(fixture)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: cmd.run(), 100)

            yield 100

            expected: List[str] = [
                "foo.txt",
                "...{}foo.txt".format(path.sep),
                "Current File"
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_file_and_changes(self) -> Generator[int, None, None]:
        """Test running with a file and dirty caption."""
        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.open_file(fixture)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(
                lambda: view.run_command("insert", {"characters": "foo"}),
                100
            )

            yield 100

            cmd.run()

            expected: List[str] = [
                "foo.txt",
                "...{}foo.txt".format(path.sep),
                "Current File, Unsaved Changes"
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_file_and_no_captions(self) -> Generator[int, None, None]:
        """Test running with a file and captions disabled."""
        self.settings.set("show_captions", False)

        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.open_file(fixture)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: cmd.run(), 100)

            yield 100

            expected: List[str] = [
                "foo.txt",
                "...{}foo.txt".format(path.sep),
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_file_and_path(self) -> Generator[int, None, None]:
        """Test running with a file and path enabled."""
        self.settings.set("include_path", True)
        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.open_file(fixture)
            self.views.append(view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: cmd.run(), 100)

            yield 100

            expected: List[str] = [
                "...{}foo.txt".format(path.sep),
                "...{}foo.txt".format(path.sep),
                "Current File"
            ]
            mock_panel.assert_called_once_with([expected], cmd._on_done)

    def test_run_with_multiple_files(self) -> Generator[int, None, None]:
        """Test running with multiple files."""
        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        bar_fixture: str = path.normpath(
            path.join(dir, "./fixtures/bar.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            foo_view: sublime.View = window.open_file(foo_fixture)
            bar_view: sublime.View = window.open_file(bar_fixture)
            self.views.append(foo_view)
            self.views.append(bar_view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: window.focus_view(bar_view), 100)

            yield 100

            cmd.run()

            expected: List[List[str]] = [
                [
                    "foo.txt",
                    "...{}foo.txt".format(path.sep),
                    ""
                ],
                [
                    "bar.txt",
                    "...{}bar.txt".format(path.sep),
                    "Current File"
                ],
            ]
            mock_panel.assert_called_once_with(expected, cmd._on_done)

    def test_run_with_multiple_sources(self) -> Generator[int, None, None]:
        """Test running with multiple sources (files & buffers)."""
        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        bar_fixture: str = path.normpath(
            path.join(dir, "./fixtures/bar.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            scratch_view: sublime.View = window.new_file()
            foo_view: sublime.View = window.open_file(foo_fixture)
            bar_view: sublime.View = window.open_file(bar_fixture)
            self.views.append(scratch_view)
            self.views.append(foo_view)
            self.views.append(bar_view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: window.focus_view(foo_view), 100)

            yield 100

            cmd.run()

            expected: List[List[str]] = [
                [
                    "untitled",
                    "untitled",
                    "Unsaved File"
                ],
                [
                    "foo.txt",
                    "...{}foo.txt".format(path.sep),
                    "Current File"
                ],
                [
                    "bar.txt",
                    "...{}bar.txt".format(path.sep),
                    ""
                ],
            ]
            mock_panel.assert_called_once_with(expected, cmd._on_done)

    def test_run_with_preview(self) -> Generator[int, None, None]:
        """Test running with multiple sources (files & buffers)."""
        self.settings.set("preview_tab", True)

        dir: str = path.dirname(__file__)

        foo_fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        bar_fixture: str = path.normpath(
            path.join(dir, "./fixtures/bar.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            scratch_view: sublime.View = window.new_file()
            foo_view: sublime.View = window.open_file(foo_fixture)
            bar_view: sublime.View = window.open_file(bar_fixture)
            self.views.append(scratch_view)
            self.views.append(foo_view)
            self.views.append(bar_view)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: window.focus_view(foo_view), 100)

            yield 100

            cmd.run()

            expected: List[List[str]] = [
                [
                    "untitled",
                    "untitled",
                    "Unsaved File"
                ],
                [
                    "foo.txt",
                    "...{}foo.txt".format(path.sep),
                    "Current File"
                ],
                [
                    "bar.txt",
                    "...{}bar.txt".format(path.sep),
                    ""
                ],
            ]

            # Foo is the "Current File" above, so should be set
            # as our selected index.
            expected_index: int = 1

            mock_panel.assert_called_once_with(
                expected,
                cmd._on_done,
                on_highlight=cmd._on_highlighted,
                selected_index=expected_index
            )
