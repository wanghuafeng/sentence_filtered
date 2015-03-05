import os
import sys
import re
import subprocess
import codecs
module_path = '/mnt/data/ghost/lib/node-sri/tools'
sys.path.append(module_path)
from sentence2digits import Sentence2Digits
char_pattern = re.compile('\s+')
def filtered_sentence():
    command = "/usr/local/bin/coffee /home/ferrero/cloudinn/node-sri/test/test_from_file.coffee -n /home/ferrero/cloudinn/node-sri/test/zky.bin digits_words.txt"
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    unmatched_sentence_list = popen.stdout.readlines()
    return unmatched_sentence_list

def get_db_sentence(stdin):
    '''get all sentence from db'''
    #lines =  sys.stdin.readlines()
    lines = stdin.readlines()
    for line in lines:
        splited_line = char_pattern.split(line)
    return [char_pattern.split(item.strip())[0].decode('utf-8') for item in lines if 1<len(char_pattern.split(item.strip())[0].decode('utf-8'))<11]


def gen_digits_words_file(db_sentence_list):
    '''write sentence in to tmp file for node-js'''
    tmp_filename = 'digits_words.txt'
    s2d = Sentence2Digits()
    com_str_list = []
    for line in db_sentence_list:
        if not line:
            continue
        pinyin_list = s2d.sentence2digits(line, True)
        if pinyin_list:
            pinyin = pinyin_list[0]
            com_str_list.append('%s\t%s\n'%(line, pinyin))
#    com_str_list = ['%s\t%s\n'%(line, s2d.sentence2digits(line, True)[0]) for line in db_sentence_list if line]
    codecs.open(tmp_filename, mode='wb', encoding='utf-8').writelines(com_str_list)

if __name__ == "__main__":
    db_sentence_list = get_db_sentence(stdin)
    gen_digits_words_file(db_sentence_list)
