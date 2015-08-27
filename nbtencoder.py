def JSON2Command(json):
	command = ""

	if isinstance(json, dict):
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