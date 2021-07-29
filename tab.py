# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

from os import path

class Tab(object):
	"""Represent a Sublime tab and the relevant metadata."""

	def __init__(self, name, is_file = False):
		"""Initialise the Tab."""
		self.name = name
		self.is_file = is_file
		self.path = None
		self.captions = []

		if self.is_file is True:
			self.path = "{path}".format(
				path=path.dirname(path.abspath(self.name)),
			)

	def add_caption(self, caption):
		"""Adds the caption to the list of captions for this Tab.
		Args:
			caption (str): Caption to add to the Tab's captions list.
		"""
		self.captions.append(str(caption))

	def get_caption(self):
		"""Returns the captions as a single, comma separated string."""
		return ", ".join(self.captions)

	def get_details(self, prefix_trim, include_path, show_captions):
		"""Returns a list of tab details.
		Args:
			prefix_trim (int): Length of prefix to trim off of Tabs that are files.
			include_path (bool): Whether or not to include the path for Tabs are files.
			show_caption (bool): Whether or not to include captions in the details.
		Returns:
			list: List containing details about the Tab.
		"""
		name = self.name
		short_name = self.name

		if self.is_file:
			name = path.basename(self.name)
			short_name = self.name[prefix_trim:]
			if prefix_trim > 0:
				short_name = "...{}".format(short_name)
			if include_path:
				name = short_name

		details = [name, short_name]

		if show_captions:
			details.append(self.get_caption())

		return details