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

import pygtk
pygtk.require("2.0")
import gtk

(SAMPLESEL_DRAG_NONE,
SAMPLESEL_DRAG_LEFT,
SAMPLESEL_DRAG_RIGHT,
SAMPLESEL_DRAG_ALL) = range(4)

SAMPLESEL_DRAG_ZONE = 2

class SampleSelector(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                gtk.gdk.BUTTON_RELEASE_MASK |
                gtk.gdk.POINTER_MOTION_MASK)

        self.connect("button-press-event", self.__on_button_press_event)
        self.connect("button-release-event", self.__on_button_release_event)
        self.connect("motion-notify-event", self.__on_motion_notify_event)
        self.connect("expose_event", self.__on_expose_event)

        self.set_size_request(9, 9) # maybe even bigger?

        self.mode = SAMPLESEL_DRAG_NONE

        self.start_value        = 0.0
        self.stop_value         = 1.0
        self.playback_position  = 0.0

    def start_pixels(self):
        return round(self.get_allocation().width * self.start_value)

    def stop_pixels(self):
        return round(self.get_allocation().width * self.stop_value)

    def __in_left_handle(self, position):
        return self.start_pixels() - SAMPLESEL_DRAG_ZONE < position < \
            self.start_pixels() + SAMPLESEL_DRAG_ZONE

    def __in_right_handle(self, position):
        return self.stop_pixels() - SAMPLESEL_DRAG_ZONE < position < \
            self.stop_pixels() + SAMPLESEL_DRAG_ZONE

    def __in_between(self, position):
        return self.start_pixels() + SAMPLESEL_DRAG_ZONE < position < \
            self.stop_pixels() - SAMPLESEL_DRAG_ZONE

    def __on_button_press_event(self, widget, event):
        if event.button != 1:
            return

        if self.__in_left_handle(event.x):
            self.mode = SAMPLESEL_DRAG_LEFT
        elif self.__in_right_handle(event.x):
            self.mode = SAMPLESEL_DRAG_RIGHT
        elif self.__in_between(event.x):
            self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))
            self.mode = SAMPLESEL_DRAG_ALL
        else:
            return

        self.x1 = event.x

    def __on_button_release_event(self, widget, event):
        if event.button != 1:
            return

        # a little update if we have moved anything
        if (self.mode != SAMPLESEL_DRAG_NONE):
            self.window.set_cursor(None)
            del self.x1
            self.mode = SAMPLESEL_DRAG_NONE

    def __on_motion_notify_event(self, widget, event):
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.state

        # default behaviour, change cursor
        if self.mode == SAMPLESEL_DRAG_NONE:
            if self.__in_left_handle(x):
                self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_SIDE))
            elif self.__in_right_handle(x):
                self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE))
            else:
                self.window.set_cursor(None)
            return

        dx = x - self.x1
        dv = float(dx) / self.get_allocation().width

        # left handle
        if self.mode == SAMPLESEL_DRAG_LEFT:
            new_start = self.start_value + dv
            if state & gtk.gdk.SHIFT_MASK:
                new_stop = self.stop_value - dv
            else:
                new_stop = self.stop_value

            if new_start < 0: new_start = 0
            if new_stop > 1: new_stop = 1

            if new_start < new_stop:
                self.start_value = new_start
                self.stop_value = new_stop
                self.queue_draw()
            self.x1 = event.x

        # right handle
        elif self.mode == SAMPLESEL_DRAG_RIGHT:
            new_stop = self.stop_value + dv
            if state & gtk.gdk.SHIFT_MASK:
                new_start = self.start_value - dv
            else:
                new_start = self.start_value

            if new_start < 0: new_start = 0
            if new_stop > 1: new_stop = 1

            if new_stop > new_start:
                self.start_value = new_start
                self.stop_value = new_stop
                self.queue_draw()
            self.x1 = event.x

        # blue thingie
        elif self.mode == SAMPLESEL_DRAG_ALL:
            new_start = self.start_value + dv
            new_stop = self.stop_value + dv

            # for smooth collision within limits
            if new_start < 0:
                new_stop -= new_start
                new_start = 0
            elif new_stop > 1:
                new_start -= new_stop - 1
                new_stop = 1

            self.start_value = new_start
            self.stop_value = new_stop
            self.queue_draw()

            self.x1 = event.x

    def __on_expose_event(self, widget, event):
        style = self.rc_get_style()

        if self.get_property("sensitive"):
            bg_color = style.base[gtk.STATE_NORMAL]
            fg_color = style.fg[gtk.STATE_NORMAL]
            selection_color = style.bg[gtk.STATE_SELECTED]
            tracker_color = style.base[gtk.STATE_NORMAL]
        else:
            bg_color = style.bg[gtk.STATE_INSENSITIVE]
            # fg_color = style.fg[gtk.STATE_INSENSITIVE]
            fg_color = style.fg[gtk.STATE_NORMAL]
            # selection_color = style.text[gtk.STATE_INSENSITIVE]
            selection_color = style.bg[gtk.STATE_SELECTED]
            tracker_color = style.base[gtk.STATE_NORMAL]

        context = widget.window.cairo_create()
        context.rectangle(event.area.x,
            event.area.y,
            event.area.width,
            event.area.height)
        context.clip()

        w = self.get_allocation().width
        h = self.get_allocation().height

        self.__draw_background(context, bg_color, fg_color)
        self.__draw_range(context, selection_color, fg_color)

        if self.playback_position > 0:
            self.__draw_position_indicator(context, tracker_color)

        return False

    def __draw_background(self, context, bg_color, fg_color):
        context.rectangle(0.5, 0.5,
                self.get_allocation().width - 1,
                self.get_allocation().height - 1)

        context.set_line_width(1.0)

        context.set_source_rgb(bg_color.red / float(0xffff),
                bg_color.green / float(0xffff),
                bg_color.blue / float(0xffff))

        context.fill_preserve()

        context.set_source_rgb(fg_color.red / float(0xffff),
                fg_color.green / float(0xffff),
                fg_color.blue / float(0xffff))

        context.stroke()

        context.rectangle(0.5, 2.5,
                self.get_allocation().width - 1,
                self.get_allocation().height - 5)

        context.set_source_rgb(fg_color.red / float(0xffff),
                fg_color.green / float(0xffff),
                fg_color.blue / float(0xffff))

        context.stroke()

    def __draw_range(self, context, bg_color, fg_color):
        context.rectangle(self.start_pixels() + 0.5,
                2.5,
                self.stop_pixels() - self.start_pixels() - 1,
                self.get_allocation().height - 5)

        context.set_line_width(1.0)

        context.set_source_rgb(bg_color.red / float(0xffff),
                bg_color.green / float(0xffff),
                bg_color.blue / float(0xffff))

        context.fill_preserve()

        context.set_source_rgb(fg_color.red / float(0xffff),
                fg_color.green / float(0xffff),
                fg_color.blue / float(0xffff))

        context.stroke()

    def __draw_position_indicator(self, context, fg_color):
        x = self.get_allocation().width * self.playback_position

        context.set_line_width(1.0)
        context.move_to(x, 2.5)
        context.line_to(x, self.get_allocation().height - 2.5)

        context.set_source_rgb(fg_color.red / float(0xffff),
                fg_color.green / float(0xffff),
                fg_color.blue / float(0xffff))

        context.stroke()
