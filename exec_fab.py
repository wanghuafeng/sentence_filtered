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
    s3_execute_python_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    current_path = '/home/huafeng/PycharmProjects/filtered_unmatch_sentence'
    scp_command = "scp {current_path}/filtered_sentence.py {current_path}/filtered_sentence_unusual_streamline.py s3:{s3_execute_python_path}".format(current_path=current_path, s3_execute_python_path=s3_execute_python_path)
    # print scp_command
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        command = 'python %s/filtered_sentence.py'%s3_execute_python_path
        fab_command = 'fab -H s3 --keepalive=10 -- "%s"'%command
        subprocess.call(fab_command, shell=True)
filtered_unmatch_sentence()