#!/usr/bin/env python3
import argparse
import serial
import select
import struct
import sys
import time
import math
from client import *

parser = argparse.ArgumentParser('Client for sending controller commands to a controller emulator')
parser.add_argument('port')
args = parser.parse_args()

def send_cmd(arg = ''):
    client.send_cmd(arg)

def p_wait(arg):
    client.p_wait(arg)

def translateCommand(command):
    if command == 'a':
        send_cmd(client.BTN_A) ; p_wait(0.3) ; send_cmd() ; p_wait(0.5)
    elif command == 'b':
        send_cmd(client.BTN_B); p_wait(0.3) ; send_cmd() ; p_wait(0.5)
    elif command == 'menua':
        send_cmd(client.LSTICK_L) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER)
        send_cmd(client.LSTICK_R) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER)
        send_cmd(client.BTN_A)
    elif command == 'menub':
        send_cmd(client.LSTICK_L) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER)
        send_cmd(client.LSTICK_R) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER)
        send_cmd(client.BTN_B)
    elif command == 'u':
        send_cmd(client.LSTICK_U) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'r':
        send_cmd(client.LSTICK_R) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'rstep':
        send_cmd(client.LSTICK_R) ; p_wait(0.3) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'd':
        send_cmd(client.LSTICK_D) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'l':
        send_cmd(client.LSTICK_L) ; p_wait(0.1) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'lstep':
        send_cmd(client.LSTICK_L) ; p_wait(0.3) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'ustep':
        send_cmd(client.LSTICK_U) ; p_wait(0.3) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'lsteps':
        send_cmd(client.LSTICK_L) ; p_wait(5) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.5)
    elif command == 'rsteps':
        send_cmd(client.LSTICK_R) ; p_wait(5) ; send_cmd(client.LSTICK_CENTER) ; p_wait(0.5)
    elif command == 'c':
        send_cmd(client.LSTICK_CENTER)
    elif command == 'R':
        send_cmd(client.BTN_R) ; p_wait(0.01)
    elif command == 'pc':
        send_cmd(client.BTN_R) ; p_wait(0.2); send_cmd() ; translateCommand('l')
    elif command == 'L':
        send_cmd(client.BTN_L)
    elif command == 'x':
        send_cmd(client.BTN_X); p_wait(0.3)  ; send_cmd() ; p_wait(0.5)
    elif command == 'y':
        send_cmd(client.BTN_Y); p_wait(0.3)  ; send_cmd() ; p_wait(0.5)
    elif command == 'min':
        send_cmd(client.BTN_MINUS); p_wait(0.3)  ; send_cmd() ; p_wait(0.001)
    elif command == 'tr':
        send_cmd(client.LSTICK_U_R) ; p_wait(0.05) ; send_cmd(client.LSTICK_CENTER)
    elif command == 't':
        send_cmd(client.LSTICK_L + RSTICK_R) ; p_wait(50); send_cmd(client.LSTICK_CENTER + RSTICK_CENTER)
    elif command == 'du':
        send_cmd(DPAD_U) ; p_wait(0.2) ; send_cmd() ; p_wait(0.4)
    elif command == 'dr':
        send_cmd(DPAD_R) ; p_wait(0.2) ; send_cmd() ; p_wait(0.4)
    elif command == 'dd':
        send_cmd(DPAD_D) ; p_wait(0.2) ; send_cmd() ; p_wait(0.4)
    elif command == 'dl':
        send_cmd(DPAD_L) ; p_wait(0.2) ; send_cmd() ; p_wait(0.4)
    elif command == 'release_one':
        release()
    elif command == 'release':
        release_pokemons()
    elif command == 'turn':
        loops = 2
        while loops > 0:
            for i in range(0,721):
                cmd = client.lstick_angle(i + 90, 0xFF)
                send_cmd(cmd)
                p_wait(0.001)
            loops = loops - 1
        send_cmd(client.LSTICK_CENTER) ; p_wait(0.5)
    elif command == 'eggs':
        eggs()
    elif command == 'hatch':
        hatch()
    elif command == 'eggs_bike':
        eggs_bike()

def eggs_bike():
    loops = 0
    translateCommand('min')
    print('vélo')
    while loops < 4:
        print('loop vélo')
        translateCommand('rsteps')
        p_wait(.5)
        translateCommand('lsteps')
        p_wait(.5)
        loops += 1  

def open_pc():
    translateCommand('x')
    p_wait(1)
    translateCommand('a')
    p_wait(2)
    translateCommand('pc')
    p_wait(1)

def pick_five():
    translateCommand('a')
    translateCommand('dd')
    translateCommand('dd')
    translateCommand('dd')
    translateCommand('dd')
    translateCommand('a')

def hatch_bike(nbloops = 7):
    loops = 0
    print('vélo')
    while loops < nbloops:
        print('loop vélo')
        translateCommand('rsteps')
        p_wait(.5)
        translateCommand('lsteps')
        p_wait(.5)
        loops +=  1

###
# Must be done : 
# - Cursor on pokemon team
# - Bike on
# - Stay at the right side  of the female NPC,  on the bottom side of the bridge
###
def hatch():
    print('Combien de boîtes à faire éclore ? :')
    boxes = int(input())
    print('Boucles à vélo (par défaut pour 5500 pas) :')
    nbloops = int(input())
    start_time = time.time()
    # 5500 step = 7 loops
    hatchedEggs = 0
    totalEggs = 0
    currentBatch = 0
    eggsInPocket = False
    # 1 box = 30 eggs
    projectedEggs = boxes * 30
    p_wait(1)
    print('{} projected eggs'.format(projectedEggs))
    while(totalEggs != projectedEggs):
        # First iteration
        if not eggsInPocket:
            open_pc()
            p_wait(.5)
            translateCommand('y')
            p_wait(.5)
            translateCommand('y')
            p_wait(.5)
            pick_five()
            translateCommand('dl')
            translateCommand('dd')
            translateCommand('a')
            print('First batch in the pocket')
            currentBatch = 1
            eggsInPocket = True
            translateCommand('b')
            p_wait(1)
            translateCommand('b')
            p_wait(1)
            translateCommand('b')
            p_wait(1)

        print('Hatching the batch')
        while hatchedEggs < 5:
            
            if(hatchedEggs == 0):
                hatch_bike(nbloops)
            else:
                translateCommand('lstep')
                translateCommand('rstep')
            
            p_wait(1)
            # appuyer sur b, attendre x secondes puis a
            translateCommand('b')
            p_wait(16)
            translateCommand('b')
            p_wait(5)

            hatchedEggs += 1
            print('Egg n° {}'.format(hatchedEggs))
            totalEggs += 1
        print('Eggs hatched : {}'.format(totalEggs))

        hatchedEggs = 0
        # Reset position
        translateCommand('lsteps')
        # Refill the pocket !
        open_pc()
        p_wait(.5)
        translateCommand('dd')
        translateCommand('dl')
        translateCommand('y')
        translateCommand('y')
        pick_five()
        p_wait(.5)
        for i in range(currentBatch):
            translateCommand('dr')
        translateCommand('du')
        translateCommand('a')
        print('Batch stored')
        if(totalEggs != projectedEggs):
            if(currentBatch == 6):
                translateCommand('du')
                translateCommand('dr')
                translateCommand('dd')
                translateCommand('dr')
                translateCommand('dr')
                currentBatch = 1
            else:
                translateCommand('dr')
                currentBatch += 1
            pick_five()
            for i in range(currentBatch):
                translateCommand('dl')
            translateCommand('dd')
            translateCommand('a')
            print('Fresh batch in the pocket')
            translateCommand('b')
            p_wait(1)
            translateCommand('b')
            p_wait(1)
            translateCommand('b')
            p_wait(1)
        else:
            elapsed_time = time.time() - start_time
            print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


        


###
# Must be in the PC, top left of the box
# 
###
def release_pokemons():
    print('Combien de boîtes à libérer ?')
    boxes = int(input())
    start_time = time.time()
    releasedPkm = 0
    projectedRelease = boxes * 30
    p_wait(.5)
    while(projectedRelease != releasedPkm):
        release()
        releasedPkm += 1
        if( releasedPkm % 6 == 0 and releasedPkm % 30 == 0):
            translateCommand('dd')
            translateCommand('dd')
            translateCommand('dr')
            translateCommand('dd')
            translateCommand('dr')
            translateCommand('dr')
        elif(releasedPkm % 6 == 0):
            translateCommand('dr')
            translateCommand('dr')
            translateCommand('dd')
        else:
            translateCommand('dr')

    elapsed_time = time.time() - start_time
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

def release():
    translateCommand('a')
    translateCommand('du')
    translateCommand('du')
    translateCommand('a')
    p_wait(.6)
    translateCommand('du')
    translateCommand('a')
    p_wait(.6)
    translateCommand('a')


###
#   Récupérer les oeufs et les mettre dans le PC (avoir 6 pkm dans l'équipe)
# COmmencer avec le curseur de menu sur la MAP
###
def eggs():
    print('Combien d\'oeufs récupérer ?')
    projectedEggs = int(input())
    start_time = time.time()
    translateCommand('lstep')
    translateCommand('lstep')
    p_wait(.4)
    eggs = 0
    while eggs < projectedEggs:
        eggs_bike() 
        print('ouveture menu')          
        p_wait(.5)
        translateCommand('x')
        p_wait(1)
        #reset cursor
        """
        translateCommand('l')
        translateCommand('r')
        """
        p_wait(.3)
        translateCommand('a')
        # Ouverture map
        print('ouveture map')          
        p_wait(2)
        translateCommand('tr')
        p_wait(.5)
        translateCommand('a')
        p_wait(.5)
        translateCommand('menua')
        print('envol')          
        #envol
        p_wait(3)
        translateCommand('min')
        p_wait(.4)
        translateCommand('lstep')
        p_wait(.5)
        translateCommand('lstep')
        p_wait(.5)
        translateCommand('ustep')
        print('récupération oeuf')          
        p_wait(.5)
        translateCommand('a')
        p_wait(1)
        translateCommand('menua')
        p_wait(4)
        translateCommand('menua')
        p_wait(3)
        translateCommand('menua')
        p_wait(3)
        translateCommand('menua')
        p_wait(3)

        translateCommand('menub')
        p_wait(.5)
        #pour être sûr
        translateCommand('menub')
        p_wait(.5)
        translateCommand('menub')
        p_wait(.5)
        translateCommand('menub')
        p_wait(.5)
        eggs = eggs +1
        print('oeufs récupérés : ')
        print(eggs)
    
    elapsed_time = time.time() - start_time
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


    # A .5
    # 
# -------------------------------------------------------------------------
# ser = serial.Serial(port=args.port, baudrate=57600,timeout=1)
# serialVar = serial.Serial(port=args.port, baudrate=19200,timeout=1)
# ser = serial.Serial(port=args.port, baudrate=31250,timeout=1)
# ser = serial.Serial(port=args.port, baudrate=40000,timeout=1)
# ser = serial.Serial(port=args.port, baudrate=62500,timeout=1)
# serialSet(args.port)
client = Client(args.port)
# Attempt to sync with the MCU
if not client.sync():
    print('Could not sync!')


client.p_wait(0.05)

if not client.send_cmd():
    print('Packet Error!')



while True:
    print('Command: ')
    command = input()
    translateCommand(command)
    
client.ser.close

