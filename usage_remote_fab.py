__author__ = 'huafeng'
#coding:utf-8
import os
import subprocess
import codecs
import simplejson


remote_path = r'/home/mdev/tmp'

def tar_():
    tar_command = '''fab -H mdev -- "cd %s;
                     tar -zxvf baidu_freq.tar.gz;
                     tar -zxvf new_words_wz_freq.tar.gz"'''%remote_path
    subprocess.call(tar_command, shell=True)

def split_file_on_unicorn():
    #on unicorn 将文件切割为n分
    scp_command = "scp split_file.py {hostname}:{desPath}".format(hostname = 'unicorn',desPath='/home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter')
    errInfo = open("err.log")#错误信息写入err.log
    IsFailed = subprocess.call(scp_command, shell=True, stderr=errInfo)
    if not IsFailed:
        fab_command = '''fab -H unicorn -- "cd /home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter;
        python split_file.py -f ghost.packet -c 10;
        mkdir splited_data;
        mv ghost.packet.partial_* splited_data"'''
        subprocess.call(fab_command, shell=True)
# split_file_on_unicorn()

# subprocess.call("scp to_code.json mdev:%s"%remote_path, shell=True)
def get_digits_file_on_mdev():
    scp_command = "scp execute_on_mdev.py mdev:%s"%remote_path
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        fab_command = '''fab -H mdev -- "cd %s;
                        python execute_on_mdev.py"'''%remote_path
        subprocess.call(fab_command, shell=True)
# get_digits_file_on_mdev()
def execute_on_s3():
    #语言模型过滤，生成的unmatch词保存在digits_words.txt文件中
    s3_path = '/home/ferrero/tmp'
    scp_command = "scp execute_on_mdev.py s3:%s"%s3_path
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        digits_words_filename = os.path.join(s3_path, 'digits_words.txt')
        command = "/usr/local/bin/coffee /home/ferrero/cloudinn/node-sri/test/test_from_file.coffee -n /home/ferrero/cloudinn/node-sri/test/zky.bin %s"%digits_words_filename
        fab_command = "fab -H s3 -- '%s'"%command
        subprocess.call(fab_command, shell=True)
# execute_on_s3()
def filtered_unmatch_sentence():
    # on s3 语言模型过滤，长度限制在[2,10]的词
    s3_execute_python_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    current_path = '/home/huafeng/PycharmProjects/filtered_unmatch_sentence'
    scp_command = "scp {current_path}/filtered_sentence.py {current_path}/filtered_sentence_unusual_streamline.py s3:{s3_execute_python_path}".format(current_path=current_path, s3_execute_python_path=s3_execute_python_path)
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        command = 'python %s/filtered_sentence.py'%s3_execute_python_path
        fab_command = 'fab -H s3 --keepalive=10 -- "%s"'%command
        subprocess.call(fab_command, shell=True)
# filtered_unmatch_sentence()
def sentence_to_prebuild_packet():
    #on s3 过滤sentence文件生成prebuild文件
    sentence2prebuile = 'sentence2Prebuild.py'
    prebuild_filename = 'sentence.prebuild'
    local_sentence2prebuile_path = '/home/huafeng/PycharmProjects/filtered_unmatch_sentence/%s'%sentence2prebuile
    s3_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    scp_command = 'scp {localfile} s3:{desPath}'.format(localfile=local_sentence2prebuile_path, desPath=s3_path)
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        gen_prebuild = 'python {s3_path}/sentence2Prebuild.py -s {s3_path}/prebuild_packet/{sentence_file} -d {s3_path}/prebuild_packet/{prebuild_file}'.format(s3_path=s3_path, sentence_file='2011_2013_words.txt', prebuild_file=prebuild_filename)#执行Sentence2Prebuild.py文件，参数为-s sentence_filename -d prebuild_filename
        fab_sentence2Prebuild_command = 'fab -H s3 --keepalive=10 -- "cd {s3_path}; {py_command}"'.format(s3_path=s3_path, py_command=gen_prebuild)#在s3执行py_command，生成prebiuld文件
        genPrebuildFailed = subprocess.call(fab_sentence2Prebuild_command, shell=True)
        if not genPrebuildFailed:
            print 'gen prebuild sucessed...'
            packet_filename = prebuild_filename.rsplit('.', 1)[0] + '.packet'#
            prebuild2Packet_command = 'python /home/ferrero/cloudinn/builds_to_packet.py -i {s3_path}/prebuild_packet/{prebuild_filename} -o {s3_path}/prebuild_packet/{packet_filename}'.format(prebuild_filename=prebuild_filename, packet_filename=packet_filename, s3_path=s3_path)
            fab_prebuild2Packet_command = 'fab -H s3 --keepalive=10 -- "cd {s3_path}; {py_command}"'.format(s3_path=s3_path, py_command=prebuild2Packet_command)
            subprocess.call(fab_prebuild2Packet_command, shell=True)
# sentence_to_prebuild_packet()
def exec_script_on_s3():
    import sys
    import subprocess
    script_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    if __name__ == "__main__":
        args = sys.argv[1:]
        if len(args) == 2:
            sentence_filename = args[1]
            assert os.path.isfile(sentence_filename), 'sentence_filename not exists...'
            prebuild_filename = sentence_filename.rsplit('.', 1)[0] + '.prebuild'
            sentence2Prebuild = 'python {script_path}/sentence2Prebuild.py -s {script_path}/prebuild_packet/{sentence_file} -d {script_path}/prebuild_packet/{prebuild_file}'.format(script_path=script_path, sentence_file=sentence_filename, prebuild_file=prebuild_filename)#执行Sentence2Prebuild.py文件，参数为-s sentence_filename -d prebuild_filename，生成prebuild文件
            genPrebuildFailed = subprocess.call(sentence2Prebuild, shell=True)
            if not genPrebuildFailed:
                print 'sentence to *.prebuild sucessed ...'
                packet_filename = sentence_filename.rsplit('.', 1)[0] + '.packet'
                prebuild2Packet = 'python /home/ferrero/cloudinn/builds_to_packet.py -i {script_path}/prebuild_packet/{prebuild_filename} -o {script_path}/prebuild_packet/{packet_filename}'.format(prebuild_filename=prebuild_filename, packet_filename=packet_filename, script_path=script_path)
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
            raise ValueError("USAGE -i sentence_filename")
def sentence2Packet_test():
    '''由sentence文件转换为packet文件，在s3上执行'''
    local_path = '/home/huafeng/PycharmProjects/filtered_unmatch_sentence/sentence2Packet.py'
    remote_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    scp_command = 'scp {local_path} s3:{remote_path}'.format(local_path=local_path, remote_path=remote_path)
    IsScpFailed = subprocess.call(scp_command, shell=True)
    if not IsScpFailed:
        print '%s sucess ...'%scp_command
        py_command = 'python {remote_path}/sentence2Packet.py -i {remote_path}/prebuild_packet/{sentence_filename}'.format(remote_path=remote_path, sentence_filename='2011_2013_words.txt')#sentence文件的绝对路径
        fab_command = 'fab -H s3 -- "{py_command}"'.format(py_command=py_command)
        subprocess.call(fab_command, shell=True)
# sentence2Packet_test()