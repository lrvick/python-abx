#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ABX Comparator
# Copyright (c) 2006 Артём Попов <artfwo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import pygst
pygst.require("0.10")
import gst

import pygtk
pygtk.require("2.0")
import gobject

from gst.extend import discoverer

class Metadata:
    def __init__(self, location):
        self.__metadata = {}
        player = gst.element_factory_make("playbin2", "player")
        player.set_property('uri', location)
        player.set_state(gst.STATE_PLAYING)
        player.get_state()
	try:
	    self.__metadata["duration"] = player.query_duration(gst.FORMAT_TIME)[0]
	except:
	    self.__error = ("Couldn't determine stream duration.",
                                    "Unsupported stream?")	
	player.set_state(gst.STATE_NULL)

    def __getitem__(self, key):
        return self.__metadata[key]
