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

###关于阻塞与非阻塞子进程使用：  
（1）当父进程不需要获取子进程数据，或者某子进程的操作比较耗时。应该使用非阻塞式，此时即便该子进程运行过程中crash同样不会影响父进程的正常运行，也即，当父进程fork出该子进程以后，他们没有了什么关系    
		非阻塞式:subprocess.Popen(command, shell=True)#耗时较久的操作，此处为非阻塞式子进程运行，不会影响常规数据流程    
（2）当父进程与子进程有数据交互（进程通讯），或者子进程crash时要求父进程同样中断，此时比较适合阻塞式    
		阻塞式:subprocess.call(command, shell=True)    
而实际上:subprocess.call(*popenargs, **kwargs) 即为 subprocess.Popen(*popenargs, **kwargs).wait()进行了已成封装    

另：stdout.read()的数据总是为ASCII（没有彻底测试，待考证）    
