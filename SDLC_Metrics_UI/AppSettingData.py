import json
import os

def JsonFilePath():
    FPath = os.environ["AppData"]
    if not os.path.exists(FPath+r"\SDLC_Metrics_UI"):
        os.mkdir(FPath+r"\SDLC_Metrics_UI")
    f = open(FPath+r"\SDLC_Metrics_UI\AppSettingData.json", "a+")
    f.close()
    return FPath+r"\SDLC_Metrics_UI\AppSettingData.json"


def ListToDict(list):
    var = {}
    var['id'] = list[0]
    var['path'] = list[1]
    var['enableGitData'] = list[2]

    var['gitCommitMessagePolicy'] = {
        'enable': list[3],
        'message': list[4]
    }

    var['gitPreventBranchesPolicy'] = {
        'enable': list[5],
        'branches': list[6]
    }
    var['LastCommitId'] = list[7]
    return var


def AddSetting(list):
    path = JsonFilePath()
    SettingData = ReadSettingData()
    if len(SettingData) > 0:
        list[0] = int(SettingData[-1]['id']) + 1
    else:
        list[0] = 1
    SettingData.append(ListToDict(list))
    WriteSettingData(SettingData)


def ReadSettingData():
    JsonFile = open(JsonFilePath(), 'r+')
    data = JsonFile.read()
    if len(data) > 0:
        AppDataFromJsonFile = json.loads(data)
    else:
        AppDataFromJsonFile = []
    JsonFile.close()
    return AppDataFromJsonFile


def WriteSettingData(SettingData):
    JsonFile = open(JsonFilePath(), 'w+')
    json.dump(SettingData, JsonFile, indent=4)
    JsonFile.close()

def ReadSettingById(id):
    print("ID ="+ id)

def WriteSettingById(ID, SettingData):
    RepoSettings = ReadSettingData()
    for dict in RepoSettings:
        if dict['id'] == ID:
            dict['path'] = SettingData[1]
            dict['enableGitData'] = SettingData[2]
            dict['gitCommitMessagePolicy'] = {
                'enable': SettingData[3],
                'message': SettingData[4]
            }
            dict['gitPreventBranchesPolicy'] = {
                'enable': SettingData[5],
                'branches': SettingData[6]
            }
    JsonFile = open(JsonFilePath(), 'w+')
    WriteSettingData(RepoSettings)
    JsonFile.close()


def WriteLastCommitId(ID, LastCommitId):
    RepoSettings = ReadSettingData()
    for dict in RepoSettings:
        if dict['id'] == ID:
            dict['LastCommitId'] = LastCommitId
    JsonFile = open(JsonFilePath(), 'w+')
    WriteSettingData(RepoSettings)
    JsonFile.close()
