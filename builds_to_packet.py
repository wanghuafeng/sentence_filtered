import os
import json
import datetime
#from pybloom import BloomFilter

from phonetic import phodecs

new_words_path = '/data/cloud/src/new_words/'
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

def open_out_files(prefix):
    fd_list = []
    out_file_num = 8
    for i in range(2,10):
        filename = os.path.join(new_words_path,'builds/%s_%d.build'%(prefix, i)) 
        fd_list.append(open(filename, 'w'))

    return fd_list



def main():
    nw_files = [os.path.join(new_words_path,filename) for filename in os.listdir(new_words_path) if filename.endswith('.log')]
    print 'Build new_words to packets at %s'%(datetime.datetime.now().isoformat())
    of_list = open_out_files('new_words')
    for filename in nw_files:
        print 'Building file:%s ...'%(filename)
        line_count = 0
        with open(filename) as f:
            for line in f:
                doc = json.loads(line.strip())
                pac = doc_to_packet(doc)
                out_file = of_list[int(doc['a'][0])-2]
                out_file.write(pac+'\n')
                line_count += 1
                if line_count !=0 and line_count % 100000 == 0:
                    print 'Done %d lines ...'%(line_count)
    for fd in of_list:
        fd.close()
    

def test_d2p():
    test_num = 10
    with open(nw_files[2],'r') as f:
        line_count = 0
        for line in f:
            doc = json.loads(line.strip(), encoding='utf-8')
            packet = doc_to_packet(doc)
            print packet.decode('utf-8')
            line_count += 1
            if line_count >= test_num:
                break

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

