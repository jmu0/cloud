import json
margin = 2


def get_key_lengths(keys, lst):
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


def print_header(keys):
    line = ''
    underline = ''
    # print header
    for key in sorted(keys.keys()):
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


def print_help():
    with open('help.txt') as f:
        print(f.read())


def print_list_of_dictionaries(keys, lst):
    print()  # print empty line
    keys = get_key_lengths(keys, lst)
    print_header(keys)
    # print table
    for s in lst:
        line = ''
        for key in sorted(keys.keys()):
            field = ''
            try:
                if s[key]:
                    if type(s[key]) == 'list':
                        field = str(len(s[key]))
                    else:
                        field = str(s[key])
            except:
                pass
            while len(field) < keys[key] + margin:
                field += ' '
            line += field
        print(line)
    print()  # print empty line


def print_server_list(lst):
    if (lst):
        keys = {
            'name': 1,
            'ip': 1,
            'is_hypervisor': 13,
            'virsh_version': 13,
            'is_nfs_server': 13,
            'load': 16
        }
        print_list_of_dictionaries(keys, lst)
    else:
        print('no list')


def print_guest_list(lst):
    if (lst):
        keys = {
            'name': 1,
            'state': 1,
            'host': 1,
            'image_path': 30
        }
        print_list_of_dictionaries(keys, lst)
    else:
        print('no list')


def print_share_list(lst):
    if (lst):
        keys = {
            'name': 1,
            'path': 1,
            'network': 1,
            'server': 1
        }
        print_list_of_dictionaries(keys, lst)
    else:
        print('no list')


def print_mount_list(lst):
    if (lst):
        keys = {
            'mount': 5,
            'shareserver': 11,
            'sharepath': 9,
            'sharename': 9,
            'server': 6,
            'size': 4,
            'used': 4,
            'available': 9,
            'usedPerc': 8,
            'mountpoint': 10
        }
        print_list_of_dictionaries(keys, lst)
    else:
        print('no list')


def print_resources(resources):
    for name, data in resources['guests'].items():
        indent = {
            1: '  ',
            2: '    ',
            3: '      '
        }
        print('')
        print(name)
        for key, value in data.items():
            line = indent[1] + key + ": "
            if type(value).__name__ == 'list':
                for i in value:
                    line += '\n' + indent[2] + json.dumps(i)
            else:
                line += str(value)
            print(line)
        print('')
