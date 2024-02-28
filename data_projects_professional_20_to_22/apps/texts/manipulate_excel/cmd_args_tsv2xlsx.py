from libs.utils.cmd_args import CMDArgs


class CMDArgsTSV2XLSX(CMDArgs):
	def __init__(self, name, required_args=None):
		self.name = name
		super().__init__(name, required_args)
