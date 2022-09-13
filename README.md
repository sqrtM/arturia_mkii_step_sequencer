# arturia_mkii_step_sequencer — v0.1

i really like my minilab (the pads are a little fussy and the cc controls have the strangest velocity settings ive ever seen in my life, but still). its just that i never understood, with all of its weird and useless built in features, why it didn't have any kind of sequencer or scheduling. seemed like a no-brainer kind of thing to me. would be extremely useful for doing live-coding/live visuals stuff and would add basically no bloat to the machine. but since the minilab doesn't have anything like that i figured id try and build the functionality myself

this is a rudimentary, proof-of-concept standalone version of the script i built for BespokeSynth which allowed you to use the pads of the arturia mkii minilab as a step sequencer with up to 64 pads.

this standalone executable aims to do the same thing, but divorced from BespokeSynth, using rtmidi and mido libraries to create the midi objects.

at the moment, this is a purely data/visual trick — the pads are held in memory as a specific sequence of 0s, 1s, and 2s (which you can view in the console), but I have not yet built the capacity to send that data out to another program (as i did with the bespoke synth version with sonic pi osc integration).

for now, this is just a toy, but it's my first working standalone .exe file, so that was really the goal here.

# how to use

just download the repo and inside of the dist folder there is a "main.exe" file. before you run it, make sure your mkii minilab is plugged into the computer.

I HIGHLY RECOMMEND SETTING YOUR PAD LIGHTS TO TOGGLE RATHER THAN GATE. 
i dont know of a way to have the program anticipate that and the way that the minilab mkii handles "note_off" signals makes working with pads set to "GATE" really weird since it instantly sends a signal to turn off the pad once you stop pressing it. so, if you do play around with this, please set pads to TOGGLE in the MIDI Control Center software which comes bundled with the minilab.

the dist folder seems rather bloated, which seems unnecessary since i went into this project with the goal of using the bare minimum amount of external modules/functions etc.. im going to see what i can do to fix that.


# known issues i am looking to fix

if you set the pads to 16, it crashes. this is because second dimension of the memory becomes empty and never recieves a value, despite expecting one. i'll fix this.

i have this set to where it reads input 1 and output 0 for the mkii. this SHOULD work for basically any setup trying out this demo, but I'm certain this will cause problems in the future, and for the next version i'm going to just have it iterate through inputs and output until it finds "mkii" and then pick that one. 

other than that, i hope you enjoy. i know some people had been asking for this and i hope this gets you interested in what else could possibly be done using the mkii and various sysex objects.

thanks!
