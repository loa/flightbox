#!/usr/bin/env python3

"""flightbox_watchdog.py: Script that checks if required FlightBox and OGN processes are running and (re-)starts them if required.
Can be used to start and monitor FlightBox via a cronjob."""
import serial
import pynmea2
from os import path
from os import system
import psutil
from utils.detached_screen import DetachedScreen
import time
import subprocess

__author__ = "Serge Guex"

# define flightbox processes that must be running
required_flightbox_processes = {}
required_flightbox_processes['flightbox'] = {'status': None}
required_flightbox_processes['flightbox_datahubworker'] = {'status': None}
required_flightbox_processes['flightbox_output_network_airconnect'] = {'status': None}
required_flightbox_processes['flightbox_transformation_sbs1ognnmea_flarm'] = {'status': None}
required_flightbox_processes['flightbox_input_network_sbs1'] = {'status': None}
required_flightbox_processes['flightbox_input_network_ogn_server'] = {'status': None}
required_flightbox_processes['flightbox_input_serial_gnss'] = {'status': None}

# define command for starting flightbox
flightbox_command = '/home/pi/opt/flightbox/flightbox.py'

#Flightbox
def check_flightbox_processes():
    global required_flightbox_processes

    for p in psutil.process_iter():
        if p.name() in required_flightbox_processes.keys():
            required_flightbox_processes[p.name()]['status'] = p.status()

def kill_all_flightbox_processes():
    for p in psutil.process_iter():
        if p.name().startswith('flightbox'):
            print("Killing process {}".format(p.name()))
            p.kill()

def start_flightbox():
    global flightbox_command

    print("Starting flightbox")
    s = DetachedScreen('flightbox', command=flightbox_command, initialize=True)
    s.disable_logs()

def restart_flightbox():
    kill_all_flightbox_processes()
    time.sleep(10.0)
    start_flightbox()


# check if script is executed directly
if __name__ == "__main__":

        check_flightbox_processes()
        
        is_flightbox_restart_required = True

        for p in required_flightbox_processes.keys():
            if required_flightbox_processes[p]['status'] not in ['running', 'sleeping']:
                print("{} not running".format(p))
                is_flightbox_restart_required = True            

                           
        if is_flightbox_restart_required:
            time.sleep(5.0)
            print('== Restarting FlightBox')
            restart_flightbox()

                    
