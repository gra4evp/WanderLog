from pathlib import Path
from typing import Literal
import torch
from torch import nn
from torchvision import transforms
import timm


class InteriorClassifier(nn.Module):
    """
    Модель для классификации интерьеров
    """
    
    def __init__(
        self,
        num_classes: int = 8,
        backbone_name: str = 'efficientnet_b3',
        pretrained: bool = True,
        use_head: bool = True,
        head_hidden_dim: int = 512,
        head_dropout: float = 0.3,
        head_activation: Literal['relu', 'gelu'] = 'relu'
    ):
        super().__init__()

        self.num_classes = num_classes
        self.backbone_name = backbone_name
        self.pretrained = pretrained

        self.use_head = use_head
        self.head_hidden_dim = head_hidden_dim
        self.head_dropout = head_dropout
        self.head_activation = head_activation

        self.backbone = timm.create_model(
            backbone_name, 
            pretrained=pretrained,
            num_classes=0
        )

        self.feature_dim = self.backbone.num_features
        if use_head:
            # Полноценная голова
            activation = nn.Identity()
            if head_activation == 'relu':
                activation = nn.ReLU()
            elif head_activation == 'gelu':
                activation = nn.GELU()
            
            self.head = nn.Sequential(
                nn.Linear(self.feature_dim, head_hidden_dim),
                activation,
                nn.Dropout(head_dropout),
                nn.Linear(head_hidden_dim, num_classes)
            )
        else:
            # Просто заменяем финальный классификатор
            self.head = nn.Linear(self.feature_dim, num_classes)

    def forward(self, x):
        features = self.backbone(x)
        return self.head(features)


def load_model(checkpoint_path: Path):
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Model file {checkpoint_path} not found")
    
    checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
    model = InteriorClassifier(num_classes=8)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model


def get_inference_transforms(img_size=380) -> transforms.Compose:
    transform = transforms.Compose(
        [
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ]
    )
    return transform

_model_instance = None  # singleton instance

def get_model() -> InteriorClassifier:
    global _model_instance
    if _model_instance is None:
        try:
            models_dir = Path(__file__).parent
            checkpoint_files = list(models_dir.glob("ckpt*"))
            if not checkpoint_files:
                raise FileNotFoundError(f"No checkpoint files found in {models_dir}")
            checkpoint_path = checkpoint_files[0]
            print(f"Using checkpoint file: {checkpoint_path}")
            _model_instance = load_model(checkpoint_path=checkpoint_path)
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            raise RuntimeError("Failed to initialize model")
    return _model_instance

