import minecraft_launcher_lib, json
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
ver=minecraft_launcher_lib.utils.get_version_list()

with open('version_list.json','w') as f:
    f.write('[')
    for i in ver:
        i['releaseTime']=str(i['releaseTime'])
        json.dump(i, f)
        f.write(',\n')
    f.write(']')