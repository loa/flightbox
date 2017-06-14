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


#NTP
def start_NTP():
    print("Starting NTP")
    subprocess.call('sudo systemctl restart ntp', shell=True)
    time.sleep(20)
    
def stop_NTP():
    print("Stoping NTP")
    subprocess.call('sudo systemctl stop ntp', shell=True)
    time.sleep(3)

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
def kill_all_pcasweb_processes():

    print("Stopping pcasweb")
    system('sudo systemctl stop pcasweb.service')
    
def start_pcasweb():
    global pcasweb_command

    print("Starting pcasweb")
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
            subprocess.call('sudo systemctl stop dump1090', shell=True)
            p.kill()

def start_dump1090():
    global dump1090_command

    print("Starting dump1090")
    subprocess.call('sudo systemctl restart dump1090', shell=True)
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
    subprocess.call('sudo systemctl restart rtlsdr-ogn', shell=True)

def restart_ogn():
    kill_all_ogn_processes()
    time.sleep(1.0)
    start_ogn()

def start_SoftAP():
    print('== Starting SoftAP')
    subprocess.call('sudo bash /usr/sbin/flightbox-wifi.sh', shell=True)
    # turn on the green LED
    time.sleep(10.0)
    
def check_gps_fix():
    ### initialize serial object
    ser = None
    fix = False
    # decouple green LED on PI from microSD
    system("sudo bash -c \"echo none > /sys/class/leds/led0/trigger\"")
    time.sleep(2)
    # turn off the green LED on PI
    system("sudo bash -c \"echo 1 > /sys/class/leds/led0/brightness\"")
    

    time.sleep(2)
    
    while True:
         try:
              # wait before attaching to serial port
              time.sleep(2)
              # create serial object
              ser = serial.Serial('/dev/ttyAMA0',9600)
              # read loop
              while True:
                   try:
                        # get line from serial device (blocking call)
                        data = ser.readline().decode().strip()
                   except:
                        # in case read was unsuccessful, exit read loop
                        break

                   if data.startswith('$GPGSA'):
                        msg = pynmea2.parse(data)
                        msg.is_valid == True
                        msg.render() == data
                        print('== Wait for GPS 3D Fix')
                        #print ('\tMode:', msg.mode)
                        #print ('\tMode fix type:', int(msg.mode_fix_type))
                        if msg.mode == 'A' and int(msg.mode_fix_type) > 1:
                             print('GPS Fix')
                             system("sudo bash -c \"echo 0 > /sys/class/leds/led0/brightness\"")
                             fix = True
                             break
              if fix == True:
                   time.sleep(10)
                   ser.close()
                   break
                   
         except(KeyboardInterrupt, SystemExit):
              # exit re-connect loop in case of termination is requested
              break
         finally:
              if ser:
                   ser.close()  

# check if script is executed directly
if __name__ == "__main__":
    
        restart_pcasweb()
        check_gps_fix()
        start_NTP()
        check_ogn_processes()
        check_dump1090_processes()
        check_flightbox_processes()
        stop_NTP()
        
        is_dump1090_restart_required = False
        is_ogn_restart_required = False
        is_flightbox_restart_required = False


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
            print('== Restarting FlightBox, Stop NTP')
            stop_NTP()
            restart_flightbox()
            
            #print('== Restarting PCASweb')
            restart_pcasweb()
                    
