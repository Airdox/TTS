import torch
from torch import nn
from typing import Iterable

def train(model: nn.Module, data: Iterable, device: torch.device) -> None:
    """
    Trainiert das Modell mit den gegebenen Daten.

    Args:
        model (nn.Module): Das zu trainierende Modell.
        data (Iterable): Trainingsdaten.
        device (torch.device): Zielgerät (CPU/GPU).
    """
    model.train()
    for batch in data:
        try:
            batch = batch.to(device)
            output = model(batch)
            loss = output.loss
            loss.backward()
        except Exception as e:
            print(f"Fehler beim Training: {e}")
