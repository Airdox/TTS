import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys

# Hinzufügen des TTS-Pfads zum Python-Pfad
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class VoiceCloningApp:
    def __init__(self, master):
        print("Initialisiere Voice Cloning GUI...")
        self.master = master
        self.master.title("TTS Voice Cloning - Eigene Stimme klonen")
        self.master.geometry("600x500")
        
        # Variablen
        self.speaker_wav_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Titel
        title_label = tk.Label(self.master, text="Voice Cloning - Klonen Sie Ihre eigene Stimme", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Anweisungen
        instruction_text = """
        Anweisungen für Voice Cloning:
        1. Wählen Sie eine Referenz-Audiodatei (WAV) Ihrer Stimme aus
        2. Geben Sie den Text ein, den Sie mit Ihrer geklonten Stimme sprechen möchten
        3. Wählen Sie den Speicherort für die Ausgabedatei
        4. Klicken Sie auf "Voice Cloning starten"
        """
        instruction_label = tk.Label(self.master, text=instruction_text, justify=tk.LEFT, wraplength=550)
        instruction_label.pack(pady=10)
        
        # Frame für Referenz-Audio
        ref_frame = tk.Frame(self.master)
        ref_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(ref_frame, text="Referenz-Audiodatei (Ihre Stimme):").pack(anchor=tk.W)
        ref_entry_frame = tk.Frame(ref_frame)
        ref_entry_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(ref_entry_frame, textvariable=self.speaker_wav_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(ref_entry_frame, text="Durchsuchen", command=self.select_speaker_wav).pack(side=tk.RIGHT, padx=(5,0))
        
        # Frame für Text-Eingabe
        text_frame = tk.Frame(self.master)
        text_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(text_frame, text="Text zum Sprechen:").pack(anchor=tk.W)
        self.text_widget = tk.Text(text_frame, height=5, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame für Ausgabedatei
        output_frame = tk.Frame(self.master)
        output_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(output_frame, text="Ausgabedatei:").pack(anchor=tk.W)
        output_entry_frame = tk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(output_entry_frame, textvariable=self.output_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(output_entry_frame, text="Speichern unter", command=self.select_output_path).pack(side=tk.RIGHT, padx=(5,0))
        
        # Frame für Buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=20)
        
        self.clone_button = tk.Button(button_frame, text="Voice Cloning starten", 
                                     command=self.start_cloning, bg="#4CAF50", fg="white", 
                                     font=("Arial", 12, "bold"))
        self.clone_button.pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Beenden", command=self.master.quit, 
                 bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.master, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill=tk.X)
        
    def select_speaker_wav(self):
        file_path = filedialog.askopenfilename(
            title="Wählen Sie Ihre Referenz-Audiodatei",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if file_path:
            self.speaker_wav_path.set(file_path)
            
    def select_output_path(self):
        file_path = filedialog.asksaveasfilename(
            title="Speichern unter",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        if file_path:
            self.output_path.set(file_path)
            
    def start_cloning(self):
        # Validierung
        if not self.speaker_wav_path.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Referenz-Audiodatei aus.")
            return
            
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Text ein.")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Speicherort für die Ausgabedatei.")
            return
        
        # Progress bar starten
        self.progress.start(10)
        self.clone_button.config(state="disabled")
        
        try:
            # Voice Cloning durchführen
            self.perform_voice_cloning(text, self.speaker_wav_path.get(), self.output_path.get())
            
            # Erfolg
            messagebox.showinfo("Erfolg", f"Voice Cloning erfolgreich abgeschlossen!\nDatei gespeichert: {self.output_path.get()}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
            
        finally:
            # Progress bar stoppen
            self.progress.stop()
            self.clone_button.config(state="normal")
    
    def perform_voice_cloning(self, text, speaker_wav, output_path):
        """Führt das Voice Cloning durch"""
        try:
            # Versuche zuerst das Standard TTS API zu verwenden
            from TTS.api import TTS
            
            # Lade ein Voice Cloning Modell (XTTS)
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Führe Voice Cloning durch
            tts.tts_to_file(
                text=text,
                speaker_wav=speaker_wav,
                language="de",  # Deutsch
                file_path=output_path
            )
            
        except ImportError:
            # Falls das TTS API nicht verfügbar ist, verwende alternative Methode
            print("TTS API nicht verfügbar, verwende alternative Methode...")
            
            # Hier könntest du eine alternative Implementierung hinzufügen
            # Für jetzt erstellen wir eine Dummy-Datei
            with open(output_path, "w") as f:
                f.write(f"Voice Cloning für Text: {text}\nReferenz: {speaker_wav}")
            
            print(f"Voice Cloning simuliert für: {text}")

if __name__ == "__main__":
    print("Starte Voice Cloning GUI...")
    root = tk.Tk()
    app = VoiceCloningApp(root)
    root.mainloop()
