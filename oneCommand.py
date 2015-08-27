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
		}
	}

def normal_sand(block, data=0):
	return {
		"Block": block,
		"Data": data,
		"Time": 1
	}


if __name__ == "__main__":
	cprint("""----------------------------------------
	        TheDestruc7i0n's 1.9 "One Command" Creator
	        (Type `INIT:` before a command to make it execute only once)
	        (Type `COND:` before a command to make it conditional)
	        (Please report bugs to me on Twitter @TheDestruc7i0n with detailed information)
	        (A known bug is when you have only one constant command and multiple "INIT:" commands. 
	        Also, you can't have only one "INIT:" command and no constant commands.)
	        ----------------------------------------""", strip=True)

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



	command_obj = None
	if len(clock_commands) or len(init_commands):
		command_sands = [normal_sand("redstone_block")]
		for command in init_commands:
			if command is init_commands[0]:
				command_sands.append(generate_sand(command, 0, "command_block"))
			else:
				command_sands.append(generate_sand(command, 0))

		if mode == 'i':
			offset = len(clock_commands) + 1
			command_sands.append(generate_sand(
				Command(format("blockdata ~ ~-{offset} ~ {auto:1b}", offset = offset)), 0
			))
		offset = len(init_commands) + 1
		command_sands.append(generate_sand(
			Command(format("fill ~ ~ ~ ~ ~{offset} ~ air", offset = offset)), 0
		))

		for command in clock_commands[::-1]:
			if command is clock_commands[-1]:
				commmand_sands.append(generate_sand(command, 1, "repeating_command_block", mode == 'i'))
			else:
				commmand_sands.append(generate_sand(command, 1))





	final_command = nbt.JSON2Command(command)


	if len(final_command) <= 32500 and final_command:
		pyperclip.copy(final)
		if not args.nocopy:
			cprint("Command copied to clipboard.")
			sys.stdout.write(final)
	elif not final_command:
		cprint("No command generated.", color=bcolors.RED)
	else:
		cprint("Command too large ({length} > 32500)", length=len(final), color=bcolors.RED)








	# if mi:
	# 	final = ""
	# 	if len(commands) > 0:
	# 		commands.reverse()
	# 		once.reverse()
	# 		for eachCommand in commands:
	# 			conditional = "conditional:1b," if eachCommand.cond else ""
	# 			if args.loud:
	# 				cprint("{cmd}{cond}", 
	# 					cmd=eachCommand,
	# 					cond = "\n  - Conditional" if eachCommand.cond else "")
	# 			if len(commands) == 1 and len(once) <= 0:
	# 				final = "setblock ~ ~1 ~ repeating_command_block 1 replace {"+ conditional +"Command:"+str(eachCommand)+"}"
	# 			else:
	# 				if len(commands) == 1:
	# 					commands.append("")
	# 				if eachCommand == commands[0]:
	# 					if len(commands) != 2:
	# 						final = "summon FallingSand ~ ~1 ~ {Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
	# 						endBraces += 2
	# 					else:
	# 						final = "summon FallingSand ~ ~1 ~ {Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)
	# 						endBraces += 1
	# 				elif eachCommand == commands[-2]:
	# 					final += str(eachCommand)
	# 				elif eachCommand == commands[-1]:
	# 					if len(once) > 0:
	# 						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:fill ~ ~ ~ ~ ~-"+str(len(once))+" ~ chain_command_block 1 replace},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
	# 						endBraces += 3
	# 						for eachOnce in once:
	# 							if eachOnce == once[-1]:
	# 								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:},Data:1,Time:1"
	# 								endBraces += 1
	# 							else:
	# 								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
	# 								endBraces += 1
	# 					else:
	# 						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1"
	# 						endBraces += 1
	# 					final += "}"*endBraces
	# 				else:
	# 					final += str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
	# 					endBraces += 1
	# 	if len(final) < 32500:
	# 		pyperclip.copy(final)
	# 		if not args.nocopy:
	# 			cprint("Command (copied to clipboard):")
	# 		sys.stdout.write(final)
	# 	else:
	# 		raise OverflowError("Command too large ("+str(len(final))+" > 32500)")
	# else:
	# 	final = ""
	# 	if len(commands) > 0:
	# 		commands.reverse()
	# 		once.reverse()
	# 		for eachCommand in commands:
	# 			conditional = "conditional:1b," if eachCommand.cond else ""
	# 			if args.loud:
	# 				cprint("{cmd}{cond}", 
	# 					cmd=eachCommand,
	# 					cond = "\n  - Conditional" if eachCommand.cond else "")
	# 			if len(commands) == 1 and len(once) <= 0:
	# 				final = "setblock ~ ~1 ~ repeating_command_block 1 replace {"+ conditional +"Command:"+str(eachCommand)+",auto:1b}"
	# 			else:
	# 				if len(commands) == 1:
	# 					commands.append("")				
	# 				if eachCommand == commands[0]:
	# 					extraADD = 2 if len(once) >= 1 else 0
	# 					if len(commands) != 2:
	# 						final = "summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
	# 						endBraces += 4
	# 					elif len(commands) == 1:
	# 						final = "summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)
	# 						endBraces += 3
	# 					else:
	# 						final = "summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)
	# 						endBraces += 3
	# 				elif eachCommand == commands[-2]:
	# 					final += str(eachCommand)
	# 				elif eachCommand == commands[-1]:
	# 					if len(once) > 0:
	# 						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:fill ~ ~ ~ ~ ~-"+str(len(once))+" ~ chain_command_block 1 replace},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"
	# 						endBraces += 3
	# 						for eachOnce in once:
	# 							onecond = "conditional:1b," if oneCond.cond else ""
	# 							if args.loud:
	# 								cprint("{cmd}\n  - Initialization{cond}", 
	# 									cmd=eachOnce,
	# 									cond = "\n  - Conditional" if eachCommand.cond else "")
	# 							if eachOnce == once[-1]:
	# 								final += onecond+"Command:" + str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:},Data:1,Time:1,Riding:{id:FallingSand,Block:stone,Time:1}"
	# 								endBraces += 1
	# 							else:
	# 								final += onecond+"Command:"+str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"
	# 								endBraces += 1
	# 					else:	
	# 						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:stone,Time:1}"
	# 						endBraces += 1
	# 					final += "}"*endBraces
	# 				else:
	# 					final += str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
	# 					endBraces += 1
	# 	if len(final) < 32500:
	# 		pyperclip.copy(final)
	# 		if not args.nocopy:
	# 			cprint("Command (copied to clipboard):")
	# 		sys.stdout.write(final)
	# 	else:
	# 		raise OverflowError("Command too large ("+str(len(final))+" > 32500)")
