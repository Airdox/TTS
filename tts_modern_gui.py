import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

APP_COLOR = "#222831"
ACCENT_COLOR = "#00adb5"
BG_COLOR = "#393e46"
FG_COLOR = "#eeeeee"
BTN_COLOR = "#00adb5"
BTN_TEXT = "#222831"

class ModernTTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TTS & Voice Cloning Studio")
        self.geometry("700x600")
        self.configure(bg=APP_COLOR)
        self.iconify()
        self.deiconify()
        self.resizable(False, False)
        self.create_style()
        self.create_widgets()

    def create_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background=APP_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', background=BG_COLOR, foreground=FG_COLOR, font=('Segoe UI', 12, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', ACCENT_COLOR)])
        style.configure('TFrame', background=APP_COLOR)
        style.configure('TLabel', background=APP_COLOR, foreground=FG_COLOR, font=('Segoe UI', 11))
        style.configure('TButton', background=BTN_COLOR, foreground=BTN_TEXT, font=('Segoe UI', 11, 'bold'))
        style.map('TButton', background=[('active', ACCENT_COLOR)])
        style.configure('TEntry', fieldbackground=BG_COLOR, foreground=FG_COLOR)

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tab 1: Standard TTS
        tts_frame = ttk.Frame(notebook)
        self.create_tts_tab(tts_frame)
        notebook.add(tts_frame, text="Text-to-Speech")

        # Tab 2: Voice Cloning
        clone_frame = ttk.Frame(notebook)
        self.create_clone_tab(clone_frame)
        notebook.add(clone_frame, text="Voice Cloning")

    def create_tts_tab(self, frame):
        title = ttk.Label(frame, text="Text-to-Speech", font=("Segoe UI", 18, "bold"), foreground=ACCENT_COLOR)
        title.pack(pady=(10, 5))
        subtitle = ttk.Label(frame, text="Geben Sie Text ein und generieren Sie Sprache mit einem Klick.")
        subtitle.pack(pady=(0, 15))

        text_label = ttk.Label(frame, text="Text eingeben:")
        text_label.pack(anchor=tk.W, padx=10)
        self.tts_text = tk.Text(frame, height=5, font=("Segoe UI", 11), bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR)
        self.tts_text.pack(fill=tk.X, padx=10, pady=5)

        output_label = ttk.Label(frame, text="Ausgabedatei:")
        output_label.pack(anchor=tk.W, padx=10, pady=(10,0))
        output_frame = tk.Frame(frame, bg=APP_COLOR)
        output_frame.pack(fill=tk.X, padx=10)
        self.tts_output_path = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=self.tts_output_path, font=("Segoe UI", 10), bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        output_btn = tk.Button(output_frame, text="Speichern unter", bg=BTN_COLOR, fg=BTN_TEXT, command=self.select_tts_output)
        output_btn.pack(side=tk.RIGHT, padx=(5,0))

        synth_btn = tk.Button(frame, text="Sprachsynthese starten", bg=ACCENT_COLOR, fg=BTN_TEXT, font=("Segoe UI", 12, "bold"), command=self.synthesize_tts)
        synth_btn.pack(pady=20)

    def create_clone_tab(self, frame):
        title = ttk.Label(frame, text="Voice Cloning", font=("Segoe UI", 18, "bold"), foreground=ACCENT_COLOR)
        title.pack(pady=(10, 5))
        subtitle = ttk.Label(frame, text="Klonen Sie Ihre Stimme mit einer Referenzaufnahme.")
        subtitle.pack(pady=(0, 15))

        ref_label = ttk.Label(frame, text="Referenz-Audiodatei (WAV):")
        ref_label.pack(anchor=tk.W, padx=10)
        ref_frame = tk.Frame(frame, bg=APP_COLOR)
        ref_frame.pack(fill=tk.X, padx=10)
        self.clone_ref_path = tk.StringVar()
        ref_entry = tk.Entry(ref_frame, textvariable=self.clone_ref_path, font=("Segoe UI", 10), bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        ref_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ref_btn = tk.Button(ref_frame, text="Durchsuchen", bg=BTN_COLOR, fg=BTN_TEXT, command=self.select_clone_ref)
        ref_btn.pack(side=tk.RIGHT, padx=(5,0))

        text_label = ttk.Label(frame, text="Text eingeben:")
        text_label.pack(anchor=tk.W, padx=10, pady=(10,0))
        self.clone_text = tk.Text(frame, height=5, font=("Segoe UI", 11), bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR)
        self.clone_text.pack(fill=tk.X, padx=10, pady=5)

        output_label = ttk.Label(frame, text="Ausgabedatei:")
        output_label.pack(anchor=tk.W, padx=10, pady=(10,0))
        output_frame = tk.Frame(frame, bg=APP_COLOR)
        output_frame.pack(fill=tk.X, padx=10)
        self.clone_output_path = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=self.clone_output_path, font=("Segoe UI", 10), bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        output_btn = tk.Button(output_frame, text="Speichern unter", bg=BTN_COLOR, fg=BTN_TEXT, command=self.select_clone_output)
        output_btn.pack(side=tk.RIGHT, padx=(5,0))

        synth_btn = tk.Button(frame, text="Voice Cloning starten", bg=ACCENT_COLOR, fg=BTN_TEXT, font=("Segoe UI", 12, "bold"), command=self.synthesize_clone)
        synth_btn.pack(pady=20)

    def select_tts_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.tts_output_path.set(file_path)

    def select_clone_ref(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.clone_ref_path.set(file_path)

    def select_clone_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.clone_output_path.set(file_path)

    def synthesize_tts(self):
        text = self.tts_text.get("1.0", tk.END).strip()
        output = self.tts_output_path.get()
        if not text:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Text ein.")
            return
        if not output:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Speicherort für die Ausgabedatei.")
            return
        try:
            from TTS.api import TTS
            tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC")
            tts.tts_to_file(text=text, file_path=output)
            messagebox.showinfo("Erfolg", "Die Sprachsynthese wurde erfolgreich abgeschlossen!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Sprachsynthese: {e}")

    def synthesize_clone(self):
        text = self.clone_text.get("1.0", tk.END).strip()
        ref = self.clone_ref_path.get()
        output = self.clone_output_path.get()
        if not ref:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Referenz-Audiodatei aus.")
            return
        if not text:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Text ein.")
            return
        if not output:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Speicherort für die Ausgabedatei.")
            return
        try:
            from TTS.api import TTS
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            tts.tts_to_file(text=text, speaker_wav=ref, language="de", file_path=output)
            messagebox.showinfo("Erfolg", "Voice Cloning erfolgreich abgeschlossen!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Voice Cloning: {e}")

if __name__ == "__main__":
    app = ModernTTSApp()
    app.mainloop()
docker run --rm ghcr.io/coqui-ai/tts-cpu python3 TTS/server/server.py --list_modelsdocker run --rm -it -p 5002:5002 ghcr.io/coqui-ai/tts-cpu python3 TTS/server/server.py --model_name tts_models/en/ljspeech/glow-tts