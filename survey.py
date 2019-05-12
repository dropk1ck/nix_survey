#!/usr/bin/env python
from __future__ import print_function
import subprocess

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

# dictionary of survey tasks to complete of the form:
#     taskname: {"cmd": cmd_to_run, "results": empty_string}
base_survey = {
    "date": {"cmd": "date", "results": ""},
    "hostname": {"cmd": "hostname", "results": ""},
    "uname": {"cmd": "uname -a", "results": ""},
    "id": {"cmd": "id", "results": ""},
}

def do_task(task):
    out, err = subprocess.Popen(task["cmd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    task["results"] = out
    return task

def task_banner(taskname):
    print(colors.fg.orange + "========== " +  colors.fg.cyan + taskname + colors.fg.orange + " ==========" + colors.reset)

def task_footer():
    print(colors.fg.orange + "===============================" + colors.reset, "\n\n")

def main():
    # perform the basic survey
    for taskname, task in base_survey.items():
        task_banner(taskname)
        task = do_task(task)
        for line in task["results"].splitlines():
            print(line)
        task_footer()

    # check for relevant kernel/system privescs
    uname_results = base_survey["uname"]["results"]
    system_name = uname_results[0]
    kernel_version = uname_results[2]

    print(colors.bg.cyan + colors.fg.black + "SURVEY COMPLETE" + colors.reset)

if __name__ == "__main__":
    main()

