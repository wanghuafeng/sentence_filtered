__author__ = 'huafeng'
#coding:utf-8
import os
import re
import sys
import time
import glob
import codecs
import simplejson
import subprocess
from datetime import datetime, timedelta

PATH = os.path.dirname(os.path.abspath(__file__))

class NgramFilterSentence(object):

    def __init__(self, build_filename):
        # self.build_filename = os.path.join(r'/home/ferrero/cloudinn/data/%s/prebuilds/'%self.yesterday_format, 'ghost.prebuild')
        # self.build_filename_bak = os.path.join(r'/home/ferrero/cloudinn/data/%s/prebuilds/'%self.yesterday_format, 'ghost.prebuild.bak')#backup file
        self.digits_words_filename = os.path.join(PATH, time.strftime('digits_words_%Y%m%d%H%M%S.txt'))
        self.build_filename = build_filename
        self.encode2NormalCodeDic = {} # key:encode_word, value: normal_code_word
        self.encodeSentence_line_dict = {}#key: encode_sentence, value:line.strip
        self.normalCodeSentence_encodeSentence_dic = {}
        self.unmatched_sentence_list = []
        self._load_encode_file()
        self._load_prebuild_file()

    def _load_prebuild_file(self):
        '''key: encode_sentence, value:line.strip'''
        with codecs.open(self.build_filename, encoding='utf-8') as f:
            for line in f.readlines():
                line_dict = simplejson.loads(line)
                sentence = line_dict.get('_id')
                if sentence:
                    self.encodeSentence_line_dict[sentence] = line

    def _load_encode_file(self):
        '''load convert code file'''
        code_filename = os.path.join(PATH, 'to_code.json')
        file_con = open(code_filename).read()
        self.encode2NormalCodeDic = simplejson.loads(file_con)

    def gen_digits_sentence_file(self):
        '''convert to normal code and write digits and sentence into file'''
        sentence_digits_list = []
        with codecs.open(self.build_filename, encoding='utf-8') as f:
            for line in f.readlines():
                line_dic = simplejson.loads(line)
                if line_dic.get("f") < 1000:
                    continue
                dpy = line_dic.get('d')
                sentence = line_dic.get('_id')
                if sentence and dpy:
                    new_sentence = sentence
                    for single_word in line:
                        encode_word = self.encode2NormalCodeDic.get(single_word)
                        if encode_word:
                            new_sentence = new_sentence.replace(single_word, encode_word)
                    self.normalCodeSentence_encodeSentence_dic[new_sentence] = sentence
                    sentence_digits_list.append("%s\t%s\n"%(new_sentence, dpy))
        # self.digits_words_filenema = os.path.join(PATH, time.strftime('digits_words%Y%m%d%H%M%S.txt'))
        time.sleep(1)#避免digits_words文件被覆盖
        codecs.open(self.digits_words_filename, mode='wb', encoding='utf8').writelines(sentence_digits_list)

    def gen_filtered_sentence(self):
        '''不能被语言模型计算出的句子'''
        # digits_words_filename = os.path.join(PATH, time.strftime('digits_words%Y%m%d%H%M%S.txt'))
        command = "/usr/local/bin/coffee /home/ferrero/cloudinn/node-sri/test/test_from_file.coffee -n /home/ferrero/cloudinn/node-sri/test/zky.bin %s"%self.digits_words_filename
        popen = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        self.unmatched_sentence_list = popen.stdout.readlines()
        print 'rm %s'%self.digits_words_filename
        subprocess.call('rm %s'%self.digits_words_filename, shell=True)#删除临时文件

    def get_unmatchSentence_mapping_line(self):
        '''prebuild文件中不能被语言模型计算出来的句子'''
        with codecs.open(self.build_filename, mode='wb', encoding='utf-8') as wf:
            for normalSentence in self.unmatched_sentence_list:
                encodeSentence = self.normalCodeSentence_encodeSentence_dic.get(normalSentence.strip().decode('utf-8'))
                if encodeSentence:#有正常编码句子转回内码文件
                    unmatch_line = self.encodeSentence_line_dict.get(encodeSentence)
                    if unmatch_line:#由内码句子取得该句子所对应的行
                        wf.write(unmatch_line)

    def main(self):
        yesterday = datetime.today() - timedelta(1)
        yesterday_format = yesterday.strftime('%Y_%m_%d')
        file_path_pattern = r'/home/ferrero/cloudinn/data/%s/*.build'%yesterday_format
        file_list = glob.glob(file_path_pattern)
        for build_name in file_list:
            if os.path.split(build_name)[-1] == "baidu_freq.build":
                os.system("mv /home/ferrero/cloudinn/data/{0}/baidu_freq.build /home/ferrero/cloudinn/data/{0}/baidu_freq.ready_to_filter".format(yesterday_format))
                continue
            os.system('cp %s %s'%(build_name, build_name+".bak"))#back ghost.prebuild file
            nfs = NgramFilterSentence(build_name)
            nfs.gen_digits_sentence_file()
            nfs.gen_filtered_sentence()
            nfs.get_unmatchSentence_mapping_line()

if __name__ == "__main__":
    args = sys.argv[1:]
    yesterday = datetime.today() - timedelta(1)
    yesterday_format = yesterday.strftime('%Y_%m_%d')
    filtered_filename = time.strftime('/home/ferrero/cloudinn/data/filtered/baidu_freq_%Y%m%d%H%M%S.build')
    if len(args) == 2:
        ready_to_filter_fileanme = args[1]
        unfilter_filename = '/home/ferrero/cloudinn/data/{yesterday_format}/{new_baidu_freq_name}'.format(yesterday_format=yesterday_format, new_baidu_freq_name=ready_to_filter_fileanme)
        if os.path.isfile(unfilter_filename):
            nfs = NgramFilterSentence(unfilter_filename)
            nfs.gen_digits_sentence_file()
            nfs.gen_filtered_sentence()
            nfs.get_unmatchSentence_mapping_line()
            os.system('cp {unfilter_filename} {filtered_filename}'.format(unfilter_filename=unfilter_filename, filtered_filename=filtered_filename  ))