# --- Fehlerbehandlung ---
$ErrorActionPreference = "Stop" # Stoppt das Skript bei einem Fehler

# --- Variablen ---
$ProjectDir = "TTS" # Name des bestehenden Projektverzeichnisses
# Nicht benötigt, da Projekt bereits vorhanden
$DockerfileFileName = "Dockerfile"
$TotalSteps = 3 # Gesamtzahl der Hauptschritte für den Fortschritt (Docker-Test optional)

# --- Funktionen ---

function Write-StepStatus {
    param(
        [int]$StepNumber,
        [string]$Message
    )
    Write-Host "`n[$StepNumber/$TotalSteps] $Message" -ForegroundColor Cyan
}

function Write-SubStatus {
    param(
        [string]$Message
    )
    Write-Host "  -> $Message" -ForegroundColor DarkGray
}

function Use-ExistingProject {
    Write-StepStatus 1 "Vorbereitung: Bestehendes Coqui TTS Projekt verwenden"
    Write-SubStatus "Nutze das bestehende Verzeichnis '$ProjectDir'."
    if (-not (Test-Path -Path $ProjectDir -PathType Container)) {
        Write-Error "Projektverzeichnis '$ProjectDir' nicht gefunden. Bitte prüfe den Pfad."
        exit 1
    }
    Set-Location $ProjectDir
    Write-SubStatus "Erfolg: Im Verzeichnis '$(Get-Location)' angekommen."
}

function New-Dockerfile {
    Write-StepStatus 2 "Konfiguration: Dockerfile '$DockerfileFileName' erstellen"
    Write-SubStatus "Definiere den Inhalt für das Dockerfile..."
    $dockerfileContent = @"
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
"@
    Set-Content -Path $DockerfileFileName -Value $dockerfileContent
    Write-SubStatus "Dockerfile '$DockerfileFileName' Inhalt geschrieben."
    Write-SubStatus "Erfolg: Dockerfile erstellt."
}

function Create-TrainScript {
    Write-StepStatus 3 "Konfiguration: Trainingsskript '$TrainScriptFileName' erstellen"
    Write-SubStatus "Definiere den Inhalt für das Trainingsskript..."
    $trainScriptContent = @"
import os
import torch
from TTS.trainer import Trainer, TrainerArgs
from TTS.config import BaseDatasetConfig, BaseAudioConfig # Corrected import for BaseAudioConfig
from TTS.tts.configs.xtts_config import XttsConfig # Wichtig für XTTS v2
from TTS.tts.models.xtts import Xtts
from TTS.tts.datasets import load_tts_samples
from TTS.tts.utils.audio import AudioProcessor
from TTS.tts.utils.text.tokenizer import TTSTokenizer # Auch für XTTS relevant

# --- Pfade und Dataset-Vorbereitung ---
# WICHTIG: Passe 'dataset_root_path' an, wo deine Trainingsdaten im Container liegen werden.
# Wenn du deine Daten in den Ordner 'my_custom_voice_dataset' innerhalb von 'TTS_Stimmklon' kopiert hast,
# dann wird der Pfad im Docker-Container '/app/my_custom_voice_dataset' sein.
dataset_root_path = "/app/my_custom_voice_dataset" # Dieser Pfad ist relativ zum WORKDIR im Dockerfile!
output_path = "/app/output" # Wo die trainierten Modelle gespeichert werden sollen

# Stelle sicher, dass der Output-Pfad existiert
os.makedirs(output_path, exist_ok=True)

# --- 1. Dataset Konfiguration ---
# Dies ist ein Beispiel für ein einfaches Dataset mit einer metadata.csv
# Deine metadata.csv sollte folgendes Format haben: "audio/datei1.wav|Dies ist der Text zur Audiodatei."
# Wenn du ein anderes Format oder einen Standard-Datensatz wie LJSpeech verwendest,
# musst du den 'formatter' anpassen.
dataset_config = BaseDatasetConfig(
    formatter="ljspeech", # Wenn dein Dataset wie LJSpeech formatiert ist (audio|text)
                          # Wenn du ein eigenes, einfaches Format hast, könnte 'custom' oder 'line_by_line' passen.
                          # Für ein einfaches Format wie "audio/file.wav|Text" ist "ljspeech" oft ein guter Start.
    meta_file_train="metadata.csv", # Der Name deiner Metadaten-Datei
    path=dataset_root_path # Der Pfad zu deinem Dataset im Container
)

# --- 2. Audio Konfiguration ---
# Passe diese Einstellungen an die Eigenschaften deiner Audiodaten an.
# 22050 Hz ist Standard für viele TTS-Modelle, aber XTTS kann auch höhere Samplerates.
# Stelle sicher, dass deine Trainingsdaten dieser Samplerate entsprechen.
audio_config = BaseAudioConfig(
    sample_rate=22050, # Wähle 22050 für Tacotron2 oder 24000/48000 für XTTS, je nach Quelldaten.
                       # Für XTTS v2 sind 24000Hz oder 48000Hz oft besser.
    do_trim_silence=True, # Entfernt Stille am Anfang und Ende der Audios
    trim_db=60.0,         # Schwellenwert für das Trimmen
    do_normalization=True, # Normalisiere Audio
    # Weitere relevante XTTS-Parameter könnten hier hinzugefügt werden,
    # basierend auf der XTTSConfig AudioProcessor-Sektion.
)

# --- 3. Modell Konfiguration (XTTS v2) ---
# Wir verwenden XTTSConfig für XTTS v2.
# Dies lädt eine Standardkonfiguration für XTTS.
# Für Finetuning von XTTS v2 benötigt man oft ein vortrainiertes Modell.
# Coqui TTS lädt dieses in der Regel automatisch, wenn man es initialisiert.
model_config = XttsConfig()
# XTTS v2 ist ein großes Modell. Es ist NICHT dafür gedacht, von Grund auf neu trainiert zu werden.
# Es wird durch Finetuning auf kleinen Mengen von Zieldaten angepasst.
# Hier könnten spezifische Finetuning-Parameter gesetzt werden, falls in der Coqui-Doku beschrieben.
# Beispiel: model_config.num_epochs = 100 # Weniger Epochen für Finetuning

# --- 4. Initialisierung des Audio-Prozessors ---
# Der Audio-Prozessor wird für die Vorverarbeitung deiner Audiodaten benötigt.
ap = AudioProcessor(**audio_config.to_dict())

# --- 5. Initialisiere den Tokenizer (für XTTS v2) ---
# XTTS v2 ist multilingual, daher muss der Tokenizer das berücksichtigen.
# Coqui TTS kümmert sich um die Details, wenn du ein Sprachmodell angibst.
tokenizer = TTSTokenizer(model_config)

# --- 6. Daten laden ---
# Dies lädt deine Audio-Samples basierend auf der dataset_config
train_samples, eval_samples = load_tts_samples(
    dataset_config,
    eval_split=True,
    eval_split_max_size=model_config.eval_split_max_size,
    eval_split_size=model_config.eval_split_size,
)

# --- 7. Modell initialisieren ---
# Coqui TTS Modelle nehmen ein config-Objekt und einen AudioProcessor (oder SpeakerManager/Tokenizer) als Input.
# Für XTTS:
model = Xtts(model_config, ap, tokenizer, speaker_manager=None) # SpeakerManager ist für Multi-Speaker-Training

# Lade ein vortrainiertes XTTS-Modell, wenn du Finetuning machst.
# Dies ist entscheidend für XTTS-Cloning. Das Skript wird das Modell herunterladen, wenn es nicht da ist.
# Normalerweise musst du hier keinen spezifischen Pfad angeben, da Coqui TTS es von Hugging Face zieht.
# Wenn du ein spezifisches Checkpoint hast, kannst du es hier laden:
# model.load_checkpoint(model_config, checkpoint_path="path/to/your/xtts_checkpoint.pth", eval=False)

# --- 8. Trainer initialisieren ---
# Der Trainer koordiniert den gesamten Trainingsprozess.
# TrainingArgs enthält allgemeine Trainingsparameter
trainer_args = TrainerArgs(
    restore_path=None, # Setze hier den Pfad zu einem Checkpoint, wenn du das Training fortsetzen möchtest
    output_path=output_path,
    epochs=100, # Anzahl der Trainingsepochen. Für Finetuning oft weniger (z.B. 100-500)
    batch_size=32, # Batch-Größe. Passe diese an die GPU-Speicher an. Größere Werte sind schneller, brauchen mehr VRAM.
    eval_batch_size=16,
    num_loader_workers=4, # Anzahl der Worker für den DataLoader
    num_eval_loader_workers=4,
    mixed_precision=True, # Nutze Mixed Precision Training für bessere Performance und geringeren VRAM-Verbrauch
    precision_mode="fp16", # Oder "bf16" falls deine GPU das unterstützt
    # Weitere TrainerArgs, die du anpassen könntest:
    # learning_rate=0.0001,
    # grad_clip=1.0,
    # checkpoint_interval=1000, # Speichere Checkpoints alle 1000 Schritte
    # use_cuda_benchmark=True, # Kann die Performance auf manchen GPUs verbessern
)

trainer = Trainer(
    trainer_args, # Pass the TrainerArgs object
    model_config,
    output_path,
    model=model,
    train_samples=train_samples,
    eval_samples=eval_samples,
    training_assets={"audio_processor": ap, "tokenizer": tokenizer}, # Stelle sicher, dass tokenizer hier übergeben wird
)

# --- 9. Starte das Training ---
Write-Host "Starte das Training des Stimmklon-Modells auf Lightning AI..."
print(f"Dataset Pfad im Container: {dataset_config.path}")
print(f"Output Pfad: {output_path}")
print(f"Anzahl Trainingssamples: {len(train_samples)}")
print(f"Anzahl Evaluierungssamples: {len(eval_samples)}")
print(f"Training mit Modell: {model_config.model_name}")

# Der Trainer kümmert sich um den Trainings-Loop, inkl. Optimierer, Scheduler etc.
# Du kannst hier spezifische Callbacks oder weitere Trainer-Parameter übergeben, wenn nötig.
trainer.fit()

print("Training abgeschlossen! Überprüfe den Output-Ordner für Modelle und Logs.")
"@
    Set-Content -Path $TrainScriptFileName -Value $trainScriptContent
    Write-SubStatus "Trainingsskript '$TrainScriptFileName' Inhalt geschrieben."
    Write-SubStatus "Erfolg: Trainingsskript erstellt."
    Write-Host "WICHTIG: Bearbeite die Datei '$TrainScriptFileName' und passe die Konfigurationen und den Trainings-Loop an deine Daten und das Coqui TTS Framework an!" -ForegroundColor Yellow
}

function Test-DockerImage {
    Write-Host "`n[Optional] Überprüfung: Lokalen Docker-Image-Build testen" -ForegroundColor DarkYellow
    Write-Host "  -> HINWEIS: Dieser Schritt ist optional und kann übersprungen werden." -ForegroundColor DarkGray
    Write-Host "  -> Lightning AI baut das Docker-Image automatisch in der Cloud." -ForegroundColor DarkGray
    Write-Host "  -> Möchtest du trotzdem einen lokalen Test durchführen? (y/N): " -ForegroundColor Yellow -NoNewline
    
    $choice = Read-Host
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Write-Host "  -> Stelle sicher, dass Docker Desktop läuft, bevor du fortfährst!" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2 # Kurze Pause, damit der Benutzer die Nachricht lesen kann

        # Überprüfe, ob Docker läuft
        try {
            docker info | Out-Null
            Write-Host "  -> Docker Daemon ist aktiv." -ForegroundColor DarkGray
        }
        catch {
            Write-Error "Docker Daemon ist nicht aktiv. Bitte starte Docker Desktop und führe das Skript erneut aus."
            return
        }

        Write-Host "  -> Starte Docker Build für Image 'coqui-tts-lightning-ai'..." -ForegroundColor DarkGray
        try {
            docker build -t coqui-tts-lightning-ai .
            Write-Host "  -> Docker-Image 'coqui-tts-lightning-ai' erfolgreich gebaut." -ForegroundColor DarkGray
            Write-Host "Tipp: Du kannst das Image jetzt lokal testen mit: docker run -it coqui-tts-lightning-ai bash" -ForegroundColor Green
            Write-Host "Vergiss nicht, danach 'exit' einzugeben, um den Container zu verlassen." -ForegroundColor Green
        }
        catch {
            Write-Error "Fehler beim Bauen des Docker-Images. Überprüfe die Fehlermeldungen von Docker."
            Write-Host "HINWEIS: Lokale Build-Fehler bedeuten nicht, dass Lightning AI den Build nicht schaffen würde." -ForegroundColor Yellow
        }
    } else {
        Write-Host "  -> Docker-Build übersprungen. Lightning AI wird das Image in der Cloud bauen." -ForegroundColor DarkGray
    }
}

# --- Hauptlogik ---
Write-Host "--- Start der Vorbereitung des Coqui TTS Projekts für Lightning AI ---" -ForegroundColor Green
Write-Host "Dies umfasst $TotalSteps Hauptschritte (+ 1 optionaler Schritt)." -ForegroundColor DarkGreen

# Rufe die Funktionen in der richtigen Reihenfolge auf
Use-ExistingProject
New-Dockerfile
Create-TrainScript
Test-DockerImage

Write-Host "`n--- Alle Vorbereitungsschritte abgeschlossen! ---" -ForegroundColor Green
Write-Host "Dein Projektordner '$ProjectDir' wurde erfolgreich vorbereitet." -ForegroundColor Green
Write-Host "Nächste Schritte:" -ForegroundColor Yellow
Write-Host "1. Bearbeite die Datei '$TrainScriptFileName' im Ordner '$ProjectDir'." -ForegroundColor Yellow
Write-Host "   Passe die Konfigurationen und den Trainings-Loop für deine Daten an." -ForegroundColor Yellow
Write-Host "2. Überprüfe das Dockerfile '$DockerfileFileName' auf die korrekte CUDA-Version." -ForegroundColor Yellow
Write-Host "3. Lege deine Trainingsdaten in '$ProjectDir\my_custom_voice_dataset' ab (oder nutze Lightning AI Volumes)." -ForegroundColor Yellow
Write-Host "4. Lade den gesamten Ordner '$ProjectDir' zu Lightning AI hoch und konfiguriere dein Training." -ForegroundColor Yellow
Write-Host "`nViel Erfolg!" -ForegroundColor Green