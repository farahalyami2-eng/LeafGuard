"""
Model inference utilities for LeafGuard AI classifiers.

All four classification models share the same backbone (EfficientNetV2-S from timm)
and ImageNet normalisation, but differ in their classification head dimensions and
the number of output classes.

Quick-start:
    from model_inference import LeafGuardModels
    models = LeafGuardModels()
    label, conf = models.predict_binary("path/to/image.jpg")
    label, conf = models.predict_disease("path/to/image.jpg")
    label, conf = models.predict_crop("path/to/image.jpg")
    label, conf = models.predict_datepalm("path/to/image.jpg")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

try:
    import timm
    _HAS_TIMM = True
except ImportError:
    _HAS_TIMM = False

# ── Paths ──────────────────────────────────────────────────────────────────

_WEIGHTS_ROOT = Path(__file__).parent / "Models Weights"

_WEIGHT_PATHS = {
    "binary":   _WEIGHTS_ROOT / "Bianry Classification Weights Models" / "binary_classifier.pt",
    "disease":  _WEIGHTS_ROOT / "Disease Detection Weights Models"     / "Disease_classifier_EffecentNet.pt",
    "datepalm": _WEIGHTS_ROOT / "Dates Classification Weights Models"  / "datepalm_classifier.pt",
    "crop":     _WEIGHTS_ROOT / "Type -Crops- Classification Weights Models" / "Types_crop_classifier.pt",
}

# ── Class labels ───────────────────────────────────────────────────────────
# Order must match the folder alphabetical sort used during training
# (torchvision ImageFolder assigns classes alphabetically).

BINARY_CLASSES: list[str] = ["diseased", "healthy"]

DISEASE_CLASSES: list[str] = [
    "Canker_Wilt",
    "Downy_Mildew",
    "Leaf_Blight",
    "Leaf_Spot",
    "Mosaic_Virus",
    "Powdery_Mildew",
    "Rot",
    "Rust",
    "Scab_Smut",
]

DATEPALM_CLASSES: list[str] = ["brown_spots", "healthy", "white_scale"]

CROP_CLASSES: list[str] = [
    "apple", "banana", "basil", "bean", "bell_pepper",
    "blueberry", "broccoli", "cabbage", "carrot", "cherry",
    "citrus", "coffee", "corn", "cucumber", "eggplant",
    "garlic", "ginger", "grape", "lettuce", "peach",
    "plum", "potato", "raspberry", "rice", "soybean",
    "squash", "strawberry", "tomato", "wheat", "zucchini",
]

# ── Preprocessing ──────────────────────────────────────────────────────────

_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD  = [0.229, 0.224, 0.225]
_INPUT_SIZE    = 224

_transform = transforms.Compose([
    transforms.Resize((_INPUT_SIZE, _INPUT_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
])

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Model architecture ─────────────────────────────────────────────────────
# The training notebooks wrap the backbone in a parent nn.Module:
#   self.backbone = timm.create_model("tf_efficientnetv2_s", ...)
#   self.head     = Sequential(BN→Drop→Linear→GELU→BN→Drop→Linear)
# State-dict keys are therefore  backbone.*  and  head.*

_HEAD_CONFIGS: dict[str, dict] = {
    "binary":   {"num_classes": 2,  "hidden_dim": 256, "dropout1": 0.3, "dropout2": 0.2},
    "disease":  {"num_classes": 9,  "hidden_dim": 512, "dropout1": 0.4, "dropout2": 0.3},
    "datepalm": {"num_classes": 3,  "hidden_dim": 256, "dropout1": 0.4, "dropout2": 0.3},
    "crop":     {"num_classes": 30, "hidden_dim": 512, "dropout1": 0.4, "dropout2": 0.3},
}


class _LeafGuardNet(nn.Module):
    """Wrapper that matches the exact state-dict layout saved by the training notebooks."""

    def __init__(self, cfg: dict) -> None:
        super().__init__()
        self.backbone = timm.create_model("tf_efficientnetv2_s", pretrained=False, num_classes=0)
        in_features = self.backbone.num_features  # 1280
        self.head = nn.Sequential(
            nn.BatchNorm1d(in_features),
            nn.Dropout(cfg["dropout1"]),
            nn.Linear(in_features, cfg["hidden_dim"]),
            nn.GELU(),
            nn.BatchNorm1d(cfg["hidden_dim"]),
            nn.Dropout(cfg["dropout2"]),
            nn.Linear(cfg["hidden_dim"], cfg["num_classes"]),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.backbone(x))


def _build_model(model_key: str) -> _LeafGuardNet:
    """Create an EfficientNetV2-S model with the correct head for *model_key*."""
    if not _HAS_TIMM:
        raise ImportError(
            "timm is required to run the AI models.\n"
            "Install it with:  pip install timm"
        )
    return _LeafGuardNet(_HEAD_CONFIGS[model_key])


def _load_weights(model: _LeafGuardNet, path: Path) -> _LeafGuardNet:
    """Load a saved state-dict into *model* and move it to DEVICE."""
    if not path.exists():
        raise FileNotFoundError(f"Weight file not found: {path}")

    state = torch.load(path, map_location=DEVICE, weights_only=False)

    # Some training scripts wrap the state-dict in a checkpoint dict
    if isinstance(state, dict):
        for wrapper_key in ("model", "state_dict", "model_state_dict"):
            if wrapper_key in state and isinstance(state[wrapper_key], dict):
                state = state[wrapper_key]
                break

    model.load_state_dict(state)
    model.to(DEVICE)
    model.eval()
    return model


# ── Public loader functions ────────────────────────────────────────────────

def load_binary_model() -> nn.Module:
    return _load_weights(_build_model("binary"),   _WEIGHT_PATHS["binary"])

def load_disease_model() -> nn.Module:
    return _load_weights(_build_model("disease"),  _WEIGHT_PATHS["disease"])

def load_datepalm_model() -> nn.Module:
    return _load_weights(_build_model("datepalm"), _WEIGHT_PATHS["datepalm"])

def load_crop_model() -> nn.Module:
    return _load_weights(_build_model("crop"),     _WEIGHT_PATHS["crop"])


# ── Inference ──────────────────────────────────────────────────────────────

def predict(model: nn.Module, image_path: str, class_names: list[str]) -> tuple[str, float]:
    """
    Run a single image through *model* and return (predicted_class, confidence).

    Args:
        model:       A loaded, eval-mode nn.Module.
        image_path:  Absolute or relative path to the plant image.
        class_names: Ordered list of class labels matching the model's output nodes.

    Returns:
        (class_name, confidence) where confidence ∈ [0, 1].
    """
    img = Image.open(image_path).convert("RGB")
    tensor = _transform(img).unsqueeze(0).to(DEVICE)  # (1, 3, 224, 224)

    with torch.no_grad():
        logits = model(tensor)                            # (1, num_classes)
        probs  = torch.softmax(logits, dim=1)
        conf, idx = probs.max(dim=1)

    return class_names[idx.item()], round(conf.item(), 4)


# ── Convenience bundle ─────────────────────────────────────────────────────

class LeafGuardModels:
    """
    Loads all four classifiers once and exposes named predict methods.
    Intended for pipeline.py so models are only loaded a single time.
    """

    def __init__(self) -> None:
        print("[LeafGuard] Loading binary classifier …")
        self._binary   = load_binary_model()
        print("[LeafGuard] Loading disease classifier …")
        self._disease  = load_disease_model()
        print("[LeafGuard] Loading date-palm classifier …")
        self._datepalm = load_datepalm_model()
        print("[LeafGuard] Loading crop classifier …")
        self._crop     = load_crop_model()
        print("[LeafGuard] All models ready.")

    def predict_binary(self, image_path: str) -> tuple[str, float]:
        """Returns ('healthy' | 'diseased', confidence)."""
        return predict(self._binary, image_path, BINARY_CLASSES)

    def predict_disease(self, image_path: str) -> tuple[str, float]:
        """Returns (disease_class, confidence) for one of 9 disease classes."""
        return predict(self._disease, image_path, DISEASE_CLASSES)

    def predict_datepalm(self, image_path: str) -> tuple[str, float]:
        """Returns ('brown_spots' | 'healthy' | 'white_scale', confidence)."""
        return predict(self._datepalm, image_path, DATEPALM_CLASSES)

    def predict_crop(self, image_path: str) -> tuple[str, float]:
        """Returns (crop_class, confidence) for one of 30 crop types."""
        return predict(self._crop, image_path, CROP_CLASSES)
