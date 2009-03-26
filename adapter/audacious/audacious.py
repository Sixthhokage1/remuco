#!/usr/bin/python

# =============================================================================
#
#    Remuco - A remote control system for media players.
#    Copyright (C) 2006-2009 Oben Sonne <obensonne@googlemail.com>
#
#    This file is part of Remuco.
#
#    Remuco is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Remuco is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Remuco.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================

"""Remuco player adapter for Audacious, implemented as an executable script."""

import dbus
from dbus.exceptions import DBusException
import gobject

import remuco
from remuco import log

# =============================================================================
# actions
# =============================================================================

IA_JUMP = remuco.ItemAction("Jump to")
PLAYLIST_ACTIONS = (IA_JUMP,)

# =============================================================================
# player adapter
# =============================================================================

class AudaciousAdapter(remuco.MPRISAdapter):
    
    def __init__(self):
        
        remuco.MPRISAdapter.__init__(self, "audacious", "Audacious",
                                     mime_types=("audio",),
                                     extra_playlist_actions=PLAYLIST_ACTIONS)
        
        self.__ad = None
        self.__poll_for_repeat_and_shuffle = False
        
    def start(self):
        
        remuco.MPRISAdapter.start(self)
        
        try:
            bus = dbus.SessionBus()
            proxy = bus.get_object("org.atheme.audacious", "/org/atheme/audacious")
            self.__ad = dbus.Interface(proxy, "org.atheme.audacious")
        except DBusException, e:
            raise StandardError("dbus error: %s" % e)

    def stop(self):
        
        remuco.MPRISAdapter.stop(self)
        
        self.__ad = None
        
    def poll(self):

        remuco.MPRISAdapter.poll(self)

        if self.__poll_for_repeat_and_shuffle:
            self.__poll_repeat()
            self.__poll_shuffle()
        
    def __poll_repeat(self):
        
        # used if audacious still does not provide this by signal "StatusChange"
        
        try:
            repeat = bool(self.__ad.Repeat())
        except DBusException, e:
            log.warning("dbus error: %s" % e)
            repeat = False
            
        self._repeat = repeat
        self.update_repeat(repeat)
        
    def __poll_shuffle(self):
        
        # used if audacious still does not provide this by signal "StatusChange"
        
        try:
            shuffle = bool(self.__ad.Shuffle())
        except DBusException, e:
            log.warning("dbus error: %s" % e)
            shuffle = False
            
        self._shuffle = shuffle
        self.update_shuffle(shuffle)
        
    # =========================================================================
    # control interface 
    # =========================================================================
    
    def ctrl_toggle_repeat(self):
        
        # audacious uses wrong method name for setting repeat mode
        
        try:
            self._mp_t.Loop(not self._repeat,
                            reply_handler=self._dbus_ignore,
                            error_handler=self._dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
            
        if self.__poll_for_repeat_and_shuffle:
            self.__poll_repeat()
    
    def ctrl_toggle_shuffle(self):
        
        # audacious uses wrong method name for setting shuffle mode
        
        try:
            self._mp_t.Random(not self._shuffle,
                              reply_handler=self._dbus_ignore,
                              error_handler=self._dbus_error)
        except DBusException, e:
            log.warning("dbus error: %s" % e)
        
        if self.__poll_for_repeat_and_shuffle:
            self.__poll_shuffle()
    
    # =========================================================================
    # actions interface
    # =========================================================================
    
    def action_playlist_item(self, action_id, positions, ids):
        
        if action_id == IA_JUMP.id:
            
            try:
                self.__ad.Jump(positions[0],
                               reply_handler=self._dbus_ignore,
                               error_handler=self._dbus_error)
            except DBusException, e:
                log.warning("dbus error: %s" % e)
            
        else:
            remuco.MPRISAdapter.action_playlist_item(self, action_id,
                                                     positions, ids)
        
        
    # =========================================================================
    # internal methods which must be adapted to provide MPRIS conformity
    # =========================================================================
    
    def _notify_status(self, status):

        if isinstance(status, int):
            # audacious only provides playback status here
            self.__poll_for_repeat_and_shuffle = True
            status = (status, self._shuffle, self._repeat, self._repeat)
        else:
            # it looks like audacious has fixed its MPRIS interface
            self.__poll_for_repeat_and_shuffle = False
        
        remuco.MPRISAdapter._notify_status(self, status)
        
    def _notify_track(self, track):
        
        # audacious provides length in 'length', not in 'time' or 'mtime'
        
        if "length" in track:
            track["mtime"] = track["length"]
            track["time"] = int(track["length"] // 1000)
            
        # audacious provides length in 'URI', not in 'location'
        
        if "URI" in track:
            track["location"] = track["URI"]
            
        remuco.MPRISAdapter._notify_track(self, track)

# =============================================================================
# main
# =============================================================================

if __name__ == '__main__':

    pa = AudaciousAdapter()
    mg = remuco.Manager(pa, player_dbus_name="org.mpris.audacious")
    
    mg.run()

