package remuco.util;

import java.util.Vector;

/**
 * Miscellaneous J2ME specific utility constants and methods.
 * 
 * @author Oben Sonne
 * 
 */
public final class Tools {

	/**
	 * Compare two byte arrays.
	 * 
	 * @param ba1
	 *            (may be null)
	 * @param ba2
	 *            (may be null)
	 * @return <code>true</code> if the arrays equal, <code>false</code>
	 *         otherwise
	 */
	public static boolean compare(byte[] ba1, byte[] ba2) {

		if (ba1 == ba2)
			return true;
		if (ba1 == null || ba2 == null)
			return false;
		if (ba1.length != ba2.length)
			return false;

		for (int i = 0; i < ba2.length; i++) {
			if (ba1[i] != ba2[i]) {
				return false;
			}

		}
		return true;
	}

	/**
	 * Compare two integer arrays.
	 * 
	 * @param ia1
	 *            (may be null)
	 * @param ia2
	 *            (may be null)
	 * @return <code>true</code> if the arrays equal, <code>false</code>
	 *         otherwise
	 */
	public static boolean compare(int[] ia1, int[] ia2) {

		if (ia1 == ia2)
			return true;
		if (ia1 == null || ia2 == null)
			return false;
		if (ia1.length != ia2.length)
			return false;

		for (int i = 0; i < ia1.length; i++) {
			if (ia1[i] != ia2[i])
				return false;
		}

		return true;

	}

	/**
	 * Compare two string arrays.
	 * 
	 * @param sa1
	 *            (may be null)
	 * @param sa2
	 *            (may be null)
	 * @return <code>true</code> if the arrays equal, <code>false</code>
	 *         otherwise
	 */
	public static boolean compare(String[] sa1, String[] sa2) {

		if (sa1 == sa2)
			return true;
		if (sa1 == null || sa2 == null)
			return false;
		if (sa1.length != sa2.length)
			return false;

		for (int i = 0; i < sa1.length; i++) {
			if (!sa1[i].equals(sa2[i]))
				return false;
		}

		return true;

	}

	/**
	 * Compare two vectors.
	 * 
	 * @param v1
	 *            (may be null)
	 * @param v2
	 *            (may be null)
	 * @return <code>true</code> if the vectors equal, <code>false</code>
	 *         otherwise
	 */
	public static boolean compare(Vector v1, Vector v2) {

		if (v1 == v2)
			return true;
		if (v1 == null || v2 == null)
			return false;
		if (v1.size() != v2.size())
			return false;

		for (int i = 0; i < v1.size(); i++) {
			if (!v1.elementAt(i).equals(v2.elementAt(i)))
				return false;
		}

		return true;

	}

	/** Format a time in seconds to something like 'mm:ss'. */
	public static String formatTime(int seconds) {
		final StringBuffer sb = new StringBuffer();
		if (seconds < 0) {
			return "";
		}
		final int s = seconds % 60;
		sb.append((int) (seconds / 60)).append(":");
		sb.append(s < 10 ? "0" : "").append(s);
		return sb.toString();
	}

	/**
	 * Sleep a while. {@link InterruptedException} gets caught but sleeping
	 * won't be continued.
	 * 
	 * @param ms
	 */
	public static void sleep(long ms) {
		try {
			Thread.sleep(ms);
		} catch (InterruptedException e) {
			// e.printStackTrace();
		}
	}

	/**
	 * Splits a string into a string array.
	 * 
	 * @param s
	 * @param splitter
	 * @return
	 */
	public static String[] splitString(String s, char splitter, boolean trim) {

		int first, last, sal;

		first = s.indexOf(splitter);
		sal = 1;
		while (first >= 0) {
			sal++;
			first = s.indexOf(splitter, first + 1);
		}
		final String ret[] = new String[sal];

		first = 0;
		last = s.indexOf(splitter);
		for (int i = 0; i < sal; i++) {
			if ((last = s.indexOf(splitter, first)) < 0) {
				last = s.length();
			}
			ret[i] = s.substring(first, last);
			if (trim) {
				ret[i].trim();
			}
			first = last + 1;
		}
		return ret;
	}

}
