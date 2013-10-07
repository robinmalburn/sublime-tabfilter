# Tab Filter

Tab Filter is a Sublime Text plugin for quickly switching between open tabs.  Invoking Tab Filter brings up a "GoTo Anything"-like quick input showing your opened tabs for the current window, allowing you to quick filter on file names to rapidly switch amongst existing tabs.

## Compatibility

This plugin is compatible with Sublime Text 2 and 3<sup>*</sup>.

**<sup>*</sup>** Sublime Text 3 is still in beta at the moment, so there could be changes whilst it's in development that could break this plugin's compatability in the future.  If you stumble across any problems, please do raise an [issue](https://github.com/robinmalburn/sublime-tabfilter/issues)


## Installation

### Package Control

Tab Filter is also available through [Package Control](http://wbond.net/sublime\_packages/package\_control).  To install, bring up the Command Palette (brought up using `ctrl+shift+p` on Linux / Windows or `cmd+shift+p` on OS X) and run the `Package Control: Install Package` command - now search for and select **Tab Filter**.

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


## Usage

### Key Bindings

Tab Filter comes with the following default keymap for Linux, OSX and Windows:  `alt+shift+p`

This can be overriden via the keybindings options in `Preferences > Package Settings > Tab Filter > Key Bindings - User` 

### Command Palette

Tab Filter can also be activated via the Command Palette (brought up using `ctrl+shift+p` on Linux / Windows or `cmd+shift+p` on OS X) and typing Tab Filter

### Settings

Tab Filter can be configured to show or hide additional captions relating to the state of each open tab.  The captions include: `Current File`, `Unsaved File`, `Unsaved Changes` and `Read Only`.  These additional captions default to being shown, but can be hidden via `Preferences > Package Settings > Tab Filter > Settings - User` 

## License

Released under [MIT license](https://github.com/robinmalburn/sublime-tabfilter/blob/master/license.txt).