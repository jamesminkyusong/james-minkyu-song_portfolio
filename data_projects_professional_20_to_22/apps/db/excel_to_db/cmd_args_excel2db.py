from libs.utils.cmd_args import CMDArgs


class CMDArgsExcel2DB(CMDArgs):
	__child_args = [
		[['--preview'], {'action': 'store_true', 'default': False, 'dest': 'is_preview', 'help': 'Do nothing on DB/ES and just show rows'}],
		[['--project_id'], {'type': int, 'default': 0, 'help': 'project id'}],
		[['--group_id_col_n'], {'help': 'column name of group id'}],
		[['--langs'], {'type': str, 'nargs': '*', 'help': 'languages'}],
		[['--lang_col_ns'], {'type': str, 'nargs': '*', 'help': 'column names of languages'}],
		[['--text_col_ns'], {'type': str, 'nargs': '*', 'help': 'column names of texts'}],
		[['--tag_name_col_ns'], {'type': str, 'nargs': '*', 'help': 'column names of tag-names'}],
		[['--tag_score_col_ns'], {'type': str, 'nargs': '*', 'help': 'column names of tag-scores'}],
	]

	__description = (
		'#1 en_fr.xlsx 파일을 읽어 corpusdb 에 저장\n'
		'    ./excel_to_db.py\n'
		'        -p ~/project/corpus_raw/texts\n'
		'        -i en_fr.xlsx\n'
		'        --lang_col_names lang1 lang2\n'
		'        --text_col_names text1 text2\n'
		'#2 corpusdb 에 존재하는 group 에 스페인어 번역 추가\n'
		'    ./excel_to_db.py\n'
		'        -p ~/project/corpus_raw/texts\n'
		'        -i en_es.xlsx\n'
		'        --group_col_name group_id\n'
		'        --lang_col_names lang1\n'
		'        --text_col_names text1\n'
		'#3 en_fr.xlsx 파일을 읽어 tag 와 함께 corpusdb 에 저장\n'
		'    ./excel_to_db.py\n'
		'        -p ~/project/corpus_raw/texts\n'
		'        -i en_fr.xlsx\n'
		'        --tag_col_name tag_id\n'
		'        --lang_col_names lang1 lang2\n'
		'        --text_col_names text1 text2'
	)


	def __init__(self, name, required_args=None):
		self.name = self.__description if self.__description else name
		self.args += self.__child_args
		super().__init__(name, required_args)
