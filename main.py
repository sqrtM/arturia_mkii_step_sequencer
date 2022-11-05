import mido
import time

from tkinter import *
from tkinter import messagebox

import threading as threading

from pythonosc.udp_client import SimpleUDPClient
ip = "127.0.0.1"
port = 1337
client = SimpleUDPClient(ip, port)



hexoffset = 112 
# arturia minilab mkii pad addresses
# begin at 0x70, or 112 in dec, so we need to add that
# amount to any address we produce in script

noteoffset = 36  
# bespoke reads the lowest pad on the mkii as note 36 by default
# if you have changed your settings for your minilab mkii, this 
# may not be the case, and if you are having problems getting the
# sequencer to run as intended, this is the most likely problem.

   
# this number, c_length (cycle length), is how many pads
# you would like the sequencer to use, between 2 and 16

c_length = 8

# any pads not used will automatically
# become membank switchers

membanks = 16 - c_length
# this variable will be used by the script to figure out
# how many pads are not being used, and turn them into
# bank switchers

padmem = [[int(0)] * c_length for _ in range(membanks)]
# this is our 2D "memory" array which keeps track of the status of each pad.
# the list will auto populate with zeroes equal to the number of pads
# we entered into c_length. the numbers will be initiallized as 0, signifying "off",
# but become 1 when an "off" pad is on the current subdivision, and 2 when a pad
# is toggled as an active sequencer.

active_mem = 0
# active_mem is the 1D memory line you are currently looking at
# this is switched with the bank switchers, if c_length is less than 15.

# these values designate the colors for
# when the pad is "on", "off", "seqon", 
# "seqoff", and the bank switches.

colorNone   = 0x00
colorRed    = 0x01
colorGreen  = 0x04
colorYellow = 0x05
colorBlue   = 0x10
colorCyan   = 0x14
colorPurple = 0x11
colorWhite  = 0x7F

offcolor  = colorCyan
oncolor   = colorPurple
seqon     = colorWhite
seqoff    = colorGreen
bankcolor = colorBlue
# for best results : in the Arturia MIDI Control Center:
# 1. set all your pads to TOGGLE, not GATE
# 2. set PAD OFF BACKLIGHT to OFF, and
# 3. set each pad color to be the same as the "seqoff" color.

sysmsg = [0x00, 0x20, 0x6B, 0x7F, 0x42, 0x02, 0x00, 0x10, 0x70, 0x14]
# this list is the system exclusive message which will
# be sent to the keyboard. the first 8 instructions are more or
# less generic and not important for what we will be doing. the
# last two are pad address and color respectively.

#########################################################################################################
# ________   _______    ________   ___  ___   _______    ________    ________   _______    ________     #
#|\   ____\ |\  ___ \  |\   __  \ |\  \|\  \ |\  ___ \  |\   ___  \ |\   ____\ |\  ___ \  |\   __  \    #
#\ \  \___|_\ \   __/| \ \  \|\  \\ \  \\\  \\ \   __/| \ \  \\ \  \\ \  \___| \ \   __/| \ \  \|\  \   #
# \ \_____  \\ \  \_|/__\ \  \\\  \\ \  \\\  \\ \  \_|/__\ \  \\ \  \\ \  \     \ \  \_|/__\ \   _  _\  #
#  \|____|\  \\ \  \_|\ \\ \  \\\  \\ \  \\\  \\ \  \_|\ \\ \  \\ \  \\ \  \____ \ \  \_|\ \\ \  \\  \| #
#    ____\_\  \\ \_______\\ \_____  \\ \_______\\ \_______\\ \__\\ \__\\ \_______\\ \_______\\ \__\\ _\ #
#   |\_________\\|_______| \|___| \__\\|_______| \|_______| \|__| \|__| \|_______| \|_______| \|__|\|__|#
#   \|_________|                 \|__|                                                                  #
#########################################################################################################

def on_note(incoming_midi):
    global active_mem
    if incoming_midi.type == "sysex":
        refresh()
        
    # first check to see if the incoming message is one of the pads.
    
    # it might be a good idea to allow the user to change some of these,
    # but unless they've tampered heavily with the mkii default settings
    # it shouldn't really present much of a problem.
    elif ((incoming_midi.channel == 9 and incoming_midi.note >= 36 and 
           incoming_midi.type != "polytouch") and
          (incoming_midi.type == "note_on" or "note_off") and 
          (incoming_midi.note >= c_length + noteoffset)):
                for x in range(membanks):
                    if x <= membanks:
                        sysmsg[-2] = 16 - membanks + hexoffset + x
                        sysmsg[-1] = colorNone  
                        outgoing_sysex = mido.Message('sysex', data=sysmsg)
                        outport.send(outgoing_sysex)  
                active_mem = incoming_midi.note - noteoffset - c_length
                sysmsg[-2] = hexoffset + incoming_midi.note - noteoffset
                sysmsg[-1] = bankcolor  
                outgoing_sysex = mido.Message('sysex', data= sysmsg)
                outport.send(outgoing_sysex) 
                refresh()
                return padmem, active_mem
            
    # note is within the c-length range
    elif noteoffset <= incoming_midi.note < c_length + noteoffset:
        #it was already on, so turn it off
        if padmem[active_mem][incoming_midi.note - noteoffset] == 2:   
            padmem[active_mem][incoming_midi.note - noteoffset] = 0
            sysmsg[-2] = 0x70 + incoming_midi.note - noteoffset
            sysmsg[-1] = offcolor  
            outgoing_sysex = mido.Message('sysex', data= sysmsg)
            outport.send(outgoing_sysex)
            return padmem
        # it was not already on, so turn it on
        else:
            sysmsg[-2] = 0x70 + incoming_midi.note - noteoffset
            sysmsg[-1] = seqoff 
            padmem[active_mem][incoming_midi.note - noteoffset] = 2
            outgoing_sysex = mido.Message('sysex', data= sysmsg)
            outport.send(outgoing_sysex)
            return padmem


def refresh():
    for x in range(16 - c_length):
        if x <= membanks:
            sysmsg[-2] = 16 - membanks + hexoffset + x
            sysmsg[-1] = 0x00
            outgoing_sysex = mido.Message('sysex', data= sysmsg)
            outport.send(outgoing_sysex)
 
    for i in range(membanks):
        for j in range(c_length):
            if padmem[i][j] == 1:
                padmem[i][j] = 0
                            
    sysmsg[-2] = active_mem + c_length + hexoffset
    sysmsg[-1] = bankcolor
    outgoing_sysex = mido.Message('sysex', data= sysmsg)
    outport.send(outgoing_sysex)
    tick(beat)
    print("refreshed!", padmem)

# this initializes the lights for the bank switches
# so they actually reflect the correct initial bank

############################################

beat = 0
KILLSWITCH = True

# main loop. called onButtonPress
def loop():
    global beat
    while KILLSWITCH == True:
        tick(beat)
        if beat < c_length - 1:
            beat += 1
        else:
            beat = 0
        # TEMPO. WE WILL MAKE 
        # THIS ACTUALLY USEFUL SOON
        time.sleep(0.5)

def create_binary_signal(arr):
    newarr = arr
    for nestedarr in newarr:
        for member in nestedarr:
            if member > 1:
                member = "1"
            else: 
                member = "0"
    return newarr

# tick keeps track of what all the lights are doing
def tick(beat):
    global active_mem
    client.send_message(f"/mkii_seq/{active_mem}", str(padmem)) 
    hit = beat
    lastpos = hit - 1
    if lastpos < 0:
        lastpos = c_length - 1  
      
    seqpos = hexoffset + hit
    hexseqpos = int(hex(seqpos), 16)
    oldhexpos = hexseqpos - 1
    if oldhexpos == 111:                      #when it reaches the last pad...
        oldhexpos = hexoffset + c_length - 1  #clear it and restart at pad0

    for pad in range(c_length):
        if padmem[active_mem][pad] == 0:
            paddec = pad + hexoffset
            padhex = int(hex(paddec), 16)
            sysmsg[-2] = padhex
            sysmsg[-1] = offcolor
            outgoing_sysex = mido.Message('sysex', data= sysmsg)
            outport.send(outgoing_sysex)
            refresh_visuals()

            
        if padmem[active_mem][pad] == 1 & padmem[active_mem][hit] != 1:
            paddec = pad + hexoffset
            padhex = int(hex(paddec), 16)
            padmem[active_mem][pad] = 0
            sysmsg[-2] = padhex
            sysmsg[-1] = offcolor
            outgoing_sysex = mido.Message('sysex', data= sysmsg)
            outport.send(outgoing_sysex)
            refresh_visuals()

                
        if padmem[active_mem][pad] == 2:
            paddec = pad + hexoffset
            padhex = int(hex(paddec), 16)
            sysmsg[-2] = padhex
            sysmsg[-1] = seqoff
            outgoing_sysex = mido.Message('sysex', data= sysmsg)
            outport.send(outgoing_sysex)   
            refresh_visuals()
    
    
    # reads the status of the pads and
    # sends the color to the controller
    if padmem[active_mem][hit] == 2:
        sysmsg[-2] = hexseqpos
        sysmsg[-1] = seqon
        outgoing_sysex = mido.Message('sysex', data= sysmsg)
        outport.send(outgoing_sysex)  
        refresh_visuals()
        
    else:
        padmem[active_mem][hit] = 1 
        sysmsg[-2] = hexseqpos   
        sysmsg[-1] = oncolor
        outgoing_sysex = mido.Message('sysex', data= sysmsg)
        outport.send(outgoing_sysex)  
        refresh_visuals()
    
    if padmem[active_mem][lastpos] == 2:
        sysmsg[-2] = hexseqpos           # genuinely no idea why this works
        sysmsg[-1] = oncolor             # i mean, shouldn't these first two
        sysmsg[-2] = oldhexpos           # sysmsg things do nothing ? but the
        sysmsg[-1] = seqoff              # script doesn't work w/o them....
        outgoing_sysex = mido.Message('sysex', data= sysmsg)
        outport.send(outgoing_sysex)  
        refresh_visuals()
    else:
        padmem[active_mem][lastpos] = 0
        sysmsg[-2] = oldhexpos
        sysmsg[-1] = offcolor
        outgoing_sysex = mido.Message('sysex', data= sysmsg)
        outport.send(outgoing_sysex) 
        refresh_visuals() 
    
###########################################
#   ________      ___  ___      ___       #
#  |\   ____\    |\  \|\  \    |\  \      #
#  \ \  \___|    \ \  \\\  \   \ \  \     #
#   \ \  \  ___   \ \  \\\  \   \ \  \    #
#    \ \  \|\  \   \ \  \\\  \   \ \  \   #
#     \ \_______\   \ \_______\   \ \__\  #
#      \|_______|    \|_______|    \|__|  #
#                                         #
###########################################

ws = Tk()
ws.title("MKII SEQUENCER")
ws.geometry('470x470')

frame1 = LabelFrame(ws, text='Default')
frame1.grid(row=1, column=1, padx=5)

frame2 = LabelFrame(ws, text='Beat')
frame2.grid(row=1, column=2, padx=5)

frame3 = LabelFrame(ws, text='Sequencing')
frame3.grid(row=1, column=3, padx=5)

frame4 = LabelFrame(ws, text='Active')
frame4.grid(row=1, column=4, padx=5)

frame5 = LabelFrame(ws, text='Bank')
frame5.grid(row=1, column=5, padx=5)

frame6 = LabelFrame(ws, text='Pads Used')
frame6.grid(row=1, column=6, padx=5)

looping = 0

def onButtonPress():
    
    global offcolor 
    global oncolor  
    global seqon    
    global seqoff   
    global bankcolor
    
    radio_1 = group_1.get()
    if radio_1 == 0:
        return messagebox.showinfo("error",'please select an option for each selection')
    if radio_1 == 1: 
        offcolor = colorNone
    if radio_1 == 2: 
        offcolor = colorRed
    if radio_1 == 3: 
        offcolor = colorGreen
    if radio_1 == 4: 
        offcolor = colorYellow
    if radio_1 == 5: 
        offcolor = colorBlue
    if radio_1 == 6: 
        offcolor = colorCyan
    if radio_1 == 7: 
        offcolor = colorPurple
    if radio_1 == 8: 
        offcolor = colorWhite
        
        
    radio_2 = group_2.get()
    if radio_2 == 0:
        return messagebox.showinfo("error",'please select an option for each selection')
    if radio_2 == 1: 
        oncolor = colorNone
    if radio_2 == 2: 
        oncolor = colorRed
    if radio_2 == 3: 
        oncolor = colorGreen
    if radio_2 == 4: 
        oncolor = colorYellow
    if radio_2 == 5: 
        oncolor = colorBlue
    if radio_2 == 6: 
        oncolor = colorCyan
    if radio_2 == 7: 
        oncolor = colorPurple
    if radio_2 == 8: 
        oncolor = colorWhite
        
        
    radio_3 = group_3.get()
    if radio_3 == 0:
        return messagebox.showinfo("error",'please select an option for each selection')
    if radio_3 == 1: 
        seqon = colorNone
    if radio_3 == 2: 
        seqon = colorRed
    if radio_3 == 3: 
        seqon = colorGreen
    if radio_3 == 4: 
        seqon = colorYellow
    if radio_3 == 5: 
        seqon = colorBlue
    if radio_3 == 6: 
        seqon = colorCyan
    if radio_3 == 7: 
        seqon = colorPurple
    if radio_3 == 8: 
        seqon = colorWhite
        
        
    radio_4 = group_4.get()
    if radio_4 == 0:
        return messagebox.showinfo("error",'please select an option for each selection')
    if radio_4 == 1: 
        seqoff = colorNone
    if radio_4 == 2: 
        seqoff = colorRed
    if radio_4 == 3: 
        seqoff = colorGreen
    if radio_4 == 4: 
        seqoff = colorYellow
    if radio_4 == 5: 
        seqoff = colorBlue
    if radio_4 == 6: 
        seqoff = colorCyan
    if radio_4 == 7: 
        seqoff = colorPurple
    if radio_4 == 8: 
        seqoff = colorWhite
        
        
    radio_5 = group_5.get()
    if radio_5 == 0:
        return messagebox.showinfo("error",'please select an option for each selection')
    if radio_5 == 1: 
        bankcolor = colorNone
    if radio_5 == 2: 
        bankcolor = colorRed
    if radio_5 == 3: 
        bankcolor = colorGreen
    if radio_5 == 4: 
        bankcolor = colorYellow
    if radio_5 == 5: 
        bankcolor = colorBlue
    if radio_5 == 6: 
        bankcolor = colorCyan
    if radio_5 == 7: 
        bankcolor = colorPurple
    if radio_5 == 8: 
        bankcolor = colorWhite
        
    radio_6 = group_6.get() + 3
    if radio_6 == 3:
        return messagebox.showinfo("error",'please select an option for each selection')

    global active_mem
    global c_length
    global membanks
    global padmem
    global beat
    
    active_mem = 0
    c_length = radio_6
    membanks = 16 - c_length
    padmem = [[int(0)] * c_length for _ in range(membanks)]
    beat = 0
    
    refresh()
    
    global looping 
    global KILLSWITCH
    if looping == 0:
        looping = 1
        KILLSWITCH = True
        threading.Thread(target=loop).start()
        
def onSilence():
    global KILLSWITCH
    global looping
    KILLSWITCH = False
    looping = 0
    refresh()
    return
        
group_1 = IntVar(value=6)
group_2 = IntVar(value=7)
group_3 = IntVar(value=8) 
group_4 = IntVar(value=3) 
group_5 = IntVar(value=5) 
group_6 = IntVar(value=5) 

# offcolor
Radiobutton(frame1, text='None', variable=group_1, value=1).pack()
Radiobutton(frame1, text='Red', variable=group_1, value=2).pack()
Radiobutton(frame1, text='Green', variable=group_1, value=3).pack()
Radiobutton(frame1, text='Yellow', variable=group_1, value=4).pack()
Radiobutton(frame1, text='Blue', variable=group_1, value=5).pack()
Radiobutton(frame1, text='Cyan', variable=group_1, value=6).pack()
Radiobutton(frame1, text='Purple', variable=group_1, value=7).pack()
Radiobutton(frame1, text='White', variable=group_1, value=8).pack()

# oncolor
Radiobutton(frame2, text='None', variable=group_2, value=1).pack()
Radiobutton(frame2, text='Red', variable=group_2, value=2).pack()
Radiobutton(frame2, text='Green', variable=group_2, value=3).pack()
Radiobutton(frame2, text='Yellow', variable=group_2, value=4).pack()
Radiobutton(frame2, text='Blue', variable=group_2, value=5).pack()
Radiobutton(frame2, text='Cyan', variable=group_2, value=6).pack()
Radiobutton(frame2, text='Purple', variable=group_2, value=7).pack()
Radiobutton(frame2, text='White', variable=group_2, value=8).pack()

# seqon
Radiobutton(frame3, text='None', variable=group_3, value=1).pack()
Radiobutton(frame3, text='Red', variable=group_3, value=2).pack()
Radiobutton(frame3, text='Green', variable=group_3, value=3).pack()
Radiobutton(frame3, text='Yellow', variable=group_3, value=4).pack()
Radiobutton(frame3, text='Blue', variable=group_3, value=5).pack()
Radiobutton(frame3, text='Cyan', variable=group_3, value=6).pack()
Radiobutton(frame3, text='Purple', variable=group_3, value=7).pack()
Radiobutton(frame3, text='White', variable=group_3, value=8).pack()

# seqoff
Radiobutton(frame4, text='None', variable=group_4, value=1).pack()
Radiobutton(frame4, text='Red', variable=group_4, value=2).pack()
Radiobutton(frame4, text='Green', variable=group_4, value=3).pack()
Radiobutton(frame4, text='Yellow', variable=group_4, value=4).pack()
Radiobutton(frame4, text='Blue', variable=group_4, value=5).pack()
Radiobutton(frame4, text='Cyan', variable=group_4, value=6).pack()
Radiobutton(frame4, text='Purple', variable=group_4, value=7).pack()
Radiobutton(frame4, text='White', variable=group_4, value=8).pack()

# bank
Radiobutton(frame5, text='None', variable=group_5, value=1).pack()
Radiobutton(frame5, text='Red', variable=group_5, value=2).pack()
Radiobutton(frame5, text='Green', variable=group_5, value=3).pack()
Radiobutton(frame5, text='Yellow', variable=group_5, value=4).pack()
Radiobutton(frame5, text='Blue', variable=group_5, value=5).pack()
Radiobutton(frame5, text='Cyan', variable=group_5, value=6).pack()
Radiobutton(frame5, text='Purple', variable=group_5, value=7).pack()
Radiobutton(frame5, text='White', variable=group_5, value=8).pack()

for x in range (1,14):
    Radiobutton(frame6, text=x+3, variable=group_6, value=x).pack()
    
selected_midi_input = StringVar(value = mido.get_input_names()[0] )
selected_midi_output = StringVar(value = mido.get_output_names()[1] )
miditarget = StringVar(value = mido.get_output_names()[0] )
 
ddin = OptionMenu(ws, selected_midi_input, *mido.get_input_names())
ddin.grid(row=2, column=1, columnspan=3)

ddout = OptionMenu(ws, selected_midi_output, *mido.get_output_names())
ddout.grid(row=3, column=1, columnspan=3)

miditarget = OptionMenu(ws, miditarget, *mido.get_output_names())
miditarget.grid(row=4, column=1, columnspan=3)

btn = Button(ws, text = 'Start', bd = '10', command = onButtonPress)
btn.grid(row=3, column=4)

btn = Button(ws, text = 'Silence', bd = '10', command = onSilence)
btn.grid(row=3, column=5)

outport = mido.open_output(selected_midi_output.get())
inport = mido.open_input(selected_midi_input.get(), callback=on_note)

def get_bg(int):
    match (int):
        case 0:
            return 'cyan'
        case 1:
            return 'pink'
        case 2: 
            return 'light green'
        

def refresh_visuals():
    for i, _ in enumerate(padmem):
        for j, _ in enumerate(padmem[i]):
            Label(ws, text='@', padx=4, background=get_bg(padmem[i][j])).grid(row=i + 6, column=j + 7)


if __name__ == '__main__':
    ws.mainloop()