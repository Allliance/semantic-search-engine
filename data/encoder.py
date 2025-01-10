from transformers import CLIPProcessor, CLIPModel
import torch
import torch

class Encoder:
    def __init__(self,
                 device=None,
                 model_name="openai/clip-vit-base-patch32"):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.model = CLIPModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.preprocess = CLIPProcessor.from_pretrained(model_name)
    
    
    def encode_image(self, images):
                    
        inputs = self.preprocess(images=images, return_tensors="pt", padding=True).to(self.device)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        
        image_features /= image_features.norm(p=2, dim=-1, keepdim=True)

        return image_features.cpu().numpy()
    
    def encode_text(self, text):
        inputs = self.preprocess(text=text, return_tensors="pt", padding=True)
        
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        
        text_features /= text_features.norm(p=2, dim=-1, keepdim=True)
        
        if len(text_features.size()) > 1:
            text_features = text_features.squeeze(0)
        
        return text_features
