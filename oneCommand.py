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

class FakeCommand:
	hasdata_regex = re.compile(r":\d{1,2}$")
	def __init__(self, blockname, init, variables=[]):
		self.cond = False
		self.init = init
		for i in variables: 
			blockname = i.sub(blockname)
		if self.hasdata_regex.search(blockname):
			datastr = self.hasdata_regex.findall(blockname)
			self.data = int(datastr[0][1:])
		else: self.data = 0
		self.block = self.hasdata_regex.sub("", blockname)
	def __str__(self):
		return format("{block} {data}",
			block=self.block,
			data=self.data)
	def prettystr(self):
		return format("{darkgray}{block}{init}",
			block = self,
			init = "\n  - Initialization" if self.init else "")


class CmdVariable:
	def __init__(self, name, replacewith):
		self.name = name
		self.replacewith = replacewith
		self.regex = re.compile(r"\$"+name.lower()+r"\b", re.IGNORECASE)
	def sub(self, string):
		return self.regex.sub(self.replacewith, string)


def generate_sand(command_obj, direction):
	if isinstance(command_obj, FakeCommand):
		return normal_sand(command_obj.block, command_obj.data)
	tag = {
		"Block": nbt.noquote_str(command_obj.block),
		"TileEntityData": {
			"Command": str(command_obj),
			"TrackOutput": nbt.int_b(0)
		},
		"Time": 1,
		"id": nbt.noquote_str("FallingSand")
	}
	data = direction+8 if command_obj.cond else direction
	if data:
		tag["Data"] = data
	return tag


def normal_sand(block, data=0):
	tag = {
		"Block": nbt.noquote_str(block),
		"Time": 1,
		"id": nbt.noquote_str("FallingSand")
	}
	if data:
		tag["Data"] = data
	return tag

def gen_stack(init_commands, clock_commands, mode, loud=False):
	final_command_obj = None
	if clock_commands or init_commands:
		command_sands = []

		repeatoffsets = []
		if mode == 'i':
			if clock_commands and isinstance(clock_commands[0], Command): 
				repeatoffsets.append(len(clock_commands) + 2)
			for command in clock_commands:
				if command.block == "repeating_command_block" and not command.cond and command is not clock_commands[0]:
					repeatoffsets.append(len(clock_commands) - clock_commands.index(command) + 2 + len(repeatoffsets))

		filloffset = len(init_commands) + len(repeatoffsets)
		if filloffset: filloffset += 1

		if filloffset:
			sand = normal_sand("command_block")
			if mode == 'i':
				sand["TileEntityData"] = {
					"auto": 1
				}
			command_sands.append(sand)

		for command in init_commands:
			if loud:
				cprint(command.prettystr(), allow_repeat=True)
			command_sands.append(generate_sand(command, 0))

		for offset in repeatoffsets[::-1]:
			blockdata = Command(format("blockdata ~ ~-{offset} ~ {auto:1b}", offset = offset), init=True)
			if loud:
				cprint(blockdata.prettystr(), allow_repeat=True)
			sand = generate_sand(blockdata, 0)
			command_sands.append(sand)

		if filloffset:
			fill = Command(format("fill ~ ~-1 ~ ~ ~{offset} ~ air", offset = filloffset), init=True)
			if loud:
				cprint(fill.prettystr(), allow_repeat=True)
			cprint("minecraft:barrier\n  - Initialization", color=bcolors.DARKGRAY, allow_repeat=True)
			command_sands.append(generate_sand(fill, 0))
			command_sands.append(normal_sand("barrier"))

		for command in clock_commands[::-1]:
			if command is clock_commands[0] and isinstance(command, Command):
				command.block = "repeating_command_block"
				command_sands.append(generate_sand(command, 1))
			else:
				sand = generate_sand(command, 1)
				if command.block == "repeating_command_block" and command.cond: 
					sand["TileEntityData"]["auto"] = 1
				command_sands.append(sand)
			if loud:
				cprint(command.prettystr(), allow_repeat=True)
		final_command_obj = nbt.cmd("summon FallingSand ~ ~1 ~ ", ride(command_sands, False))

	final_command = nbt.JSON2Command(final_command_obj)

	return final_command

tag_regex =        re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:)[\t]*)+", re.IGNORECASE)
init_tag_regex =   re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*INIT:", re.IGNORECASE)
cond_tag_regex =   re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*COND:", re.IGNORECASE)
repeat_tag_regex = re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*REPEAT:", re.IGNORECASE)
block_tag_regex =  re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*BLOCK:[ \t]*(minecraft:)?[a-z_](:\d{1,2})?", re.IGNORECASE)
block_regex =      re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*BLOCK:[ \t]*", re.IGNORECASE)
define_regex =     re.compile(r"^[ \t]*DEFINE:", re.IGNORECASE)
undefine_regex =   re.compile(r"^[ \t]*UNDEFINE:", re.IGNORECASE)
set_regex =        re.compile(r"^[ \t]*SET:", re.IGNORECASE)
import_regex =     re.compile(r"^[ \t]*IMPORT:", re.IGNORECASE)
comment_regex =    re.compile(r"^[ \t]*#", re.IGNORECASE)
nonewline_regex =  re.compile(r"^[ \t]*-", re.IGNORECASE)

def parse_commands(commands, context = None):
	init_commands = []
	clock_commands = []
	variables = []
	varnames = []

	compactedcommands = []
	next_command = ""
	for command in commands[::-1]:
		if nonewline_regex.match(command):
			next_command = nonewline_regex.sub("", command).replace("\t", "").rstrip() + next_command
		else:
			compactedcommands.insert(0, command.replace("\t", "").rstrip() + next_command)
			next_command = ""

	# do all INIT and COND checking
	for command in compactedcommands:
		command = command.strip()
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
				cprint("""WARNING: Duplicate variable {var}. Using first definition.
				          To overwrite the previous value of a variable, use the {bold}SET:{endc}{color} prepend.
				          To undefine a variable, use the {bold}UNDEFINE:{endc}{color} prepend.""", color=bcolors.YELLOW, var=name, strip=True)
			else:
				varnames.append(name)
				variables.append(CmdVariable(name, contents))

		elif set_regex.match(command):
			command_split = set_regex.sub("", command).split()
			while not command_split[0]: command_split = command_split[1:]
			while not command_split[1]: command_split = command_split[:1] + command_split[2:]
			if len(command_split) < 2: continue
			name = command_split[0]
			contents = " ".join(command_split[1:])
			for i in variables:
				name = i.sub(name)
				contents = i.sub(contents)

			if name in varnames: 
				for i in variables:
					if i.name == name:
						variables.remove(i)
				varnames.remove(name)
			varnames.append(name)
			variables.append(CmdVariable(name, contents))

		elif undefine_regex.match(command):
			variable = undefine_regex.sub("", command).strip().split()[0]
			if variable in varnames:
				for i in variables:
					if i.name == name:
						variables.remove(i)
				varnames.remove(name)

		elif import_regex.match(command):
			if context is None:
				continue
			libraryname = import_regex.sub("", command).strip()
			if isinstance(context, str):
				if os.path.exists(os.path.join(context, libraryname)):
					lib = open(os.path.join(context,libraryname))
				elif os.path.exists(os.path.join(context, libraryname+".1cc")):
					lib = open(os.path.join(context, libraryname+".1cc"))
				else:
					cprint("Failed to import {lib}. File not found.", color=bcolors.RED, lib=libraryname)
					continue
			else:
				lib = None
				for i in context:
					if os.path.exists(os.path.join(i, libraryname)):
						lib = open(os.path.join(i,libraryname))
						break
					elif os.path.exists(os.path.join(i, libraryname+".1cc")):
						lib = open(os.path.join(i, libraryname+".1cc"))
						break
				if not lib:
					cprint("Failed to import {lib}. File not found.", color=bcolors.RED, lib=libraryname)
					continue

			imported_init, imported_clock = parse_commands(lib.read().split("\n"), context)
			init_commands += imported_init
			clock_commands += imported_clock

		else:
			init = False
			conditional = False
			block = "chain_command_block"
			if cond_tag_regex.match(command): conditional = True
			if init_tag_regex.match(command): init = True
			if repeat_tag_regex.match(command): block = "repeating_command_block"
			if block_tag_regex.match(command):
				block = block_regex.sub("", command).strip()
				if init:
					init_commands.append(FakeCommand(block, init, variables))
				else:
					clock_commands.append(FakeCommand(block, init, variables))
				continue

			command = tag_regex.sub("", command).strip()
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
	 {green}Prepend your command with `SET:` to make it an overriding variable definition.{endc}
	        Example: `DEFINE:world hello` and `say $world` would say `hello`.
	 {green}Prepend your command with `UNDEFINE:` to make it a variable undefiner.{endc}
	 {green}Prepend your command with `REPEAT:` to make it a repeating command block.{endc}
	 {green}Prepend your command with `INIT:` to make it only run when the structure is deployed.{endc}
	 {green}`BLOCK:minecraft:{name}:{data}` will summon a block (thereby stopping the current `REPEAT:` signal.){endc}
	 {green}Prepend your command with `COND:` to make it a conditional command.{endc}
	        Please report any bugs at the GitHub repo: {line}{blue}https://github.com/destruc7i0n/OneCommand/issues{endc}
	        {peach}----------------------------------------{endc}""", strip=True)

	# get mode if not specified by argument
	if not args.mode:
		if args.filepath == "stdin":
			cprint("WARNING: Mode must be specified by command line in stdin mode. Using instant mode.", color=bcolors.YELLOW)
			mode = "i"
		else:
			mode = cinput("Manual (m) or Instant (i)? ").strip().lower()
			if mode not in ["m", "i"]:
				raise ValueError("Not manual or instant")
	else:
		mode = args.mode

	commands = []
	# get commands if file not specified
	if not args.filepath:
		context = os.path.dirname(__file__)
		x = 1
		command = cinput("Command {num}: ", num=x).strip()
		while command:
			x += 1
			commands.append(command)
			command = cinput("Command {num}: ", num=x).strip()
	# get commands from specified file
	else:
		if args.filepath == "stdin":
			commands = sys.stdin.read().split("\n")
			context = os.path.dirname(__file__)
		elif os.path.exists(args.filepath):
			commands = open(args.filepath).read().split("\n")
			context = os.path.dirname(args.filepath)
		else:
			raise IOError(format("File {file} not found.", file=args.filepath))


	init_commands, clock_commands = parse_commands(commands, context)


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
