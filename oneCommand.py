endBraces = 0
x = 1
commands = []
once = []
print "----------------------------------------\nTheDestruc7i0n's 1.9 \"One Command\" Creator\n\n(Type \"INIT:\" before a command to make it execute only once)\n(Please report bugs to me on Twitter @TheDestruc7i0n with detailed information)\n(A known bug is when you have only one constant command and multiple \"INIT:\" commands. Also, you cannot have only one \"INIT:\" command and no constant commands.)\n----------------------------------------\n"
mi = raw_input("Manual (m) or Instant (i)? ")
if mi == "m":
	mi = True
elif mi == "i":
	mi = False
else:
	raise Exception("Error")

inp = raw_input("Command "+str(x)+": ")
while inp != "":
	x+=1
	commands.append(str(inp))
	inp = raw_input("Command "+str(x)+": ")

for testing in commands[:]:
	if testing[:5] == "INIT:":
		once.append(testing.replace("INIT:",""))
		commands.remove(testing)

if mi:
	if len(commands) > 0:
		commands.reverse()
		once.reverse()
		for eachCommand in commands:
			if len(commands) == 1 and len(once) <= 0:
				final = "/setblock ~ ~1 ~ repeating_command_block 1 replace {Command:"+str(eachCommand)+"}"
			else:
				if len(commands) == 1:
					commands.append("")
				if eachCommand == commands[0]:
					if len(commands) != 2:
						final = "/summon FallingSand ~ ~1 ~ {Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 2
					else:
						final = "/summon FallingSand ~ ~1 ~ {Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)
						endBraces += 1
				elif eachCommand == commands[-2]:
					final += str(eachCommand)
				elif eachCommand == commands[-1]:
					if len(once) > 0:
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:fill ~ ~ ~ ~ ~-"+str(len(once))+" ~ chain_command_block 1 replace},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 3
						for eachOnce in once:
							if eachOnce == once[-1]:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:},Data:1,Time:1"
								endBraces += 1
							else:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
								endBraces += 1
					else:
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:"+str(eachCommand)+"},Data:1,Time:1"
						endBraces += 1
					final += "".join(["}" for i in xrange(endBraces)])
				else:
					final += str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
					endBraces += 1
		if len(final) < 32500:
			print "\nCommand: \n\n"+final
			raw_input("\nWindows: Right click top screen bar, click Edit > Mark, select the command, hit enter.\nOSX: idk\n\nHit enter to close...")
		else:
			raise Exception("Too Large")
	else:
		raise Exception("Error")
else:
	if len(commands) > 0:
		commands.reverse()
		once.reverse()
		for eachCommand in commands:
			if len(commands) == 1 and len(once) <= 0:
				final = "/setblock ~ ~1 ~ repeating_command_block 1 replace {Command:"+str(eachCommand)+",auto:1b}"
			else:
				if len(commands) == 1:
					commands.append("")				
				if eachCommand == commands[0]:
					extraADD = 2 if len(once) >= 1 else 0
					if len(commands) != 2:
						final = "/summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 4
					elif len(commands) == 1:
						final = "/summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)
						endBraces += 3
					else:
						final = "/summon FallingSand ~ ~1 ~ {Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,TileEntityData:{Command:setblock ~ ~-"+str((len(commands)+len(once))+1+extraADD)+" ~ redstone_block},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)
						endBraces += 3
				elif eachCommand == commands[-2]:
					final += str(eachCommand)
				elif eachCommand == commands[-1]:
					if len(once) > 0:
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:fill ~ ~ ~ ~ ~-"+str(len(once))+" ~ chain_command_block 1 replace},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
						endBraces += 3
						for eachOnce in once:
							if eachOnce == once[-1]:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:},Data:1,Time:1,Riding:{id:FallingSand,Block:stone,Time:1}"
								endBraces += 1
							else:
								final += str(eachOnce)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
								endBraces += 1
					else:	
						final += "},Data:1,Time:1,Riding:{id:FallingSand,Block:repeating_command_block,TileEntityData:{Command:"+str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:stone,Time:1}"
						endBraces += 1
					final += "".join(["}" for i in xrange(endBraces)])
				else:
					final += str(eachCommand)+"},Data:1,Time:1,Riding:{id:FallingSand,Block:chain_command_block,TileEntityData:{Command:"
					endBraces += 1

		if len(final) < 32500:
			print "\nCommand: \n\n"+final
			raw_input("\nWindows: Right click top screen bar, click Edit > Mark, select the command, hit enter.\nOSX: idk\n\nHit enter to close...")
		else:
			raise Exception("Too Large")
	else:
		raise Exception("Error")
