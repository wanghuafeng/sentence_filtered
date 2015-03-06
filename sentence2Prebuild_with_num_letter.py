__author__ = "wanghuafeng"
# -*- coding: utf-8 -*-
'''
for horder to crawl baidu_freq
sentence.txt ===>> *.prebuild
'''
from phonetic import phodecs, cnltk
import sys
import re
import os
import json
import time
import codecs

CHN_CHAR = re.compile(ur"[\u4e00-\u9fa5]+")#汉字正则
CHN_NUM_LETTER_PATTERN = re.compile(ur"[\u4e00-\u9fa5\da-zA-Z]+")
NUM_LETTER_PATTERN = re.compile(u"\w+")
_curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
MARKER_OBJ = phodecs.Phodecs()
coding_map = {'a': '2', 'c': '2', 'b': '2', 'e': '3', 'd': '3', 'g': '4', 'f': '3', 'i': '4', 'h': '4', 'k': '5', 'j': '5', 'm': '6', 'l': '5', 'o': '6', 'n': '6', 'q': '7', 'p': '7', 's': '7', 'r': '7', 'u': '8', 't': '8', 'w': '9', 'v': '8', 'y': '9', 'x': '9', 'z': '9'}
def wdict_build(word):
    wdict = {}
    wdict["w"] = MARKER_OBJ.convert_word(word['w'], word['pinyins'])
    wdict["dpy"] = MARKER_OBJ.get_dpy(word['pinyins'])
    wdict["adpy"] = MARKER_OBJ.get_adpy(word['pinyins'])
    return wdict

def cloud_build(fd, stdin):
    unmatched_sentence_list = stdin.readlines()#unicode
    seen = set()
    unmatched_sentence_unique_list = (item for item in unmatched_sentence_list if item not in seen and not seen.add(item))
    column_len = len(unmatched_sentence_list[1].split('\t'))
    for line in unmatched_sentence_unique_list:
        splited_line = line.rstrip().split('\t')
        char_line = splited_line[0]
        freq = splited_line[-1] if column_len>1 else '0'
        for chars_num_letter in CHN_NUM_LETTER_PATTERN.findall(char_line):
            length = len(chars_num_letter)
            if length < 1 or length >= 15:
                continue

            #处理字母或数字
            num_letter_info_list = []
            for num_letter in NUM_LETTER_PATTERN.findall(chars_num_letter):
                num_str = ''.join([coding_map.get(letter) if coding_map.get(letter) else letter for letter in num_letter.lower()])
                num_list = [num_letter, num_str, num_str]
                num_letter_info_list.append(num_list)

            #处理汉字
            char_info_list = []
            for char in CHN_CHAR.findall(chars_num_letter):
                word = {}
                word['w'] = char
                pinyin_result = cnltk.cut_for_pinyin(char.encode('utf-8'), HFO=True)
                # pinyin_result = s2p.sentence2pinyin(chars, True)
                if type(pinyin_result) != list:
                # Temporary handle for wired return type of cut_for_pinyin api.
                # TODO: update here after using new version of cnltk
                    word['pinyins'] = pinyin_result.split()
                else:
                    continue

                try:
                    wdict = wdict_build(word)
                    # words_info_list = {'_id':wdict['w'], 'd':wdict['dpy'],'a':wdict['adpy'], 'f':0, 'uf':0}
                    words_info_list = [wdict['w'], wdict['dpy'], wdict['adpy']]
                    char_info_list.append(words_info_list)
                except:
                    print "Build %s failed!" % char
            # print chars_num_letter, num_letter_info_list, char_info_list
            if num_letter_info_list and char_info_list:#含有数字或字母以及汉字
                num_letter_len = len(num_letter_info_list)
                char_len = len(char_info_list)
                d_value = abs(char_len-num_letter_len)
                null_list = ['', '', '']
                [num_letter_info_list.append(null_list) if num_letter_len<char_len else char_info_list.append(null_list) for item in range(d_value)]
                if CHN_CHAR.match(chars_num_letter):#若以汉字开头
                    dpy_str = ''.join([''.join((item[0][1], item[1][1])) for item in zip(char_info_list, num_letter_info_list)])
                    adpy_str = ''.join([''.join((item[0][2], item[1][2])) for item in zip(char_info_list, num_letter_info_list)])
                else:#以数字或字母开头
                    dpy_str = ''.join([''.join((item[0][1], item[1][1])) for item in zip(num_letter_info_list, char_info_list)])
                    adpy_str = ''.join([''.join((item[0][2], item[1][2])) for item in zip(num_letter_info_list, char_info_list)])
                # print chars_num_letter, '==>', adpy_str, '==>', dpy_str
                json_info_str = json.dumps({'_id':chars_num_letter, 'd':dpy_str,'a':adpy_str, 'f':freq, 'uf':0})
            elif char_info_list:#只含有汉字
                json_info_str = json.dumps({'_id':chars_num_letter, 'd':char_info_list[0][1],'a':char_info_list[0][2], 'f':freq, 'uf':0})
                # print chars_num_letter, char_info_list[0][1], char_info_list[0][2]

            else:#只包含字母或数字
                json_info_str = json.dumps({'_id':chars_num_letter, 'd':num_letter_info_list[0][1],'a':num_letter_info_list[0][2], 'f':freq, 'uf':0})
                # print chars_num_letter, '==>', num_letter_info_list[0][1], '==>', num_letter_info_list[0][2]
            fd.write(json_info_str + '\n')

if __name__ == '__main__':

    args = sys.argv[1:]
    if len(args) == 4:
        sentence_filename = args[1]
        prebuild_filename = args[3]
        assert os.path.isfile(sentence_filename), 'sentence_file not exists'
        # filename = 'unmatch.prebuild'
        # unmatch_filename = 'total_unmatch_10.txt'
        with codecs.open(prebuild_filename, 'w', encoding='utf-8') as wf, \
        codecs.open(sentence_filename, encoding='utf-8') as f:
            cloud_build(wf, f)
    else:
        print 'USAGE: -s sentence_filename -d prebuild_filename'