#!/usr/bin/env python3

"""flightbox_watchdog.py: Script that checks if required FlightBox and OGN processes are running and (re-)starts them if required.
Can be used to start and monitor FlightBox via a cronjob."""

from os import path
from os import system
import psutil
from utils.detached_screen import DetachedScreen
import time

__author__ = "Serge Guex"

# define OGN processes that must be running
required_ogn_processes = {}
required_ogn_processes['ogn-rf'] = {'status': None}
required_ogn_processes['ogn-decode'] = {'status': None}

# define DUMP1090 processes that must be running
required_dump1090_processes = {}
required_dump1090_processes['dump1090'] = {'status': None}

# define flightbox processes that must be running
required_flightbox_processes = {}
required_flightbox_processes['flightbox'] = {'status': None}
required_flightbox_processes['flightbox_datahubworker'] = {'status': None}
required_flightbox_processes['flightbox_output_network_airconnect'] = {'status': None}
required_flightbox_processes['flightbox_transformation_sbs1ognnmea_flarm'] = {'status': None}
required_flightbox_processes['flightbox_input_network_sbs1'] = {'status': None}
required_flightbox_processes['flightbox_input_network_ogn_server'] = {'status': None}
required_flightbox_processes['flightbox_input_serial_gnss'] = {'status': None}

# define pcasweb processes that must be running
required_pcasweb_processes = {}
required_pcasweb_processes['pcasweb'] = {'status': None}

# define path where OGN binaries are located
ogn_path = '/home/pi/opt/rtlsdr-ogn'

# define command for starting dump1090
dump1090_command = 'sudo systemctl start dump1090'

# define command for starting flightbox
flightbox_command = '/home/pi/opt/flightbox/flightbox.py'

# define command for starting pcasweb
pcasweb_command = 'sudo systemctl start pcasweb.service'

# define command for starting ogn
ogn_command = 'sudo systemctl start rtlsdr-ogn'

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
    time.sleep(15.0)

def restart_flightbox():
    kill_all_flightbox_processes()
    time.sleep(5.0)
    start_flightbox()

#PCAS WEB
def check_pcasweb_processes():
    global required_pcasweb_processes

    for p in psutil.process_iter():
        if p.name() in required_pcasweb_processes.keys():
            required_pcasweb_processes[p.name()]['status'] = p.status()

def kill_all_pcasweb_processes():
    for p in psutil.process_iter():
        if p.name().startswith('pcasweb.sh'):            
            print("Killing process {}".format(p.name()))
            system('sudo killall pcasweb')
            system('sudo systemctl stop pcasweb.service')
            #p.kill()

def start_pcasweb():
    global pcasweb_command

    print("Starting pcasweb and stop NTP")
    system('sudo systemctl stop ntp')
    time.sleep(5.0)
    system('sudo systemctl start pcasweb.service')
	time.sleep(5.0)


def restart_pcasweb():
    kill_all_pcasweb_processes()
    time.sleep(5.0)
    start_pcasweb()


#DUMP1090
def check_dump1090_processes():
    global required_dump1090_processes

    for p in psutil.process_iter():
        if p.name() in required_dump1090_processes.keys():
            required_dump1090_processes[p.name()]['status'] = p.status()

def kill_all_dump1090_processes():
    for p in psutil.process_iter():
        if p.name().startswith('dump1090'):            
            print("Killing process {}".format(p.name()))
            system('sudo systemctl stop dump1090')
            p.kill()

def start_dump1090():
    global dump1090_command

    print("Starting dump1090 and NTP")
    system('sudo systemctl start ntp')
    system('sudo systemctl start dump1090')
    time.sleep(5.0)

def restart_dump1090():
    kill_all_dump1090_processes()
    time.sleep(5.0)
    start_dump1090()

#OGN
def check_ogn_processes():
    global required_ogn_processes

    for p in psutil.process_iter():
        if p.name() in required_ogn_processes.keys():
            required_ogn_processes[p.name()]['status'] = p.status()


def kill_all_ogn_processes():
    global ogn_path

    for p in psutil.process_iter():
        if p.name().startswith('ogn-'):
            print("Killing process {}".format(p.name()))
            p.kill()


def start_ogn():
    global ogn_path

    print("Starting OGN")
    system('sudo systemctl start rtlsdr-ogn')

def restart_ogn():
    kill_all_ogn_processes()
    time.sleep(1.0)
    start_ogn()


# check if script is executed directly
if __name__ == "__main__":
    check_dump1090_processes()
    check_ogn_processes()
    check_flightbox_processes()
    check_pcasweb_processes()
    
    is_dump1090_restart_required = False
    is_ogn_restart_required = False
    is_flightbox_restart_required = False
    is_pcasweb_restart_required = False

    for p in required_dump1090_processes.keys():
        if required_dump1090_processes[p]['status'] not in ['running', 'sleeping']:
            print("{} not running".format(p))
            is_dump1090_restart_required = True

    for p in required_ogn_processes.keys():
        if required_ogn_processes[p]['status'] not in ['running', 'sleeping']:
            print("{} not running".format(p))
            is_ogn_restart_required = True

    for p in required_flightbox_processes.keys():
        if required_flightbox_processes[p]['status'] not in ['running', 'sleeping']:
            print("{} not running".format(p))
            is_flightbox_restart_required = True            

    for p in required_pcasweb_processes.keys():
        if required_pcasweb_processes[p]['status'] not in ['running', 'sleeping']:
            #print("{} not running".format(p))
            is_pcasweb_restart_required = True


    if is_dump1090_restart_required:
        time.sleep(2.0)
        print('== Restarting DUMP1090')
        restart_dump1090()			

    if is_ogn_restart_required:
        time.sleep(5.0)
        print('== Restarting OGN')
        restart_ogn()
			
    if is_flightbox_restart_required:
        time.sleep(2.0)
        print('== Restarting FlightBox')
        restart_flightbox()
        
    if is_pcasweb_restart_required:
        time.sleep(2.0)
        #print('== Restarting PCASweb')
        restart_pcasweb()
        

