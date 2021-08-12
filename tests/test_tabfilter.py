# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime  # type: ignore
from unittesting import DeferrableTestCase  # type: ignore
from os import path
from unittest.mock import patch
from typing import List, Dict, Generator
try:
    import tabfilter
    from lib import settings, entities
except ImportError:
    # If we're running these tests in UnitTesting, then we need to use
    # The package name - Tab Filter - so let's grab import lib and try again.
    from importlib import import_module
    tabfilter = import_module(".tabfilter", "Tab Filter")
    settings = import_module(".lib.settings", "Tab Filter")
    entities = import_module(".lib.entities", "Tab Filter")

TabFilterCommand = tabfilter.TabFilterCommand

DEFAULT_SETINGS = settings.DEFAULT_SETINGS


class TabFilterCommandTestCase(DeferrableTestCase):
    """Tests the tab filter command works as expected."""

    settings: sublime.Settings
    layout: Dict[str, List]

    def setUp(self) -> None:
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        self.layout = sublime.active_window().layout()
        for setting in DEFAULT_SETINGS:
            self.settings.set(setting, DEFAULT_SETINGS[setting])

        # Close any existing views so as to avoid polluting the results.
        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.window().run_command("close_file")

    def tearDown(self) -> None:
        # Restore the original layout
        sublime.active_window().set_layout(self.layout)

        for view in sublime.active_window().views():
            view.window().focus_view(view)
            view.set_scratch(True)
            view.window().run_command("close_file")

    def test_gather_tabs_no_files(self) -> None:
        """Tests gathering tabs when there are no files."""
        window: sublime.Window = sublime.active_window()
        groups: List[int] = list(range(window.num_groups()))
        cmd: TabFilterCommand = TabFilterCommand(window)

        self.assertListEqual(
            [],
            cmd.gather_tabs(groups)
        )

    def test_gather_tabs_single_group(self) -> None:
        """Tests gathering tabs from a single group layout."""
        window: sublime.Window = sublime.active_window()
        view: sublime.View = window.new_file()
        view.set_scratch(True)
        groups: List[int] = list(range(window.num_groups()))

        cmd: TabFilterCommand = TabFilterCommand(window)

        self.assertListEqual(
            [entities.Tab(view)],
            cmd.gather_tabs(groups)
        )

    def test_gather_tabs_multiple_groups(self) -> None:
        """Tests gathering tabs from a multi-group layout."""
        window: sublime.Window = sublime.active_window()
        view: sublime.View = window.new_file()
        view.set_scratch(True)
        second_view: sublime.View = window.new_file()
        second_view.set_scratch(True)

        # 2 column layout
        layout: Dict[str, List] = {
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0]
        }

        sublime.active_window().set_layout(layout)
        sublime.active_window().set_view_index(second_view, group=1, idx=0)

        cmd: TabFilterCommand = TabFilterCommand(window)

        groups: List[int] = list(range(window.num_groups()))

        self.assertListEqual(
            [entities.Tab(view), entities.Tab(second_view)],
            cmd.gather_tabs(groups)
        )

    def test_gather_tabs_selected_group(self) -> None:
        """Tests gathering tabs from the selected layout."""
        window: sublime.Window = sublime.active_window()
        view: sublime.View = window.new_file()
        view.set_scratch(True)
        second_view: sublime.View = window.new_file()
        second_view.set_scratch(True)

        # 2 column layout
        layout: Dict[str, List] = {
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0]
        }

        sublime.active_window().set_layout(layout)
        sublime.active_window().set_view_index(second_view, group=1, idx=0)

        cmd: TabFilterCommand = TabFilterCommand(window)

        groups: List[int] = [second_view.sheet().group()]

        self.assertListEqual(
            [entities.Tab(second_view)],
            cmd.gather_tabs(groups)
        )

    def test_format_tabs(self) -> None:
        """Tests formatting tabs."""
        window: sublime.Window = sublime.active_window()
        view: sublime.View = window.new_file()
        view.set_scratch(True)

        cmd: TabFilterCommand = TabFilterCommand(window)

        tabs: List[entities.Tab] = [entities.Tab(view)]

        with patch.object(
                settings.CommonPrefixTabSetting,
                "apply",
                return_value=tabs
        ) as mock_apply:
            setting: settings.CommonPrefixTabSetting

            setting = settings.CommonPrefixTabSetting(
                self.settings,
                sublime.active_window()
            )

            details: List[List[str]] = [tab.get_details() for tab in tabs]

            self.assertEqual(
                details,
                cmd.format_tabs(tabs, (setting,))
            )
            mock_apply.assert_called_once_with(tabs)

    def test_display_quick_info_no_preview(self) -> None:
        """Tests displaying the quick info panel, without preview."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            cmd: TabFilterCommand = TabFilterCommand(window)

            tabs: List[List[str]] = [["untitled", "untitled"]]

            cmd.display_quick_info_panel(tabs, preview=False)

            mock_panel.assert_called_once_with(tabs, cmd.on_done)

    def test_display_quick_info_with_preview(self) -> None:
        """Tests displaying the quick info panel, with preview."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            cmd: TabFilterCommand = TabFilterCommand(window)

            tabs: List[List[str]] = [["untitled", "untitled"]]

            cmd.display_quick_info_panel(tabs, preview=True)

            mock_panel.assert_called_once_with(
                tabs,
                cmd.on_done,
                on_highlight=cmd.on_highlighted,
                selected_index=-1
            )

    @patch.object(settings.CommonPrefixTabSetting, "apply")
    @patch.object(settings.ShowGroupCaptionTabSetting, "apply")
    @patch.object(settings.ShowCaptionsTabSetting, "apply")
    @patch.object(settings.IncludePathTabSetting, "apply")
    def test_run(
        self,
        mock_common_prefix_apply,
        mock_group_caption_apply,
        mock_captions_apply,
        mock_include_path_apply
    ) -> None:
        """Tests the run method with a mocked set up."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()
            view: sublime.View = window.new_file()
            view.set_scratch(True)

            tabs: List[entities.Tab] = [entities.Tab(view)]
            details: List[List[str]] = [tab.get_details() for tab in tabs]

            mock_common_prefix_apply.return_value = tabs
            mock_group_caption_apply.return_value = tabs
            mock_captions_apply.return_value = tabs
            mock_include_path_apply.return_value = tabs

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            mock_common_prefix_apply.assert_called_once_with(tabs)
            mock_group_caption_apply.assert_called_once_with(tabs)
            mock_captions_apply.assert_called_once_with(tabs)
            mock_include_path_apply.assert_called_once_with(tabs)

            mock_panel.assert_called_once_with(details, cmd.on_done)

    @patch.object(settings.CommonPrefixTabSetting, "apply")
    @patch.object(settings.ShowGroupCaptionTabSetting, "apply")
    @patch.object(settings.ShowCaptionsTabSetting, "apply")
    @patch.object(settings.IncludePathTabSetting, "apply")
    def test_run_with_no_files(
        self,
        mock_common_prefix_apply,
        mock_group_caption_apply,
        mock_captions_apply,
        mock_include_path_apply
    ) -> None:
        """Tests the run method with a mocked set up and no files."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            tabs: List = []

            mock_common_prefix_apply.return_value = tabs
            mock_group_caption_apply.return_value = tabs
            mock_captions_apply.return_value = tabs
            mock_include_path_apply.return_value = tabs

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            mock_common_prefix_apply.assert_called_once_with(tabs)
            mock_group_caption_apply.assert_called_once_with(tabs)
            mock_captions_apply.assert_called_once_with(tabs)
            mock_include_path_apply.assert_called_once_with(tabs)

            mock_panel.assert_called_once_with([], cmd.on_done)

    def test_run_with_scratch_default_settings(self) -> None:
        """Test running with a scratch buffer and default settings."""
        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            view: sublime.View = window.new_file()
            view.set_scratch(True)

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run()

            expected: List[str] = [
                "untitled",
                "untitled",
                "Current File, Unsaved File"
            ]

            mock_panel.assert_called_once_with([expected], cmd.on_done)

    def test_run_with_file_default_settings(self) -> Generator[int, None, None]:
        """Test running with a file and default settings."""
        dir: str = path.dirname(__file__)

        fixture: str = path.normpath(
            path.join(dir, "./fixtures/foo.txt")
        )

        with patch.object(sublime.Window, "show_quick_panel") as mock_panel:
            window: sublime.Window = sublime.active_window()

            window.open_file(fixture)

            cmd: TabFilterCommand = TabFilterCommand(window)

            sublime.set_timeout(lambda: cmd.run(), 100)

            yield 100

            expected: List[str] = [
                "foo.txt",
                "...{}foo.txt".format(path.sep),
                "Current File"
            ]
            mock_panel.assert_called_once_with([expected], cmd.on_done)

    def test_run_with_active_group(self) -> Generator[int, None, None]:
        """Test running with active group restriction & defaults."""
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

            # 2 column layout
            layout: Dict[str, List] = {
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0]
            }

            window.set_layout(layout)
            window.set_view_index(foo_view, group=1, idx=0)
            window.set_view_index(scratch_view, group=0, idx=0)
            window.set_view_index(bar_view, group=0, idx=0)

            yield 100

            window.focus_view(bar_view)

            cmd: TabFilterCommand = TabFilterCommand(window)
            cmd.run(active_group_only=True)

            expected: List[List[str]] = [
                [
                    "bar.txt",
                    "...{}bar.txt".format(path.sep),
                    "Current File"
                ],
                [
                    "untitled",
                    "untitled",
                    "Unsaved File"
                ],
            ]

            mock_panel.assert_called_once_with(expected, cmd.on_done)

    def test_on_done_callback_with_valid_index(self) -> None:
        """Tests the on done callback works with valid selection."""
        index: int = 0

        with patch.object(sublime.Window, "focus_view") as mock_focus_view:
            window: sublime.Window = sublime.active_window()
            cmd: TabFilterCommand = TabFilterCommand(window)
            # add the view to the internal list
            cmd.views.append(window.new_file())
            cmd.on_done(index)

            mock_focus_view.assert_called_once_with(cmd.views[index])

    def test_on_done_callback_with_no_selection(self) -> None:
        """Tests the on done callback works with no selection and can restore
            the currently selected tab where available.
        """
        index: int = -1

        with patch.object(sublime.Window, "focus_view") as mock_focus_view:
            window: sublime.Window = sublime.active_window()
            cmd: TabFilterCommand = TabFilterCommand(window)
            # add the view to the internal list
            cmd.views.append(window.new_file())
            cmd.on_done(index)

            mock_focus_view.assert_not_called()

            # now ensure that if a current tab is supported,
            # we revert to showing that tab.
            cmd.current_tab_idx = 0
            cmd.on_done(index)
            mock_focus_view.assert_called_once_with(cmd.views[0])

    def test_on_done_callback_with_invalid_index(self) -> None:
        """Tests the on done callback handles invalid data."""

        with patch.object(sublime.Window, "focus_view") as mock_focus_view:
            window: sublime.Window = sublime.active_window()
            cmd: TabFilterCommand = TabFilterCommand(window)
            # Test values greatly below the minimum expected range.
            cmd.on_done(-100)
            mock_focus_view.assert_not_called()

            # Also test values greatly outside the expected range.
            cmd.on_done(100)
            mock_focus_view.assert_not_called()

    def test_on_highlighted_callback_with_valid_index(self) -> None:
        """Tests the on highlighted callback works with valid selection."""
        index: int = 0

        with patch.object(sublime.Window, "focus_view") as mock_focus_view:
            window: sublime.Window = sublime.active_window()
            cmd: TabFilterCommand = TabFilterCommand(window)
            # add the view to the internal list
            cmd.views.append(window.new_file())
            cmd.on_highlighted(index)

            mock_focus_view.assert_called_once_with(cmd.views[index])

    def test_on_highlighted_callback_with_invalid_index(self) -> None:
        """Tests the on highlighted callback handles invalid data."""

        with patch.object(sublime.Window, "focus_view") as mock_focus_view:
            window: sublime.Window = sublime.active_window()
            cmd: TabFilterCommand = TabFilterCommand(window)
            # Test values greatly below the minimum expected range.
            cmd.on_highlighted(-100)
            mock_focus_view.assert_not_called()

            # Also test values greatly outside the expected range.
            cmd.on_highlighted(100)
            mock_focus_view.assert_not_called()
