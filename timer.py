#! /usr/bin python3

import gi,time
gi.require_version ('Gtk', '3.0')
gi.require_version ('Notify', '0.7')
from gi.repository import Gtk,GLib,Gdk,Pango,Notify
from GtkLc import GtkLc, CircularLevelBar


class Timer ():
  # params: hour,minute,second in seconds
  #         progressui = None if not needed

  def __init__ (self, hour, minute, second, countdown_label, progressui):
    self.sigint      = 0 # 0:running, 1:kill, 2:kill pause
    self.total_time = hour + minute + second
    self.total_time_origin = self.total_time # not implemented yet

    self.ui = progressui
    self.label = countdown_label
    self.label.set_label (str(int(self.total_time)))
    
    Notify.init ('Timer')
    self.noti = Notify.Notification.new ('Timer', 'End of timer', 'alarm-symbolic')
    
    
  def start_timer (self):
    self.sigint = 0
    # on 1 ms total time reduce by 1ms
    self.pid = GLib.timeout_add (1, self._timer_gsource_func, self.ui) 

  def pause_timer (self):
    self.sigint = 2

  def kill_timer (self):
    self.sigint = 1
    
  def _timer_gsource_func (self, ui):  
    if self.sigint is 0:
      # by the time gsourcefunc running, total time has reduced.
      # the integer has elapsed by 1 point
      self.label.set_label (str (int(self.total_time) + 1))
      
      # supposedly reduce by 1ms but compare to actual clock, it lags by few ms
      self.total_time -= 0.00120000000 # adjustment precision (trial & error)..fix ??
      self.ui.set_value (self.total_time)
      
      if self.total_time <= 0 :
        
        self.total_time  = 1.0
        self.sigint      = 1.0
        # revert condition, actual number would be stopped at 1
        self.label.set_label (str (int(self.total_time) - 1) )

        self.noti.show ()
        #print ('end of timer')
        return False

      return True
    
    if self.sigint is 1:
      return False
  
    if self.sigint is 2:
      return False

class TimerApp (Gtk.Stack):
  def __init__ (self):
    Gtk.Stack.__init__ (self)
    self.set_transition_type (Gtk.StackTransitionType.SLIDE_LEFT)
    

    self.newTimer = None
    # stack left
    grid1 = Gtk.Grid ()
    GtkLc.set_all_margins_widget (grid1, 15)
    self.add_named (grid1, 'grid1')

    hour_label   = Gtk.Label ('Hours')
    grid1.attach (hour_label, 0,0,1,1)

    hour_spin    = Gtk.SpinButton.new_with_range (0,99,1)
    grid1.attach (hour_spin, 0,1,1,1)

    minute_label = Gtk.Label ('Minutes')
    grid1.attach (minute_label, 0,2,1,1)

    minute_spin  = Gtk.SpinButton.new_with_range (0,59,1)
    grid1.attach (minute_spin, 0,3,1,1)

    second_label = Gtk.Label ('Seconds')
    grid1.attach (second_label, 0,4,1,1)

    second_spin  = Gtk.SpinButton.new_with_range (0,59,1)
    grid1.attach (second_spin, 0,5,1,1)

    start_button = Gtk.Button ('Start')
    start_button.set_margin_top (15)
    start_button.set_hexpand (True)
    start_button.set_vexpand (True)
    start_button.set_valign (Gtk.Align.END)
    grid1.attach (start_button, 0,7,1,1)
    
    self.set_visible_child (grid1)

    # stack right
    grid2 = Gtk.Grid ()
    self.add_named (grid2, 'grid2')

    overlay = Gtk.Overlay ()
    grid2.attach (overlay, 0,0,1,1)

    levelbar = GtkLc.CircularLevelBar ()
    levelbar.set_value (1)
    levelbar.set_hexpand (True)
    overlay.add (levelbar)

    # change this to Gtk.LevelBar if GtkLcCircularLevelBar is broken
    # label should move to other place rather than being overlayed
    #levelbar = Gtk.LevelBar ()
    #levelbar.set_value (1)
    #levelbar.set_hexpand (True)
    #overlay.add (levelbar)

    status_label = Gtk.Label ()
    status_label.override_font (Pango.FontDescription.from_string ('condensed 14'))
    overlay.add_overlay (status_label)

    buttonbox = Gtk.ButtonBox ()
    buttonbox.set_layout (Gtk.ButtonBoxStyle.EXPAND)
    buttonbox.set_vexpand (True)
    buttonbox.set_valign (Gtk.Align.END)
    grid2.attach (buttonbox, 0,1,1,1)

    pause_button = Gtk.ToggleButton ('Pause')
    buttonbox.add (pause_button)

    cancel_button = Gtk.Button ('Cancel')
    buttonbox.add (cancel_button)


    start_button.connect  ('clicked', self.on_start_timer, 
                                      hour_spin, 
                                      minute_spin, 
                                      second_spin,
                                      grid2, 
                                      status_label, 
                                      levelbar)
    pause_button.connect  ('clicked', self.on_pause_timer, levelbar)
    cancel_button.connect ('clicked', self.on_cancel_timer, grid1)


  def on_start_timer (self, button, hour_spin, minute_spin, second_spin, grid2, countdown_label, levelbar):
    self.set_visible_child (grid2)
    
    hour   = hour_spin.get_value_as_int ()
    minute = minute_spin.get_value_as_int ()
    second = second_spin.get_value_as_int ()

    hour_sec    = hour   * 3600
    minute_sec  = minute * 60
    
    levelbar.set_max_value ( hour_sec + minute_sec + second )
    levelbar.set_value ( hour_sec + minute_sec + second )
    
    self.newTimer = Timer (hour_sec, minute_sec, second, countdown_label, levelbar)
    self.newTimer.start_timer ()
    
  def on_pause_timer (self, button,levelbar):
    if button.get_active ():
      self.newTimer.pause_timer ()
    if not button.get_active ():
      self.newTimer.start_timer ()

  def on_cancel_timer (self, button, grid1):
    self.newTimer.kill_timer ()
    self.set_visible_child (grid1)


   
#win = Gtk.Window ()
#timer = TimerApp ()
#win.add (timer)

#win.show_all ()
#Gtk.main ()
#Gtk.init ()   
