from flask import Flask
from flask import request
from flask_restful import Resource, Api, reqparse
from flask import render_template
import subprocess
import os
import time

app = Flask(__name__)
api = Api(app)

def write_config(nasip, module):
    keys = ["[nasip]"]
    with open("config/update.%s.config"%module, "r") as fr:
        lines = fr.readlines()
        with open("update.config", "w") as fw:
            for line in lines:
                line = line.strip()
                for key in keys:
                    if key in line:
                        line = line.replace(key, nasip)
                fw.write(line + "\n")

def update_client():
    subprocess.call("python update.py", shell=True)

def update_gitcode():
    pwd = os.getcwd()
    os.chdir("/root/git/HA")
    os.system("git pull")
    os.chdir(pwd)
        
def restart_ha():
    def is_ha_ready():
        proc = subprocess.Popen("tail -f /var/log/HAServer_debugLog", shell=True, stdout = subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if "local HA is ready" in line:
                break
            time.sleep(0.01)

    cmds = [
        "/usr/bin/python /usr/local/NAS/misc/HAAgent/HAAgentRun.py kill",
        "/usr/bin/python /usr/local/NAS/misc/HAAgent/HAAgentRun.py",
    ]
    for cmd in cmds:
        os.system(cmd)
    is_ha_ready()

@app.route('/autotest', methods=['POST'])
def autotest():
    #print request.form
    update_gitcode()
    restart_ha()
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
    write_config(args['ip_dest'], args['module'])
    update_client()
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

if __name__ == '__main__':
   app.run(host="0.0.0.0")
