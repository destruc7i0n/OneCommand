from __future__ import print_function

from util import *
import nbtencoder as nbt

import re
import sys, os

cprintconf.name = "Generator"
cprintconf.color = bcolors.PEACH

class Command:
	def __init__(self, cmd, block="chain_command_block", init=False, conditional=False, variables=[]):
		self.cmd = cmd
		self.cond = conditional
		self.init = init
		self.block = block
		for i in variables:
			self.cmd = i.sub(self.cmd)
	def __str__(self):
		return self.cmd
	def prettystr(self):
		return format("{cmd}{init}{cond}{repeat}",
			cmd = self.cmd,
			init = "\n  - Initialization" if self.init else "",
			cond = "\n  - Conditional" if self.cond else "",
			repeat="\n  - Repeating" if self.block == "repeating_command_block" else "")

class CmdVariable:
	def __init__(self, name, replacewith):
		self.name = name
		self.replacewith = replacewith
		self.regex = re.compile("\\$"+name.lower()+"\\b", re.IGNORECASE)
	def sub(self, string):
		return self.regex.sub(self.replacewith, string)


def generate_sand(command_obj, direction):
	tag = {
		"Block": command_obj.block,
		"Time": 1,
		"TileEntityData": {
			"Command": str(command_obj),
			"TrackOutput": nbt.int_b(0)
		},
		"id": "FallingSand"
	}
	data = direction+8 if command_obj.cond else direction
	if data:
		tag["Data"] = data
	return tag


def normal_sand(block, data=0):
	tag = {
		"Block": block,
		"Time": 1,
		"id": "FallingSand"
	}
	if data:
		tag["Data"] = data
	return tag

def gen_stack(init_commands, clock_commands, mode, loud=False):
	final_command_obj = None
	if clock_commands or init_commands:
		command_sands = []

		filloffset = len(init_commands) + int(bool(mode == 'i' and clock_commands))
		filloffset += 1*int(bool(filloffset))

		if filloffset:
			sand = normal_sand("command_block")
			sand["TileEntityData"] = {
				"auto": 1
			}
			command_sands.append(sand)

		for command in init_commands:
			if loud:
				cprint(command.prettystr())
			command_sands.append(generate_sand(command, 0))

		if mode == 'i' and clock_commands:
			offset = len(clock_commands) + 2
			blockdata = Command(format("blockdata ~ ~-{offset} ~ {auto:1b}", offset = offset), init=True)
			if loud:
				cprint(blockdata.prettystr())
			sand = generate_sand(blockdata, 0)
			if not init_commands:
				sand["TileEntityData"]["auto"] = 1
			command_sands.append(sand)

		if filloffset:
			fill = Command(format("fill ~ ~-1 ~ ~ ~{offset} ~ air", offset = filloffset), init=True)
			if loud:
				cprint(fill.prettystr())
			command_sands.append(generate_sand(fill, 0))
			command_sands.append(normal_sand("barrier"))

		for command in clock_commands[::-1]:
			if command is clock_commands[0]:
				command.block = "repeating_command_block"
				command_sands.append(generate_sand(command, 1))
			else:
				command_sands.append(generate_sand(command, 1))
			if loud:
				cprint(command.prettystr())
		final_command_obj = nbt.cmd("summon FallingSand ~ ~1 ~ ", ride(command_sands, False))

	final_command = nbt.JSON2Command(final_command_obj)

	return final_command

tag_regex = re.compile(r"^[ \t]*(INIT:|COND:|REPEAT:)", re.IGNORECASE)
init_tag_regex = re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:)[ \t]*)*INIT:", re.IGNORECASE)
cond_tag_regex = re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:)[ \t]*)*COND:", re.IGNORECASE)
repeat_tag_regex = re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:)[ \t]*)*REPEAT:", re.IGNORECASE)
init_regex = re.compile(r"INIT:", re.IGNORECASE)
cond_regex = re.compile(r"COND:", re.IGNORECASE)
repeat_regex = re.compile(r"REPEAT:", re.IGNORECASE)
define_regex = re.compile(r"^[ \t]*DEFINE:", re.IGNORECASE)
comment_regex = re.compile(r"^[ \t]*#", re.IGNORECASE)

def parse_commands(commands):
	init_commands = []
	clock_commands = []
	variables = []
	varnames = []
	# do all INIT and COND checking
	for command in commands:
		command = command.strip().rstrip()
		if comment_regex.match(command): continue

		if define_regex.match(command):
			command_split = define_regex.sub("", command).split()
			while not command_split[0]: command_split = command_split[1:]
			while not command_split[1]: command_split = command_split[:1] + command_split[2:]
			if len(command_split) < 2: continue
			name = command_split[0]
			contents = " ".join(command_split[1:])
			for i in variables:
				name = i.sub(name)
				contents = i.sub(contents)

			if name in varnames: 
				cprint("WARNING: Duplicate variable {var}. Using first definition.", color=bcolors.YELLOW, var=name)
			else:
				varnames.append(name)
				variables.append(CmdVariable(name, contents))
			continue

		init = False
		conditional = False
		block = "chain_command_block"

		if cond_tag_regex.match(command): 
			conditional = True
			command = cond_regex.sub("", command)
		if init_tag_regex.match(command): 
			init = True
			command = init_regex.sub("", command)
		if repeat_tag_regex.match(command):
			block = "repeating_command_block"
			command = repeat_regex.sub("", command)

		command = command.strip().rstrip()
		if not command: continue

		command_obj = Command(command, block=block, conditional=conditional, init=init, variables=variables)
		if init:
			init_commands.append(command_obj)
		else:
			clock_commands.append(command_obj)
	return init_commands, clock_commands

def ride(entities, have_id=True):
	topmost = None
	absoluteTopmost = None
	
	for entity in entities:
		if topmost == None:
			absoluteTopmost = entity
		else:
			topmost["Riding"] = entity
		topmost = entity
	if not have_id: del absoluteTopmost["id"]
	return absoluteTopmost

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-m", "--mode", help="Choose activation mode for system", dest="mode", default="", choices=["m", "i"])
	parser.add_argument("-f", "--command_file", help="File to load commands from", dest="filepath", nargs="?",
		default=None, const="stdin")
	parser.add_argument("-C", "--no-copy", help="Don't copy the output command", dest="nocopy", action="store_true")
	parser.add_argument("-q", "--quiet", help="Silence output", dest="quiet", action="store_true")
	parser.add_argument("-v", "--verbose", help="Detailed output", dest="loud", action="store_true")
	parser.add_argument("-O", "--no-output", help="Don't dump cmd to STDOUT", dest="nostdout", action="store_true")
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

	cprint("""{peach}----------------------------------------{endc}
	  {cyan}TheDestruc7i0n{endc} and {golden}Wire Segal{endc}'s 1.9 One Command Generator
	 {green}Prepend your command with `#` to comment it out.{endc}
	 {green}Prepend your command with `DEFINE:` to make it a variable definition.{endc}
	        Example: `DEFINE:world hello` and `say $world` would say `hello`.
	 {green}Prepend your command with `REPEAT:` to make it a repeating command block.{endc}
	 {green}Prepend your command with `INIT:` to make it only run when the structure is deployed.{endc}
	 {green}Prepend your command with `COND:` to make it a conditional command.{endc}
	        Please report any bugs at the GitHub repo: {line}{blue}https://github.com/destruc7i0n/OneCommand/issues{endc}
	        {peach}----------------------------------------{endc}""", strip=True)

	# get mode if not specified by argument
	if not args.mode:
		if args.filepath == "stdin":
			cprint("WARNING: Mode must be specified by command line in stdin mode. Using instant mode.", color=bcolors.YELLOW)
			mode = "i"
		else:
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
		if args.filepath == "stdin":
			commands = sys.stdin.read().split("\n")
		elif os.path.exists(args.filepath):
			commands = open(args.filepath).read().split("\n")
		else:
			raise IOError(format("File {file} not found.", file=args.filepath))


	init_commands, clock_commands = parse_commands(commands)


	final_command = gen_stack(init_commands, clock_commands, mode, args.loud)
	


	if len(final_command) <= 32500 and final_command:
		pyperclip.copy(final_command)
		if args.nocopy:
			cprint("{bold}Final command{endc}", func=sys.stderr.write)
		else:
			cprint("{bold}Copied to clipboard{endc}", func=sys.stderr.write)
		if args.nostdout:
			if not args.quiet: sys.stderr.write(format("{bold}.{endc}"))
		else:
			if not args.quiet: sys.stderr.write(format("{bold} - {endc}"))
			sys.stdout.write(final_command + "\n")
	elif not final_command:
		cprint("No command generated.", color=bcolors.RED)
	else:
		cprint("Command too large ({length} > 32500)", length=len(final_command), color=bcolors.RED)
