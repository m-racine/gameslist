# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.

#Ok, so obv. needed tests
#adding a new game
#modifying an existing game
#beating a game
#abandoning a game
#metacritic fetch- a few variants
#aging calculations
#priority calculations
#aging 0 when beaten/abandoned?
#current time fetches?
#logging time
#fetching current time (steam?)
#deleting a game
#lending a game
#recommend a game (check priroity)
#pass over a game
#searching for types of games (lots of tests of different searchs)
    #ie, by platform, by played, by recommended etc

#ratings
#rate a as better than b
#rate a as more desireed (wl) than b
#check priorities based on that
#make sure only grabs 5 paris to compare
#check grabs valid pairs to compare
#what are the comparison rules:
  #less  ratings > more ratings 
  # for owned: beaten > played > unplayed > abandoned
  #for owned: 
  #for wished: older > newer

#humble wishlist fetch
#itch wishlist fetch
#gog wishlist fetch
#steam wishlist fetch
#discount comparisons?

#probably many many more in the end