Preface
=======

(Originally, 1337ris was a Java game I wrote in high school. This is a Python rewrite I did back in the fall of 2008. The following notes were taken from the webpage I used to maintain for this game.)

The idea for this came up while I was taking the introductory computer programming class at UW. One of the great things about 142 was that they offered an extra option to learn Python in addition to Java. Anyways, toward the end of the quarter, they introduced to us a game programming library called Pygame, and, lo and behold, our final "assignment" was to create our own game in Python using Pygame. I had been doing game projects on my own as a hobby for several years, so I jumped at the opportunity to make a game with Pygame.

As for what game I decided to make, well, I realized that 1337ris would be a perfect game for Pygame, so I quickly got to work porting the Java version to Python. And after about a month of designing, coding, and debugging, 1337ris 2.0 was born.

Oddly enough, in the end, there wasn't much actual "porting" involved, as I found that, when I had finished 1337ris, I had spent more time redesigning and writing new code. The game itself was a lot more polished than its original Java counterpart was—all of the game modes were actually finished, the game had snazzy screen effects and transitions, and the soundtrack had been greatly expanded and improved upon. In some ways, it wasn't just an enhancement or port of the original 1337ris—it was an entirely new game by itself.

On the technical side, I'm pretty happy with the design and structure of 1337ris. One of the key aspects of the internal design of 1337ris is its Game State Machine, based in part off of a technique I learned from David Brackeen's Developing Games in Java. The Game State class hierarchy was very effective in implementing the other game modes quickly and efficiently. However, it has its limitations. Perhaps there's a better, more generalized design that I could have come up with, but really, who cares? Besides, overgeneralizing isn't necessarily a good thing: just take a look at what happened to C++!

Introduction
============

You've probably encountered Alexey Pajitnov's Tetris at some point or another, in one of its various forms. So you might be wondering why you'd want to play yet another reincarnation of the Soviet puzzle game. To answer that, I ask one question:

How many of them were truly 1337?

1337ris is like Tetris, only, as the name implies, more 1337. In addition to yer standard, traditional Tetris-style gameplay, 1337ris adds some additional twists, such as "bomb" and "dynamite" blocks to spice up the gameplay a bit. But that's not all. 1337ris also offers three additional game modes, "Cross-Cut", "Convergence", and "Psychedelic", all with their own weird interpretations of the falling blocks puzzle. What exactly are they? Why don't you find out for yourself!

Oh, and of course, 1337ris couldn't truly be 1337 without nicely polished graphics, awesome screen effects, configurable keys and settings, high scores, and stuff like that. Don't worry, 1337ris doesn't disappoint.

Pronunciation
=============

To squash any confusion over how to pronounce this game's bizarre name, it's a joke on 1337speak, so it is officially pronounced "leet-ris". However, I usually slur the two together, so it sounds more like "lee-tris" (as it's supposed to be a "-tris" game, anyway).

The Story of the Original 1337ris
=================================

1337ris was originally a Java game I wrote at the end of my junior year in high school, in June of 2007. I can't recall the exact circumstances or motive, but I think part of it was that it was near the end of the year, and, hence, there wasn't much to do in my Java class. Exams had come and gone, and most of my time was spent either goofing off with friends or idly browsing the web in the back of the classroom. Aside from that, I'm not really sure of the exact circumstances 1337ris was born. I'm pretty sure someone else in the class suggested I make a Tetris game one Friday morning, and I came back the next Monday with a prototype for it, but that's about all I can remember.

I got my brother to make some pretty graphics, and then, over one frenzied weekend, I wrote the first prototype of 1337ris. It was surprisingly functional for a Tetris game—there were some rough edges (such as the piece rotation system), but it was an actual, playable Tetris game. And after about a week of testing and bug-fixing, it was (sort of) done. It didn't have any of the crazy cool game modes that had originally been planned, but it played Tetris, and it had bombs and dynamite. And it was awesome.

Later on down the line, I included it as a part of the scenario for a fictional website I helped make for a website competition, the Carcer High School Net-A-Thon (basically, a fictional LAN party for charity). For this, I decided to fix a few lingering bugs (mainly with sound) and add a bit more music.

But that would be that. I left 1337ris unfinished, and moved on to other things. And until the Python game assignment of CSE 142 came along, 1337ris was pretty much a thing of the past in my mind.
