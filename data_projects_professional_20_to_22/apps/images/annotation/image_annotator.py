#!../../../bin/python3

from datetime import datetime
import io
import os
import pickle
import sys

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import pandas as pd

from cmd_opts_child import CMDOptsChild
from config import Config
from image_info import ImageInfo, ImageBlock, ImageBox
from libs.utils.df_utils import DFUtils


def annotate(filename, pickle_filename):
	document = None
	if os.path.exists(pickle_filename):
		print('%s [INFO][image_annotator.annotate] Loading from %s ...' % (str(datetime.now()), pickle_filename))
		with open(pickle_filename, 'rb') as pickle_file:
			document = pickle.load(pickle_file)

	if not document:
		with io.open(filename, 'rb') as image_file:
			content = image_file.read()

		image = types.Image(content=content)
		response = client.document_text_detection(image=image)
		document = response.full_text_annotation

	image_info = ImageInfo('image_info')
	image_info.blocks = []
	for block in document.pages[0].blocks:
		image_info.blocks += [get_image_block(block)]

	with open(pickle_filename, 'wb') as pickle_file:
		pickle.dump(document, pickle_file)

	return image_info


def get_image_block(block):
	coordinate_func = lambda bounds: [
		min([bound.x for bound in bounds.vertices]),
		min([bound.y for bound in bounds.vertices]),
		max([bound.x for bound in bounds.vertices]),
		max([bound.y for bound in bounds.vertices])
	]

	words = []
	for box in block.paragraphs:
		for word in box.words:
			coordinate = coordinate_func(word.bounding_box)
			if len(word.property.detected_languages) >= 1:
				lang_code = word.property.detected_languages[0].language_code
			else:
				lang_code = 'null'
			text = ''.join([symbol.text for symbol in word.symbols])
			words += [(coordinate, lang_code, text)]

	image_boxes = []
	for coordinate, lang_code, text in words:
		image_box = next((image_box for image_box in image_boxes if image_box.coordinate[1] == coordinate[1]), None)
		if image_box:
			image_box.update_coordinate(coordinate)
			image_box.lang_codes[lang_code] = image_box.lang_codes.get(lang_code, 0) + 1
			image_box.text += f' {text}'
		else:
			image_box = ImageBox('image_box')
			image_box.coordinate = coordinate
			image_box.text = text
			image_box.lang_codes = {}
			image_box.lang_codes[lang_code] = 1
			image_boxes += [image_box]

	image_block = ImageBlock('image_block')
	image_block.boxes = image_boxes
	image_block.coordinate = [
		min([box.coordinate[0] for box in image_boxes]),
		min([box.coordinate[1] for box in image_boxes]),
		max([box.coordinate[2] for box in image_boxes]),
		max([box.coordinate[3] for box in image_boxes])
	]
	image_block.text = ' '.join([box.text for box in image_boxes])

	return image_block


def draw_box(image_info, filename, width):
	print('%s [INFO][image_annotator.draw_box] Opening %s ...' % (str(datetime.now()), filename))

	outer_coordinate = lambda coordinate: [
		coordinate[0] - width,
		coordinate[1] - width,
		coordinate[2] + width,
		coordinate[3] + width
	]

	image = Image.open(filename)
	image_draw = ImageDraw.Draw(image)
	for block_index, block in enumerate(image_info.blocks):
		image_draw.rectangle(outer_coordinate(block.coordinate), outline='blue', width=width)
		for box_index, box in enumerate(block.boxes):
			print(f'block#, box#: {block_index}, {box_index}')
			print(f'xy: {box.coordinate}')
			print(f'text: {box.text}')
			image_draw.rectangle(box.coordinate, outline='red', width=width)

	output_file = '_boxed.'.join(filename.split('.'))
	image.save(output_file)
	print('%s [INFO][image_annotator.draw_box] Saved as %s' % (str(datetime.now()), output_file))


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def main():
	opts = CMDOptsChild('opts', sys.argv[1:])
	if not opts.is_loaded:
		return

	config = Config('config')
	if not config.is_loaded:
		print('[CRITICAL][image_annotator.main] Can\'t open config.ini.')
		return

	if opts.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	global client
	client = vision.ImageAnnotatorClient()

	rows = []
	box_width = 2
	for input_file in opts.input_files:
		with open(f'{opts.path}/{input_file}', 'r+') as f:
			image_files = [line.replace('\n', '') for line in f.readlines()]
			for image_file_with_path in image_files:
				pickle_file_with_path = image_file_with_path.split('.')[0] + '.pickle'
				image_info = annotate(image_file_with_path, pickle_file_with_path)
				draw_box(image_info, image_file_with_path, box_width)

				image_file = image_file_with_path.split('/')[-1]
				for block_index, block in enumerate(image_info.blocks):
					for box_index, box in enumerate(block.boxes):
						rows.append([
							image_file,
							block_index + 1,
							box_index + 1,
							box.coordinate[0],
							box.coordinate[1],
							box.coordinate[2],
							box.coordinate[3],
							box.get_lang_code(),
							box.text
						])

	col_names = ['image_file', 'block_id', 'box_id', 'left_x', 'top_y', 'right_x', 'bottom_y', 'lang_code', 'text']
	df = pd.DataFrame(rows, columns=col_names)
	df_utils = DFUtils('df_utils')
	df_utils.save(df, opts.path, opts.output_file, 100000)


if __name__ == '__main__':
	main()
