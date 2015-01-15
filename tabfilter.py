# Copyright (c) 2013, 2014 Robin Malburn
# See the file license.txt for copying permission.

import sublime
import sublime_plugin
import os

class TabFilterCommand(sublime_plugin.WindowCommand):
	"""Provides a GoToAnything style interface for searching and selecting open tabs"""

	def run(self):
		"""Shows a quick panel to filter and select tabs from the active window"""
		
		window = sublime.active_window()
		names = []
		captions = []
		dirs = []
		self.views = []
		self.prefix = ""
		self.settings = sublime.load_settings("tabfilter.sublime-settings")

		for view in window.views():
			self.views.append(view)

			if view.file_name() is None:
				name = view.name()
				#set the view name to untitled if we get an empty name
				if len(name) == 0:
					name = "untitled"
			else:
				name = view.file_name()
				dirs.append(os.path.dirname(view.file_name())+os.path.sep)

			names.append(name)

			if self.settings.get("show_captions", True):
				view_captions = []

				if window.get_view_index(window.active_view()) == window.get_view_index(view):
					view_captions.append("Current File")

				if view.file_name() is None:
					view_captions.append("Unsaved File")
				elif view.is_dirty():
					view_captions.append("Unsaved Changes")

				if view.is_read_only():
					view_captions.append("Read Only")

				caption = ", ".join(view_captions)
				
				captions.append(caption)

		self.prefix = os.path.commonprefix(dirs)

		if self.settings.get("show_captions", True):
			tabs = [[os.path.basename(path), path.replace(self.prefix, ''), caption] for path, caption in zip(names, captions)]
		else:
			tabs = [[os.path.basename(path), path.replace(self.prefix, '')] for path in names]

		window.show_quick_panel(tabs, self._on_done)

	def _on_done(self,index):
		"""Callback handler to move focus to the selected tab index"""
		if index > - 1:
			sublime.active_window().focus_view(self.views[index])
