# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime
import sublime_plugin
from os import path
from typing import List
from .entities import Tab


class TabFilterCommand(sublime_plugin.WindowCommand):
    """Provides a GoToAnything style interface for working with open tabs"""

    views: List[sublime.View]
    prefix: int
    settings: sublime.Settings
    current_tab_idx: int = -1

    def run(self) -> None:
        """Shows a quick panel for tabs from the active window."""
        tabs = []
        self.views = []
        self.prefix = 0
        self.settings = sublime.load_settings("tabfilter.sublime-settings")
        self.current_tab_idx = -1

        idx: int = 0
        for view in self.window.views():
            self.views.append(view)
            if self.window.active_view().id() == view.id():
                # save index for later usage
                self.current_tab_idx = idx
            tabs.append(self.make_tab(view))
            idx = idx + 1

        common_prefix: str = path.commonprefix(
            [entity.path for entity in tabs if entity.is_file]
            )

        if path.isdir(common_prefix) is False:
            common_prefix = common_prefix[:common_prefix.rfind(path.sep)]
        self.prefix = len(common_prefix)

        show_captions: bool = self.settings.get("show_captions", True)
        include_path: bool = self.settings.get("include_path", False)
        preview_tab: bool = self.settings.get("preview_tab", False)

        details: List[List[str]] = [entity.get_details(self.prefix, include_path, show_captions) for entity in tabs]

        if preview_tab is True:
            # We can't support previewing the tab if there's
            # more than one window group
            preview_tab = self.window.num_groups() == 1

        if preview_tab is True:
            self.window.show_quick_panel(
                details,
                self._on_done,
                on_highlight=self._on_highlighted,
                selected_index=self.current_tab_idx
            )
            return

        self.window.show_quick_panel(details, self._on_done)

    def make_tab(self, view: sublime.View) -> Tab:
        """Makes a new Tab entity relating to the given view.
        Args:
            view (sublime.View): Sublime View to build the Tab from
        Returns (Tab): Tab entity containing metadata about the view.

        """
        name: str = view.file_name()
        is_file: bool = True

        # If the name is not set, then we're dealing with a buffer
        # rather than a file, so deal with it accordingly.
        if name is None:
            is_file = False
            name = view.name()
            # set the view name to untitled if we get an empty name
            if len(name) == 0:
                name = "untitled"

        entity: Tab = Tab(name, is_file)

        if self.window.active_view().id() == view.id():
            entity.add_caption("Current File")

        if view.file_name() is None:
            entity.add_caption("Unsaved File")
        elif view.is_dirty():
            entity.add_caption("Unsaved Changes")

        if view.is_read_only():
            entity.add_caption("Read Only")

        return entity

    def _on_done(self, index) -> None:
        """Callback handler to move focus to the selected tab index"""
        if index == -1 and self.current_tab_idx != -1:
            # If the selection was quit, re-focus the last selected Tab
            self.window.focus_view(self.views[self.current_tab_idx])
        elif index > - 1:
            self.window.focus_view(self.views[index])

    def _on_highlighted(self, index) -> None:
        """Callback handler to focuses the currently selected/highlighted Tab"""
        self.window.focus_view(self.views[index])
