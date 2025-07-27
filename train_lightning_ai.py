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
