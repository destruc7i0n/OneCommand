class cmd:
	def __init__(self, command, obj, as_string=False):
		self.command = command
		self.obj = obj
		self.as_string = as_string
	def __str__(self):
		return JSON2Command(self)
	def __repr__(self):
		return str(self)

def JSON2Command(json):
	command = ""

	if isinstance(json, cmd):
		command += json.command
		command += JSON2Command(json.obj)
		if json.as_string:
			command.replace(ur'"', ur'\"')
			command = '"' + command + '"'

	elif isinstance(json, dict):
		command += "{"

		for tag in json:
			command += tag
			command += ":"
			command += JSON2Command(json[tag])
			command += ","

		if command[-1] == ",":
			command = command[:-1]

		command += "}"

	elif isinstance(json, list):
		command += "["

		for tag in json:
			command += JSON2Command(tag)
			command += ","
		else:
			if command[-1] == ",":
				command = command[:-1]
		command += "]"

	elif isinstance(json, str):
		command += '"'
		command += json.replace(ur'"', ur'\"')
		command += '"'

	else:
		command += str(json)

	return command