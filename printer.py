margin = 2


def getKeyLengths(keys, lst):
    for item in lst:
        for key in item:
            if type(item[key]) == 'list':
                if key in keys:
                    if keys[key] < len(str(len(item[key]))):
                        keys[key] = len(str(len(item[key])))
            else:
                if key in keys:
                    if keys[key] < len(str(item[key])):
                        keys[key] = len(str(item[key]))
    return keys


def printHeader(keys):
    line = ''
    underline = ''
    # print header
    for key in keys:
        field = key
        while len(field) < keys[key] + margin:
            field += ' '
        line += field
        underline_field = ''
        for i in range(keys[key]):
            underline_field += '-'
        for i in range(margin):
            underline_field += ' '
        underline += underline_field
    print(line)
    print(underline)


def printListOfDictionaries(keys, lst):
    print()  # print empty line
    keys = getKeyLengths(keys, lst)
    printHeader(keys)
    # print table
    for s in lst:
        line = ''
        for key in keys:
            if s[key]:
                if type(s[key]) == 'list':
                    field = str(len(s[key]))
                else:
                    field = str(s[key])
            while len(field) < keys[key] + margin:
                field += ' '
            line += field
        print(line)
    print()  # print empty line


def printServerList(lst):
    if (lst):
        keys = {
            'name': 1,
            'ip': 1,
            'mac': 1,
            'is_hypervisor': 13,
            'virsh_version': 13
        }
        printListOfDictionaries(keys, lst)
    else:
        print('no list')


def printGuestList(lst):
    if (lst):
        keys = {
            'name': 1,
            'state': 1
        }
        printListOfDictionaries(keys, lst)
    else:
        print('no list')