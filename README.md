# Tab Filter

Tab Filter is a Sublime Text 2 plugin for quickly switching between open tabs.  Invoking Tab Filter brings up a "GoTo Anything"-like quick input showing your opened tabs for the current window, allowing you to quick filter on file names to rapidly switch amongst existing tabs.

## Installation

### Manual

##### Linux

Using git:

    $ cd ~/.config/sublime-text-2/Packages/
    $ git clone git://github.com/robinmalburn/sublime-tabfilter.git 'Tab Filter'

Without git:

Download the repository as a zip file and extract the sublime-tabfilter-master folder.  Copy the contents of this folder to:
	`~/.config/sublime-text-2/Packages/Tab Filter`

##### OSX:

Using git:

	$ cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
    $ git clone git://github.com/robinmalburn/sublime-tabfilter.git 'Tab Filter'

Without git:

Download the repository as a zip file and extract the sublime-tabfilter-master folder.  Copy the contents of this folder to:
	`~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Tab Filter`

##### Windows

I don't currently run Windows, so not sure where the packages live on that platform.  The plugin will work on Windows, though, so if anyone wants to contribute the directories that apply to Windows XP, Vista, 7, or 8, please feel free.


### Package Control

[Package Control](http://wbond.net/sublime\_packages/package\_control) support coming soon!  Hopefully...

## Usage

### Key Bindings

Tab Filter comes with the following default keymap for Linux, OSX and Windows:  `alt+shift+p`

This can be overriden via the keybindings options in `Preferences > Package Settings > Tab Filter > Key Bindings - User` 

### Command Palette

Tab Filter can also be activated via the Command Palette (brought up using `ctrl+shift+p`) and typing Tab Filter

### Settings

Tab Filter can be configured to show full paths instead of just filenames via the `show_full_path` setting, which can be customised via `Preferences > Package Settings > Tab Filter > Settings - User` 

## License

Released under MIT license.
