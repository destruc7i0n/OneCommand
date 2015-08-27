from __future__ import print_function

from util import *
import nbtencoder as nbt

import argparse
import sys, os

cprintconf.name = "One Command"
cprintconf.color = bcolors.PEACH

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", help="Uses manual mode", dest="mode", default="", choices=["m", "i"])
parser.add_argument("-f", "--command_file", help="File to load commands from", dest="filepath",
	default=None)
parser.add_argument("-C", "--no-copy", help="Don't copy the output command", dest="nocopy", action="store_true")
parser.add_argument("-q", "--quiet", help="Silence output", dest="quiet", action="store_true")
parser.add_argument("-v", "--verbose", help="Detailed output", dest="loud", action="store_true")
args = parser.parse_args()

if args.quiet:
	def cprint(*args, **kwargs):
		pass

if args.nocopy:
	class pyperclip:
		@staticmethod
		def copy(*args, **kwargs): pass
		@staticmethod
		def paste(*args, **kwargs): pass
else:
	import pyperclip

class Command:
	def __init__(self, cmd, init=False, conditional=False):
		self.cmd = cmd
		self.cond = conditional
		self.init = init
	def __str__(self):
		return self.cmd
	def prettystr(self):
		return format("{cmd}{init}{cond}",
			cmd = self.cmd,
			init = "\n  - Initialization" if self.init else "",
			cond = "\n  - Conditional" if self.cond else "",)


def generate_sand(command_obj, direction, block="chain_command_block", auto=True):
	return {
		"Block": block,
		"Data": direction+8 if command_obj.cond else direction,
		"Time": 1,
		"TileEntityData": {
			"Command": str(command_obj),
			"auto": int(auto)
		},
		"id": "FallingSand"
	}

def normal_sand(block, data=0):
	return {
		"Block": block,
		"Data": data,
		"Time": 1,
		"id": "FallingSand"
	}

def ride(entities):
	topmost = None
	absoluteTopmost = None
	
	for entity in entities:
		if topmost == None:
			absoluteTopmost = entity
		else:
			topmost["Riding"] = entity
		topmost = entity
	return absoluteTopmost

if __name__ == "__main__":
	cprint("""{peach}----------------------------------------{endc}
	  {cyan}TheDestruc7i0n{endc} and {golden}Wire Segal{endc}'s 1.9 One Command Creator
	 {green}Prepend your command with `INIT:` to make it only run when the structure is deployed.{endc}
	 {green}Prepend your command with `COND:` to make it a conditional command.{endc}
	        Please report any bugs at the GitHub repo: {line}{blue}https://github.com/destruc7i0n/OneCommand/issues{endc}
	        {peach}----------------------------------------{endc}""", strip=True)

	# get mode if not specified by argument
	if not args.mode:
		mode = cinput("Manual (m) or Instant (i)? ").strip().rstrip().lower()
		if mode not in ["m", "i"]:
			raise ValueError("Not manual or instant")
	else:
		mode = args.mode



	commands = []
	# get commands if file not specified
	if not args.filepath:
		x = 1
		command = cinput("Command {num}: ", num=x).strip().rstrip()
		while command:
			x += 1
			commands.append(command)
			command = cinput("Command {num}: ", num=x).strip().rstrip()
	# get commands from specified file
	else:
		if os.path.exists(args.filepath):
			commands = open(args.filepath).read().split("\n")
		else:
			raise IOError(format("File {file} not found.", file=args.filepath))


	init_commands = []
	clock_commands = []
	# do all INIT and COND checking
	for command in commands:
		if not command: continue
		if command[0] == "#": continue
		init = False
		conditional = False
		while command[:5] in ["INIT:","COND:"]:
			if command[:5] == "COND:": conditional = True
			elif command[:5] == "INIT:": init = True
			command = command[5:]
		command_obj = Command(command, conditional=conditional, init=init)
		if init:
			init_commands.append(command_obj)
		else:
			clock_commands.append(command_obj)



	final_command_obj = None
	if clock_commands or init_commands:
		command_sands = []

		for command in init_commands:
			if args.loud:
				cprint(command.prettystr())
			if command is init_commands[0]:
				command_sands.append(generate_sand(command, 0, "command_block"))
			else:
				command_sands.append(generate_sand(command, 0))

		if mode == 'i' and clock_commands:
			offset = len(clock_commands) + 1
			blockdata = Command(format("blockdata ~ ~-{offset} ~ {auto:1b}", offset = offset), init=True)
			if args.loud:
				cprint(blockdata.prettystr())
			command_sands.append(generate_sand(blockdata, 0))

		offset = len(init_commands) + int(bool(mode == 'i' and clock_commands))
		fill = Command(format("fill ~ ~ ~ ~ ~{offset} ~ air", offset = offset), init=True)
		if args.loud:
			cprint(fill.prettystr())
		command_sands.append(generate_sand(fill, 1))

		for command in clock_commands[::-1]:
			if args.loud:
				cprint(command.prettystr())
			if command is clock_commands[0]:
				command_sands.append(generate_sand(command, 1, "repeating_command_block", mode == 'i'))
			elif command is clock_commands[-1]:
				command_sands.append(generate_sand(command, 0))
			else:
				command_sands.append(generate_sand(command, 1))
		final_command_obj = nbt.cmd("summon FallingSand ~ ~1 ~ ", ride(command_sands))

	final_command = nbt.JSON2Command(final_command_obj)


	if len(final_command) <= 32500 and final_command:
		pyperclip.copy(final_command)
		if not args.nocopy:
			cprint("Command copied to clipboard.")
			sys.stdout.write(final_command + "\n")
	elif not final_command:
		cprint("No command generated.", color=bcolors.RED)
	else:
		cprint("Command too large ({length} > 32500)", length=len(final), color=bcolors.RED)
