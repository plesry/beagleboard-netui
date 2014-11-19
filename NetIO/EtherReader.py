#!/usr/bin/python2
import os
import subprocess
SHELL_SCRIPTS = './shellscripts/ip_fetch.sh'
DEVICE = 'usb0'


def call_scripts(scripts=SHELL_SCRIPTS, device=DEVICE):
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_path = os.path.join(pkg_dir, scripts)
    shell_proc = subprocess.Popen(
        [scripts_path, device],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return shell_proc.communicate()


def compile_info(iplist):
    ipdict = dict()

    if len(iplist) == 6 \
            and iplist[0].strip('\n') != "ERROR":
        ipdict["device"] = iplist[0]
        ipdict["ip_addr"] = iplist[2]
        ipdict["subnet_mask"] = iplist[3]
        ipdict["gateway"] = iplist[4]
        ipdict["dns"] = iplist[5].strip('\n')
#        ipdict["dynamic"] = int(iplist[1])
        if int(iplist[1]) == 1:
            ipdict["dynamic"] = True
        else:
            ipdict["dynamic"] = False

    return ipdict


def fetch(scripts=SHELL_SCRIPTS, device=DEVICE):
    out, err = call_scripts(scripts, device)
    iplist = out.split(' ')
    return compile_info(iplist)
