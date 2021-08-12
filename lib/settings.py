# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

from abc import ABC, abstractmethod
from typing import List, Dict, Union
from .entities import Tab
from sublime import Settings, View, Window  # type: ignore
from os import path

DEFAULT_SETINGS: Dict[str, Union[bool, str]] = {
    "show_captions": True,
    "include_path": False,
    "preview_tab": False,
    "show_group_caption": False,
}


class Setting(ABC):
    """A single setting relating to the package."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """Returns if the setting is enabled or not."""


class TabSetting(Setting):
    """A setting relating to one or more tabs."""

    settings: Settings
    window: Window

    def __init__(self, settings: Settings, window: Window) -> None:
        """Initialise the setting instance with a copy
         of the sublime package settings.
         """
        self.settings = settings
        self.window = window

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


class ShowGroupCaptionTabSetting(TabSetting):
    """Setting for showing captions on tabs."""
    def is_enabled(self) -> bool:
        return (
            self.settings.get("show_group_caption") is True
            and self.window.num_groups() > 1
        )

    def apply(self, tabs: List[Tab]) -> List[Tab]:
        if self.is_enabled() is False:
            return tabs

        for tab in tabs:
            view: View = tab.get_view()
            # Group's are zero based, so lets add 1 one to the offset
            # to make them a bit more human friendly.
            group: int = view.sheet().group() + 1
            tab.add_caption(f"Group: {group}")
        return tabs


class CommonPrefixTabSetting(TabSetting):
    """Setting for truncating the common prefix on files."""
    def is_enabled(self) -> bool:
        # There's currently no support for opting out of this "setting".
        return True

    def apply(self, tabs: List[Tab]) -> List[Tab]:
        if self.is_enabled() is False:
            return tabs

        prefix: int = 0
        common_prefix: str = path.commonprefix(
            [
                tab.get_path()
                for tab in tabs
                if tab.is_file_view()
            ]
        )

        if path.isdir(common_prefix) is False:
            common_prefix = common_prefix[:common_prefix.rfind(path.sep)]
        prefix = len(common_prefix)

        if prefix > 0:
            for tab in tabs:
                if tab.is_file_view():
                    tab.set_subtitle(f"...{tab.get_subtitle()[prefix:]}")
        return tabs
