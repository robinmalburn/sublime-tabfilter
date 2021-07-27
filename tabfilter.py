# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

import sublime
import sublime_plugin
import os
try:
	#Python 3 / ST3 relative import within package.
	from . import tab
except ValueError:
	#Python 2 / ST2 fallback for relative import.
	import tab

class BaseTabFilter(sublime_plugin.WindowCommand):
	"""Provides a GoToAnything style interface for searching and selecting open tabs."""

	window = None
	views = None
	settings = None
	current_tab_idx = -1
	prefix = ""
	show_group_caption = False
	group_caption_prefix = "Group:"
	preview_tab = False

	def __init__(self, *args, **kwargs):
		"""Initialises the tab filter instance and calls the parent command initiaser."""
		super().__init__(*args, **kwargs)
		self.window = sublime.active_window()
		self.views = []
		self.settings = sublime.load_settings("tabfilter.sublime-settings")
		self.group_caption_prefix = str(self.settings.get("group_caption", type(self).group_caption_prefix))
		self.show_group_caption = self.settings.get("show_group_caption", type(self).show_group_caption)
		self.preview_tab = self.settings.get("preview_tab", type(self).preview_tab)

	def run(self):
		"""Shows a quick panel to filter and select tabs from the active window"""

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
				tabs.append(self.make_tab(view, group_idx))
				idx = idx + 1
		return tabs

	def format_tabs(self, tabs):
		"""Formats tabs for display in the quick info panel.
			Args:
				tabs (list[Tab]): A list of one or more tabs for formating.
			Returns (list[list[str]]): Returns a list of lists containing the title, subtitle and
			 captions for each quick info panel entry.
		"""
		common_prefix = os.path.commonprefix([entity.path for entity in tabs if entity.is_file])
		if os.path.isdir(common_prefix) is False:
			common_prefix = common_prefix[:common_prefix.rfind(os.path.sep)]
		self.prefix = len(common_prefix)

		show_captions = self.settings.get("show_captions", True)
		include_path = self.settings.get("include_path", False)

		return [entity.get_details(self.prefix, include_path, show_captions) for entity in tabs]

	def display_quick_info_panel(self, tabs):
		"""Displays the quick info panel with the formatted tabs.
			Args:
				tabs (list[list[str]]): A list of lists containing the title, subtitle and captions for display.
		"""
		if self.preview_tab is True:
			self.window.show_quick_panel(tabs, self._on_done, on_highlight=self._on_highlighted, selected_index=self.current_tab_idx)
			return

		self.window.show_quick_panel(tabs, self._on_done)

	def make_tab(self, view, group_idx):
		"""Makes a new Tab entity relating to the given view.
		Args:
			view (sublime.View): Sublime View to build the Tab from.
			group_idx (int): The index of the group the view beings to.
		Returns (Tab): Tab entity containing metadata about the view.
		"""
		name = view.file_name()
		is_file = True

		#If the name is not set, then we're dealing with a buffer
		#rather than a file, so deal with it accordingly.
		if name is None:
			is_file = False
			name = view.name()
			#set the view name to untitled if we get an empty name
			if len(name) == 0:
				name = "untitled"

		entity = tab.Tab(name, is_file)

		if self.window.get_view_index(self.window.active_view()) == self.window.get_view_index(view):
			entity.add_caption("Current File")

		if self.show_group_caption:
			group_caption = "{0} {1}".format(
				self.group_caption_prefix,
				group_idx
			)
			entity.add_caption(group_caption)

		if view.file_name() is None:
			entity.add_caption("Unsaved File")
		elif view.is_dirty():
			entity.add_caption("Unsaved Changes")

		if view.is_read_only():
			entity.add_caption("Read Only")

		return entity

	def _on_done(self,index):
		"""Callback handler to move focus to the selected tab index"""
		if index == -1 and self.current_tab_idx != -1:
			# If the selection was quit, re-focus the last selected Tab
			self.window.focus_view(self.views[self.current_tab_idx])
		elif index > - 1:
			self.window.focus_view(self.views[index])

	def _on_highlighted(self, index):
		"""Callback handler to focuses the currently selected/highlighted Tab"""
		self.window.focus_view(self.views[index])

class TabFilterCommand(BaseTabFilter):
	"""Provides a GoToAnything style interface for searching and selecting open tabs across all groups."""

	def run(self):
		"""Shows a quick panel to filter and select tabs from the active window."""
		tabs = self.gather_tabs(range(self.window.num_groups()))

		self.display_quick_info_panel(self.format_tabs(tabs))

	def display_quick_info_panel(self, tabs):
		"""Displays the quick info panel with the formatted tabs.
			Args:
				tabs (list[list[str]]): A list of lists containing the title, subtitle and captions for display.
		"""
		if self.preview_tab is True:
			# We can't support previewing the tab if there's more than one window group
			# or if we're running Sublime Text 2.
			self.preview_tab = self.window.num_groups() == 1 and sublime.version() != '2221'

		super().display_quick_info_panel(tabs)

class TabFilterActiveGroupCommand(BaseTabFilter):
	"""Provides a GoToAnything style interface for searching and selecting open tabs within the active group."""

	def run(self):
		"""Shows a quick panel to filter and select tabs from the active window."""
		tabs = self.gather_tabs([self.window.active_group()])

		self.display_quick_info_panel(self.format_tabs(tabs))


	def display_quick_info_panel(self, tabs):
		"""Displays the quick info panel with the formatted tabs.
			Args:
				tabs (list[list[str]]): A list of lists containing the title, subtitle and captions for display.
		"""
		if self.preview_tab is True:
			# We can't support previewing if we're running Sublime Text 2.
			self.preview_tab = sublime.version() != '2221'

		super().display_quick_info_panel(tabs)