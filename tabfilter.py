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

class TabFilterCommand(sublime_plugin.WindowCommand):
	"""Provides a GoToAnything style interface for searching and selecting open tabs"""

	def run(self):
		"""Shows a quick panel to filter and select tabs from the active window"""

		tabs = []
		self.window = sublime.active_window()
		self.views = []
		self.prefix = ""
		self.settings = sublime.load_settings("tabfilter.sublime-settings")
		self.current_tab_idx = -1

		idx = 0
		for view in self.window.views():
			self.views.append(view)
			if self.window.active_sheet().view().id() == view.id():
				# save index for later usage
				self.current_tab_idx = idx
			tabs.append(self.make_tab(view))
			idx = idx + 1

		self.prefix = len(os.path.commonprefix([entity.name for entity in tabs if entity.is_file]))

		show_captions = self.settings.get("show_captions", True)
		include_path = self.settings.get("include_path", False)
		preview_tab = self.settings.get("preview_tab", False)

		tabs = [entity.get_details(self.prefix, include_path, show_captions) for entity in tabs]

		on_highlight_cb = None
		selected_index = 0

		if preview_tab is True and self.window.num_groups() == 1:
		    # This doesn't work with a multi group layout
		    # but otherwise, replace our defaulted arguments.
		    on_highlight_cb = self._on_highlighted
		    selected_index = self.current_tab_idx

		self.window.show_quick_panel(tabs, self._on_done, on_highlight=on_highlight_cb, selected_index=selected_index)

	def make_tab(self, view):
		"""Makes a new Tab entity relating to the given view.
		Args:
			view (sublime.View): Sublime View to build the Tab from
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
