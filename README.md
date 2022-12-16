# arturia minilab mkii step sequencer — v0.3

---------------------------------------------------------------------------------------------------------------------------

QUICK NOTE: 
I feel as though the more i add to this project, the more libraries I'm adding and the messier everything is getting (to be expected! this is an extension of the very first program I ever wrote! the fact that it still works and can be built upon (in a loose sense of the phrase) at all is remarkable). rather than continuing to patch over a lot of this stuff, I think I'm going to be completely rewriting this program in Java, since any GUI I create will be much less fussy and I can just use the standard library for most if not all of what I need. follow development here : https://github.com/sqrtM/MkiiStepSequencer_JavaEdition


-----------------------------------------------------------------------------------------------------------------------------

i really like my minilab (the pads are a little fussy and the cc controls have the strangest velocity settings ive ever seen in my life, but still). its just that i never understood, with all of its weird and useless built in features, why it didn't have any kind of sequencer or scheduling. seemed like a no-brainer kind of thing to me. would be extremely useful for doing live-coding/live visuals stuff and would add basically no bloat to the machine. but since the minilab doesn't have anything like that i figured id try and build the functionality myself

this is a rudimentary, proof-of-concept standalone version of the script i built for BespokeSynth which allowed you to use the pads of the arturia mkii minilab as a step sequencer with up to 64* pads.

this standalone executable aims to do the same thing, but divorced from BespokeSynth, using rtmidi and mido libraries to create the midi objects and python-osc to push signals out. i am also using the rich library to draw pretty things to the console.

~~at the moment, this is a purely data/visual trick — the pads are held in memory as a specific sequence of 0s, 1s, and 2s (which you can view in the console), but I have not yet built the capacity to send that data out to another program (as i did with the bespoke synth version with sonic pi osc integration).~~

presently, this sequencer creates and sends signals, organized by signal bank. the next step is to send them asyncronously and at different tempos, ideally giving a similiar functionality to a more complex, dedicated hardware step sequencer.

for now, this is just mostly just a toy, but it's my first working standalone .exe file, and that was really the goal here.

![image](https://user-images.githubusercontent.com/79169638/201188439-1bbfc3b3-92f9-48df-a266-18f98cd5683b.png)

# how to use

just download the main.exe file and start it up. you can test this even if you don't have an mkii lying around ; this will still run in console so long as there is at least ONE valid in and ONE valid out MIDI port.

if you do want to use this with your mkii:
I HIGHLY RECOMMEND SETTING YOUR PAD LIGHTS TO TOGGLE RATHER THAN GATE. 
i dont know of a way to have the program anticipate that and the way that the minilab mkii handles "note_off" signals makes working with pads set to "GATE" really weird since it instantly sends a signal to turn off the pad once you stop pressing it. so, if you do play around with this, please set pads to TOGGLE in the MIDI Control Center software which comes bundled with the minilab.

# known issues i am looking to fix

*if you set the pads to 16, it crashes. this is because second dimension of the memory becomes empty and never recieves a value, despite expecting one. i'll fix this. everything from 4-15 works just fine.

~~i have this set to where it reads input 1 and output 0 for the mkii. this SHOULD work for basically any setup trying out this demo, but I'm certain this will cause problems in the future, and for the next version i'm going to just have it iterate through inputs and output until it finds "mkii" and then pick that one.~~ (this is now a tkinter menu)

I am currently working on ~~two~~ interrelated things: ~~getting a visualizer set up, and~~ allowing the signals to move asyncronously. these are both important because, 1.) the user needs to be able to see HOW the signals interrelate rhythmically, and 2.) because a visualized UI allows for greater control over the signals. I spent a lot of time putting this together in tkinter, and it worked like a charm (!) except the performance was horrifically bad (!) because tkinter isn't really made to do lots of updates like that, ~~so I'm instead getting this set up to where it is visualized in the console using a library like Rich. one I can realiably draw everything to the screen, I'll start exporting the signals asyncronously.~~

the visualizer now works pretty well and updates as you change your settings. neat!

but for now, this does work as a rudimentary step sequencer, so long as you are happy with all of your banks being at the same tempo. not very useful at the moment!, but can be useful for things like livecoding and toggling visuals, which is something I do a lot of. so if you're also into that, maybe you can find some use in this early build.

other than that, i hope you enjoy. i know some people had been asking for this and i hope this gets you interested in what else could possibly be done using the mkii and various sysex objects.

thanks!
