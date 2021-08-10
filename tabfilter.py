# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime  # type: ignore
import sublime_plugin  #type: ignore
from os import path
from typing import List, Tuple
from .entities import Tab
from .settings import TabSetting, ShowCaptionsTabSetting, IncludePathTabSetting


class TabFilterCommand(sublime_plugin.WindowCommand):
    """Provides a GoToAnything style interface for working with open tabs"""

    views: List[sublime.View] = []
    prefix: int = 0
    current_tab_idx: int = -1
    settings: sublime.Settings

    def run(self) -> None:
        """Shows a quick panel for tabs from the active window."""
        tabs = []
        self.views = []
        self.prefix = 0
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        self.current_tab_idx = -1
        tab_settings: Tuple[TabSetting, ...] = (
            ShowCaptionsTabSetting(self.settings),
            IncludePathTabSetting(self.settings)
        )

        idx: int = 0
        for view in self.window.views():
            self.views.append(view)
            if self.window.active_view().id() == view.id():
                # save index for later usage
                self.current_tab_idx = idx
            tabs.append(Tab(view))
            idx = idx + 1

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

        preview_tab: bool = self.settings.get("preview_tab", False)

        details: List[List[str]] = [entity.get_details() for entity in tabs]

        if preview_tab is True:
            # We can't support previewing the tab if there's
            # more than one window group
            preview_tab = self.window.num_groups() == 1

        if preview_tab is True:
            self.window.show_quick_panel(
                details,
                self.on_done,
                on_highlight=self.on_highlighted,
                selected_index=self.current_tab_idx
            )
            return

        self.window.show_quick_panel(details, self.on_done)

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
