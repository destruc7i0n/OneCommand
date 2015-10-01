from __future__ import print_function

from util import *
import nbtencoder as nbt

import math

cprintconf.name = "Generator"
cprintconf.color = bcolors.PEACH

class Command:
	def __init__(self, cmd, block="chain_command_block", init=False, conditional=False):
		self.cmd = cmd
		self.cond = conditional
		self.init = init
		self.block = block
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
	def __init__(self, blockname, init):
		self.cond = False
		self.init = init
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
		self.regex = re.compile(r"\|\$"+name.lower()+r"\||\$"+name.lower()+r"\b", re.IGNORECASE)
	def sub(self, string):
		return self.regex.sub(self.replacewith, string)

def macrofunc(string, params, args):
	for i in range(min(len(args), len(params))):
		string = re.sub(r"\|" + params[i] + r"\|", args[i], string)
	return string

class CmdMacro:
	param = r"\((?:(?:(?:-?\d+(?:\.\d+)?|\"(?:[^\"\\]*(?:\\.)*)*\"),\s*)*(?:-?\d+(?:\.\d+)?|\"(?:[^\"\\]*(?:\\.)*)*\"))?\)"
	param_regex = re.compile(param)
	def __init__(self, name, params, replacewith, function=macrofunc):
		self.name = name
		self.replacewith = replacewith
		self.params = params
		self.regex = re.compile(r"\$"+name.lower()+self.param, re.IGNORECASE)
		self.function = function
	def sub(self, string):
		while self.regex.search(string):
			found = self.regex.finditer(string)
			for find in found:
				params = self.param_regex.search(find.group()).group()[1:-1]
				params = re.sub(r",\s", ",", params)
				paraml = params.split(",")
				parsedparams = []
				for i in paraml:
					if i:
						if i[0] == '"':
							i = i[1:-1].replace('\\"', '"').replace('\\\\', '\\')
						parsedparams.append(i)
				try:
					output = self.function(self.replacewith, self.params, parsedparams)
				except:
					cprint("{params} is not a valid argument list for ${funcname}.", color=bcolors.RED, params=params, funcname=self.name)
					output = ""
				string = string.replace(find.group(), output)
		return string

sin = lambda string, params, args: repr(math.sin(math.radians(float(args[0]))))
cos = lambda string, params, args: repr(math.sin(math.radians(float(args[0]))))
tan = lambda string, params, args: repr(math.sin(math.radians(float(args[0]))))
sinr= lambda string, params, args: repr(math.sin(float(args[0])))
cosr= lambda string, params, args: repr(math.sin(float(args[0])))
tanr= lambda string, params, args: repr(math.sin(float(args[0])))
floor=lambda string, params, args: repr(int(math.floor(float(args[0]))))
ceil= lambda string, params, args: repr(int(math.ceil(float(args[0]))))
rnd_l=lambda string, params, args: repr(round(float(args[0]), int(args[1])))
add = lambda string, params, args: repr(float(args[0]) + float(args[1]))
sub = lambda string, params, args: repr(float(args[0]) - float(args[1]))
mul = lambda string, params, args: repr(float(args[0]) * float(args[1]))
div = lambda string, params, args: repr(float(args[0]) / float(args[1]))
pow_l=lambda string, params, args: repr(float(args[0]) **float(args[1]))


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

tag_regex =         re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:)[ \t]*)+", re.IGNORECASE)
init_tag_regex =    re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*INIT:", re.IGNORECASE)
cond_tag_regex =    re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*COND:", re.IGNORECASE)
repeat_tag_regex =  re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*REPEAT:", re.IGNORECASE)
block_tag_regex =   re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*BLOCK:[ \t]*(minecraft:)?[a-z_](:\d{1,2})?", re.IGNORECASE)
block_regex =       re.compile(r"^[ \t]*((INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*BLOCK:[ \t]*", re.IGNORECASE)
define_regex =      re.compile(r"^[ \t]*DEFINE:", re.IGNORECASE)
word_regex =        re.compile(r"[a-zA-Z0-9_]+") # this regex has had me laughing for a while, but i need it
param_regex =       re.compile(r"\(([a-zA-Z0-9_]+,)*[a-zA-Z0-9_]+\)")
macro_regex =       re.compile(r"[a-zA-Z0-9_]+\(([a-zA-Z0-9_]+,)*[a-zA-Z0-9_]+\)")
undefine_regex =    re.compile(r"^[ \t]*UNDEFINE:", re.IGNORECASE)
import_regex =      re.compile(r"^[ \t]*IMPORT:", re.IGNORECASE)
for_regex =         re.compile(r"^[ \t]*FOR: \(\d+\.\.\.\d+\)", re.IGNORECASE)
endfor_regex =      re.compile(r":ENDFOR[ \t]*$", re.IGNORECASE)

comment_regex =     re.compile(r"^[ \t]*#")
skipnewline_regex = re.compile(r"\\[ \t]*$")
line_var_regex =    re.compile(r"\$line\b", re.IGNORECASE)

def preprocess(commands, context = None, filename = None):
	currtime = time.localtime()
	variables = {
		"file": CmdVariable("file", str(filename)),
		"date": CmdVariable("date", format("{month}/{day}/{year}", # I'm american >:D
			month = currtime.tm_mon,
			day = currtime.tm_mday,
			year = currtime.tm_year
		)), 
		"time": CmdVariable("time", format("{hour}:{minute}:{second}",
			hour = currtime.tm_hour,
			minute = currtime.tm_min,
			second = currtime.tm_sec
		)),
		"pi": CmdVariable("pi", repr(math.pi)),
		"e": CmdVariable("e", repr(math.e)),
		"max_int": CmdVariable("max_int", "2147483647"),
		"min_int": CmdVariable("min_int", "-2147483648"),
		"max_short": CmdVariable("max_short", "32767"),
		"min_short": CmdVariable("min_short", "-32768"),
		"max_byte": CmdVariable("max_byte", "127"),
		"min_byte": CmdVariable("min_byte", "-128")
	}
	functions = {
		"sin":   CmdMacro("sin",   [], "", sin),
		"cos":   CmdMacro("cos",   [], "", cos),
		"tan":   CmdMacro("tan",   [], "", tan),
		"sinr":  CmdMacro("sinr",  [], "", sinr),
		"cosr":  CmdMacro("cosr",  [], "", cosr),
		"tanr":  CmdMacro("tanr",  [], "", tanr),
		"floor": CmdMacro("floor", [], "", floor),
		"ceil":  CmdMacro("ceil",  [], "", ceil),
		"round": CmdMacro("round", [], "", rnd_l),
		"add":   CmdMacro("add",   [], "", add),
		"sub":   CmdMacro("sub",   [], "", sub),
		"mul":   CmdMacro("mul",   [], "", mul),
		"div":   CmdMacro("div",   [], "", div),
		"pow":   CmdMacro("pow",   [], "", pow_l)
	}
	func_regex = re.compile("\\$("+"|".join(map(lambda x: functions[x].name, functions))+")"+CmdMacro.param, re.IGNORECASE)
	outcommands = []
	compactedcommands = []
	cindex = 0
	while cindex < len(commands):
		command = line_var_regex.sub(str(cindex+1), commands[cindex])
		if skipnewline_regex.search(command):
			new_command = skipnewline_regex.sub("", command)
			next_command = "\\"
			while skipnewline_regex.search(next_command):
				if cindex != len(commands)-1:
					cindex += 1
					next_command = line_var_regex.sub(str(cindex+1), commands[cindex])
				else:
					next_command = ""
				new_command += skipnewline_regex.sub("", next_command.strip())
			compactedcommands.append(new_command)
		else:
			compactedcommands.append(command)
		cindex += 1


	for command in compactedcommands:
		command = command.strip()
		if not command or comment_regex.match(command): continue

		for var in variables:
			command = variables[var].sub(command)
		while func_regex.search(command):
			for macro in functions:
				command = functions[macro].sub(command)

		if define_regex.match(command):
			command_split = define_regex.sub("", command).split()
			if len(command_split) < 2: continue

			name = command_split[0]

			contents = " ".join(command_split[1:])

			if macro_regex.match(name):
				params = param_regex.search(name).group()[1:-1].split(",")
				name = word_regex.search(name).group()
				functions[name] = CmdMacro(name, params, contents)
				func_regex = re.compile("\\$("+"|".join(map(lambda x: functions[x].name, functions))+")"+CmdMacro.param, re.IGNORECASE)
				continue

			if word_regex.match(name):
				variables[name] = CmdVariable(name, contents)

		elif undefine_regex.match(command):
			variables_to_remove = undefine_regex.sub("", command).strip().split()
			for var in variables_to_remove:
				if var in variables:
					del variables[var]
				if var in functions:
					del functions[var]

		elif import_regex.match(command):
			if context is None: continue

			libraryname = import_regex.sub("", command).strip()
			if not libraryname: continue

			if isinstance(context, str):
				if os.path.exists(os.path.join(context, libraryname)):
					importedcontext = context
					importedname = libraryname
					lib = open(os.path.join(context,libraryname))
				elif os.path.exists(os.path.join(context, libraryname+".1cc")):
					importedcontext = context
					importedname = libraryname+".1cc"
					lib = open(os.path.join(context, libraryname+".1cc"))
				else:
					cprint("Failed to import {lib}. File not found.", color=bcolors.RED, lib=libraryname)
					continue
			else:
				lib = None
				for i in context:
					if os.path.exists(os.path.join(i, libraryname)):
						importedcontext = i
						importedname = libraryname
						lib = open(os.path.join(i,libraryname))
						break
					elif os.path.exists(os.path.join(i, libraryname+".1cc")):
						importedcontext = i
						importedname = libraryname+".1cc"
						lib = open(os.path.join(i, libraryname+".1cc"))
						break
				if not lib:
					cprint("Failed to import {lib}. File not found.", color=bcolors.RED, lib=libraryname)
					continue

			outcommands += preprocess(lib.read().split("\n"), importedcontext, importedname)
		else:
			outcommands.append(command)
	return outcommands

			



def parse_commands(commands, context = None, filename = None):
	init_commands = []
	clock_commands = []

	commands = preprocess(commands, context, filename)

	# do all INIT and COND checking
	for command in commands:

		subcommands = command.split("|\\n|")
		for subcommand in subcommands:
			subcommand = subcommand.strip()
			init = False
			conditional = False
			block = "chain_command_block"
			if cond_tag_regex.match(subcommand): conditional = True
			if init_tag_regex.match(subcommand): init = True
			if repeat_tag_regex.match(subcommand): block = "repeating_command_block"
			if block_tag_regex.match(subcommand):
				block = block_regex.sub("", subcommand).strip()
				if init:
					init_commands.append(FakeCommand(block, init))
				else:
					clock_commands.append(FakeCommand(block, init))
				continue

			command = tag_regex.sub("", subcommand).strip()
			if not subcommand: continue

			command_obj = Command(subcommand, block=block, conditional=conditional, init=init)
			
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
		filename = None
		context = os.path.curdir
		x = 1
		command = cinput("Command {num}: ", num=x).strip()
		while command:
			x += 1
			commands.append(command)
			command = cinput("Command {num}: ", num=x).strip()
	# get commands from specified file
	else:
		if args.filepath == "stdin":
			filename = None
			commands = sys.stdin.read().split("\n")
			context = os.path.dirname(__file__)
		elif os.path.exists(args.filepath):
			filename = os.path.basename(args.filepath)
			commands = open(args.filepath).read().split("\n")
			context = os.path.dirname(args.filepath)
		else:
			raise IOError(format("File {file} not found.", file=args.filepath))

	init_commands, clock_commands = parse_commands(commands, context, filename)

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
