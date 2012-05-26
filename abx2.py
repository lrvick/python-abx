#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gtk
import gst
import random
import gobject

def factorial(n):
    if n == 0: return 1
    else: return n * factorial(n - 1)

def p_value(n, k):
    p = 0
    for i in range(n - k + 1):
        p += (factorial(n) / (factorial(i) * factorial(n - i))) * \
            (0.5 ** i) * (0.5 **(n - i))
    return p

# the gtk class
class AbxComparator:

    a_location, a_duration, b_duration, b_location = None, None, None, None
    sound_player = gst.element_factory_make("playbin2", "sound_player")
    current_location = None

    correct, incorrect = 0, 0

    begin_sample, end_sample, current_sample = 0, 0, 0

    mouse_active_on_hscale = False

    # set the locations if available
    def __init__(self, a_location=None, b_location=None):
        ui = "abx-comparator.ui"
        builder = gtk.Builder()
        builder.add_from_file(ui)
        builder.connect_signals(self)
        window = builder.get_object("abx_audio_window")
        window.show_all()

        self.a_button = builder.get_object("a_button")
        self.b_button = builder.get_object("b_button")
        self.x_button = builder.get_object("x_button")
        self.isa_button = builder.get_object("isa_button")
        self.isb_button = builder.get_object("isb_button")
        self.stop_button = builder.get_object("stop_button")
        self.repeat_button = builder.get_object("repeat_button")
        self.audio_position = builder.get_object("audio_position")
        self.audio_adjustment = builder.get_object("adjustment1")
        self.show_results_button = builder.get_object("show_results_button")
        self.text_buffer = builder.get_object("resultsview").get_buffer()
        self.begin_button = builder.get_object("startbutton")
        self.end_button = builder.get_object("endbutton")

    def _on_main_window_delete_event(self, *args):
        self.quit()

    def _on_quit_button_clicked(self, *args):
        self.quit()

    def _on_show_results_button_toggled(self, *args):
        self.update_results()

    def _on_clear_results_button_clicked(self, *args):
        self.correct, self.incorrect = 0, 0
        self.update_results()

    def _on_a_button_toggled(self, *args):
        if self.a_button.get_active():
            if self.sound_player.get_state()[1] == gst.STATE_PAUSED:
                self.sound_player.set_state(gst.STATE_PLAYING)
                gobject.timeout_add(50, self.update_slider)
                return
            if self.sound_player.get_state()[1] == gst.STATE_PLAYING:
                self.current_sample = self.sound_player.query_position(gst.FORMAT_TIME)[0]
            else:
                self.current_sample = self.begin_sample
            self.phoenix()
            self.x_button.set_active(False)
            self.b_button.set_active(False)
            self.sound_player.set_property('uri', self.a_location)
            self.sound_player.set_state(gst.STATE_PLAYING)
            self.sound_player.get_state()
            self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.current_sample)
            self.begin_button.set_sensitive(True)
            self.end_button.set_sensitive(True)
            gobject.timeout_add(50, self.update_slider)
        else:
            self.sound_player.set_state(gst.STATE_PAUSED)

    def _on_b_button_toggled(self, *args):
        if self.b_button.get_active():
            if self.sound_player.get_state()[1] == gst.STATE_PAUSED:
                self.sound_player.set_state(gst.STATE_PLAYING)
                gobject.timeout_add(50, self.update_slider)
                return
            if self.sound_player.get_state()[1] == gst.STATE_PLAYING:
                self.current_sample = self.sound_player.query_position(gst.FORMAT_TIME)[0]
            else:
                self.current_sample = self.begin_sample
            self.phoenix()
            self.a_button.set_active(False)
            self.x_button.set_active(False)
            self.sound_player.set_property('uri', self.b_location)
            self.sound_player.set_state(gst.STATE_PLAYING)
            self.sound_player.get_state()
            self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.current_sample)
            self.begin_button.set_sensitive(True)
            self.end_button.set_sensitive(True)
            gobject.timeout_add(50, self.update_slider)
        else:
            self.sound_player.set_state(gst.STATE_PAUSED)

    def _on_x_button_toggled(self, *args):
        if self.x_button.get_active():
            if self.sound_player.get_state()[1] == gst.STATE_PAUSED:
                self.sound_player.set_state(gst.STATE_PLAYING)
                gobject.timeout_add(50, self.update_slider)
                return
            if self.sound_player.get_state()[1] == gst.STATE_PLAYING:
                self.current_sample = self.sound_player.query_position(gst.FORMAT_TIME)[0]
            else:
                self.current_sample = self.begin_sample
            self.phoenix()
            self.a_button.set_active(False)
            self.b_button.set_active(False)
            self.sound_player.set_property('uri', self.current_location)
            self.sound_player.set_state(gst.STATE_PLAYING)
            self.sound_player.get_state()
            self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.current_sample)
            self.begin_button.set_sensitive(True)
            self.end_button.set_sensitive(True)
            gobject.timeout_add(50, self.update_slider)
        else:
            self.sound_player.set_state(gst.STATE_PAUSED)
     
    def _on_isa_button_clicked(self, *args):
        self.stop()
        if self.current_location == self.a_location: 
            self.correct += 1
        else:
            self.incorrect += 1
        self.update_gui()

    def _on_isb_button_clicked(self, *args):
        self.stop()
        if self.current_location == self.b_location: 
            self.correct += 1
        else:
            self.incorrect += 1
        self.update_gui()

    def _start_selection_button_toggled(self, *args):
        if self.begin_button.get_active():
            self.begin_button.set_label(str("%.2f" %(self.sound_player.query_position(gst.FORMAT_TIME)[0] / gst.MSECOND / 1000.0)))
            self.begin_sample = self.sound_player.query_position(gst.FORMAT_TIME)[0]
        else:
            self.begin_button.set_label("Start")
            self.begin_sample = 0

    def _end_selection_button_toggled(self, *args):
        if self.end_button.get_active():
            self.end_button.set_label(str("%.2f" %(self.sound_player.query_position(gst.FORMAT_TIME)[0] / gst.MSECOND / 1000.0)))
            self.end_sample = self.sound_player.query_position(gst.FORMAT_TIME)[0]
            self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.begin_sample)
        else:
            self.end_button.set_label("End")
            self.end_sample = 0

    def _on_stop_button_clicked(self, *args):
        self.stop()

    def _on_repeat_button_toggled(self, *args):
        return

    def _a_file_chosen(self, button):
        self.a_location = button.get_uri()
        self.a_duration = self.load_file(self.a_location)
        self.update_gui()

    def _b_file_chosen(self, button):
        self.b_location = button.get_uri()
        self.b_duration = self.load_file(self.b_location)
        self.update_gui()

    def _hscale_button_press(self, *args):
        self.mouse_active_on_hscale = True

    def _hscale_button_release(self, *args):
        self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.audio_adjustment.value)
        self.mouse_active_on_hscale = False
        return
        
    def load_file(self, location):
        tempPlayer = gst.element_factory_make("playbin2", "tempPlayer")
        tempPlayer.set_property('uri', location)
        tempPlayer.set_state(gst.STATE_PLAYING)
        tempPlayer.get_state()

        try:
	        duration = tempPlayer.query_duration(gst.FORMAT_TIME)[0]
        except:
	        self.error = ("Couldn't determine stream duration.",
                                    "Unsupported stream?")	

        tempPlayer.set_state(gst.STATE_NULL)

        #testing
        print location, duration
        #end testing
        return duration

    def update_gui(self, *args):
        if (self.a_duration != None and self.b_duration != None):
            self.audio_adjustment.upper = min(self.a_duration, self.b_duration)
            self.enable_buttons()
            if random.random() > 0.5:
                self.current_location = self.a_location
            else:
                self.current_location = self.b_location
        self.update_results()

    def update_results(self, *args):
        if self.show_results_button.get_active():
            score_value = str(self.correct)
            p = "%.2f%%" % round(p_value(self.correct + self.incorrect, self.correct) * 100, 2)
        else:
            score_value, p = "hidden", "hidden"
        
        self.text_buffer.set_text("Score: " + score_value + " / " + str(self.correct + self.incorrect) + "\np = " + str(p))

    def update_slider(self, *args):
        if self.mouse_active_on_hscale:
            return True
        if self.sound_player.get_state()[1] == gst.STATE_NULL:
            return False
        if self.sound_player.query_position(gst.FORMAT_TIME)[0] > self.audio_adjustment.upper or self.sound_player.query_position(gst.FORMAT_TIME)[0] > self.end_sample and self.end_sample != 0:
            #repeat if selected
            if self.repeat_button.get_active():
                if self.end_sample > self.begin_sample:
                    self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.begin_sample)
                else:
                    self.sound_player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, 0.0)
            else:
                self.stop()
                return False
        try:
            self.audio_adjustment.value = self.sound_player.query_position(gst.FORMAT_TIME)[0]
        except:
            self.sound_player.get_state()
        return self.sound_player.get_state()[1] == gst.STATE_PLAYING

    # a dirty hack to work around bugs in playbin2
    # idea from the quodlibet player
    def phoenix (self, *args):
        self.sound_player.set_state(gst.STATE_NULL)
        self.sound_player.get_state()
        self.sound_player = None
        self.sound_player = gst.element_factory_make("playbin2", "sound_player")
        
    def enable_buttons(self, *args):
        self.a_button.set_sensitive(True)
        self.x_button.set_sensitive(True)
        self.b_button.set_sensitive(True)
        self.isa_button.set_sensitive(True)
        self.isb_button.set_sensitive(True)
        self.stop_button.set_sensitive(True)
        self.audio_position.set_sensitive(True)

    def stop(self, *args):
        self.a_button.set_active(False)
        self.b_button.set_active(False)
        self.x_button.set_active(False)
        self.begin_button.set_sensitive(False)
        self.end_button.set_sensitive(False)
        self.sound_player.set_state(gst.STATE_NULL)
        self.audio_adjustment.value = 0
    
    def quit(self, *args):
        gtk.main_quit(*args)

# MAIN CODE STARTS HERE

# set window icon
gtk.window_set_default_icon_from_file("abx-comparator.svg")

# if we have at least 2 arguments, go ahead and set file A
if 2 < len(sys.argv) <= 3:
    a = sys.argv[1]
    if not gst.uri_is_valid(a):
        a = "file://" + os.path.abspath(a)
else:
    a = None

# and if we have 3, set file B as well
if len(sys.argv) == 3:
    b = sys.argv[2]
    if not gst.uri_is_valid(b):
        b = "file://" + os.path.abspath(b)
else:
    b = None

# define the app class
app = AbxComparator(a, b)
# launch the window
gtk.main()
