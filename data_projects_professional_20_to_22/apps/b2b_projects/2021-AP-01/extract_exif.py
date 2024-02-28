#!../../../bin/python3

from datetime import datetime
import collections
import os
import shutil
import sys

import exifread
import pandas as pd

from libs.utils.cmd_args import CMDArgs
from libs.utils.df_utils import DFUtils


app_name = 'extract_exif'
now_s = lambda: str(datetime.now())
gps_list2float = lambda value: sum(map(lambda x: x[1]/(60**x[0]), enumerate(map(lambda x: float(eval(x)), value.replace('[', '').replace(']', '').split(',')))))
gps_float2str = lambda key, tags: str(gps_list2float(str(tags[key]))) + ' ' + str(tags[key + 'Ref']) if key in tags.keys() else ''

code_flash_map = {
	'0': 'No Flash',
	'1': 'Fired',
	'5': 'Fired, Return not detected',
	'7': 'Fired, Return detected',
	'8': 'On, Did not fire',
	'9': 'On, Fired',
	'13': 'On, Return not detected',
	'15': 'On, Return detected',
	'16': 'Off, Did not fire',
	'20': 'Off, Did not fire, Return not detected',
	'24': 'Auto, Did not fire',
	'25': 'Auto, Fired',
	'29': 'Auto, Fired, Return not detected',
	'31': 'Auto, Fired, Return detected',
	'32': 'No flash function',
	'48': 'Off, No flash function',
	'65': 'Fired, Red-eye reduction',
	'69': 'Fired, Red-eye reduction, Return not detected',
	'71': 'Fired, Red-eye reduction, Return detected',
	'73': 'On, Red-eye reduction',
	'77': 'On, Red-eye reduction, Return not detected',
	'79': 'On, Red-eye reduction, Return detected',
	'80': 'Off, Red-eye reduction',
	'88': 'Auto, Did not fire, Red-eye reduction',
	'89': 'Auto, Fired, Red-eye reduction',
	'93': 'Auto, Fired, Red-eye reduction, Return not detected',
	'95': 'Auto, Fired, Red-eye reduction, Return detected'
}

code_meteringmode_map = {
	'0': 'Unknown',
	'1': 'Average',
	'2': 'Center-weighted average',
	'3': 'Spot',
	'4': 'Multi-spot',
	'5': 'Multi-segment',
	'6': 'Partial',
	'255': 'Other'
}

code_exposuremode_map = {
	'0': 'Auto',
	'1': 'Manual',
	'2': 'Auto bracket'
}

code_whitebalance_map = {
	'0': 'Auto',
	'1': 'Manual'
}


def get_tags_on_os(path, heic_file):
	tags = {}

	try:
		raw_values = os.popen('identify -format \'%[EXIF:*]\' {}/{}'.format(path, heic_file)).readlines()
		if not raw_values:
			return tags

		raw_tags = {}
		for raw_value in raw_values:
			k, v = raw_value.strip().split('=', 2)
			raw_tags[k] = v
	
		tags['Image Make'] = raw_tags['exif:Make']
		tags['Image Model'] = raw_tags['exif:Model']
		tags['EXIF ExposureTime'] = raw_tags['exif:ExposureTime']
		tags['EXIF ApertureValue'] = raw_tags['exif:ApertureValue']
		tags['EXIF FocalLength'] = raw_tags['exif:FocalLength']
		tags['EXIF ISOSpeedRatings'] = raw_tags['exif:PhotographicSensitivity']
		tags['EXIF Flash'] = code_flash_map[raw_tags['exif:Flash']]
		tags['EXIF DateTimeOriginal'] = raw_tags['exif:DateTimeOriginal']
		tags['EXIF DateTimeDigitized'] = raw_tags['exif:DateTimeDigitized']
		tags['EXIF BrightnessValue'] = raw_tags['exif:BrightnessValue']
		tags['EXIF MeteringMode'] = code_meteringmode_map[raw_tags['exif:MeteringMode']]
		tags['EXIF ExposureMode'] = code_exposuremode_map[raw_tags['exif:ExposureMode']]
		tags['EXIF WhiteBalance'] = code_whitebalance_map[raw_tags['exif:WhiteBalance']]
		tags['EXIF LensMake'] = raw_tags['exif:LensMake']
		tags['EXIF LensModel'] = raw_tags['exif:LensModel']
		if 'exif:GPSLatitude' in raw_tags:
			tags['GPS GPSLatitude'] = '[' + raw_tags['exif:GPSLatitude'] + ']'
			tags['GPS GPSLatitudeRef'] = raw_tags['exif:GPSLatitudeRef']
		if 'exif:GPSLongitude' in raw_tags:
			tags['GPS GPSLongitude'] = '[' + raw_tags['exif:GPSLongitude'] + ']'
			tags['GPS GPSLongitudeRef'] = raw_tags['exif:GPSLongitudeRef']
		if 'exif:GPSAltitude' in raw_tags:
			tags['GPS GPSAltitude'] = raw_tags['exif:GPSAltitude']
	except:
		tags = {}
		print('{} [MAJOR][{}.get_tags_on_os] Error: {}'.format(now_s(), app_name, str(sys.exc_info()).replace('"', ' ')))

	return tags


def get_file_and_tags_list(path):
	heic_files, tags_list = [], []

	all_heic_files = list(filter(lambda name: name[-4:].lower() == 'heic', os.listdir(path)))
	all_heic_files.sort()
	all_heic_files_count = len(all_heic_files)
	success_count = 0
	failed_count = 0

	for i, heic_file in enumerate(all_heic_files):
		print('{} [INFO][{}.get_file_and_tags_list] [{:,}/{:,}] Opening {} ...'.format(now_s(), app_name, i+1, all_heic_files_count, heic_file))
		f = open(path + '/' + heic_file, 'rb')
		try:
			exif = exifread.process_file(f)
			heic_files += [heic_file]
			tags_list += [exif]
			success_count += 1
		except:
			print('{} [MINOR][{}.get_file_and_tags_list] [{:,}/{:,}] Try opening {} again ...'.format(now_s(), app_name, i+1, all_heic_files_count, heic_file))
			exif = get_tags_on_os(path, heic_file)
			if exif:
				heic_files += [heic_file]
				tags_list += [exif]
				success_count += 1
			else:
				print('{} [MAJOR][{}.get_file_and_tags_list] [{:,}/{:,}] Cannot open {}'.format(now_s(), app_name, i+1, all_heic_files_count, heic_file))
				error_path = f'{path}/error'
				(not os.path.exists(error_path)) and os.mkdir(error_path)
				src_file_p = f'{path}/{heic_file}'
				dst_file_p = f'{error_path}/{heic_file}'
				shutil.move(src_file_p, dst_file_p)
				failed_count += 1

	return heic_files, tags_list, all_heic_files_count, success_count, failed_count


def get_metadata_list(file_list, tags_list):
	metadata_list = []

	file_i = 0
	files_count = len(file_list)
	for heic_file, tags in zip(file_list, tags_list):
		file_i += 1
		print('{} [INFO][{}.get_metadata_list] [{:,}/{:,}] Extracting {} ...'.format(now_s(), app_name, file_i, files_count, heic_file))

		metadata_list += [[
			heic_file,
			tags['Image Make'],
			tags['Image Model'],
			tags['EXIF ExposureTime'],
			eval(str(tags['EXIF ApertureValue'])),
			eval(str(tags['EXIF FocalLength'])),
			int(str(tags['EXIF ISOSpeedRatings'])),
			tags['EXIF Flash'],
			tags['EXIF DateTimeOriginal'],
			tags['EXIF DateTimeDigitized'],
			eval(str(tags['EXIF BrightnessValue'])),
			tags['EXIF MeteringMode'],
			tags['EXIF ExposureMode'],
			tags['EXIF WhiteBalance'],
			tags['EXIF LensMake'],
			tags['EXIF LensModel'],
			gps_float2str('GPS GPSLatitude', tags),
			gps_float2str('GPS GPSLongitude', tags),
			eval(str(tags['GPS GPSAltitude'])) if 'GPS GPSAltitude' in tags.keys() else ''
		]]

	return metadata_list


def save_data(path, output_file, col_names, rows):
	df = pd.DataFrame(data=rows, columns=col_names)
	df_utils = DFUtils('df_utils')
	df_utils.save(df, path, output_file)


def print_summary(all_count, success_count, failed_count):
	print('{} [INFO][{}.print_summary] ===== ===== ====='.format(now_s(), app_name))
	print('{} [INFO][{}.print_summary] summary'.format(now_s(), app_name))
	print('{} [INFO][{}.print_summary] ===== ===== ====='.format(now_s(), app_name))
	print('{} [INFO][{}.print_summary] all count     : {:,}'.format(now_s(), app_name, all_count))
	print('{} [INFO][{}.print_summary] success count : {:,}'.format(now_s(), app_name, success_count))
	print('{} [INFO][{}.print_summary] failed count  : {:,}'.format(now_s(), app_name, failed_count))
	print('{} [INFO][{}.print_summary] verification  : {}'.format(now_s(), app_name, all_count == (success_count + failed_count)))


def main():
	args_exif = CMDArgs('cmd_args_exif', ['path'])
	args = args_exif.values

	col_names = [
		'Filename',
		'Make',
		'Model',
		'Exposure',
		'Aperture',
		'Focal Length',
		'ISO Speed',
		'Flash',
		'DateTimeOriginal',
		'CreateDate',
		'BrightnessValue',
		'MeteringMode',
		'ExposureMode',
		'WhiteBalance',
		'LensMake',
		'LensModel',
		'Latitude',
		'Longitude',
		'Altitude'
	]

	file_list, tags_list, all_count, success_count, failed_count = get_file_and_tags_list(args.path)
	rows = get_metadata_list(file_list, tags_list)

	output_file = args.path.rsplit('/')[-1] + '.xlsx'
	save_data(args.path, output_file, col_names, rows)

	print_summary(all_count, success_count, failed_count)


if __name__ == '__main__':
	main()
