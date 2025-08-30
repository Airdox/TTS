import tkinter as tk
from tkinter import messagebox

def test_gui():
    messagebox.showinfo("Test", "GUI funktioniert!")

def start_tts():
    messagebox.showinfo("TTS", "TTS würde hier starten...")

# Hauptfenster erstellen
root = tk.Tk()
root.title("TTS Test GUI")
root.geometry("400x300")

# Label
label = tk.Label(root, text="TTS Test Anwendung", font=("Arial", 16))
label.pack(pady=20)

# Test Button
test_btn = tk.Button(root, text="GUI Test", command=test_gui, bg="lightblue")
test_btn.pack(pady=10)

# TTS Button
tts_btn = tk.Button(root, text="TTS Test", command=start_tts, bg="lightgreen")
tts_btn.pack(pady=10)

# Info Label
info_label = tk.Label(root, text="Wenn Sie diese GUI sehen können, funktioniert Tkinter korrekt.")
info_label.pack(pady=20)

root.mainloop()
