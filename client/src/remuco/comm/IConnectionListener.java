/*   
 *   Remuco - A remote control system for media players.
 *   Copyright (C) 2006-2009 Oben Sonne <obensonne@googlemail.com>
 *
 *   This file is part of Remuco.
 *
 *   Remuco is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   Remuco is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with Remuco.  If not, see <http://www.gnu.org/licenses/>.
 *   
 */
package remuco.comm;

import remuco.UserException;
import remuco.player.PlayerInfo;

/**
 * Interface for classes interested in the state of a {@link Connection}.
 * 
 * @see Connection#Connection(String, IConnectionListener, IMessageListener)
 * 
 * @author Oben Sonne
 */
public interface IConnectionListener {

	/**
	 * Notifies a successful connection.
	 * @param conn the connected connection
	 * @param pinfo information about the connected player
	 */
	public void notifyConnected(Connection conn, PlayerInfo pinfo);

	/**
	 * Notifies a disconnection caused by the reason described in
	 * <i>reason</i>.
	 */
	public void notifyDisconnected(UserException reason);

}
