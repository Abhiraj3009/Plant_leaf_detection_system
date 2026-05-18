import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV3Large

def build_leaf_model(num_classes):
    print("Configuring pre-trained MobileNetV3 backbone...")
    
    # 1. Load the pre-trained neural network core
    base_model = MobileNetV3Large(
        input_shape=(224, 224, 3),
        include_top=False,    # Chop off the original 1000-class ImageNet head
        weights='imagenet',   # Use pre-trained features (edges, textures, shapes)
        pooling='avg'         # Collapse spatial dimensions efficiently
    )
    
    # 2. Freeze the base weights so we don't destroy existing patterns
    base_model.trainable = False

    # 3. Create our custom classification top layer (The "Head")
    inputs = layers.Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False) # Keep base batch normalization locked
    
    x = layers.Dense(128, activation='relu')(x) # Hidden layer to learn leaf patterns
    x = layers.Dropout(0.3)(x)                   # Randomly deactivates 30% of nodes to prevent overfitting
    
    outputs = layers.Dense(num_classes, activation='softmax')(x) # Outputs confidence % for your classes

    model = models.Model(inputs, outputs)
    return model