__author__ = 'huafeng'
#coding:utf-8
import os
import json
import datetime
#from pybloom import BloomFilter

from phonetic import phodecs

#nw_files = [os.path.join(new_words_path,filename) for filename in ['new_words_2014_05_24_22200.log'] if filename.endswith('.log')]

#bf_file  = open('/home/ubuntu/misc_jiaxu/bloom_filter/cloud_bf.dump')
#bf = BloomFilter.fromfile(bf_file)

MARKER_OBJ = phodecs.Phodecs()

def doc_to_packet(doc):
    inner_word = doc['_id']
    real_word = MARKER_OBJ.restore_word(inner_word)
    try:
        packet = (u'%s|%s|%s|%s'%(real_word,
                                inner_word,
                                doc['a'],
                                doc['d'])).encode('utf-8')
    except UnicodeDecodeError, e:
        print e.object
        raise
    return packet

def convert_one_file(in_file,out_file):
    with open(out_file,'w') as outf:
        with open(in_file) as inf:
            for line in inf:
                doc = json.loads(line.strip())
                pac = doc_to_packet(doc)
                outf.write(pac+'\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert build doc to packet doc.')
    parser.add_argument('-i', '--infile', action='store')
    parser.add_argument('-o', '--outfile', action='store')
    args = parser.parse_args()
    if args.infile and args.outfile:
        convert_one_file(args.infile, args.outfile)
    else:
        parser.print_help()
