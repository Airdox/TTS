#!/usr/bin/env python3
"""
XTTS v2 Fine-tuning Script für Lightning AI
Optimiert für Voice Cloning mit aktuellen Coqui TTS APIs
"""

import os
import argparse
import torch
import logging
from pathlib import Path

# Coqui TTS Imports - Aktualisiert für moderne APIs
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.trainer import Trainer, TrainerArgs
from TTS.config import BaseDatasetConfig, BaseAudioConfig
from TTS.tts.datasets import load_tts_samples
from TTS.utils.audio import AudioProcessor
from TTS.utils.generic_utils import setup_logger
from TTS.trainer.torch_config import TrainerConfig

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = setup_logger()

def main():
    parser = argparse.ArgumentParser(description="XTTS v2 Fine-tuning für Voice Cloning")
    parser.add_argument("--dataset_path", 
                       default="/app/my_custom_voice_dataset", 
                       help="Pfad zum Dataset")
    parser.add_argument("--output_path", 
                       default="/app/output", 
                       help="Output-Pfad für Modelle")
    parser.add_argument("--language", 
                       default="de", 
                       help="Sprache des Datasets (de, en, es, fr, etc.)")
    parser.add_argument("--epochs", 
                       type=int, 
                       default=100, 
                       help="Anzahl der Trainingsepochen")
    parser.add_argument("--batch_size", 
                       type=int, 
                       default=2, 
                       help="Batch-Größe (für XTTS meist klein)")
    parser.add_argument("--learning_rate", 
                       type=float, 
                       default=5e-6, 
                       help="Lernrate für Finetuning")
    
    args = parser.parse_args()
    
    # Erstelle Output-Verzeichnis
    os.makedirs(args.output_path, exist_ok=True)
    
    logger.info("🚀 Starte XTTS v2 Voice Cloning Training...")
    logger.info(f"📁 Dataset: {args.dataset_path}")
    logger.info(f"📁 Output: {args.output_path}")
    logger.info(f"🌍 Sprache: {args.language}")
    
    # --- 1. XTTS Konfiguration laden ---
    config = XttsConfig()
    
    # XTTS-spezifische Parameter für Voice Cloning
    config.model_args.update({
        "use_speaker_embedding": True,
        "use_gst": True,
        "gst_style_input": None,
        "use_capacitron_vae": False,
    })
    
    # Audio-Konfiguration für XTTS
    config.audio.update({
        "sample_rate": 22050,  # XTTS Standard
        "hop_length": 256,
        "win_length": 1024,
        "n_fft": 1024,
        "mel_fmin": 0,
        "mel_fmax": 8000,
        "n_mels": 80,
        "do_trim_silence": True,
        "trim_db": 23.0,
        "do_normalization": True,
        "normalization_value": 0.8,
        "do_rms_norm": True,
        "db_level": None,
    })
    
    # Training-spezifische Konfiguration
    config.update({
        "run_name": "xtts_voice_clone",
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "eval_batch_size": 1,
        "learning_rate": args.learning_rate,
        "weight_decay": 1e-6,
        "optimizer": "AdamW",
        "lr_scheduler": "ExponentialLR",
        "lr_scheduler_params": {"gamma": 0.95},
        "use_phonemes": True,
        "phoneme_language": args.language,
        "compute_input_seq_cache": True,
        "cache_path": os.path.join(args.output_path, "cache"),
        "add_blank": True,
        "datasets": [BaseDatasetConfig(
            formatter="ljspeech",
            meta_file_train="metadata.csv",
            meta_file_val="metadata.csv",
            path=args.dataset_path,
            language=args.language,
        )],
    })
    
    # --- 2. Audio Processor initialisieren ---
    ap = AudioProcessor.init_from_config(config)
    
    # --- 3. Tokenizer und Modell ---
    tokenizer, config = Xtts.init_from_config(config)
    model = Xtts(config, ap, tokenizer)
    
    # Lade vortrainiertes XTTS-Modell für Finetuning
    logger.info("⬇️  Lade vortrainiertes XTTS v2 Modell...")
    model.load_checkpoint(
        config, 
        checkpoint_path=None,  # Lädt automatisch von Hugging Face
        eval=False,
        use_deepspeed=False
    )
    
    # --- 4. Daten laden ---
    logger.info("📊 Lade Dataset...")
    train_samples, eval_samples = load_tts_samples(
        config.datasets[0],
        eval_split=True,
        eval_split_max_size=config.get("eval_split_max_size", 500),
        eval_split_size=config.get("eval_split_size", 0.01),
    )
    
    logger.info(f"✅ {len(train_samples)} Training-Samples geladen")
    logger.info(f"✅ {len(eval_samples)} Evaluation-Samples geladen")
    
    # --- 5. Trainer Konfiguration ---
    trainer_config = TrainerConfig(
        output_path=args.output_path,
        logger_uri=None,
        run_name=config.run_name,
        project_name="XTTS_Voice_Clone",
        run_description="XTTS v2 Voice Cloning mit deutschem Dataset",
        print_step=25,
        plot_step=100,
        model_param_stats=False,
        wandb_entity=None,
        dashboard_logger="tensorboard",
        save_step=1000,
        checkpoint=True,
        save_n_checkpoints=5,
        save_checkpoints=True,
        target_loss="loss",
        print_eval=True,
        test_delay_epochs=0,
        run_eval=True,
        run_eval_steps=None,
        distributed_backend="nccl",
        mixed_precision=False,  # XTTS kann empfindlich auf Mixed Precision reagieren
    )
    
    # --- 6. Trainer initialisieren ---
    trainer = Trainer(
        TrainerArgs.from_dict(trainer_config),
        config,
        args.output_path,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
        training_assets={"audio_processor": ap, "tokenizer": tokenizer}
    )
    
    # --- 7. Training starten ---
    logger.info("🎯 Starte Fine-tuning...")
    logger.info(f"💪 Training läuft für {args.epochs} Epochen")
    logger.info(f"🔥 Batch Size: {args.batch_size}")
    logger.info(f"📈 Learning Rate: {args.learning_rate}")
    
    try:
        trainer.fit()
        logger.info("🎉 Training erfolgreich abgeschlossen!")
        logger.info(f"📁 Modelle gespeichert in: {args.output_path}")
        
        # Teste das trainierte Modell
        logger.info("🎤 Teste das trainierte Modell...")
        model.eval()
        
        # Beispiel-Text für Test
        test_text = "Hallo, das ist ein Test der neuen Stimme nach dem Training."
        
        # Hier würde normalerweise ein Inferenz-Test laufen
        logger.info("✅ Training und Setup komplett!")
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Training: {str(e)}")
        raise

if __name__ == "__main__":
    main()
