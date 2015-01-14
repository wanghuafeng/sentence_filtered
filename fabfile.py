__author__ = 'huafeng'

import os
import time
from fabric.api import * 
env.use_ssh_config = True

def build_to_packet():
    env.keepalive = 10
    command = "python {0}/builds_to_packet.py -i {0}/unmatch.prebuild -o {0}/ghost.packet".format('/home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter')
    run(command)

def test_cd():
    env.keepalive = 10
    command = 'cd /home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter; ls'
    run(command)

def scp_remote():
    with cd('/home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter'):
        command = 'scp builds_to_packet.py ana:~'
        command = 'ssh ana'
        run(command)
        time.sleep(1)
        run('ls')

# @hosts('s1', 's2')
# env.hosts = ['s1', 's3']
def multi_server():
    run('uname -a')

def local_test():
    command = "ls"
    local(command)