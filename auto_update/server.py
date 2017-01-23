from flask import Flask
from flask import request
from flask_restful import Resource, Api, reqparse
from flask import render_template
import subprocess
import os
import time
import sys

app = Flask(__name__)
api = Api(app)

def write_config(nasip, port, module):
    paras = {
        "[nasip]" : nasip, 
        "[port]" : str(port),
    }
    with open("config/update.%s.config"%module, "r") as fr:
        lines = fr.readlines()
        with open("update.config", "w") as fw:
            for line in lines:
                line = line.strip()
                for key in paras.keys():
                    if key in line:
                        line = line.replace(key, paras[key])
                fw.write(line + "\n")

def openssh(ip, port):
    try:
        cmd = "nc %s %s"%(ip, str(port))
        print cmd
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
        time.sleep(0.5)
        proc.kill()
        data = proc.communicate()
        if "OpenSSH" in data[0]:
            print "ssh port:%s is open"%str(port)
            return True
        else:
            print "ssh port:%s is close"%str(port)
            return False
    except:
        return False

def update_client():
    subprocess.call("python update.py", shell = True)

def update_client_redund(nasip):
    subprocess.call("ps -ef | grep tunnel.exp | awk '{print $2}' | xargs kill -9", shell = True)
    subprocess.call("expect tunnel.exp %s &"%nasip, shell = True)
    time.sleep(3)
    if openssh("localhost", 5511):
        update_client()
    subprocess.call("ps -ef | grep tunnel.exp | awk '{print $2}' | xargs kill -9", shell = True)

@app.route('/autotest', methods=['POST'])
def autotest():
    #print request.form
    cmd = "/usr/bin/python /usr/local/NAS/misc/Cmd/NASCmd.py"
    parser = reqparse.RequestParser()
    parser.add_argument('module', type=str)
    args = parser.parse_args()
    print args
    cmd += " -f /usr/local/NAS/misc/Cmd/Script/%s.txt"%args['module']
    os.system(cmd)
    return render_template(
                    'update.html',
           )

@app.route('/update', methods=['POST'])
def update():
    #print request.form
    parser = reqparse.RequestParser()
    parser.add_argument('ip_dest', type=str)
    parser.add_argument('module', type=str)
    parser.add_argument('user_dest', type=str)
    parser.add_argument('password_dest', type=str)
    args = parser.parse_args()
    print args
    #write_config(request.remote_addr)
    if openssh(args['ip_dest'], 22):
        write_config(args['ip_dest'], 22, args['module'])
        update_client()
    write_config("localhost", 5511, args['module'])
    update_client_redund(args['ip_dest'])
    return render_template(
                    'update.html',
           )

#api.add_resource(HelloWorld, '/')
def read_modules():
    configs = os.listdir("./config")
    return [ m.split(".")[1] for m in configs ]
    

@app.route('/')
def index():
    modules = read_modules()
    return render_template(
                    'index.html',
                    modules = modules,
           )

def main():
   app.run(host="0.0.0.0")
    
def test_openssh():
    print openssh("127.0.0.1", 22)
    print openssh("127.0.0.1", 5511)

if __name__ == '__main__':
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()
