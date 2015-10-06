from classes import Command, FakeCommand
from util import cprint, format, bcolors
import nbtencoder as nbt

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
			if loud:
				cprint("minecraft:command_block:0\n  - Initialization", color=bcolors.DARKGRAY, allow_repeat=True)
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