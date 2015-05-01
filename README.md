# README #

Collection of scripts.


## Merge Subtitles ##

Merges subtitles from 2 files in the SubRip format. Built for someone learning a new language.

- ver 1: based on counter. Works but hard to find 2 subtitles that match up well.
- ver 2: based on timestamp.  Works better, but issues still like incorrect order of languages, too much text shows for the time duration etc.

## Substitute Checker ##

Checks and notifies on available substitute teacher positions in the Aesop system.

I use [Pushover](https://pushover.net/) ($5 for ios) for notifications, but it can be any email address.

To run, you can setup an hourly cron job:
0 * * * * ./check.sh userid pin from@email to@email


### How do I get set up? ###

Needs python 2.7.3+

