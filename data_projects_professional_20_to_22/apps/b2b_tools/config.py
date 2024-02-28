import configparser
import os, sys


class Config:
    __config_file = 'config/config.ini'


    def __parse_mt(self, config_mt):
        self.mt_url = config_mt['url']
        self.mt_token = config_mt['key']


    def __get_config_file(self):
        return os.path.abspath(os.path.dirname(__file__)) + '/' + self.__config_file


    def __init__(self): 
        try:
            config_file = self.__get_config_file()
            if not os.path.exists(config_file):
                self.is_loaded = False
                return
            
            config = configparser.ConfigParser()
            config.read(config_file)
            self.__parse_mt(config['FLITTO_MT'])
        except:
            print('[CRITICAL][config.init] %s' % str(sys.exc_info()).replace('"', ' '))
            self.is_loaded = False
