# Copyright (c) 2013 Robin Malburn
# See the file license.txt for copying permission.

import sublime, sublime_plugin
import os

def get_setting(key):
	if key is not None:
		settings = sublime.load_settings("tabfilter.sublime-settings")
		return settings.get(key)

class TabFilterCommand(sublime_plugin.WindowCommand):
	def run(self):
		window = sublime.active_window()
		views = window.views()
		active_view = window.active_view()
		self.name_list = []
		self.view_list = []

		for view in views:
			if view.file_name() is None:
				name = view.name()
				#set the view name to untitled if we get an empty name
				if len(name) == 0:
					name = "untitled"
			else:
				if get_setting("show_full_path") is True:
					name = view.file_name()
				else: 
					name = os.path.basename(view.file_name())

			# check if this name is already in use, and if so, try to append 
			if get_setting("show_full_path") is False:
				for entry in self.name_list:
					if entry[0] == name:
						index = self.name_list.index(entry)
						if self.view_list[index].file_name() is not None:
							self.name_list[index][0] = self.view_list[index].file_name()
						if view.file_name() is not None:
							name = view.file_name()

			captions = []

			if window.get_view_index(active_view) == window.get_view_index(view):
				captions.append("Current File")

			if view.file_name() is None:
				captions.append("Unsaved File")
			elif view.is_dirty():
				captions.append("Unsaved Changes")

			if view.is_read_only():
				caption.append("Read Only")

			caption = ", ".join(captions)
			
			self.view_list.append(view)
			self.name_list.append([name, caption])

		window.show_quick_panel(self.name_list, self._on_done)

	def _on_done(self,index):
		if index > - 1:
			sublime.active_window().focus_view(self.view_list[index])