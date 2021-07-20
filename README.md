# Tab Filter

Tab Filter is a Sublime Text plugin for quickly switching between open tabs.  Invoking Tab Filter brings up a "GoTo Anything"-like quick input showing your opened tabs for the current window, allowing you to quick filter on file names to rapidly switch amongst existing tabs.

## Compatibility

This plugin is compatible with Sublime Text 3 and 4 (and still should be with 2).

## Installation

### Package Control

Tab Filter is also available through [Package Control](http://wbond.net/sublime\_packages/package\_control).  To install, bring up the Command Palette (brought up using `ctrl+shift+p` on Linux / Windows or `cmd+shift+p` on OS X) and run the `Package Control: Install Package` command - now search for and select **Tab Filter**.

### Manual

##### Linux

Using git:

    $ cd ~/.config/sublime-text-3/Packages/
    $ git clone git://github.com/robinmalburn/sublime-tabfilter.git 'Tab Filter'

Without git:

Download the repository as a zip file and extract the sublime-tabfilter-master folder.  Copy the contents of this folder to:
	`~/.config/sublime-text-3/Packages/Tab Filter`

##### OSX:

Using git:

	$ cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/
    $ git clone git://github.com/robinmalburn/sublime-tabfilter.git 'Tab Filter'

Without git:

Download the repository as a zip file and extract the sublime-tabfilter-master folder.  Copy the contents of this folder to:
	`~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Tab Filter`

##### Windows

I don't currently run Windows, so not sure where the packages live on that platform.  The plugin will work on Windows, though, so if anyone wants to contribute the directories that apply to Windows XP, Vista, 7, or 8, please feel free.


## Usage

### Key Bindings

Tab Filter comes with the following default keymap for Linux, OSX and Windows:  `alt+shift+p`

This can be overriden via the keybindings options in `Preferences > Package Settings > Tab Filter > Key Bindings - User`

### Command Palette

Tab Filter can also be activated via the Command Palette (brought up using `ctrl+shift+p` on Linux / Windows or `cmd+shift+p` on OS X) and typing Tab Filter

### Settings

Additional configuration settings for Tab Filter can be altered via `Preferences > Package Settings > Tab Filter > Settings - User`

##### Captions

Tab Filter can be configured to show or hide additional captions relating to the state of each open tab.  The captions include: *Current File*, *Unsaved File*, *Unsaved Changes* and *Read Only*.  Captions are shown by default, but this behaviour can be changed by setting the `show_captions` setting to `false`.

##### Path/Filename Filtering

By default, Tab Filter only shows the basename of open tabs (where they're really files and not just buffers, of course).  This configuration can be changed to instead show and therefore allow filtering by the full, non-common path of the file instead by changing the `include_path` option to `true`.

##### Preview currently selected entry

By default, Tab Filter only focuses the tab if it gets selected. To always focus/preview the currently highlighted entry, set `preview_tab` to `true`. Note that this currently only works with a single group layout (no splitted window).


## License

Released under [MIT license](https://github.com/robinmalburn/sublime-tabfilter/blob/master/license.txt).