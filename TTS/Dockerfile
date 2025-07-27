# Verwende ein offizielles Python-Image als Basis
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die requirements.txt in den Container und installiere die Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- WICHTIG: PyTorch mit CUDA-Unterstützung installieren ---
# Wähle die passende CUDA-Version für deine Lightning AI GPU-Instanz!
# Beispiel: cu118 für CUDA 11.8. Wenn Lightning AI z.B. CUDA 12.1 hat, nutze cu121.
# Prüfe die Lightning AI Dokumentation für die empfohlenen PyTorch/CUDA-Versionen.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Kopiere den gesamten Projektordner (TTS_Stimmklon) in den Container
# Dies beinhaltet Coqui TTS und deine train_lightning_ai.py
COPY . .

# Installiere Coqui TTS im Container im "editable" Modus
# Dies stellt sicher, dass alle Coqui TTS Skripte und Module verfügbar sind
RUN pip install -e .

# Optional: Wenn du deine Trainingsdaten direkt ins Image packen möchtest (nur für kleine Datensätze!)
# Annahme: Deine Daten liegen im lokalen Ordner 'my_custom_voice_dataset'
COPY my_custom_voice_dataset /app/my_custom_voice_dataset

# Definiere den Befehl, der ausgeführt wird, wenn der Container startet.
# Da Lightning AI das Trainingsskript direkt startet, kann dies einfach ein "Sleep" sein,
# oder ein Befehl, der die Umgebung initialisiert.
# Wir setzen hier einfach 'bash', da Lightning AI den Entrypoint überschreibt.
CMD ["bash"]
