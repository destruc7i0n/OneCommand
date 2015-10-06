from lib import *
from classes import *
from sands import gen_stack
from util import cprint, bcolors
import time

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
		"pi":        CmdVariable("pi",        repr(math.pi)),
		"e":         CmdVariable("e",         repr(math.e)),
		"max_int":   CmdVariable("max_int",   "2147483647"),
		"min_int":   CmdVariable("min_int",   "-2147483648"),
		"max_short": CmdVariable("max_short", "32767"),
		"min_short": CmdVariable("min_short", "-32768"),
		"max_byte":  CmdVariable("max_byte",  "127"),
		"min_byte":  CmdVariable("min_byte",  "-128")
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

	commands = []
	cindex = 0
	while cindex < len(compactedcommands):
		command = compactedcommands[cindex]
		if for_regex.match(command):
			string = for_tag_regex.sub("", for_regex.match(command).group()).strip()[1:-2]
			arguments = string.split(",")
			if len(arguments) == 1:
				start, stop, step = 0.0, float(arguments[0]), 1.0
				if not stop % 1:
					start, stop, step = int(start), int(stop), int(step)
			elif len(arguments) == 2:
				start, stop, step = float(arguments[0]), float(arguments[1]), 1.0
				if not start % 1 and not stop % 1:
					start, stop, step = int(start), int(stop), int(step)
			else:
				start, stop, step = float(arguments[0]), float(arguments[1]), float(arguments[2])
				if not start % 1 and not stop % 1 and not step % 1:
					start, stop, step = int(start), int(stop), int(step)
			repeatcomms = []
			next_command = ""
			while cindex != len(commands)-1 and not endfor_regex.search(compactedcommands[cindex+1]):
				cindex += 1
				next_command = compactedcommands[cindex]
				if next_command: 
					repeatcomms.append(next_command)
			cindex += 1
			if step:
				if step > 0:
					i, end, func = min(start, stop), max(start, stop), lessthan
				elif step < 0:
					i, end, func = max(start, stop), min(start, stop), greatthan
				while func(i, end):
					for cmd in repeatcomms:
						commands.append(fornum_regex.sub(str(i), cmd))
					i += step
		else:
			commands.append(command)
		cindex += 1


	for command in commands:
		command = command.strip()
		if not command or comment_regex.match(command): continue

		for var in variables:
			command = variables[var].sub(command)
		while func_regex.search(command):
			for macro in functions:
				command = functions[macro].sub(command)

		if define_regex.match(command):
			command_split = define_tag_regex.sub("", command).split()
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

		subcommands = command.split("\\;")
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

			subcommand = tag_regex.sub("", subcommand).strip()
			if not subcommand: continue

			command_obj = Command(subcommand, block=block, conditional=conditional, init=init)
			
			if init:
				init_commands.append(command_obj)
			else:
				clock_commands.append(command_obj)
	return init_commands, clock_commands