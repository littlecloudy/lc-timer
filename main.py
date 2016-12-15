#! /env/bin python3

import sys
from gi.repository import Gio
from timer import *


class App (Gtk.Application):
  def __init__ (self):
    Gtk.Application.__init__ (self,
                              application_id='org.littlecloudy.timer',
                              flags=Gio.ApplicationFlags.FLAGS_NONE)

    self.connect ('activate', self.on_activate_app)

  def on_activate_app (self, app):
    win = Gtk.ApplicationWindow ()
    app.add_window (win)

    header = Gtk.HeaderBar ()
    header.set_title ('Timer')
    header.set_show_close_button (True)
    win.set_titlebar (header)



    timer = TimerApp ()
    win.add (timer)
    
    
    win.show_all ()

if __name__ == '__main__':
  app = App ()
  app.run (None)