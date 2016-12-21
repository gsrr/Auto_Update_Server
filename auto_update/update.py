import os

def readFile(path):
    data = []
    with open(path , "r") as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                continue
            data.append(line)
    return data

def parsefiles(data):
    info = {}
    for line in data:
        line = line.strip()
        if line == "":
            continue
        [key, value] = line.split("=",1)
        info[key] = value if info.has_key(key) == False else (info[key] + ("," + value))
    return info

def createExp(info, f1, f2):
    with open("./template.exp", "r") as fr:
        lines = fr.readlines()
        with open("update.exp" , "w") as fw:
            for line in lines:
                if "[nasip]" in line:
                    line = line.replace("[nasip]", info['nasip'])
                if "[from]" in line:
                    line = line.replace("[from]", f1)
                if "[to]" in line:
                    line = line.replace("[to]", f2)
                fw.write(line)
    return 0
    

def main():
    data = readFile("update.config")
    info = parsefiles(data)
    for f1, f2 in zip(info['from'].split(","), info['to'].split(",")):
        createExp(info, f1, f2)
        os.system("expect update.exp")

if __name__ == "__main__":
    main()
