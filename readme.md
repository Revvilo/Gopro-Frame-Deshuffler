WIP

Sick of this Hero 7 messing up my footage.

At some stage this script will brute-force the deshuffling pattern by running ffmpeg on every permutation of a sequence of frames, incrementing the length of the block of frames it tries to deshuffle with each pass.

Buy a new Gopro man, it's not worth it. Unless it is. I don't judge. This program might save you :D

MY USE NOTES:
Always start attempt with sequence: 10342 and using the MPV precise timestamp and counting each frame which changes after the initial freeze; use the 4th frame's timestamp and add 1ms. (Eg; 00:02:36.723 becomes 00:02:36.724)
I wrote this program to brute-force the required sequence, but with my GoPro it looks to be the same every time. I found the sequence using Resolve and saving each frame into the media pool under their sequence number and reshuffling them on the timeline and reverse engineering the sequence like that.