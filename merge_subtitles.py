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
from time import strptime  # parse time
from time import strftime  # format time
from time import mktime


def parse_args():
   """Parses arguments"""
   import optparse

   p = optparse.OptionParser()
   p.add_option("-l", "--log", dest="loglevel", help="set log level to any of: debug, info, warn, error, critical (default: %default)")
   p.add_option("-f", "--logfile", dest="logfile", help="log to file with this name")
   p.add_option("-1", dest="first", help="first file (default: %default)")
   p.add_option("-2", dest="second", help="second file (default: %default)")
   p.add_option("-o", dest="output", help="output merged file (default: %default)")
   p.add_option("--use_ts", action="store_true", dest="use_ts", help="use timestamp, else counter (default: %default)")   
   p.add_option("--overwrite", action="store_true", dest="overwrite", help="overwrite file if exists (default: %default)")   
   p.add_option("-d", "--diff", dest="diff", help="if 0, same numbers are merged. If 2, second:3 will get merged to first:1. If -2, second:3 will get merged to first:5 (default: %default)")

   # set defaults
   p.set_defaults(loglevel="info", diff = 0, first="1.srt", second="2.srt", output="3.srt", use_ts = False, overwrite=True)
   (opts, args) = p.parse_args()

   opts.diff = int(opts.diff)
   #trace ("opts: " +  str(opts))
   return opts


class TS:
   def __init__(self, ts, ms):
      self.ts = strptime("2000 " + ts, "%Y %H:%M:%S")  # 2000 is to make time.mktime() work properly
      self.ms = ms

   def get_ts(self):
      return strftime("%H:%M:%S", self.ts)

   def __str__(self):
     return "%s,%d" % (self.get_ts(), self.ms)

   def __sub__(self, other):
      a = mktime(self.ts) + float(self.ms) / 1000
      b = mktime(other.ts) + float(other.ms) / 1000
      debug("returning: %f" % (a-b))
      return a - b


def parse_from_to(ts):
   tokens = ts.split(' ')
   start = tokens[0].split(',')
   start = TS(start[0], int(start[1]))

   end = tokens[2].split(',')
   end = TS(end[0], int(end[1]))

   debug("%s %d, %s %d" % (start.get_ts(), start.ms, end.get_ts(), end.ms))
   return (start, end)


def parse_ts(lines):
   ptr = 0
   items = list()
   while ptr < len(lines):
      # skip blank line
      if len(lines[ptr].strip()) == 0:
         ptr += 1

      # discard counter
      ptr += 1

      if ptr >= len(lines):
         break

      # read ts
      ts = parse_from_to(lines[ptr].strip())
      ptr += 1

      text = ""
      # read text until blank line
      while len(lines[ptr].strip()) != 0:
         text += lines[ptr]
         ptr += 1
         debug("incr ptr: %d" % ptr)

      text = text.strip()
      debug("text: %s" % text)
      # append to items
      tuple = (ts, text)
      items.append(tuple)

   return items



def ts_write(out, counter, start, end, text):
   out.write("%d\n" % counter)
   out.write("%s --> %s\n" % (start, end))
   out.write(text + "\n")
   out.write("\n")


def do_ts(opts, out, lines1, lines2):
   # remove counters
   # parse into array of tuples (from, to, list of lines)
   lang1 = parse_ts(lines1)   
   lang2 = parse_ts(lines2)
   trace("1: %d, 2: %d" % (len(lang1), len(lang2)))

   # init
   counter = 1
   m_counter = s_counter = 0

   # cases for merging language text
   # A: merge text from 1 and 2
   # B: output text from 1 only
   # C: output text from 2 only

   # cases for timestamp merge - avoid overlap
   # 1: determine start: use from whatever lang has more counters
   # 2: determine end:  use from whatever lang has more counters
   # 3: determine merge case:
   #     if start2 - start1 <= 1 second  --> merge
   #        else                         --> more counter lang only

   if len(lang1) >= len(lang2):
      master = lang1
      slave = lang2
   else:
      master = lang2
      slave = lang1

   # loop
   while counter <= len(master):
      debug("*** looping: %d" % counter)

      (m_ts, m_text) = master[m_counter]
      (m_start, m_end) = m_ts

      (s_ts, s_text) = slave[s_counter]
      (s_start, s_end) = s_ts

      if s_start - m_start <= 1.0 and s_counter < len(slave):
         # merge the two languages
         debug("merge")
         text = m_text + "\n" + s_text
         m_counter += 1
         s_counter += 1
      else:
         # emit master only
         debug("master only")
         text = m_text
         m_counter += 1

      ts_write(out, counter, m_start, m_end, text)
      counter += 1


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

   if opts.use_ts:
      do_ts(opts, out, lines1, lines2)
   else:
      do_counter(opts, out, lines1, lines2)

   out.close()



def do_counter(opts, out, lines1, lines2):

   # what counter we are on
   counter1 = int(lines1[0].strip().decode('utf-8-sig'))
   counter2 = int(lines2[0].strip().decode('utf-8-sig'))

   # line number in file
   ptr1 = 0
   ptr2 = 0

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


   # begin the process
   while  ptr1 < len(lines1):
      if ptr1 < len(lines1) and len(lines1[ptr1].strip()) > 0:
         counter1 = int(lines1[ptr1].strip().decode('utf-8-sig'))
      else:
         done1 = True
      if ptr2 < len(lines2) and len(lines2[ptr2].strip()) > 0:
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



if __name__ == '__main__':
   main()
else:
   pass

