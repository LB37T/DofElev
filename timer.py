import tkinter as tk
from tkinter import messagebox
import time
import datetime
import winsound

class TimerRow:
    def __init__(self, master, remove_cb):
        self.frame = tk.Frame(master)
        self.name = tk.Entry(self.frame, width=20)
        self.name.insert(0, 'Timer')
        self.minutes = tk.Entry(self.frame, width=8)
        self.minutes.insert(0, '60')
        self.label = tk.Label(self.frame, text='00:00:00', width=10)
        self.end_label = tk.Label(self.frame, text='Fin: --:--:--', width=14)
        self.start_btn = tk.Button(self.frame, text='Start', command=self.start)
        self.reset_btn = tk.Button(self.frame, text='Reset', command=self.reset)
        self.del_btn = tk.Button(self.frame, text='X', command=lambda: remove_cb(self))
        for w in [self.name,self.minutes,self.label,self.end_label,self.start_btn,self.reset_btn,self.del_btn]: w.pack(side='left', padx=3)
        self.frame.pack(pady=2, anchor='w')
        self.end_time = None
        self.running = False
    def start(self):
        try:
            secs = float(self.minutes.get())
            self.end_time = time.time() + secs
            end_dt = datetime.datetime.now() + datetime.timedelta(seconds=secs)
            self.end_label.config(text='Fin: ' + end_dt.strftime('%H:%M:%S'))
            self.running = True
        except:
            messagebox.showerror('Erreur','Secondes invalides')
    def reset(self):
        self.running = False
        self.label.config(text='00:00:00')
        self.end_label.config(text='Fin: --:--:--')
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
    def tick(self):
        if self.running:
            remain = int(self.end_time - time.time())
            if remain <= 0:
                self.running = False
                self.label.config(text='FINI')
                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
            else:
                m,s = divmod(remain,60)
                h,m = divmod(m,60)
                self.label.config(text=f'{h:02}:{m:02}:{s:02}')

class App:
    def __init__(self, root):
        self.root = root
        root.title('Multi Timer Elevage')
        root.geometry('760x400')
        root.attributes('-topmost', True)
        top = tk.Frame(root)
        top.pack(pady=8)
        tk.Button(top,text='Ajouter timer',command=self.add).pack()
        self.body = tk.Frame(root)
        self.body.pack(fill='both', expand=True)
        self.rows=[]
        for _ in range(3): self.add()
        self.loop()
    def add(self):
        row = TimerRow(self.body, self.remove)
        self.rows.append(row)
    def remove(self,row):
        row.frame.destroy()
        self.rows.remove(row)
    def loop(self):
        for r in self.rows: r.tick()
        self.root.after(250, self.loop)

root=tk.Tk()
App(root)
root.mainloop()
