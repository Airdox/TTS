import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import tempfile

class SimpleTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTS Studio - Thorsten Deutsche Stimme")
        self.root.geometry("600x400")
        self.root.configure(bg="#2c3e50")
        
        # Variables
        self.output_path = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="TTS Studio", font=("Arial", 20, "bold"), 
                        bg="#2c3e50", fg="#ecf0f1")
        title.pack(pady=20)
        
        # Text input
        tk.Label(self.root, text="Text eingeben:", bg="#2c3e50", fg="#ecf0f1", 
                font=("Arial", 12)).pack(anchor="w", padx=20)
        
        self.text_widget = tk.Text(self.root, height=6, width=60, font=("Arial", 11))
        self.text_widget.pack(pady=10, padx=20)
        
        # Output file selection
        output_frame = tk.Frame(self.root, bg="#2c3e50")
        output_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(output_frame, text="Ausgabedatei:", bg="#2c3e50", fg="#ecf0f1", 
                font=("Arial", 12)).pack(anchor="w")
        
        path_frame = tk.Frame(output_frame, bg="#2c3e50")
        path_frame.pack(fill="x", pady=5)
        
        tk.Entry(path_frame, textvariable=self.output_path, font=("Arial", 10)).pack(
            side="left", fill="x", expand=True)
        tk.Button(path_frame, text="Durchsuchen", command=self.select_output,
                 bg="#3498db", fg="white").pack(side="right", padx=(5,0))
        
        # Buttons
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Demo Test", command=self.demo_test,
                 bg="#f39c12", fg="white", font=("Arial", 12, "bold"),
                 padx=20).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="TTS Starten", command=self.start_tts,
                 bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                 padx=20).pack(side="left", padx=10)
    
    def select_output(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def demo_test(self):
        # Set demo text and temp output
        demo_text = "Hallo, das ist ein Test der deutschen Thorsten Stimme."
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, demo_text)
        
        temp_path = os.path.join(tempfile.gettempdir(), "tts_demo.wav")
        self.output_path.set(temp_path)
        
        self.start_tts()
    
    def start_tts(self):
        text = self.text_widget.get("1.0", tk.END).strip()
        output = self.output_path.get()
        
        if not text:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Text ein.")
            return
        
        if not output:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Ausgabedatei.")
            return
        
        try:
            # Show loading message
            self.root.config(cursor="wait")
            self.root.update()
            
            # Import and use TTS
            from TTS.api import TTS #no-space-check
            tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC")
            tts.tts_to_file(text=text, file_path=output)
            
            # Reset cursor
            self.root.config(cursor="")
            
            messagebox.showinfo("Erfolg", f"TTS erfolgreich!\nDatei: {output}")
            
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Fehler", f"TTS Fehler: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTTSApp(root)
    root.mainloop()


import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
