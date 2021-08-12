# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime  # type: ignore
import sublime_plugin  # type: ignore
from typing import List, Tuple
from .lib.entities import Tab
from .lib.settings import (
    TabSetting,
    CommonPrefixTabSetting,
    ShowCaptionsTabSetting,
    IncludePathTabSetting,
    ShowGroupCaptionTabSetting,
)


class TabFilterCommand(sublime_plugin.WindowCommand):
    """Provides a GoToAnything style interface for
       searching and selecting open tabs.
    """
    window: sublime.Window
    views: List[sublime.View] = []
    current_tab_idx: int = -1
    settings: sublime.Settings

    def gather_tabs(self, group_indexes: List[int]) -> List[Tab]:
        """Gather tabs from the given group indexes."""
        tabs: List[Tab] = []
        idx: int = 0
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

    def format_tabs(
        self,
        tabs: List[Tab],
        formatting_settings: Tuple[TabSetting, ...]
    ) -> List[List[str]]:
        """Formats tabs for display in the quick info panel."""
        for setting in formatting_settings:
            tabs = setting.apply(tabs)

        return [entity.get_details() for entity in tabs]

    def display_quick_info_panel(
        self,
        tabs: List[List[str]],
        preview: bool
    ) -> None:
        """Displays the quick info panel with the formatted tabs."""
        if preview is True:
            self.window.show_quick_panel(
                tabs,
                self.on_done,
                on_highlight=self.on_highlighted,
                selected_index=self.current_tab_idx
            )
            return

        self.window.show_quick_panel(tabs, self.on_done)

    def on_done(self, index: int) -> None:
        """Callback handler to move focus to the selected tab index."""
        if index == -1 and self.current_tab_idx != -1:
            # If the selection was quit, re-focus the last selected Tab
            self.window.focus_view(self.views[self.current_tab_idx])
        elif index > -1 and index < len(self.views):
            self.window.focus_view(self.views[index])

    def on_highlighted(self, index: int) -> None:
        """Callback handler to focus the currently highlighted Tab."""
        if index > -1 and index < len(self.views):
            self.window.focus_view(self.views[index])

    def run(self, active_group_only=False) -> None:
        """Shows a quick panel to filter and select tabs from
            the active window.
        """
        self.views = []
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        
        groups: List[int] = [self.window.active_group()]

        if active_group_only is False:
            groups = list(range(self.window.num_groups()))

        tabs = self.gather_tabs(groups)

        preview: bool = self.settings.get("preview_tab") is True

        if active_group_only is False:
            preview = preview and self.window.num_groups() == 1

        formatting_settings: Tuple[TabSetting, ...] = (
            CommonPrefixTabSetting(self.settings, self.window),
            ShowGroupCaptionTabSetting(self.settings, self.window),
            ShowCaptionsTabSetting(self.settings, self.window),
            IncludePathTabSetting(self.settings, self.window),
        )

        self.display_quick_info_panel(
            self.format_tabs(tabs, formatting_settings),
            preview
        )
