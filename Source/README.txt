-------------
General Stuff
-------------

First off, what is 1337ris? In a nutshell, 1337ris is a unique, multi-mode spin-off of Alexey Pajitnov's legendary game Tetris. In addition to normal Tetris-style gameplay, 1337ris introduces "bombs" and "dynamite," as well as three different playing modes, each with their own odd twist. (Yes, that was almost directly copied and pasted from 1337ris's About screen.)

To run 1337ris, go into the command line, change the working directory to this folder, type "python 1337ris.py", and press Return. The game window should pop up shortly thereafter.

In order to be able to run 1337ris, you will need to have Python (http://www.python.org) and pygame (http://www.pygame.org) installed.

There are also exectuable versions of 1337ris for Windows and Mac OS X available on my UW student website (http://students.washington.edu/htwcoder/1337ris/). With these, anyone can run 1337ris, even if they don't have Python or pygame installed. (For anyone who's curious, I made these with py2exe and py2app, respectively.)

This is version 2.0 of 1337ris. As stated in the About screen, the original version was an unfinished Java game I made a few years ago. The basic concept, look, and feel are the same, but this new Python version is much more polished and refined, and everything actually works. I still have the original 1.0 Java version of 1337ris -- you can download it at http://students.washington.edu/htwcoder/1337ris/original/.

------------
Sound Issues
------------

On certain systems (including mine), pygame seems to have a bug where streaming music may "distort" slightly once it starts looping. This completely out of my control -- like I said, it seems to be a pygame bug. If you're *really* annoyed by it, you can turn off the Streaming Music option in Settings (that's basically what it's there for).

------------------------
Cross-Cut Clarifications
------------------------

The in-game help is supposed to be concise and direct, but if you're still confused about this mode, I'll do my best to clarify some of the potentially confusing aspects.

Basically the main difference between this and the other modes is how the tetrominoes are placed. In all the other modes, the tetrominoes fall from the top of the playing field. However, in Cross-Cut, tetrominoes *don't* fall. Instead, they start out in the middle, and you are supposed to move them around. Of course, you have a time limit: initially, you have 10 seconds to place, but with each level, that time limit gets shorter and shorter. (The tetromino glows more and more white as the remaining time diminishes.) Once that time limit expires, the tetromino locks in place -- no matter where it is. You could leave it hanging on the top of the screen, and once the time limit expires, then that's where it goes. You could stick it on the side of the screen, in the middle of the field -- you can stick it anywhere, as long as it doesn't collide with other previously placed blocks.

Remember drop/speedup? In the other game modes, if you don't want to wait for the tetromino to fall on its own, you can either speed up its fall or just drop it entirely, right? Well, Cross-Cut doesn't have exactly that, but it has something similar. If your tetromino collides with the top of the screen, the bottom of the screen, or another block already on the playing field, it will automatically lock in that position. What exactly do I mean by "collide"? Basically, if your tetromino is *next* to the top/bottom or another block, you're fine. But if you move it in that direction again (i.e., the tetromino would either overlap or go out of bounds), then your tetromino locks, since it is unable to move in that direction. HOWEVER, you can still run into the sides of the playing field without worrying about automatic locking -- that would make the game just too difficult. :)

Also, one added dimension of Cross-Cut is that, while in the other game modes, you can only move horizontally, in Cross-Cut, you can now move vertically. How? The speedup key (down arrow by default) moves down, while the drop key (space by default) moves up. Now, speedup makes sense, since that's, in effect, almost like a "move down" key in the other versions. But why drop? Well, here's the thing. First of all, you can't really "drop" in Cross-Cut, as I already said. But the main thing is that the up arrow key (which is more intuitive) maps to Rotate by default. Now, I thought about changing this, but see, you can rotate in Cross-Cut too. What about making a new control for moving up in Cross-Cut mode? I also thought about that, but that was also flawed, mainly because I found that most people I knew expected rotate to be the Up key (which is why I made it the default key). So what other key would make sense for moving up? I can't think of any good solution, so using the drop key was kind of a compromise. However, if I (or someone else) comes up with something, it'll probably go in the next release.

-------------
And Lastly...
-------------

Oh yeah, if you find a bug, feel free to email me: htwcoder@u.washington.edu. Just remember, if you find a bug, it's best if you can clearly reproduce it, and then tell me those steps, so I can see the bug for myself. If an error message prints out or something, include that too.


Hope you enjoy 1337ris!