# Copyright (c) 2013 Robin Malburn
# See the file license.txt for copying permission.

import sublime
import sublime_plugin
import os

class TabFilterCommand(sublime_plugin.WindowCommand):
	def run(self):
		window = sublime.active_window()
		name_list = []
		caption_list = []
		dir_list = []
		self.view_list = []
		self.prefix = ""
		self.settings = sublime.load_settings("tabfilter.sublime-settings")

		for view in window.views():
			self.view_list.append(view)

			if view.file_name() is None:
				name = view.name()
				#set the view name to untitled if we get an empty name
				if len(name) == 0:
					name = "untitled"
			else:
				name = view.file_name()
				dir_list.append(os.path.dirname(view.file_name())+os.path.sep)

			name_list.append(name)

			if self.settings.get("show_captions", True):
				captions = []

				if window.get_view_index(window.active_view()) == window.get_view_index(view):
					captions.append("Current File")

				if view.file_name() is None:
					captions.append("Unsaved File")
				elif view.is_dirty():
					captions.append("Unsaved Changes")

				if view.is_read_only():
					caption.append("Read Only")

				caption = ", ".join(captions)
				
				caption_list.append(caption)

		self.prefix = os.path.commonprefix(dir_list)
		tabs = list(map(self._common_names, name_list, caption_list)) #wrap the result of our map function as a list for Python 3.x support
		window.show_quick_panel(tabs, self._on_done)

	def _on_done(self,index):
		if index > - 1:
			sublime.active_window().focus_view(self.view_list[index])

	def _common_names(self, path, caption):
		if self.settings.get("show_captions", True):
			return [os.path.basename(path), path.replace(self.prefix, ''), caption]
		else:
			return [os.path.basename(path), path.replace(self.prefix, '')]