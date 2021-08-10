# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

from abc import ABC, abstractmethod
from typing import List
from .entities import Tab
from sublime import Settings, View  # type: ignore


class Setting(ABC):
    """A single setting relating to the package."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """Returns if the setting is enabled or not."""


class TabSetting(Setting):
    """A setting relating to one or more tabs."""

    settings: Settings

    def __init__(self, settings: Settings) -> None:
        """Initialise the setting instance with a copy
         of the sublime package settings.
         """
        self.settings = settings

    @abstractmethod
    def apply(self, tabs: List[Tab]) -> List[Tab]:
        """Applies the setting to the given list of tabs."""


class ShowCaptionsTabSetting(TabSetting):
    """Setting for showing captions on tabs."""
    def is_enabled(self) -> bool:
        return self.settings.get("show_captions") is True

    def apply(self, tabs: List[Tab]) -> List[Tab]:
        if self.is_enabled() is False:
            return tabs

        for tab in tabs:
            self._populate_captions(tab)
        return tabs

    def _populate_captions(self, tab: Tab) -> None:
        view: View = tab.get_view()
        if view.window().active_view().id() == view.id():
            tab.add_caption("Current File")

        if view.file_name() is None:
            tab.add_caption("Unsaved File")
        elif view.is_dirty():
            tab.add_caption("Unsaved Changes")

        if view.is_read_only():
            tab.add_caption("Read Only")


class IncludePathTabSetting(TabSetting):
    """Setting for including the path on tabs."""
    def is_enabled(self) -> bool:
        return self.settings.get("include_path") is True

    def apply(self, tabs: List[Tab]) -> List[Tab]:
        if self.is_enabled() is False:
            return tabs

        for tab in tabs:
            if tab.is_file_view() is True:
                tab.set_title(tab.get_subtitle())
        return tabs
