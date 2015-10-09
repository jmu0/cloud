import os
import sys
import socket
import subprocess


def is_nfs_server():
    ''' is localhost nfs server'''
    return os.path.isfile('/etc/exports')


def get_shares():
    # TODO: create resource class to associate with mounts and vm's
    ''' get local shares'''
    with open('/etc/exports', 'r') as f:
        exportsfile = f.readlines()
    exports = []
    for line in exportsfile:
        share = line_to_share(line)
        if share:
            exports.append(share)
    return exports


def get_mounts():
    ''' get nfs mounts on localhost '''
    mounts = []
    f = os.popen('df -h -t nfs -t nfs4 2> /dev/null')
    lines = f.read()
    lines = str(lines).splitlines()[1:]
    f.close()
    servername = socket.gethostname()
    for line in lines:
        line = line.split()
        server = line[0].split(':')
        path = server[1]
        server = server[0]
        name = path.split('/')[-1:][0]
        mount = {
            'mount': line[0],
            'shareserver': server,
            'sharepath': path,
            'sharename': name,
            'server': servername,
            'size': line[1],
            'used': line[2],
            'available': line[3],
            'usedPerc': line[4],
            'mountpoint': line[5]
        }
        mounts.append(mount)
    return mounts


def line_to_share(line):
    ''' line in exportfs to share dict'''
    if not line.strip()[0] == '#':
        servername = socket.gethostname()
        line = line.split()
        path = line[0]
        name = path.split('/')[-1:][0]
        options = line[1].split('(')
        network = options[0]
        options = options[1]
        options = options[:-1]
        options = options.split(',')
        share = {
            'name': name,
            'path': path,
            'network': network,
            'options': options,
            'server': servername
        }
        return share
    else:
        return False


def share_to_line(share):
    ''' share dict to exports line '''
    line = share['path'] + ' '
    line += share['network'] + '('
    for o in share['options']:
        line += o + ','
    line = line[:-1]
    line += ')\n'
    return line


def check_if_mounted(mountpoint):
    ''' check if mountpoint is mounted '''
    mounts = get_mounts()
    servername = socket.gethostname()
    for m in mounts:
        if m['mountpoint'] == mountpoint and m['server'] == servername:
            return True
    return False


def mount(share):
    ''' mount share '''
    mountpoint = '/mnt/'
    mountpoint += share['server'] + '/'
    mountpoint += share['name']
    share['mountpoint'] = mountpoint
    # print(mountpoint)
    if not check_if_mounted(mountpoint):
        # print('not mounted')
        sharepath = share['server'] + ':' + share['path']
        # print(sharepath)
        if not os.path.isdir(mountpoint):
            # print('create path' + str(mountpoint))
            cmd = ['mkdir', '-p', mountpoint]
            res = subprocess.call(cmd)
            if not res == 0:
                print('could not create mountpoint')
                print(str(sys.exc_info()[1]))
                return False
        cmd = ['mount', sharepath, mountpoint]
        # print('mounting')
        res = subprocess.call(cmd)
        if not res == 0:
            print('could not mount share')
            print(str(sys.exc_info()[1]))
            return False
        else:
            return share
    else:
        return share


def create_share(path):
    ''' create share from path on localhost'''
    # check if localhost is nfs server
    if not is_nfs_server():
        print('not a nfs server')
        return False
    # check if path exists
    if not os.path.isdir(path):
        print('path ' + path + ' does not exist')
        return False
    # check if already sahared
    shares = get_shares()
    for s in shares:
        if s['path'] == path:
            print('path already shared: ' + path)
            return False
    # add line to /etc/exports
    line = share_to_line({
        'path': path,
        'network': '10.0.0.1/24',
        'options': ['rw', 'sync', 'subtree_check', 'no_root_squash']
    })
    with open('/etc/exports', 'a') as f:
        f.write(line)
    # update exports
    res = subprocess.call(['exportfs', '-rav'])
    if res == 0:
        return True
    else:
        print('could not update exports')
        return False


def sync_share(primary_share, secondary_share):
    ''' sync primary share to secondary shares '''
    # mount shares
    primary_share = mount(primary_share)
    secondary_share = mount(secondary_share)
    if not primary_share:
        print('could not mount primary share')
        return False
    if not secondary_share:
        print('could not mount secondary share')
        return False
    prim_path = primary_share['mountpoint'] + '/'
    sec_path = secondary_share['mountpoint']
    cmd = ['rsync', '--archive', '--update', '--delete',
           '--exclude=.cloud.json', prim_path, sec_path]
    res = subprocess.call(cmd)
    if res == 0:
        return True
    else:
        return False


def migrate_share(share_name, to_server):
    ''' migrate share to server (sync, set primary) '''
    # TODO: resources; .cloud.json file in share to store metadata
    # TODO: migrate share
    pass

# arch: enable * start rpcbind.service + nfs-server.service
# exportfs -rav
# /nfs/test 10.0.0.1/24(rw,sync,subtree_check,no_root_squash)
