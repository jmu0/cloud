#!/usr/bin/python3

# TODO: copy scripts to /usr/share/cloud
# TODO: link cloud.py in /usr/bin
# TODO: probe which distribution (sysvinit / upstart / systemd)
# TODO: copy startup script

# startup: /etc/init (ubuntu ...)

# systemd: (arch ...)
#   copy to /etc/systemd/system
#   sudo systemclt enable cloud.service
#   sudo systemctl start cloud.service

# sysvinit: /etc/init.d (debian ...)
#   copy to /etc/init.d
#   ????  sudo update-rc.d /etc/init.d/cloud defaults
#   sudo update-rc.d /etc/init.d/cloud enable
#   sudo /etc/init.d/cloud start


