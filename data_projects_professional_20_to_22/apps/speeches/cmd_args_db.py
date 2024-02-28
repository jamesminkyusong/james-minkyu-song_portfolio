from libs.utils.cmd_args import CMDArgs


class CMDArgsDB(CMDArgs):
	__child_args = [
		[['--event_id'], {'type': int, 'help': 'event_id'}]
	]


	def __validate(self):
		message = None

		if self.values.event_id <= 0:
			message = '--event_id is not valid!'

		if message:
			self.parser.error(message)


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
