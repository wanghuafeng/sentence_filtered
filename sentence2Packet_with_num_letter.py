__author__ = 'huafeng'
#encoding:utf-8
'''
sentence ==>> prebuild ==>> packet
'''
import os
import sys
import subprocess
script_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        sentence_filename = args[1]#sentence ==> *.prebuild
        assert os.path.isfile(sentence_filename), 'sentence_filename not exists...'
        prebuild_filename = sentence_filename.rsplit('.', 1)[0] + '.prebuild'
        sentence2Prebuild = 'python {script_path}/sentence2Prebuild_with_num_letter.py -s {sentence_file} -d {prebuild_file}'.format(script_path=script_path, sentence_file=sentence_filename, prebuild_file=prebuild_filename)#执行Sentence2Prebuild.py文件，参数为-s sentence_filename -d prebuild_filename，生成prebuild文件
        genPrebuildFailed = subprocess.call(sentence2Prebuild, shell=True)
        if not genPrebuildFailed:#*.prebuild ==> *.packet
            print 'sentence to *.prebuild sucessed ...'
            packet_filename = sentence_filename.rsplit('.', 1)[0] + '.packet'
            prebuild2Packet = 'python /home/ferrero/cloudinn/builds_to_packet.py -i {prebuild_filename} -o {packet_filename}'.format(prebuild_filename=prebuild_filename, packet_filename=packet_filename)
            prebuild2PacketFailed = subprocess.call(prebuild2Packet, shell=True)
            if not prebuild2PacketFailed:
                print '*.prebuild to *.packet sucess ...'
            else:
                print '*.prebuild to *.packet failed ...'
                raise ValueError('*.prebuild to *.packet failed ...')
        else:
            print 'sentence to prebuild failed...'
            raise ValueError("sentence to prebuild failed...")
    else:
        print "USAGE -i sentence_filename"
