# python-abx #

<http://github.com/lrvick/python-abx>

## About ##

A simple GTK application for performing ABX testing using python and gstreamer.

This codebase is a slightly cleaned up fork of [python-abx](https://code.google.com/archive/p/python-abx/) which was abandoned, and itself was a fork of the long
dead [ABX-Comparator](http://freecode.com/projects/abx-comparator)

## Requirements ##
  * python2.7
  * GTK2
  * gstreamer-0.10 (And various good, bad, and ugly modules as needed)
  * python-gtk
  * python-gst

## Current Features ##

  * Swap A/B on at any point while playing
  * Perform any number of tests and show/hide results at any time

## Usage / Installation ##

1. run abx.py

    ```bash
    ./abx.py
    ```
2. Select files for A and B

3. Play A,B,X and make make your guesses

4. "Show" to show results

## Notes ##

  I only tweaked this enough to get it working for me.
  Use at your own risk. You may be eaten by a grue.
