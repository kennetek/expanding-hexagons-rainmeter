# import json
import configparser
import os
from msshortcut import __readLink

color_fg = 'FFFFFF'
color_bg = 'DE2A2A'
width = 66
spacing = 90
row = 2


def configfilter(config, image='', command='', length=0, n1=0, n2=-1):
    end = str(n1)
    if n2 >= 0:
        end += str(n2)
    dummy = configparser.ConfigParser()
    dummy.optionxform = str
    for section in config.sections():
        dummy[section + end] = {}
        for pair in config[section]:
            dummy[section + end][pair] = config[section][pair] \
                .replace('{n}', str(n1)) \
                .replace('{m}', str(n2)) \
                .replace('{cmd}', command) \
                .replace('{img}', image) \
                .replace('{len}', str(length)) \
                .replace('{color_bg}', color_bg) \
                .replace('{color_fg}', color_fg)
    return dummy


class Button:

    def __init__(self, n, x, y, image, command):
        self.x = x
        self.y = y
        self.n = n
        self.image = image
        self.command = command
        self.images = []
        self.commands = []

    def add(self, image, command):
        self.images.append(image)
        self.commands.append(command)
        return self

    def build(self, configfile):
        size = len(self.images)
        config = expand if size > 0 else single
        for idx in range(size):
            configfilter(expandbutton, self.images[idx], self.commands[idx], 0, self.n, idx).write(configfile)
        configfilter(config, self.image, self.command, size, self.n, -1).write(configfile)

    def vars(self, v, n1):
        size = len(self.images)
        if size > 0:
            v['Variables']['XMAX' + str(n1)] = str(-width * size)
            v['Variables']['XX' + str(n1)] = str(-width * size)
            v['Variables']['ICON' + str(n1)] = 'icon2.png'
        v['Variables']['XI' + str(n1)] = str(self.x)
        v['Variables']['YI' + str(n1)] = str(self.y)
        return v


def configinit(s):
    result = configparser.ConfigParser()
    result.optionxform = str
    result.read(".\\ref\\" + s)
    return result


default = configinit('default.ini')
single = configinit('single.ini')
expand = configinit('expand.ini')
expandbutton = configinit('expandbutton.ini')
vars = configinit('variable.ini')

data = []
for filename in os.listdir(".\\shortcuts"):
    if not (filename.__contains__(".lnk") or filename.__contains__(".url")):
        continue
    print(f"filename: {filename}")
    target = "\"" + __readLink(".\\shortcuts\\" + filename).replace("\n", "") + "\""
    print(f"Target: {target}")
    name = "".join([c for c in os.path.splitext(filename)[0].lower() if c.isalpha()])
    image = "placeholder-icon.png"
    for imagename in os.listdir(".\\@Resources\\Icons"):
        if name.__eq__(os.path.splitext(imagename)[0].lower()):
            image = imagename
            break
    if filename.__contains__("#") and not filename.__contains__("#0") and len(data) > 0:
        data[-1].append({'name': image, 'cmd': target})
    else:
        data.append([{'name': image, 'cmd': target}])

# file_paths = open("data.json", 'r')
# paths = file_paths.read()
# file_paths.close()
# paths = json.loads(paths)
# data = paths["items"]

with open('example.ini', 'w') as configfile:
    button = []
    cs = 0
    ce = row - 1
    for butt in data:
        c = cs if len(butt) <= 1 else ce
        m1 = c % row
        m2 = (c - m1) / row
        b = Button(c, spacing * m1 + 0.5 * spacing * (m2 % 2), spacing * m2, butt[0]['name'], butt[0]['cmd'])
        for i in range(1, len(butt)):
            b.add(butt[i]['name'], butt[i]['cmd'])
        b.vars(vars, c)
        if len(butt) <= 1:
            cs += 1
            if (cs + 1) % row == 0:
                cs += 1
        else:
            ce += row
        button.append(b)

    default.write(configfile)
    vars.write(configfile)

    for thing in button:
        thing.build(configfile)
