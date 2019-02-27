import json
import os

def json_save(objs, filePath):
    try:
        s = json.dumps(objs, sort_keys=True, indent=4)
        fd = open(filePath,"w")
        fd.write(s)
        fd.close()
        return True
    except Exception as e:
        print("json save failed: \n",str(e))
        return False

def json_load(filePath, noexcept=False):
    try:
        fd = open(filePath, "r")
        s = fd.read()
        obj = json.loads(s)
        fd.close()
        return obj
    except Exception as e:
        if noexcept:
            pass
        else:
            print("json load exceptions: \n", str(e))
        return None
    
class ManagerService:
    def __init__(self):
        pwd = os.getcwd()
        self.usrdbPath = os.path.abspath(os.path.dirname(pwd)+os.path.sep+".") + os.path.sep + os.path.join("database", "usrdb")
        self.usrdb = json_load(self.usrdbPath)
        
    def getUsrdb(self):
        return self.usrdb
    
    def updateUsrdb(self, key, value):
        self.usrdb[key] = value
        json_save(self.usrdb, self.usrdbPath)
        
    def queryUsr(self, usrname):
        if usrname in self.usrdb:
            return True
        else:
            return False
        
    def deleteUsr(self, usrname):
        if usrname in self.usrdb:
            self.usrdb.pop(usrname)
            json_save(self.usrdb, self.usrdbPath)
        else:
            pass 
    