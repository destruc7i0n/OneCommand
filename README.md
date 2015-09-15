# OneCommand
A python script to generate one-command contraptions in Minecraft 1.9, by [myself](http://thedestruc7i0n.ca) and [yrsegal](http://github.com/yrsegal).

## User Interfaces
### The GUI
### [Windows Executable](https://github.com/destruc7i0n/OneCommand/releases/download/v1.0.2/OneCommandGUI.v1.0.2.zip)
This Tk-written wrapper for the OneCommand library allows you to edit your commands in a clean GUI. For those not on windows, you would simply run `oneCommandGUI.py`.
### [Sublime Text Plugin](https://packagecontrol.io/packages/One%20Command%20Syntax%20Highlighter)
A OneCommand syntax/generator has been written as a plugin for Sublime Text. You can check it out above, or download via [Package Control](https://packagecontrol.io).

## The Command Line
oneCommand.py has been designed from scratch with the CLI in mind. The arguments are as follows:
* `-m {m,i}`, `--mode {m,i}`: Choose whether to have the contraption activated manually (`m`) or instantly, upon deployment (`i`).
* `-f [FILE]`, `--command_file [FILE]`: Use a file as input. Without an argument, it will pull from `STDIN`.
* `-C`, `--no-copy`: By default, OneCommand will copy the output to the clipboard. This argument prevents that behavior.
* `-q`, `--quiet`: Silences all output besides the command itself.
* `-v`, `--verbose`: More detailed output.
* `-O`, `--no-output`: Doesn't dump the command to `STDOUT`. If `-O` and `-C` are used, the command will not be outputted at all.
* `-h`, `--help`: Shows the list of arguments.

## The Syntax
Most of the differences between the OneCommand syntax and regular commands lie in the prepends.  

* `INIT:` as a prepend will make the command only run once, when you run the command.
* `COND:` as a prepend will make the command only run if the previous one was successful. Not recommended to use on the first command, nor the first `INIT:` command.
* `REPEAT:` as a prepend will make the command in a repeating command block. This is included to allow for different-speed clocks, and similar functions.
* `BLOCK:` as a prepend will use the following command (format `minecraft:BLOCKNAME:DATA`) as a normal block instead of a command. This can be used to visually seperate parts of a module; remember that `REPEAT:` must be used afterwards to carry the signal.
* `-` as a prepend will append the current line to the previous one.

There's also the `DEFINE:` syntax, similar to the C `#define` directive. This allows simpler-to-read blocks of code to be written.  
The syntax is `DEFINE: identifier replacewith`. You can then use this by calling out, anywhere in your code, `$identifier`.
