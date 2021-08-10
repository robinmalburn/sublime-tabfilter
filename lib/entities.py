# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

from os import path
from sublime import View  # type: ignore
from typing import Optional, List


class Tab(object):
    """Represent a Sublime tab and the relevant metadata."""
    view: View
    title: str = "untitled"
    subtitle: str = "untitle"
    is_file: bool = True
    path: Optional[str] = None
    captions: List[str] = []

    def __init__(self, view: View) -> None:
        """Initialise the Tab."""
        self.view = view
        self.captions = []

        name: Optional[str] = view.file_name()

        if name is None:
            # If the name is not set, then we're dealing with a buffer
            # rather than a file, so deal with it accordingly.
            self.is_file = False
            name = view.name()

            # set the view name to untitled if we get an empty name
            if len(name) == 0:
                name = "untitled"

        self.set_title(name)
        self.set_subtitle(name)

        if self.is_file is True:
            self.path = path.dirname(name)
            self.set_title(path.basename(name))

    def get_title(self) -> str:
        """Gets the title of the tab."""
        return self.title

    def set_title(self, title: str) -> None:
        """Sets the title of the tab."""
        self.title = title

    def get_subtitle(self) -> str:
        """Get the subtitle of the tab."""
        return self.subtitle

    def set_subtitle(self, subtitle: str) -> None:
        """Set the subtitle of the tab."""
        self.subtitle = subtitle

    def is_file_view(self) -> bool:
        """Gets whether the tab's view is a file or not."""
        return self.is_file

    def get_path(self) -> Optional[str]:
        """Gets the path for a view tab, or None otherwise."""
        return self.path

    def get_view(self) -> View:
        """Gets the view associated with the tab."""
        return self.view

    def add_caption(self, caption: str) -> None:
        """Adds the caption to the list of captions for this Tab."""
        self.captions.append(str(caption))

    def get_captions(self) -> List[str]:
        """Gets the current captions."""
        return self.captions[:]

    def get_details(self) -> List[str]:
        """Returns a list of tab details."""
        details: List[str] = [self.get_title(), self.get_subtitle()]

        captions: List[str] = self.get_captions()

        if len(captions) > 0:
            details.append(", ".join(captions))

        return details
