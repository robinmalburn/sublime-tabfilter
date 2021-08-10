# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime  # type: ignore
import sublime_plugin  # type: ignore
from os import path
from typing import List, Tuple
from .lib.entities import Tab
from .lib.settings import TabSetting, ShowCaptionsTabSetting, IncludePathTabSetting


class BaseTabFilter(sublime_plugin.WindowCommand):
    """Provides a GoToAnything style interface for searching and selecting open tabs."""
    views: List[sublime.View] = []
    prefix: int = 0
    current_tab_idx: int = -1
    settings: sublime.Settings

    def __init__(self, *args, **kwargs):
        """Initialises the tab filter instance and calls the parent command initialiser."""
        super().__init__(*args, **kwargs)
        self.views = []
        self.settings = sublime.load_settings("tabfilter.sublime-settings")

    def run(self):
        """Shows a quick panel to filter and select tabs from the active window."""

        # To be replaced with consistent abstract method when moving to Python 3 only implementation.
        raise NotImplementedError("Subclasses must implemented run method locally.")

    def gather_tabs(self, group_indexes):
        """Gather tabs from the given group indexes.
            Args:
                group_indexes (list[int]): A list of zero or more group indexes to retrieve tabs from.
            Returns (list[Tab]): A list of zero or more tabs from the given group indexes.
        """
        tabs = []
        idx = 0
        self.views = []
        for group_idx in group_indexes:
            for view in self.window.views_in_group(group_idx):
                self.views.append(view)
                if self.window.active_view().id() == view.id():
                    # save index for later usage
                    self.current_tab_idx = idx
                tabs.append(Tab(view))
                idx = idx + 1
        return tabs

    def format_tabs(self, tabs):
        """Formats tabs for display in the quick info panel.
            Args:
                tabs (list[Tab]): A list of one or more tabs for formating.
            Returns (list[list[str]]): Returns a list of lists containing the title, subtitle and
             captions for each quick info panel entry.
        """
        tab_settings: Tuple[TabSetting, ...] = (
            ShowCaptionsTabSetting(self.settings),
            IncludePathTabSetting(self.settings)
        )

        common_prefix: str = path.commonprefix(
            [entity.path for entity in tabs if entity.is_file]
            )

        if path.isdir(common_prefix) is False:
            common_prefix = common_prefix[:common_prefix.rfind(path.sep)]
        self.prefix = len(common_prefix)

        if self.prefix > 0:
            for tab in tabs:
                if tab.is_file_view():
                    tab.set_subtitle(f"...{tab.get_subtitle()[self.prefix:]}")

        for setting in tab_settings:
            tabs = setting.apply(tabs)

        return [entity.get_details() for entity in tabs]

    def display_quick_info_panel(self, tabs, preview):
        """Displays the quick info panel with the formatted tabs.
            Args:
                tabs (list[list[str]]): A list of lists containing the title, subtitle and captions for display.
        """
        if preview is True:
            self.window.show_quick_panel(
                tabs,
                self.on_done,
                on_highlight=self.on_highlighted,
                selected_index=self.current_tab_idx
            )
            return

        self.window.show_quick_panel(tabs, self.on_done)

    def on_done(self, index) -> None:
        """Callback handler to move focus to the selected tab index."""
        if index == -1 and self.current_tab_idx != -1:
            # If the selection was quit, re-focus the last selected Tab
            self.window.focus_view(self.views[self.current_tab_idx])
        elif index > -1 and index < len(self.views):
            self.window.focus_view(self.views[index])

    def on_highlighted(self, index) -> None:
        """Callback handler to focus the currently highlighted Tab."""
        if index > -1 and index < len(self.views):
            self.window.focus_view(self.views[index])


class TabFilterCommand(BaseTabFilter):
    """Provides a GoToAnything style interface for searching and selecting open tabs across all groups."""

    def run(self):
        """Shows a quick panel to filter and select tabs from the active window."""
        tabs = self.gather_tabs(range(self.window.num_groups()))

        preview: bool = (
            self.settings.get("preview_tab") is True
            and self.window.num_groups() == 1
        )

        self.display_quick_info_panel(
            self.format_tabs(tabs),
            preview
        )


class TabFilterActiveGroupCommand(BaseTabFilter):
    """Provides a GoToAnything style interface for searching and selecting open tabs within the active group."""

    def run(self):
        """Shows a quick panel to filter and select tabs from the active window."""
        tabs = self.gather_tabs([self.window.active_group()])

        self.display_quick_info_panel(
            self.format_tabs(tabs),
            self.settings.get("preview_tab") is True
        )