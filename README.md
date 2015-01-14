# sentence_filtered
语言模型过滤不匹配句子，通过fabric进行远程控制

若需要使用fabric时通过subprocess中的call方法执行fab_command且不添加-f参数，则需要在目录中添加fabfile.py文件，
文件中可以设置env的一些参数，例如（env.use_ssh_config = True）   

##fab [options] -- [shell command]  

fab_command = '''fab -H unicorn -- "cd /home/wanghuafeng/cloud_word/node-sri/test/unmatch_ngram_filter;   
        python split_file.py -f ghost.packet -c 10;   
        mkdir splited_data;   
        mv ghost.packet.partial_* splited_data"'''    

exec_fab文件将filtered_sentence.py拷贝到远程s3服务器中的指定目录，并在s3执行该文件，同时将标准输出显示在本地以便调试  
test/unmatch_ngram_filter  
