import tkinter as tk
from tkinter import filedialog, messagebox
from TTS.api import synthesize

class TTSApp:
    def __init__(self, master):  # Umbenennen von 'root' zu 'master', um Konflikte zu vermeiden
        print("Initialisiere GUI...")  # Debugging-Ausgabe
        self.master = master
        self.master.title("TTS GUI")

        self.label = tk.Label(master, text="Geben Sie den Text ein, den Sie in Sprache umwandeln möchten:")
        self.label.pack(pady=10)

        self.text_entry = tk.Entry(master, width=50)
        self.text_entry.pack(pady=10)

        self.synthesize_button = tk.Button(master, text="Synthese starten", command=self.synthesize)
        self.synthesize_button.pack(pady=10)

        self.output_label = tk.Label(master, text="Wählen Sie den Speicherort für die Ausgabedatei:")
        self.output_label.pack(pady=10)

        self.output_button = tk.Button(master, text="Speicherort auswählen", command=self.select_output_path)
        self.output_button.pack(pady=10)

        self.output_path = None

    def select_output_path(self):
        self.output_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if self.output_path:
            messagebox.showinfo("Ausgabepfad", f"Ausgabepfad ausgewählt: {self.output_path}")

    def synthesize(self):
        text = self.text_entry.get()
        if not text:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Text ein.")
            return

        if not self.output_path:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Speicherort für die Ausgabedatei.")
            return

        try:
            result = synthesize(text)
            with open(self.output_path, "w") as f:
                f.write(result)
            messagebox.showinfo("Erfolg", "Die Sprachsynthese wurde erfolgreich abgeschlossen!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    print("Starte Tkinter...")  # Debugging-Ausgabe
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
