import tkinter as tk
from tkinter import messagebox, ttk
import time
import datetime
import json
import os
import sys
import pygame

SAVE_FILE = 'timers_save.json'
SETTINGS_FILE = 'settings.json'

pygame.mixer.init()
ALARM_ACTIVE = False

base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
LOFI_PATH = os.path.join(base_path, 'lofi.wav')

APP_BG = '#1f232a'
PANEL_BG = '#252a33'
ROW_BG = '#2b313c'
ROW_BORDER = '#3a404c'
INPUT_BG = '#11151b'
LABEL_BG = '#20252d'
TEXT_FG = '#f3f4f6'
MUTED_FG = '#c7cbd4'
ACCENT_BG = '#374151'
ACCENT_DARK = '#1f2937'


class TimerRow:
    def __init__(self, master, remove_cb):
        self.frame = tk.Frame(master, bg=ROW_BG, highlightbackground=ROW_BORDER, highlightthickness=1)

        self.name = tk.Entry(self.frame, width=18, bg=INPUT_BG, fg='#00ffaa', insertbackground='white', relief='flat')
        self.name.insert(0, 'Timer')

        self.seconds = tk.Entry(self.frame, width=8, bg=INPUT_BG, fg='#00ccff', insertbackground='white', relief='flat')
        self.seconds.insert(0, '60')

        self.label = tk.Label(self.frame, text='00:00:00', width=10, bg=LABEL_BG, fg=TEXT_FG)

        self.progress = ttk.Progressbar(self.frame, length=140, mode='determinate')

        self.end_label = tk.Label(self.frame, text='Fin: --:--:--', width=14, bg=ROW_BG, fg=MUTED_FG)

        self.edit_open = False

        self.toggle_btn = tk.Button(self.frame, text='±', command=self.toggle_edit, bg=ACCENT_BG, fg='white', width=3, relief='flat', activebackground='#4b5563', activeforeground='white')

        self.plus10_btn = tk.Button(self.frame, text='+10', command=lambda: self.modify_time(10), bg='#164e63', fg='white', relief='flat', activebackground='#155e75', activeforeground='white')
        self.minus10_btn = tk.Button(self.frame, text='-10', command=lambda: self.modify_time(-10), bg='#164e63', fg='white', relief='flat', activebackground='#155e75', activeforeground='white')
        self.plus60_btn = tk.Button(self.frame, text='+60', command=lambda: self.modify_time(60), bg='#1d4ed8', fg='white', relief='flat', activebackground='#2563eb', activeforeground='white')
        self.minus60_btn = tk.Button(self.frame, text='-60', command=lambda: self.modify_time(-60), bg='#1d4ed8', fg='white', relief='flat', activebackground='#2563eb', activeforeground='white')
        self.plus1k_btn = tk.Button(
            self.frame,
            text='+1000',
            command=lambda: self.add_input_time(1000),
            bg='#2563eb',
            fg='white',
            relief='flat',
            activebackground='#3b82f6',
            activeforeground='white'
        )

        self.plus10k_btn = tk.Button(
            self.frame,
            text='+10000',
            command=lambda: self.add_input_time(10000),
            bg='#7c3aed',
            fg='white',
            relief='flat',
            activebackground='#8b5cf6',
            activeforeground='white'
        )

        self.start_btn = tk.Button(self.frame, text='Start', command=self.start, bg='#14532d', fg='white', relief='flat', activebackground='#166534', activeforeground='white')
        self.reset_btn = tk.Button(self.frame, text='Reset', command=self.reset, bg='#7f1d1d', fg='white', relief='flat', activebackground='#991b1b', activeforeground='white')
        self.del_btn = tk.Button(self.frame, text='X', command=lambda: remove_cb(self), bg='#444444', fg='white', relief='flat', activebackground='#525252', activeforeground='white')

        widgets = [
            self.name,
            self.seconds,
            self.label,
            self.progress,
            self.end_label,
            self.toggle_btn,
            self.plus1k_btn,
            self.plus10k_btn,
            self.start_btn,
            self.reset_btn,
            self.del_btn
        ]

        for w in widgets:
            w.pack(side='left', padx=3)

        self.edit_widgets = [self.plus10_btn, self.minus10_btn, self.plus60_btn, self.minus60_btn]

        self.frame.pack(fill='x', pady=5, padx=8, ipadx=5, ipady=5)

        self.running = False
        self.end_time = None
        self.total_duration = 0

    def toggle_edit(self):
        self.edit_open = not self.edit_open
        if self.edit_open:
            for w in self.edit_widgets:
                w.pack(side='left', padx=2)
        else:
            for w in self.edit_widgets:
                w.pack_forget()

    def add_input_time(self, val):
        if self.running:
            self.end_time += val
            self.total_duration += val
            App.instance.save_all()
            return

        self.seconds.delete(0, 'end')
        self.seconds.insert(0, str(val))
        self.start()

    def modify_time(self, val):
        if self.running:
            self.end_time += val
            self.total_duration += val
            App.instance.save_all()

    def start(self):
        try:
            secs = int(float(self.seconds.get()))
            self.total_duration = secs
            self.end_time = time.time() + secs

            end_dt = datetime.datetime.now() + datetime.timedelta(seconds=secs)
            self.end_label.config(text='Fin: ' + end_dt.strftime('%H:%M:%S'))

            self.running = True
            App.instance.save_all()
        except:
            messagebox.showerror('Erreur', 'Secondes invalides')

    def reset(self):
        global ALARM_ACTIVE

        self.running = False
        self.progress['value'] = 0

        self.label.config(text='00:00:00', bg=LABEL_BG, fg=TEXT_FG)
        self.end_label.config(text='Fin: --:--:--')

        pygame.mixer.music.stop()
        ALARM_ACTIVE = False

        App.instance.save_all()

    def tick(self):
        global ALARM_ACTIVE

        if not self.running:
            if self.label.cget("text") != "FINI":
                self.label.config(
                    text='00:00:00',
                    bg=LABEL_BG,
                    fg=TEXT_FG
                )

                self.progress['value'] = 0

            return

        remain = int(self.end_time - time.time())

        if remain <= 0:
            self.running = False
            self.progress['value'] = 100

            self.label.config(
                text='FINI',
                bg='#7f1d1d',
                fg='white'
            )

            if not ALARM_ACTIVE and os.path.exists(LOFI_PATH):
                pygame.mixer.music.load(LOFI_PATH)
                pygame.mixer.music.play(-1)
                ALARM_ACTIVE = True

            return

        h = remain // 3600
        m = (remain % 3600) // 60
        s = remain % 60

        self.label.config(text=f'{h:02}:{m:02}:{s:02}')

        progress = (
            ((self.total_duration - remain) / self.total_duration) * 100
            if self.total_duration > 0 else 0
        )

        self.progress['value'] = max(0, min(100, progress))

        ratio = min(1, max(0, remain / 7200))

        r = int(200 * (1 - ratio) + 40 * ratio)
        g = int(100 * ratio + 20)

        self.label.config(
            bg=f'#{r:02x}{g:02x}20',
            fg='white'
        )


class App:
    instance = None

    def __init__(self, root):
        App.instance = self

        self.root = root

        root.title('Elevage')
        root.geometry('1250x650')
        root.configure(bg=APP_BG)
        root.iconbitmap(os.path.join(base_path, 'ico.ico'))

        default_font = ('Segoe UI', 12)
        root.option_add('*Font', default_font)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass

        style.configure('TProgressbar', troughcolor='#161b22', background='#22c55e', bordercolor='#161b22', lightcolor='#22c55e', darkcolor='#22c55e', thickness=12)

        top = tk.Frame(root, bg=APP_BG)
        top.pack(pady=12)

        tk.Button(top, text='＋ Timer', command=self.add, bg='#3b4252', fg='white', relief='flat', activebackground='#4b5563', activeforeground='white').pack(side='left', padx=5)
        tk.Button(top, text='▶ Start All', command=self.start_all, bg='#14532d', fg='white', relief='flat', activebackground='#166534', activeforeground='white').pack(side='left', padx=5)
        tk.Button(top, text='■ Reset All', command=self.reset_all, bg='#7f1d1d', fg='white', relief='flat', activebackground='#991b1b', activeforeground='white').pack(side='left', padx=5)

        tk.Label(top, text='Volume', bg=APP_BG, fg=TEXT_FG).pack(side='left', padx=(20, 5))

        self.vol = tk.Scale(top, from_=0, to=100, orient='horizontal', length=160, bg=APP_BG, fg=TEXT_FG, highlightthickness=0, troughcolor='#11151b', activebackground='#60a5fa', command=self.set_volume)
        self.vol.pack(side='left')

        self.body = tk.Frame(root, bg=PANEL_BG)
        self.body.pack(fill='both', expand=True, padx=12, pady=8)

        self.rows = []

        for _ in range(6):
            self.add()

        self.load_settings()
        self.load_all()

        self.loop()

    def save_settings(self):
        data = {'volume': self.vol.get()}
        with open(SETTINGS_FILE, 'w', encoding='utf8') as f:
            json.dump(data, f)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            data = json.load(open(SETTINGS_FILE, 'r', encoding='utf8'))
            self.vol.set(data.get('volume', 15))
        else:
            self.vol.set(15)

    def save_all(self):
        data = []
        for r in self.rows:
            data.append({
                'name': r.name.get(),
                'seconds': r.seconds.get(),
                'end_time': r.end_time,
                'running': r.running,
                'total_duration': r.total_duration
            })

        with open(SAVE_FILE, 'w', encoding='utf8') as f:
            json.dump(data, f)

    def load_all(self):
        if not os.path.exists(SAVE_FILE):
            return

        data = json.load(open(SAVE_FILE, 'r', encoding='utf8'))

        for i, row in enumerate(self.rows):
            if i >= len(data):
                break

            d = data[i]

            row.name.delete(0, 'end')
            row.name.insert(0, d.get('name', 'Timer'))

            row.seconds.delete(0, 'end')
            row.seconds.insert(0, str(d.get('seconds', '60')))

            row.end_time = d.get('end_time')
            row.running = d.get('running', False)
            row.total_duration = d.get('total_duration', 0)

            if row.end_time and row.end_time <= time.time():
                row.running = False
                row.label.config(text='FINI', bg='#7f1d1d', fg='white')
                row.progress['value'] = 100

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val) / 100)
        self.save_settings()

    def start_all(self):
        for r in self.rows:
            r.start()

    def reset_all(self):
        for r in self.rows:
            r.reset()

    def add(self):
        row = TimerRow(self.body, self.remove)
        self.rows.append(row)

    def remove(self, row):
        row.frame.destroy()
        self.rows.remove(row)

    def loop(self):
        for r in self.rows:
            r.tick()

        self.save_all()
        self.root.after(250, self.loop)


root = tk.Tk()
App(root)
root.mainloop()