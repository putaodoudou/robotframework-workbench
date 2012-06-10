import ttk
import Tkinter as tk
import SocketServer
import StringIO
import Tkinter as tk
import json
from rwb.runner.log import RobotLogTree, RobotLogMessages
from rwb.lib import AbstractRwbApp
from rwb.widgets import Statusbar

from rwb.runner.listener import RemoteRobotListener

NAME = "monitor"
DEFAULT_SETTINGS = {
    NAME: {
        "port": 8910,
        "host": "localhost",
        }
    }

class MonitorApp(AbstractRwbApp):
    def __init__(self):
        AbstractRwbApp.__init__(self, NAME, DEFAULT_SETTINGS)
        self.wm_geometry("900x500")
        port = self.get_setting("monitor.port")
        print "using port", port
        self.listener = RemoteRobotListener(self, port=port, callback=self._listen)
        self.wm_title("rwb.monitor port: %s" % self.listener.port)
        self._create_menubar()
        self._create_statusbar()
        self._create_notebook()
#        self.label = tk.Label(self, text="port: %s" % self.listener.port, anchor="w")
#        self.label.pack(padx=4, pady=4, fill="x")
        self.stack = []
        self.event_id = 0
#        self.status_label.configure(text="port: %s" % self.listener.port)

    def _create_menubar(self):
        self.menubar = tk.Menu(self)
        self.configure(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.file_menu.add_command(label="Exit", command=self._on_exit)

        self.menubar.add_cascade(menu=self.file_menu, label="File", underline=0)

    def _on_exit(self):
        self.destroy()

    def _create_statusbar(self):
        self.statusbar = Statusbar(self)
        self.statusbar.pack(side="bottom", fill="x")
        self.statusbar.add_section("port",12, "port %s" % self.listener.port)
        self.statusbar.add_progress(mode="indeterminate")
        # grip = ttk.Sizegrip(self.statusbar)
        # grip.pack(side="right")
        # self.status_label = ttk.Label(self.statusbar, text="", anchor="w")
        # self.status_label.pack(side="left", fill="both", expand="true", padx=8)
        # self.statusbar.pack(side="bottom", fill="x")

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side="top", fill="both", expand=True)
        self.log_tree = RobotLogTree(self.notebook, auto_open=("failed","suite","test","keyword"))
        self.log_messages = RobotLogMessages(self.notebook)
        self.notebook.add(self.log_tree, text="Details")
        self.notebook.add(self.log_messages, text="Messages")
        self.notebook.pack(side="top", fill="both", expand=True)
        self.listeners = (self.log_tree, self.log_messages)

    def _listen(self, cmd, *args):
        self.event_id += 1
        for listener in self.listeners:
            listener.listen(self.event_id, cmd, args)

        if cmd in ("start_test", "start_suite", "start_keyword"):
            name = args[0]
            cmd_type = cmd.split("_")[1]
            self.stack.append((cmd_type, name))
            self.update_display()
        elif cmd in ("end_test", "end_suite", "end_keyword"):
            cmd_type = cmd.split("_")[1]
            self.stack.pop()
            self.update_display()

    def update_display(self):
        if len(self.stack) == 1:
            self.statusbar.progress_start()
        elif len(self.stack) == 0:
            self.statusbar.progress_stop()

        s = ".".join([x[1] for x in self.stack]).strip()
        self.statusbar.message(s, clear=True, lifespan=0)

if __name__ == "__main__":
    app = MonitorApp()
    app.mainloop()