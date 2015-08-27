from __future__ import print_function


import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--manual", help="Uses manual mode", dest="manual", action="store_true")
parser.add_argument("-i", "--instant", help="Uses instant mode", dest="instant", action="store_false")
parser.add_argument("-f", "--command_file", help="File to load commands from", dest="filepath", action="store",
	default="")
parser.add_argument("-C", "--no-copy", help="Don't copy the output command", dest="nocopy", action="store_true")
parser.add_argument("-q", "--quiet", help="Silence output", dest="quiet", action="store_true")
parser.add_argument("-v", "--verbose", help="Detailed output", dest="loud", action="store_true")
args = parser.parse_args()

if args.quiet:
	def print(*args, **kwargs):
		pass

if args.nocopy:
	class pyperclip:
		@staticmethod
		def copy(*args, **kwargs): pass
		@staticmethod
		def paste(*args, **kwargs): pass
else:
	import pyperclip

print("""
----------------------------------------
TheDestruc7i0n's 1.9 "One Command" Creator

(Type `INIT:` before a command to make it execute only once)
(Type `COND:` before a command to make it conditional)
(Please report bugs to me on Twitter @TheDestruc7i0n with detailed information)
(A known bug is when you have only one constant command and multiple "INIT:" commands. 
Also, you cannot have only one "INIT:" command and no constant commands.)
----------------------------------------
""")

class Command:
	def __init__(self, cmd, conditional):
		self.cmd = cmd
		self.cond = conditional
	def __str__(self):
		return self.cmd

endBraces = 0
x = 1
once = []
if not args.manual and args.instant:
	mi = raw_input("Manual (m) or Instant (i)? ")
	if mi == "m":
		mi = True
	elif mi == "i":
		mi = False
	else:
		raise ValueError("Not manual or instant")
else:
	mi = args.manual if args.manual else args.instant

cmdtext = []
if not args.filepath:
	inp = raw_input("Command "+str(x)+": ")
	while inp != "":
		x+=1
		cmdtext.append(str(inp))
		inp = raw_input("Command "+str(x)+": ")
elif args.filepath == "stdin":
	cmdtext = sys.stdin.read().split("\n")
else:
	import os.path
	if os.path.exists(args.filepath):
		cmdtext = open(args.filepath).read().split("\n")
	else:
		raise IOError("File "+args.filepath+" not found.")

commands = []
for cmd in cmdtext[:]:
	init = False
	cond = False
	if cmd[:5] == "INIT:":
		cmd = cmd[5:]
		init = True
		if cmd[:5] == "COND:":
			cmd = cmd[5:]
			cond = True
	elif cmd[:5] == "COND:":
		cmd = cmd[5:]
		cond = True
		if cmd[:5] == "INIT:":
			cmd = cmd[5:]
			init = True
	if init:
		once.append(Command(cmd, cond))
	else:
		commands.append(Command(cmd, cond))

if mi:
	final = ""
	if len(commands) > 0:
		commands.reverse()
		once.reverse()
		for eachCommand in commands:
			conditional = "conditional:1b," if eachCommand.cond else ""
			if args.loud:
				print(eachCommand)
				if eachCommand.cond:
					print("  - Conditional")
			if len(commands) == 1 and len(once) <= 0:
				final = "setblock ~ ~1 ~ repeating_command_block 1 replace {"+ conditional +"Command:"+str(eachCommand)+"}"
			else:
				if len(commands) == 1:
					commands.append("")
				if eachCommand == commands[0]:
					if len(commands) != 2:
						final = "summon FallingSand ~ ~1 ~ {Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 2
					else:
						final = "summon FallingSand ~ ~1 ~ {Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)
						endBraces += 1
				elif eachCommand == commands[-2]:
					final += str(eachCommand)
				elif eachCommand == commands[-1]:
					if len(once) > 0:
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:fill ~ ~ ~ ~ ~-"+str(len(once))+" ~ chain_command_block 1 replace},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 3
						for eachOnce in once:
							if eachOnce == once[-1]:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:},Data:1,Time:1"
								endBraces += 1
							else:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
								endBraces += 1
					else:
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1"
						endBraces += 1
					final += "}"*endBraces
				else:
					final += str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
					endBraces += 1
	if len(final) < 32500:
		pyperclip.copy(final)
		if not args.nocopy:
			print("\nCommand (copied to clipboard): \n\n"+final)
		sys.stdout.write(final)
	else:
		raise OverflowError("Command too large ("+str(len(final))+" > 32500)")
else:
	final = ""
	if len(commands) > 0:
		commands.reverse()
		once.reverse()
		for eachCommand in commands:
			conditional = "conditional:1b," if eachCommand.cond else ""
			if args.loud:
				print(eachCommand)
				if eachCommand.cond:
					print("  - Conditional")
			if len(commands) == 1 and len(once) <= 0:
				final = "setblock ~ ~1 ~ repeating_command_block 1 replace {"+ conditional +"Command:"+str(eachCommand)+",auto:1b}"
			else:
				if len(commands) == 1:
					commands.append("")				
				if eachCommand == commands[0]:
					extraADD = 2 if len(once) >= 1 else 0
					if len(commands) != 2:
						final = "summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 4
					elif len(commands) == 1:
						final = "summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)
						endBraces += 3
					else:
						final = "summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)
						endBraces += 3
				elif eachCommand == commands[-2]:
					final += str(eachCommand)
				elif eachCommand == commands[-1]:
					if len(once) > 0:
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:fill ~ ~ ~ ~ ~-"+str(len(once))+" ~ chain_command_block 1 replace},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 3
						for eachOnce in once:
							if eachOnce == once[-1]:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:},Data:1,Time:1,Riding:{id:FallingSand,Block:stone,Time:1}"
								endBraces += 1
							else:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
								endBraces += 1
					else:	
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{"+ conditional +"Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:stone,Time:1}"
						endBraces += 1
					final += "}"*endBraces
				else:
					final += str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
					endBraces += 1
	if len(final) < 32500:
		pyperclip.copy(final)
		if not args.nocopy:
			print("\nCommand (copied to clipboard): \n\n"+final)
		sys.stdout.write(final)
	else:
		raise OverflowError("Command too large ("+str(len(final))+" > 32500)")
