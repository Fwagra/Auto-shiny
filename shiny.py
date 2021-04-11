#!/usr/bin/env python3

import argparse
import serial
import select
import struct
import sys
import time
import math

parser = argparse.ArgumentParser('Client for sending controller commands to a controller emulator')
parser.add_argument('--port')
parser.add_argument('--command')
parser.add_argument('--eggs')
parser.add_argument('--cycles')
parser.add_argument('--boxes')
args = parser.parse_args()


STATE_OUT_OF_SYNC   = 0
STATE_SYNC_START    = 1
STATE_SYNC_1        = 2
STATE_SYNC_2        = 3
STATE_SYNC_OK       = 4

# Actual Switch DPAD Values
A_DPAD_CENTER    = 0x08
A_DPAD_U         = 0x00
A_DPAD_U_R       = 0x01
A_DPAD_R         = 0x02
A_DPAD_D_R       = 0x03
A_DPAD_D         = 0x04
A_DPAD_D_L       = 0x05
A_DPAD_L         = 0x06
A_DPAD_U_L       = 0x07

# Enum DIR Values
DIR_CENTER    = 0x00
DIR_U         = 0x01
DIR_R         = 0x02
DIR_D         = 0x04
DIR_L         = 0x08
DIR_U_R       = DIR_U + DIR_R
DIR_D_R       = DIR_D + DIR_R
DIR_U_L       = DIR_U + DIR_L
DIR_D_L       = DIR_D + DIR_L

BTN_NONE         = 0x0000000000000000
BTN_Y            = 0x0000000000000001
BTN_B            = 0x0000000000000002
BTN_A            = 0x0000000000000004
BTN_X            = 0x0000000000000008
BTN_L            = 0x0000000000000010
BTN_R            = 0x0000000000000020
BTN_ZL           = 0x0000000000000040
BTN_ZR           = 0x0000000000000080
BTN_MINUS        = 0x0000000000000100
BTN_PLUS         = 0x0000000000000200
BTN_LCLICK       = 0x0000000000000400
BTN_RCLICK       = 0x0000000000000800
BTN_HOME         = 0x0000000000001000
BTN_CAPTURE      = 0x0000000000002000

DPAD_CENTER      = 0x0000000000000000
DPAD_U           = 0x0000000000010000
DPAD_R           = 0x0000000000020000
DPAD_D           = 0x0000000000040000
DPAD_L           = 0x0000000000080000
DPAD_U_R         = DPAD_U + DPAD_R
DPAD_D_R         = DPAD_D + DPAD_R
DPAD_U_L         = DPAD_U + DPAD_L
DPAD_D_L         = DPAD_D + DPAD_L

LSTICK_CENTER    = 0x0000000000000000
LSTICK_R         = 0x00000000FF000000 #   0 (000)
LSTICK_U_R       = 0x0000002DFF000000 #  45 (02D)
LSTICK_U         = 0x0000005AFF000000 #  90 (05A)
LSTICK_U_L       = 0x00000087FF000000 # 135 (087)
LSTICK_L         = 0x000000B4FF000000 # 180 (0B4)
LSTICK_D_L       = 0x000000E1FF000000 # 225 (0E1)
LSTICK_D         = 0x0000010EFF000000 # 270 (10E)
LSTICK_D_R       = 0x0000013BFF000000 # 315 (13B)

RSTICK_CENTER    = 0x0000000000000000
RSTICK_R         = 0x000FF00000000000 #   0 (000)
RSTICK_U_R       = 0x02DFF00000000000 #  45 (02D)
RSTICK_U         = 0x05AFF00000000000 #  90 (05A)
RSTICK_U_L       = 0x087FF00000000000 # 135 (087)
RSTICK_L         = 0x0B4FF00000000000 # 180 (0B4)
RSTICK_D_L       = 0x0E1FF00000000000 # 225 (0E1)
RSTICK_D         = 0x10EFF00000000000 # 270 (10E)
RSTICK_D_R       = 0x13BFF00000000000 # 315 (13B)

NO_INPUT       = BTN_NONE + DPAD_CENTER + LSTICK_CENTER + RSTICK_CENTER

# Commands to send to MCU
COMMAND_NOP        = 0x00
COMMAND_SYNC_1     = 0x33
COMMAND_SYNC_2     = 0xCC
COMMAND_SYNC_START = 0xFF

# Responses from MCU
RESP_USB_ACK       = 0x90
RESP_UPDATE_ACK    = 0x91
RESP_UPDATE_NACK   = 0x92
RESP_SYNC_START    = 0xFF
RESP_SYNC_1        = 0xCC
RESP_SYNC_OK       = 0x33

# Compute x and y based on angle and intensity
def angle(angle, intensity):
    # y is negative because on the Y input, UP = 0 and DOWN = 255
    x =  int((math.cos(math.radians(angle)) * 0x7F) * intensity / 0xFF) + 0x80
    y = -int((math.sin(math.radians(angle)) * 0x7F) * intensity / 0xFF) + 0x80
    return x, y

def lstick_angle(angle, intensity):
    return (intensity + (angle << 8)) << 24

def rstick_angle(angle, intensity):
    return (intensity + (angle << 8)) << 44

# Precision wait
def p_wait(waitTime):
    t0 = time.perf_counter()
    t1 = t0
    while (t1 - t0 < waitTime):
        t1 = time.perf_counter()

# Wait for data to be available on the serial port
def wait_for_data(timeout = 1.0, sleepTime = 0.1):
    t0 = time.perf_counter()
    t1 = t0
    inWaiting = ser.in_waiting
    while ((t1 - t0 < sleepTime) or (inWaiting == 0)):
        time.sleep(sleepTime)
        inWaiting = ser.in_waiting
        t1 = time.perf_counter()

# Read X bytes from the serial port (returns list)
def read_bytes(size):
    bytes_in = ser.read(size)
    return list(bytes_in)

# Read 1 byte from the serial port (returns int)
def read_byte():
    bytes_in = read_bytes(1)
    if len(bytes_in) != 0:
        byte_in = bytes_in[0]
    else:
        byte_in = 0
    return byte_in

# Discard all incoming bytes and read the last (latest) (returns int)
def read_byte_latest():
    inWaiting = ser.in_waiting
    if inWaiting == 0:
        inWaiting = 1
    bytes_in = read_bytes(inWaiting)
    if len(bytes_in) != 0:
        byte_in = bytes_in[0]
    else:
        byte_in = 0
    return byte_in

# Write bytes to the serial port
def write_bytes(bytes_out):
    ser.write(bytearray(bytes_out))
    return

# Write byte to the serial port
def write_byte(byte_out):
    write_bytes([byte_out])
    return

# Compute CRC8
# https://www.microchip.com/webdoc/AVRLibcReferenceManual/group__util__crc_1gab27eaaef6d7fd096bd7d57bf3f9ba083.html
def crc8_ccitt(old_crc, new_data):
    data = old_crc ^ new_data

    for i in range(8):
        if (data & 0x80) != 0:
            data = data << 1
            data = data ^ 0x07
        else:
            data = data << 1
        data = data & 0xff
    return data

# Send a raw packet and wait for a response (CRC will be added automatically)
def send_packet(packet=[0x00,0x00,0x08,0x80,0x80,0x80,0x80,0x00], debug=False):
    if not debug:
        bytes_out = []
        bytes_out.extend(packet)

        # Compute CRC
        crc = 0
        for d in packet:
            crc = crc8_ccitt(crc, d)
        bytes_out.append(crc)
        write_bytes(bytes_out)
        # print(bytes_out)

        # Wait for USB ACK or UPDATE NACK
        byte_in = read_byte()
        commandSuccess = (byte_in == RESP_USB_ACK)
    else:
        commandSuccess = True
    return commandSuccess

# Convert DPAD value to actual DPAD value used by Switch
def decrypt_dpad(dpad):
    if dpad == DIR_U:
        dpadDecrypt = A_DPAD_U
    elif dpad == DIR_R:
        dpadDecrypt = A_DPAD_R
    elif dpad == DIR_D:
        dpadDecrypt = A_DPAD_D
    elif dpad == DIR_L:
        dpadDecrypt = A_DPAD_L
    elif dpad == DIR_U_R:
        dpadDecrypt = A_DPAD_U_R
    elif dpad == DIR_U_L:
        dpadDecrypt = A_DPAD_U_L
    elif dpad == DIR_D_R:
        dpadDecrypt = A_DPAD_D_R
    elif dpad == DIR_D_L:
        dpadDecrypt = A_DPAD_D_L
    else:
        dpadDecrypt = A_DPAD_CENTER
    return dpadDecrypt

# Convert CMD to a packet
def cmd_to_packet(command):
    cmdCopy = command
    low              =  (cmdCopy & 0xFF)  ; cmdCopy = cmdCopy >>  8
    high             =  (cmdCopy & 0xFF)  ; cmdCopy = cmdCopy >>  8
    dpad             =  (cmdCopy & 0xFF)  ; cmdCopy = cmdCopy >>  8
    lstick_intensity =  (cmdCopy & 0xFF)  ; cmdCopy = cmdCopy >>  8
    lstick_angle     =  (cmdCopy & 0xFFF) ; cmdCopy = cmdCopy >> 12
    rstick_intensity =  (cmdCopy & 0xFF)  ; cmdCopy = cmdCopy >>  8
    rstick_angle     =  (cmdCopy & 0xFFF)
    dpad = decrypt_dpad(dpad)
    left_x, left_y   = angle(lstick_angle, lstick_intensity)
    right_x, right_y = angle(rstick_angle, rstick_intensity)

    packet = [high, low, dpad, left_x, left_y, right_x, right_y, 0x00]
    # print (hex(command), packet, lstick_angle, lstick_intensity, rstick_angle, rstick_intensity)
    return packet

# Send a formatted controller command to the MCU
def send_cmd(command=NO_INPUT):
    commandSuccess = send_packet(cmd_to_packet(command))
    return commandSuccess

# Force MCU to sync
def force_sync():
    # Send 9x 0xFF's to fully flush out buffer on device
    # Device will send back 0xFF (RESP_SYNC_START) when it is ready to sync
    write_bytes([0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])

    # Wait for serial data and read the last byte sent
    wait_for_data()
    byte_in = read_byte_latest()

    # Begin sync...
    inSync = False
    if byte_in == RESP_SYNC_START:
        write_byte(COMMAND_SYNC_1)
        byte_in = read_byte()
        if byte_in == RESP_SYNC_1:
            write_byte(COMMAND_SYNC_2)
            byte_in = read_byte()
            if byte_in == RESP_SYNC_OK:
                inSync = True
    return inSync

# Start MCU syncing process
def sync():
    inSync = False

    # Try sending a packet
    inSync = send_packet()
    if not inSync:
        # Not in sync: force resync and send a packet
        inSync = force_sync()
        if inSync:
            inSync = send_packet()
    return inSync



# -------------------------------------------- APP ---------------------------------------------------------
def translateCommand(command, time = 1):
    if command == 'a':
        send_cmd(BTN_A) ; p_wait(0.3) ; send_cmd() ; p_wait(0.5)
    elif command == 'b':
        send_cmd(BTN_B); p_wait(0.3) ; send_cmd() ; p_wait(0.5)
    elif command == 'menua':
        send_cmd(LSTICK_L) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER)
        send_cmd(LSTICK_R) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER)
        send_cmd(BTN_A)
    elif command == 'menub':
        send_cmd(LSTICK_L) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER)
        send_cmd(LSTICK_R) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER)
        send_cmd(BTN_B)
    elif command == 'u':
        send_cmd(LSTICK_U) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'r':
        send_cmd(LSTICK_R) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'rstep':
        send_cmd(LSTICK_R) ; p_wait(0.3) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'd':
        send_cmd(LSTICK_D) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'l':
        send_cmd(LSTICK_L) ; p_wait(0.1) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'lstep':
        send_cmd(LSTICK_L) ; p_wait(0.3) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'ustep':
        send_cmd(LSTICK_U) ; p_wait(0.3) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'moveup':
        send_cmd(LSTICK_U) ; p_wait(time) ; send_cmd(LSTICK_CENTER) ; p_wait(0.1)
    elif command == 'lsteps':
        send_cmd(LSTICK_L) ; p_wait(5) ; send_cmd(LSTICK_CENTER) ; p_wait(0.5)
    elif command == 'rsteps':
        send_cmd(LSTICK_R) ; p_wait(5) ; send_cmd(LSTICK_CENTER) ; p_wait(0.5)
    elif command == 'reset':
        send_cmd(LSTICK_R + RSTICK_R) ; p_wait(.2) ; send_cmd(LSTICK_CENTER + RSTICK_CENTER) ; p_wait(0.5)
    elif command == 'turnback':
        send_cmd(RSTICK_R) ; p_wait(2) ; send_cmd(RSTICK_CENTER) ; p_wait(0.5)
    elif command == 'quarterturn':
        send_cmd(RSTICK_R) ; p_wait(1) ; send_cmd(RSTICK_CENTER) ; p_wait(0.5)
    elif command == 'c':
        send_cmd(LSTICK_CENTER)
    elif command == 'R':
        send_cmd(BTN_R) ; p_wait(0.01)
    elif command == 'pc':
        send_cmd(BTN_R) ; p_wait(0.2); send_cmd() ; translateCommand('l')
    elif command == 'L':
        send_cmd(BTN_L)
    elif command == 'x':
        send_cmd(BTN_X); p_wait(0.3)  ; send_cmd() ; p_wait(0.5)
    elif command == 'y':
        send_cmd(BTN_Y); p_wait(0.3)  ; send_cmd() ; p_wait(0.5)
    elif command == 'min':
        send_cmd(BTN_MINUS); p_wait(0.3)  ; send_cmd() ; p_wait(0.001)
    elif command == 'tr':
        send_cmd(LSTICK_U_R) ; p_wait(0.05) ; send_cmd(LSTICK_CENTER)
    elif command == 'cycle':
        send_cmd(LSTICK_R + RSTICK_R) ; p_wait(time); send_cmd(LSTICK_CENTER + RSTICK_CENTER)
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
                cmd = lstick_angle(i + 90, 0xFF)
                send_cmd(cmd)
                p_wait(0.001)
            loops = loops - 1
        send_cmd(LSTICK_CENTER) ; p_wait(0.5)
    elif command == 'eggs':
        eggs()
    elif command == 'hatch':
        hatch()
    elif command == 'eggs_bike':
        eggs_bike()
    elif command == 'pnh':
        pickNHatch()
    elif command == 'test':
        testCommands()

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
    print('How many boxes to hatch ? :')
    boxes = int(input())
    print('Bike loops (7 = 5500 steps) :')
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
def release_pokemons(projectedRelease = ''):
    if(not projectedRelease):
        print('How many boxes to release ?')
        projectedRelease = int(input())

    start_time = time.time()
    releasedPkm = 0
    # projectedRelease = boxes * 30
    p_wait(1)
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
# Get eggs from the daycare
#   - Must have 6 pkm in the team
#   - Bike off
#   - Cursor's menu over the map
###
def eggs(projectedEggs = ''):
    if(not projectedEggs):
        print('How many eggs to pick ?')
        projectedEggs = int(input())

    start_time = time.time()
    translateCommand('lstep')
    translateCommand('lstep')
    p_wait(.4)
    eggs = 0
    while eggs < projectedEggs:
        eggs_bike() 
        print('Opening menu')          
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
        print('Opening map')          
        p_wait(2)
        translateCommand('tr')
        p_wait(.5)
        translateCommand('a')
        p_wait(.5)
        translateCommand('menua')
        print('Flying')          
        #envol
        p_wait(3)
        translateCommand('min')
        p_wait(.4)
        translateCommand('lstep')
        p_wait(.5)
        translateCommand('lstep')
        p_wait(.5)
        translateCommand('ustep')
        print('Picking egg')          
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
        print('eggs picked : ')
        print(eggs)
    
    elapsed_time = time.time() - start_time
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

def pickNHatch(projectedEggs = '', cycles = ''):
    if(not projectedEggs):
        print('How many eggs to pick ?')
        projectedEggs = int(input())
    if(not cycles):    
        print('How many cycles ? (look on bulbapedia)')
        cycles = int(input())

    timeToCycle = (cycles * 3.3) + 5
    start_time = time.time()
    hatched = 0

    while(hatched != projectedEggs):
        print('Bike step')
        # turn back
        translateCommand('turnback')
        p_wait(.2)
        translateCommand('u')
        p_wait(.2)

        # bike 
        translateCommand('min')
        p_wait(.2)
        translateCommand('moveup', 1)
        p_wait(.2)
        
        translateCommand('quarterturn')
        p_wait(.2)

        # loop with bike
        translateCommand('moveup', 2)
        p_wait(.2)
        translateCommand('cycle', timeToCycle)

        print('Egg hatching')
        p_wait(1)
        translateCommand('b')
        p_wait(16)
        translateCommand('b')
        p_wait(2)

        # bike off
        translateCommand('min')
        p_wait(.5)
        translateCommand('x')
        p_wait(1.3)

        translateCommand('a')
        print('Opening map')          
        p_wait(2.5)
        translateCommand('a')
        p_wait(.5)
        translateCommand('menua')
        p_wait(3)


        print('move to daycare')
        translateCommand('turnback')
        p_wait(.2)
        translateCommand('rstep')
        p_wait(.2)
        translateCommand('moveup', 0.8)


        print('Pick the next egg')
        translateCommand('a')
        p_wait(1)
        translateCommand('a')
        p_wait(4)
        translateCommand('a')
        p_wait(2)
        translateCommand('a')
        p_wait(.5)
        translateCommand('a')
        p_wait(2)
        translateCommand('d')
        p_wait(.2)
        translateCommand('a')
        p_wait(2.8)
        translateCommand('a')
        p_wait(1.5)
        translateCommand('a')
        p_wait(1)
        hatched = hatched +1
        print('eggs picked : ')
        print(hatched)
    
    elapsed_time = time.time() - start_time
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


# def testCommands():
    #commands to test


# -------------------------------------------------------------------------

# ser = serial.Serial(port=args.port, baudrate=57600,timeout=1)
ser = serial.Serial(port=args.port, baudrate=19200,timeout=1)
# ser = serial.Serial(port=args.port, baudrate=31250,timeout=1)
# ser = serial.Serial(port=args.port, baudrate=40000,timeout=1)
# ser = serial.Serial(port=args.port, baudrate=62500,timeout=1)

# Attempt to sync with the MCU
if not sync():
    print('Could not sync!')


p_wait(0.05)

if not send_cmd():
    print('Packet Error!')

if(args.command == 'pnh'):
    pickNHatch(int(args.eggs), int(args.cycles))

if(args.command == 'stop'):
    translateCommand('reset')

if(args.command == 'release'):
    release_pokemons(args.eggs)

if(not args.command):
    while True:
        print('Command : ')
        command = input()
        translateCommand(command)
    
ser.close

