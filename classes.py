from util import format, cprint
import re

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