#!/usr/bin/python3
import server
# import storage
import printer
import sys
import worker
import os
import time


os.environ['PYTHONUNBUFFERED'] = 'True'  # for redirecting stdout to log file


def get_servers():
    return server.get_from_socket('servers')


def get_guests():
    return server.get_from_socket('guests')


def get_shares():
    return server.get_from_socket('shares')


def get_mounts():
    return server.get_from_socket('mounts')


if len(sys.argv) == 1:
    printer.print_help()
elif sys.argv[1] == 'help':
    printer.print_help()
elif sys.argv[1] == 'sys':
    start = time.time()
    print(server.get_server_props())
    print(str(time.time() - start) + ' seconds')
elif sys.argv[1] == 'run':
    worker.run()
elif sys.argv[1] == 'scan':
    print(server.scan_cloud())
elif sys.argv[1] == 'wake':
    if len(sys.argv) == 3:
        print(server.wake(sys.argv[2]))
    else:
        print('geen hostname')
elif sys.argv[1] == 'servers':
    printer.print_server_list(get_servers())
elif sys.argv[1] == 'guests':
    printer.print_guest_list(get_guests())
elif sys.argv[1] == 'shares':
    printer.print_share_list(get_shares())
elif sys.argv[1] == 'mounts':
    printer.print_mount_list(get_mounts())
elif sys.argv[1] == 'migrate':
    if len(sys.argv) == 4:
        ''' migrate guest to server'''
        guest = sys.argv[2]
        to_server = sys.argv[3]
        command = 'cmd {"action":"migrate","guest":"' + guest
        command += '","to_server":"' + to_server + '"}'
        resp = server.get_from_socket(command)
        print(resp)
    elif len(sys.argv) == 5 and sys.argv[2] == 'all':
        ''' migrate all '''
        from_server = sys.argv[3]
        to_server = sys.argv[4]
        command = 'cmd {"action":"migrateAll","from_server":"' + from_server
        command += '","to_server":"' + to_server + '"}'
        resp = server.get_from_socket(command)
        print(resp)
    else:
        print('Invalid arguments.')
elif sys.argv[1] == 'share':
    if len(sys.argv) == 3:
        path = sys.argv[2]
        command = 'cmd {"action":"create_share","path":"' + path + '"}'
        resp = server.get_from_socket(command)
        print(resp)
    else:
        print('Invalid arguments.')
elif sys.argv[1] == 'mount':
    if len(sys.argv) == 3:
        s = sys.argv[2].split('@')
        if len(s) == 2:
            server_name = s[2]
            share_name = s[1]
        else:
            server_name = server.get_hostname()
            share_name = sys.argv[2]
        command = 'cmd {"action":"mount","share_name":"' + share_name + '"'
        command += ',"server_name":"' + server_name + '"}'
        resp = server.get_from_socket(command)
        print(resp)
    else:
        print('Invalid arguments.')
    # TODO: move this to worker (see migrate)
    '''
    if len(sys.argv) == 3:
        shares = get_shares()
        m_share = False
        for share in shares:
            s = share['server'] + ':' + share['path']
            if s == sys.argv[2]:
                m_share = share
        print(storage.mount(m_share))
    else:
        print('Invalid arguments.')
    '''
elif sys.argv[1] == 'move':
    # TODO: move guest
    pass
elif sys.argv[1] == 'shutdown':
    # TODO: stop guest
    pass
elif sys.argv[1] == 'destroy':
    # TODO: destroy guest
    pass
