#!/usr/bin/env python
"""Banshee player adapter for Remuco, implemented as an executable script.

__author__ = "Oben Sonne <obensonne@googlemail.com>"
__copyright__ = "Copyright 2009, Oben Sonne"
__license__ = "GPL"
__version__ = "0.8.0"

"""
import os.path

import dbus
from dbus.exceptions import DBusException
from xdg.BaseDirectory import xdg_cache_home as xdg_cache

import remuco
from remuco import log

# =============================================================================
# banshee dbus names
# =============================================================================

DBUS_NAME = "org.bansheeproject.Banshee"
DBUS_PATH_ENGINE = "/org/bansheeproject/Banshee/PlayerEngine"
DBUS_IFACE_ENGINE = "org.bansheeproject.Banshee.PlayerEngine"
DBUS_PATH_CONTROLLER = "/org/bansheeproject/Banshee/PlaybackController"
DBUS_IFACE_CONTROLLER = "org.bansheeproject.Banshee.PlaybackController"

# =============================================================================
# banshee player adapter
# =============================================================================

class BansheeAdapter(remuco.PlayerAdapter):
    
    def __init__(self):
        
        remuco.PlayerAdapter.__init__(self, "Banshee",
                                      max_rating=5,
                                      playback_known=True,
                                      volume_known=True,
                                      repeat_known=True,
                                      shuffle_known=True,
                                      progress_known=True)
        
        self.__dbus_signal_handler = ()
    
        self.__repeat = False
        self.__shuffle = False
        self.__volume = 0
        
        self.__progress_length = 0
    
        log.debug("init done")
        
    def start(self):
        
        remuco.PlayerAdapter.start(self)
        
        try:
            bus = dbus.SessionBus()
            proxy = bus.get_object(DBUS_NAME, DBUS_PATH_ENGINE)
            self.__bse = dbus.Interface (proxy, DBUS_IFACE_ENGINE)
            proxy = bus.get_object(DBUS_NAME, DBUS_PATH_CONTROLLER)
            self.__bsc = dbus.Interface(proxy, DBUS_IFACE_CONTROLLER)
        except DBusException, e:
            raise StandardError("dbus error: %s" % e)

        try:
            self.__dbus_signal_handler = (
                self.__bse.connect_to_signal("EventChanged",
                                             self.__notify_event),
                self.__bse.connect_to_signal("StateChanged",
                                             self.__notify_playback),
            )
        except DBusException, e:
            raise StandardError("dbus error: %s" % e)
        
        try:
            self.__bse.GetCurrentTrack(reply_handler=self.__notify_track,
                                       error_handler=self.__dbus_error)
            self.__bse.GetCurrentState(reply_handler=self.__notify_playback,
                                       error_handler=self.__dbus_error)
            self.__bse.GetVolume(reply_handler=self.__notify_volume,
                                 error_handler=self.__dbus_error)
        except DBusException, e:
            # this is not necessarily a fatal error
            log.warning("dbus error: %s" % e)

        log.debug("start done")
        
    def stop(self):
        
        remuco.PlayerAdapter.stop(self)
        
        for handler in self.__dbus_signal_handler:
            handler.remove()
            
        self.__dbus_signal_handler = ()
        
        self.__bsc = None
        self.__bse = None

        log.debug("stop done")
        
    def poll(self):
        
        try:
            self.__bsc.GetRepeatMode(reply_handler=self.__notify_repeat,
                                     error_handler=self.__dbus_error)
            self.__bsc.GetShuffleMode(reply_handler=self.__notify_shuffle,
                                      error_handler=self.__dbus_error)
            self.__bse.GetPosition(reply_handler=self.__notify_progress,
                                   error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
        
        return True
        
    # =========================================================================
    # control interface
    # =========================================================================
    
    def ctrl_toggle_playing(self):
        
        try:
            self.__bse.TogglePlaying(reply_handler=self.__dbus_ignore,
                                     error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)

    def ctrl_next(self):
        
        try:
            self.__bsc.Next(False,
                            reply_handler=self.__dbus_ignore,
                            error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
    
    def ctrl_previous(self):
        
        try:
            self.__bsc.Previous(False,
                                reply_handler=self.__dbus_ignore,
                                error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
    
    
    def ctrl_volume(self, direction):
        
        if direction == 0:
            volume = 0
        else:
            volume = self.__volume + direction * 5
            volume = min(volume, 100)
            volume = max(volume, 0)
            
        try:
            self.__bse.SetVolume(dbus.UInt16(volume),
                                 reply_handler=self.__dbus_ignore,
                                 error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
            
        self.__notify_event("volume", None, None)
        

    def ctrl_toggle_repeat(self):
        
        try:
            self.__bsc.SetRepeatMode(int(not self.__repeat),
                                     reply_handler=self.__dbus_ignore,
                                     error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
            
        self.poll()
            
    def ctrl_toggle_shuffle(self):

        try:
            self.__bsc.SetShuffleMode(int(not self.__shuffle),
                                      reply_handler=self.__dbus_ignore,
                                      error_handler=self.__dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
            
        self.poll()

    # =========================================================================
    # internal methods
    # =========================================================================
    
    def __notify_event(self, event, message, buff_percent):
        
        try:
            
            if event == "startofstream" or event == "trackinfoupdated":
                self.__bse.GetCurrentTrack(reply_handler=self.__notify_track,
                                           error_handler=self.__dbus_error)
            elif event == "volume":
                self.__bse.GetVolume(reply_handler=self.__notify_volume,
                                     error_handler=self.__dbus_error)
            else:
                log.debug("event: %s (%s)" %(event, message))
                
        except DBusException, e:
            log.warning("dbus error: %s" % e)
    
    def __notify_playback(self, state):
        
        log.debug("state: %s" % state)

        if state == "playing":
            playback = remuco.PLAYBACK_PLAY
        elif state == "idle":
            playback = remuco.PLAYBACK_STOP
            self.update_item(None, None, None)
        else:
            playback = remuco.PLAYBACK_PAUSE
            
        self.update_playback(playback)
        
    def __notify_volume(self, volume):
        
        self.__volume = volume
        self.update_volume(volume)
        
    def __notify_track(self, track):
        
        id = track.get("URI")
        
        if not id:
            self.update_item(None, None, None)
            self.__progress_length = 0
            return
        
        info = {}
        info[remuco.INFO_TITLE] = track.get("name")
        info[remuco.INFO_ARTIST] = track.get("artist")
        info[remuco.INFO_ALBUM] = track.get("album")
        info[remuco.INFO_RATING] = track.get("rating", 0)
        
        self.__progress_length = int(track.get("length", 0))

        img = None
        art_id = track.get("artwork-id")
        if art_id:
            file = "%s/album-art/%s.jpg" % (xdg_cache, art_id)
            if os.path.isfile(file):
                img = file
            else:
                img = self.find_image(id)
            
        log.debug("track: %s" % info)

        self.update_item(id, info, img)
        
    def __notify_repeat(self, repeat):
        
        self.__repeat = repeat > 0
        self.update_repeat(self.__repeat)
    
    def __notify_shuffle(self, shuffle):
        
        self.__shuffle = shuffle > 0
        self.update_shuffle(self.__shuffle)
        
    def __notify_progress(self, ms):
        
        self.update_progress(ms / 1000, self.__progress_length)

    def __dbus_error(self, error):
        """ DBus error handler. """
        
        if self.__bsc is None:
            return # do not log errors when not stopped already
        
        log.warning("dbus error: %s" % error)
        
    def __dbus_ignore(self):
        """ DBus reply handler for methods without reply. """
        
        pass
        
# =============================================================================
# main
# =============================================================================

if __name__ == '__main__':

    ba = BansheeAdapter()
    mg = remuco.Manager(ba, player_dbus_name=DBUS_NAME)
    
    mg.run()
