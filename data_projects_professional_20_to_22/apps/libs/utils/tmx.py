import os
from xml.etree import ElementTree as etree
from lxml import etree as lxml_etree

from libs.utils.code_books import LanguageFormat
from libs.utils.lang_code_converter import LangCodeConverter


class TMX:
	__lang_code_converter = LangCodeConverter('lang_code_conveter')
	__encoding = 'utf-8'


	def add_translation(self, sid, lang_codes, texts, prop_type=None, prop_text=None):
		if self.__lang_format == LanguageFormat.BCP47:
			new_lang_codes = [self.__lang_code_converter.iso639_1_to_bcp47(lang_code) for lang_code in lang_codes]
		else:
			new_lang_codes = lang_codes

		tu = etree.SubElement(self.__body, 'tu')
		tu.set('datatype', 'xml')
		tu.set('srclang', new_lang_codes[0])
		tu.set('tuid', str(sid))

		if prop_text:
			prop = etree.SubElement(tu, 'prop')
			if prop_type:
				prop.set('type', prop_type)
			seg = etree.SubElement(prop, 'seg')
			seg.text = prop_text

		for tuv in zip(new_lang_codes, texts):
			lang_code = tuv[0]
			text = tuv[1]
			tuv = etree.SubElement(tu, 'tuv')
			tuv.set('xml:lang', lang_code)
			seg = etree.SubElement(tuv, 'seg')
			seg.text = text


	def save(self, path, output_file):
		temp_tmx_file = '%s/temp_%s' % (path, output_file)
		tmx_file = '%s/%s' % (path, output_file)
		self.__tree.write(temp_tmx_file, encoding=self.__encoding, xml_declaration=True)

		parser = lxml_etree.XMLParser()
		lxml_tree = lxml_etree.parse(temp_tmx_file, parser)
		lxml_tree.write(tmx_file, encoding=self.__encoding, xml_declaration=True, pretty_print=True)

		if os.path.exists(temp_tmx_file):
			os.remove(temp_tmx_file)


	def __create(self):
		tmx = etree.Element('tmx')
		self.__tree = etree.ElementTree(tmx)
		self.__body = etree.SubElement(tmx, 'body')


	def __init__(self, name, lang_format=LanguageFormat.ISO639):
		self.name = name
		self.__lang_format = lang_format
		self.__create()
