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
import codecs
# module_path = "/home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter/tools"
# sys.path.append(module_path)
# from sentence2pinyin import Sentence2Pinyin
# s2p = Sentence2Pinyin()

CHN_CHAR = re.compile(ur"[\u4e00-\u9fa5]+")
_curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
MARKER_OBJ = phodecs.Phodecs()

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
    for line in unmatched_sentence_unique_list:
        for chars in CHN_CHAR.findall(line):
            length = len(chars)
            if length <= 1 or length >= 15:# or cnltk.is_basic(chars):
                continue
            word = {}
            word['w'] = chars
            pinyin_result = cnltk.cut_for_pinyin(chars.encode('utf-8'), HFO=True)
            # pinyin_result = s2p.sentence2pinyin(chars, True)
            if type(pinyin_result) != list:
            # Temporary handle for wired return type of cut_for_pinyin api.
            # TODO: update here after using new version of cnltk
                word['pinyins'] = pinyin_result.split()
            else:
                continue

            try:
                wdict = wdict_build(word)
                json.dump({'_id':wdict['w'], 'd':wdict['dpy'],
                           'a':wdict['adpy'], 'f':0, 'uf':0}, fd, encoding='utf-8', ensure_ascii=False)
                fd.write('\n')
            except:
                print "Build %s failed!" % chars

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