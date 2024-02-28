import operator


class ImageBox:
	coordinate = None
	lang_codes = {}
	text = ''


	def update_coordinate(self, new_coordinate):
		if self.coordinate:
			self.coordinate = [
				min(self.coordinate[0], new_coordinate[0]),
				min(self.coordinate[1], new_coordinate[1]),
				max(self.coordinate[2], new_coordinate[2]),
				max(self.coordinate[3], new_coordinate[3])
			]
		else:
			self.coordinate = new_coordinate


	def get_lang_code(self):
		return max(self.lang_codes.items(), key=operator.itemgetter(1))[0]


	def __init__(self, name):
		self.name = name


class ImageBlock:
	boxes = []
	coordinate = None
	lang_code = ''
	text = ''


	def __init__(self, name):
		self.name = name


class ImageInfo:
	blocks = []


	def __init__(self, name):
		self.name = name
