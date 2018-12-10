# SublimeLinter-contrib-golangci-lint

This linter plugin for [SublimeLinter][docs] provides an interface to [golangci-lint](https://github.com/golangci/golangci-lint), a linter for Go (golang).

## Installation

- Install SublimeLinter 3 from [here](https://packagecontrol.io/packages/SublimeLinter)
- Install SublimeLinter-golangcilint from [here](https://packagecontrol.io/packages/SublimeLinter-contrib-golang-cilint)
- Install the `golangci-lint` helper from [here](https://github.com/golangci/golangci-lint#install)

## Configuration

In order for `golangci-lint` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. Before going any further, please read and follow the steps in [“Finding a linter executable”](http://sublimelinter.readthedocs.org/en/latest/troubleshooting.html#finding-a-linter-executable) through “Validating your PATH” in the documentation. Once you have installed `golangci-lint`, you can proceed to install the SublimeLinter-contrib-golangci-lint plugin if it is not yet installed.

**Note:** The linter creates a temporary directory to allow SublimeLinter to scan changes in the code that are still in the buffer _(aka. not saved yet)_. If the SublimeText sidebar is visible, you will notice _—for a split of a second—_ that a folder named `.golangcilint-*` appears and disappears. Make sure to add this folder to your `.gitignore` file, and also the “folder_exclude_patterns” in SublimeText’s preferences:

```
{
    "folder_exclude_patterns":
    [
        ".svn",
        ".git",
        ".hg",
        "CVS",
        "cache",
        "uploads",
        ".golangci-*",
        ".golangcilint-*",
        ".gometalinter-*"
    ],
}
```

## Plugin installation

Please use [Package Control][pc] to install the linter plugin. This will ensure that the plugin will be updated when new versions are available. If you want to install from source so you can modify the source code, you probably know what you are doing so we won’t cover that here.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette][cmd] and type `install`. Among the commands you should see `Package Control: Install Package`. If that command is not highlighted, use the keyboard or mouse to select it. There will be a pause of a few seconds while Package Control fetches the list of available plugins.
1. When the plugin list appears, type `golangci-lint`. Among the entries you should see `SublimeLinter-contrib-golangci-lint`. If that entry is not highlighted, use the keyboard or mouse to select it.

## Usage

If you are launching Sublime from a window manager, it's possible your GOPATH will not be set correctly. There are two ways around that:

1. Launch Sublime from a shell with GOPATH already set correctly.
2. Set the `gopath` setting in the linter configuration for SublimeLinter-contrib-golangci-lint.

## Settings
For general information on how SublimeLinter works with settings, please see [Settings][settings]. For information on generic linter settings, please see [Linter Settings][linter-settings].

Go vendoring will not work with SublimeLinter when `lint_mode=background`. Use `save`, `load/save` or `manual`.

## Contributing
If you would like to contribute enhancements or fixes, please do the following:

1. Fork the plugin repository.
1. Hack on a separate topic branch created from the latest `master`.
1. Commit and push the topic branch.
1. Make a pull request.
1. Be patient.  ;-)

Please note that modications should follow these coding guidelines:

- Indent is 4 spaces.
- Code should pass flake8 and pep257 linters.
- Vertical whitespace helps readability, don’t be afraid to use it.
- Please use descriptive variable names, no abbrevations unless they are very well known.

Thank you for helping out!

[docs]: http://sublimelinter.readthedocs.org
[installation]: http://sublimelinter.readthedocs.org/en/latest/installation.html
[locating-executables]: http://sublimelinter.readthedocs.org/en/latest/usage.html#how-linter-executables-are-located
[pc]: https://sublime.wbond.net/installation
[cmd]: http://docs.sublimetext.info/en/sublime-text-3/extensibility/command_palette.html
[settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html
[linter-settings]: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html
[inline-settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html#inline-settings
