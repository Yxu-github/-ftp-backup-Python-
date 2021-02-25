import tkinter as Tkinter
from tkinter import ttk
import time
import win32
import threading
class PopupProgressBar:
    def __init__(self, title):
        self.title = title
        self.root = None
        self.bar = None
        self.bar_lock = threading.Lock()
        self.thread = None
        self.thread_upd = None
        self.is_stop_thread_upd = False
        self.value = 0
        self.text = ""
        self.labelText = None  # Tkinter.StringVar()
        if not self.title:
            self.title = "PopupProgressBar"

    def start(self):
        self.thread = threading.Thread(target=PopupProgressBar._run_, args=(self,))
        self.thread.daemon=True
        self.thread.start()

    def _run_(self):
        root = Tkinter.Tk()
        root.geometry('500x80+500+200')
        root.title(self.title)
        self.root = root

        self.labelText = Tkinter.StringVar(self.root)
        self.labelText.set(self.text)

        ft = ttk.Frame(self.root)
        ft.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)

        label1 = Tkinter.Label(ft, textvariable=self.labelText)
        label1.pack(fill=Tkinter.X, side=Tkinter.TOP)

        pb_hD = ttk.Progressbar(ft, orient='horizontal', length=300, mode='determinate')
        pb_hD.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)


        self.bar = pb_hD
        self.bar["maximum"] = 100
        self.bar["value"] = 0


        self.thread_upd = threading.Thread(target=PopupProgressBar._update_, args=(self,))
        self.thread_upd.daemon=True
        self.thread_upd.start()

        self.root.mainloop()

    def _update_(self):
        while not self.is_stop_thread_upd:
            try:
                self.update_data(self.value)
                self.labelText.set(self.text)
                time.sleep(0.01)
            except Exception:
                return
    def update_data(self, value):
        if not self.bar:
            return
        if self.bar_lock.acquire():
            self.bar["value"] = value
            self.bar_lock.release()

    def stop(self):
        if self.root:
            self.root.quit()
        print(1)
        if self.thread_upd:
            self.is_stop_thread_upd = True
            self.thread_upd.join()
        print(2)
        if self.thread:
            self.thread.join()
        print(3)


