import sands
import nbtencoder as nbt
from classes import Command, FakeCommand
from util import cprint, format, bcolors

def ride(entities, have_id=True):
	bottommost = entities[0]
	bottommost["Passengers"] = entities[1:]
	if not have_id: del bottommost["id"]
	return bottommost

def cart(command):
	return {
		"id": nbt.noquote_str("MinecartCommandBlock"),
		"Command": command
	}

def cart_block(offset, block, damage=0, data={}):
	cmd = format("setblock ~ ~{offset} ~ {block} {dmg} replace", block=block, dmg=damage)
	if offset: cmd = format(cmd, offset=offset)
	else:      cmd = format(cmd, offset="")
	if data:   cmd = nbt.cmd(cmd, data, True)
	return cart(cmd)


def cart_command_block(offset, command_obj, direction=0, mode='i'):
	if isinstance(command_obj, FakeCommand):
		return cart_block(offset, command_obj.block, command_obj.data)
	tag = {
		"Command": str(command_obj),
		"TrackOutput": nbt.int_b(0)
	}
	if command_obj.block == "chain_command_block" or (mode == 'i' and command_obj.block == "repeating_command_block"):
		tag["auto"] = 1
	data = direction+8 if command_obj.cond else direction
	return cart_block(offset, command_obj.block, data, tag)


def gen_cart_stack(init_commands, clock_commands, mode, loud=False):
	final_command_obj = None
	if clock_commands or init_commands:
		entities = []
		entities.append(sands.normal_sand("activator_rail"))
		for command in init_commands:
			if hasattr(command, "cmd"):
				if loud:
					cprint(command.prettystr())
				entities.append(cart(command.cmd))
		offset = 1
		for command in clock_commands:
			if offset == 1:
				command.block = "repeating_command_block"
			if loud:
				cprint(command.prettystr())
			entities.append(cart_command_block(offset, command, 1, mode))
			offset += 1

		filloffset = offset+1
		offset += 2
		entities.append(cart_command_block(offset, Command(format("clone ~ ~-2 ~ ~ ~-{o1} ~ ~ ~-{o2} ~ replace move", o1=offset-1,o2=offset+2))))
		offset += 1
		entities.append(cart_command_block(offset, Command(format("fill ~ ~-{o1} ~ ~ ~-{o2} ~ air", o1=offset,o2=offset+2))))

		offset += 1
		activatesand = sands.normal_sand("command_block")
		activatesand["TileEntityData"] = {"auto": 1}

		entities.append(cart_block(offset, "air"))
		entities.append(cart(nbt.cmd(format("summon FallingSand ~ ~{o} ~ ", o=offset), activatesand, True)))

		entities.append(cart_command_block(filloffset, Command(format("fill ~ ~ ~ ~ ~{o} ~ air", o=offset-filloffset))))
		entities.append(cart("kill @e[r=1,type=MinecartCommandBlock]"))
		stack = ride(entities)
		final_stack = sands.ride([
			stack, 
			sands.normal_sand("redstone_block"),
			sands.normal_sand("barrier")
		], False)
		final_command_obj = nbt.cmd("summon FallingSand ~ ~1 ~ ", final_stack)

	final_command = nbt.JSON2Command(final_command_obj)
	return final_command