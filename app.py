import os.path
import json
import subprocess
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.process
from check_answer import * 
import time
from wrap import *

filename = "tmp.txt"
editFlag = 0
all_the_text = ""
question_num = 0

'''
    处理文件编辑的接口:edit
    HTTP协议，使用Get方法
    参数：filename = 1.sh
    返回：1.sh的内容
'''

class FileEditHandler(tornado.web.RequestHandler):
    def get(self):
        filename = self.get_argument('filename','')     #获取参数的值
        fp = open(filename)                             #本地打开文件
        try:
            all_the_text = fp.read()                    #读取文件内容
            self.write(all_the_text)                    #返回文件内容
        finally:
            fp.close()                                  #关闭文件

    def post(self):
        pass

'''
    处理文件保存的接口:save
    HTTP协议，使用Post方法
    参数：filename 和 content
    返回：空
'''

class FileSaveHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        global filename, editFlag
        content = self.get_argument('file_content','')       #获取content
        fp = open(filename,'w')                         #写文件
        fp.write(content)
        fp.close()
        print(content)
        editFlag = 0
        self.render("index.html",tutorial_content = all_the_text)
        pass

class TutorialEditHandler(tornado.web.RequestHandler):
    def get(self, *d):
        global all_the_text
        fp = open("tutorial/" + d[0] + ".html")         #本地打开文件
        try:
            all_the_text = fp.read()                    #读取文件内容
            self.render("index.html",tutorial_content = all_the_text)
        finally:
            fp.close()
        pass

    def post(self):
        pass

class InitHandler(tornado.web.RequestHandler):
    def get(self, *d):
        global all_the_text
        fp = open("tutorial/0.html")                    #本地打开文件
        try:
            all_the_text = fp.read()                    #读取文件内容
            self.render("index.html",tutorial_content = all_the_text)
        finally:
            fp.close()
        pass

    def post(self):
        pass

class ShellHandler(tornado.web.RequestHandler):
    def get(self, *d):
        global editFlag, filename, question_num, p
        line = self.get_argument('line', '')
        print(line)
        if line.find("myedit") == 0:
            editFlag = 1
            filename = line[7:]
            retStr = ""
        else:
            send_all(p, line + '\n')
            time.sleep(0.02)
            ret = recv_some(p)
            retStr = ret.decode()
            print(ret)

        check_ans_var = CheckAnswer(question_num)
        if check_ans_var.check_ans(line, retStr):
            retStr += "\nChallenge Pass\n"

        self.write(json.dumps({
            'file_editor': editFlag,
            'output': retStr,
        }))

    def post(self):
        pass

    def on_finish(self):
        pass

class PwdHandler(tornado.web.RequestHandler):
    def get(self, *d):
        global p
        send_all(p, 'pwd\n')
        time.sleep(0.02)
        ret = recv_some(p)
        retStr = ret.decode()[:-1] + "$ "
        self.write(retStr)
        pass

    def post(self):
        pass

'''
    配置URL映射关系
    /url : shell的每一行输入
    /edit : edit的接口
    /save : save的接口
'''

application = tornado.web.Application([
    ("/symbol", PwdHandler),
    ("/tutorial/([0-9]+)", TutorialEditHandler),
    ("/shell", ShellHandler),    
    ("/save", FileSaveHandler),
    ("/()", InitHandler),
    ("/(.*)", tornado.web.StaticFileHandler, {
        "path": os.path.dirname(os.path.realpath(__file__)),
        "default_filename": "index.html",
    }),
], debug=True)

if __name__ == "__main__":

    application.listen(3000)                            #监听3000端口
    p = Popen('bash', stdin=PIPE, stdout=PIPE)
    tornado.ioloop.IOLoop.current().start()   
    

