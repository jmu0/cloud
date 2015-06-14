def printServerList(lst):
    if (lst):
        for s in lst:
            print(s['name'])
    else:
        print('no list')


def printGuestList(lst):
    if (lst):
        for g in lst:
            print(g['name'])
    else:
        print('no list')
