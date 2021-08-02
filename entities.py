# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

from os import path
from typing import Optional, List


class Tab(object):
    """Represent a Sublime tab and the relevant metadata."""
    name: str
    is_file: bool = False
    path: Optional[str] = None
    captions: List[str] = []

    def __init__(self, name: str, is_file: bool = False) -> None:
        """Initialise the Tab."""
        self.name = name
        self.is_file = is_file
        self.captions = []

        if self.is_file is True:
            self.path = "{path}".format(
                path=path.dirname(path.abspath(self.name)),
            )

    def add_caption(self, caption: str) -> None:
        """Adds the caption to the list of captions for this Tab.
        Args:
            caption (str): Caption to add to the Tab's captions list.
        """
        self.captions.append(str(caption))

    def get_caption(self) -> str:
        """Returns the captions as a single, comma separated string."""
        return ", ".join(self.captions)

    def get_details(
        self,
        prefix_trim: int,
        include_path: bool = False,
        show_captions: bool = False
    ) -> List[str]:
        """Returns a list of tab details.
        Args:
            prefix_trim (int): Length of prefix to trim off of files.
            include_path (bool): Whether or not to include the path for files.
            show_caption (bool): Whether or not to include captions.
        Returns:
            list: List containing details about the Tab.
        """
        name: str = self.name
        short_name: str = self.name

        if self.is_file:
            name = path.basename(self.name)
            short_name = self.name[prefix_trim:]
            if prefix_trim > 0:
                short_name = "...{}".format(short_name)
            if include_path:
                name = short_name

        details: List[str] = [name, short_name]

        if show_captions:
            details.append(self.get_caption())

        return details
