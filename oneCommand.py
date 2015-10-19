from __future__ import print_function

from parse import *
from wireutils import *

color_printing_config.name = "Generator"
color_printing_config.color = ansi_colors.PEACH

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-m", "--mode", help="Choose activation mode for system", dest="mode", default="", choices=["m", "i"])
	parser.add_argument("-f", "--command_file", help="File to load commands from", dest="filepath", nargs="?",
		default=None, const="stdin")
	parser.add_argument("-a", "--alternate-parser", help="Use the old parser", dest="nocart", action="store_true")
	parser.add_argument("-C", "--no-copy", help="Don't copy the output command", dest="nocopy", action="store_true")
	parser.add_argument("-q", "--quiet", help="Silence output", dest="quiet", action="store_true")
	parser.add_argument("-v", "--verbose", help="Detailed output", dest="loud", action="store_true")
	parser.add_argument("-O", "--no-output", help="Don't dump cmd to STDOUT", dest="nostdout", action="store_true")
	args = parser.parse_args()
	if args.quiet:
		def color_print(*args, **kwargs):
			pass

	if args.nocopy:
		class pyperclip:
			@staticmethod
			def copy(*args, **kwargs): pass
			@staticmethod
			def paste(*args, **kwargs): pass
	else:
		import pyperclip

	color_print("""{peach}----------------------------------------{endc}
	  {cyan}TheDestruc7i0n{endc} and {golden}Wire Segal{endc}'s 1.9 One Command Generator
	 {green}Prepend your command with `#` to comment it out.{endc}
	 {green}Prepend your command with `DEFINE:` to make it a variable definition.{endc}
	        Example: `DEFINE:world hello` and `say $world` would say `hello`.
	 {green}Prepend your command with `REPEAT:` to make it a repeating command block.{endc}
	 {green}Prepend your command with `INIT:` to make it only run when the structure is deployed.{endc}
	 {green}`BLOCK:minecraft:{name}:{data}` will summon a block (thereby stopping the current `REPEAT:` signal.){endc}
	 {green}Prepend your command with `COND:` to make it a conditional command.{endc}
	        Please report any bugs at the GitHub repo: {line}{blue}https://github.com/destruc7i0n/OneCommand/issues{endc} {endc}
	        {peach}----------------------------------------{endc}""", strip=True)

	# get mode if not specified by argument
	if not args.mode:
		if args.filepath == "stdin":
			color_print("WARNING: Mode must be specified by command line in stdin mode. Using instant mode.", color=ansi_colors.YELLOW)
			mode = "i"
		else:
			mode = color_input("Manual (m) or Instant (i)? ").strip().lower()
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
		try:
			command = color_input("Command {num}: ", num=x).strip()
			while command:
				x += 1
				commands.append(command)
				command = color_input("Command {num}: ", num=x).strip()
		except (KeyboardInterrupt, EOFError): print(); quit()
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

	if args.nocart:
		final_command = gen_stack(init_commands, clock_commands, mode, args.loud)
	else:
		final_command = gen_cart_stack(init_commands, clock_commands, mode, args.loud)
	


	if len(final_command) <= 32500 and final_command:
		pyperclip.copy(final_command)
		if args.nocopy:
			color_print("{bold}Final command{endc}", func=sys.stderr.write)
		else:
			color_print("{bold}Copied to clipboard{endc}", func=sys.stderr.write)
		if args.nostdout:
			if not args.quiet: sys.stderr.write(format("{bold}.{endc}"))
		else:
			if not args.quiet: sys.stderr.write(format("{bold} - {endc}"))
			sys.stdout.write(final_command + "\n")
	elif not final_command:
		color_print("No command generated.", color=ansi_colors.RED)
	else:
		color_print("Command too large ({length} > 32500)", length=len(final_command), color=ansi_colors.RED)
