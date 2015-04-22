#!/usr/bin/env python
#
# Merges subtitles from 2 files into a third one.
#
# 1.0: simple merge. don't change any times.
#   assumes blank lines at end
#
# 1
# 00:00:01,791 --> 00:00:04,104
# subtitles by ion1010
#
# 2
# 00:001:06,145 --> 00:01:07,150
# Ha Ha Ha Ha!
#


import sys
import time
import httplib
import urllib
import os
import os.path
from utils import *

def parse_args():
   """Parses arguments"""
   import optparse

   p = optparse.OptionParser()
   p.add_option("-l", "--log", dest="loglevel", help="set log level to any of: debug, info, warn, error, critical (default: %default)")
   p.add_option("-f", "--logfile", dest="logfile", help="log to file with this name")
   p.add_option("-1", dest="first", help="first file (default: %default)")
   p.add_option("-2", dest="second", help="second file (default: %default)")
   p.add_option("-o", dest="output", help="output merged file (default: %default)")
   p.add_option("--overwrite", action="store_true", dest="overwrite", help="overwrite file if exists (default: %default)")   
   p.add_option("-d", "--diff", dest="diff", help="if 0, same numbers are merged. If 2, second:3 will get merged to first:1. If -2, second:3 will get merged to first:5 (default: %default)")

   # set defaults
   p.set_defaults(loglevel="info", diff = 0, first="1.srt", second="2.srt", output="3.srt", overwrite=True)
   (opts, args) = p.parse_args()

   opts.diff = int(opts.diff)
   #trace ("opts: " +  str(opts))
   return opts


def main():

   opts = parse_args()
   log = init_logging(opts.loglevel, opts.logfile)

   # start profile
   start = time.time()

   # initialize files
   with open(opts.first) as f:
      lines1 = f.readlines()
   with open(opts.second) as f:
      lines2 = f.readlines()
   if os.path.exists(opts.output):
      if opts.overwrite:
         if os.path.isfile(opts.output):
            os.remove(opts.output)
         else:
            fatal("output folder %s needs manual removal" % opts.output)
      else:
         fatal("%s already exists, exiting" % opts.output)

   out = open(opts.output, 'a')

   # what counter we are on
   counter1 = int(lines1[0].strip().decode('utf-8-sig'))
   counter2 = int(lines2[0].strip().decode('utf-8-sig'))

   # line number in file
   ptr1 = 0
   ptr2 = 0

   trace("first: starts at %d" % counter1)
   trace("second: starts at %d" % counter2)

   # have we reached end of file?
   done1 = False
   done2 = False

   # handle diff
   # if diff > 0, skip that many blanks in 2
   # if diff < 0, skip that many blanks in 1
   if opts.diff > 0:
      for i in range(abs(opts.diff)):
         while len(lines2[ptr2].strip()) != 0:
            ptr2 += 1
         if len(lines2[ptr2].strip()) == 0:
            ptr2 += 1
   elif opts.diff < 0:
      for i in range(abs(opts.diff)):
         while len(lines1[ptr1].strip()) != 0:
            ptr1 += 1
         if len(lines1[ptr1].strip()) == 0:
            ptr1 += 1


   # loop over each line in first file
   while  ptr1 < len(lines1):
      if len(lines1[ptr1].strip()) > 0:
         counter1 = int(lines1[ptr1].strip().decode('utf-8-sig'))
      else:
         done1 = True
      if len(lines2[ptr2].strip()) > 0:
         counter2 = int(lines2[ptr2].strip().decode('utf-8-sig'))
      else:
         done2 = True

      debug("*** looping")
      debug("counter1: %d" % counter1)
      debug("counter2: %d" % counter2)
      debug("ptr1: %d" % ptr1)
      debug("ptr2: %d" % ptr2)

      # add to output until encounter blank
      while not done1 and len(lines1[ptr1].strip()) != 0:
         debug("writing: " + lines1[ptr1].strip())
         out.write(lines1[ptr1])
         ptr1 += 1
         debug("incr ptr1: %d" % ptr1)

      if not done2 and counter1 + opts.diff == counter2:
         # merge
         ptr2 += 2  # skip counter and timestamp
         while len(lines2[ptr2].strip()) != 0:
            debug("writing: " + lines2[ptr2].strip())
            out.write(lines2[ptr2])
            ptr2 += 1
            debug("incr ptr2: %d" % ptr2)

      # skip blank line
      if not done1 and len(lines1[ptr1].strip()) == 0:
         ptr1 += 1 
      if not done2 and len(lines2[ptr2].strip()) == 0:
         ptr2 += 1
      out.write("\n")

   out.close()
   #trace("#\t TOTAL TIME: " + get_elapsed_time( int(time.time() - start)))


if __name__ == '__main__':
   main()
else:
   pass
