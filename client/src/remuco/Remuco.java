package remuco;

import javax.microedition.lcdui.Alert;
import javax.microedition.lcdui.AlertType;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Form;
import javax.microedition.midlet.MIDlet;
import javax.microedition.midlet.MIDletStateChangeException;

import remuco.ui.CMD;
import remuco.ui.Theme;
import remuco.ui.UI;
import remuco.util.FormLogger;
import remuco.util.Log;

/**
 * MIDlet of the Remuco client.
 * <p>
 * <h1>Some general notes about the client source</h1>
 * A lot of classes are declared as <code>final</code>. This has no software
 * design specific but performance reason. There a lot of discussion in the net
 * about using final classes (and so methods) for performance reasons. To draw a
 * conclusion of these discussions it is actually bad style to use final classes
 * to improve performance since it may confuse other developers and since the
 * performance benefit is probably very small (due to nowadays very
 * sophisticated JIT compilers). However, in my understanding the last point is
 * valid for Java code running in JREs but it is unclear if it applies to a
 * J2ME-RE. So final classes may still improve performance. This is an
 * assumption. Once it is proved that this assumption is wrong, I will undo all
 * the performance related final declaration of classes.
 * <h1>Emulator Code</h1>
 * Some code is only used to while running inside the WTK emulator. All
 * corresponding code is either tagged with <code>emulator</code> in its JavaDoc
 * or is located inside an if-statement block using the condition
 * {@link #EMULATION}.
 * 
 * @author Oben Sonne
 * 
 */
public final class Remuco extends MIDlet implements CommandListener {

	/**
	 * @emulator If <code>true</code>, the client runs inside the WTK emulator.
	 */
	public static boolean EMULATION = false;

	/** Command for the log form to run the garbage collector */
	private static final Command CMD_RUNGC = new Command("Run GC",
			Command.SCREEN, 2);

	/** Command for the log form to show memory status */
	private static final Command CMD_SYSINFO = new Command("System",
			Command.SCREEN, 1);

	private final Alert alertLoadConfig;

	private final Alert alertSaveConfig;

	private final boolean configSuccessfullyLoaded;

	private final Display display;

	private Displayable displayableAfterLog;

	private final Form logForm;

	/** Alert displaying current memory status */
	private final Form logSysInfoForm;

	/** Text for the memory status alert */
	private final StringBuffer logSysInfoText;

	/**
	 * We need to know this since {@link #startApp()} might get called more than
	 * once (e.g. after we have been paused).
	 */
	private boolean startAppFirstTime = true;

	private final UI ui;

	public Remuco() {

		String emu = this.getAppProperty("Remuco-emulation");

		EMULATION = emu != null && emu.equalsIgnoreCase("true");

		// get the display

		display = Display.getDisplay(this);

		Theme.loadListIcons(display.getBestImageWidth(Display.LIST_ELEMENT));

		// set up logging

		logSysInfoText = new StringBuffer();

		logSysInfoForm = new Form("System Info");
		logSysInfoForm.addCommand(CMD_RUNGC);
		logSysInfoForm.addCommand(CMD.BACK);
		logSysInfoForm.setCommandListener(this);

		logForm = new Form("Log");
		logForm.addCommand(CMD.BACK);
		logForm.addCommand(CMD_SYSINFO);
		logForm.setCommandListener(this);
		if (EMULATION) {
			Log.ln("RUNING IN EMULATION MODE ..");
			logForm.append("Emulation -> logging goes to standard out!");
		} else {
			Log.setOut(new FormLogger(logForm));
		}

		// load the configuration

		configSuccessfullyLoaded = Config.load();

		Config.setApplicationProperties(this);

		// set up some displayables

		alertLoadConfig = new Alert("Error");
		alertLoadConfig.setString("Erros while loading configuration. "
				+ "Please inspect the log for details! Configuration erros "
				+ "are normal, if you installed a new version of the client.");
		alertLoadConfig.setType(AlertType.ERROR);
		alertLoadConfig.setTimeout(Alert.FOREVER);
		alertLoadConfig.setCommandListener(this);

		alertSaveConfig = new Alert("Error");
		alertSaveConfig.setString("Erros while saving configuration."
				+ " Please inspect the log for details!");
		alertSaveConfig.setType(AlertType.ERROR);
		alertSaveConfig.setTimeout(Alert.FOREVER);
		alertSaveConfig.setCommandListener(this);

		// set up the start screen

		ui = new UI(this, display);

	}

	public void commandAction(Command c, Displayable d) {

		if (c == CMD.LOG) {

			displayableAfterLog = d;

			display.setCurrent(logForm);

		} else if (c == CMD_RUNGC) {

			System.gc();

		} else if (c == CMD.BACK && d == logSysInfoForm) {

			display.setCurrent(logForm);

		} else if (c == CMD_RUNGC && d == logSysInfoForm) {

			// run garbage collector

			System.gc();

			updateSysInfoForm();

		} else if (c == CMD_SYSINFO) {

			// show memory usage

			updateSysInfoForm();

			display.setCurrent(logSysInfoForm);

		} else if (c == CMD.BACK && d == logForm) {

			// display the displayable shown before the log

			if (displayableAfterLog != null)
				display.setCurrent(displayableAfterLog);
			else
				Log.ln("A BUG !! Do not know what to show after Log !?");

		} else if (c == CMD.EXIT) {

			if (!Config.save())
				display.setCurrent(alertSaveConfig);
			else
				notifyDestroyed();

		} else if (c == Alert.DISMISS_COMMAND && d == alertLoadConfig) {

			// continue start up

			ui.showYourself();

		} else if (c == Alert.DISMISS_COMMAND && d == alertSaveConfig) {

			// continue shut down

			notifyDestroyed();

		} else {

			Log.ln("[ROOT] unexpected command: " + c.getLabel());

		}

	}

	protected void destroyApp(boolean unconditional)
			throws MIDletStateChangeException {

		Config.save();

	}

	protected void pauseApp() {

		Log.ln("[RM] paused");

	}

	protected void startApp() throws MIDletStateChangeException {

		if (startAppFirstTime) {

			startAppFirstTime = false;

			if (!configSuccessfullyLoaded) {
				display.setCurrent(alertLoadConfig);
				return;
			}

			ui.showYourself();

			Log.ln("[RM] started");

		} else {

			Log.ln("[RM] unpaused");

		}

	}

	private void updateSysInfoForm() {

		logSysInfoForm.deleteAll();
		logSysInfoText.delete(0, logSysInfoText.length());

		final long memTotal = Runtime.getRuntime().totalMemory() / 1024;
		final long memFree = Runtime.getRuntime().freeMemory() / 1024;
		final long memUsed = memTotal - memFree;

		logSysInfoText.append("--- Memory --- \n");
		logSysInfoText.append("Total : ").append(memTotal).append(" KB\n");
		logSysInfoText.append("Used  : ").append(memUsed).append(" KB\n");
		logSysInfoText.append("Free  : ").append(memFree).append(" KB\n");
		logSysInfoText.append("--- Misc --- \n");
		logSysInfoText.append("UTF-8 : ");
		logSysInfoText.append(Config.UTF8 ? "yes" : "no").append("\n");

		logSysInfoForm.append(logSysInfoText.toString());

	}

}
