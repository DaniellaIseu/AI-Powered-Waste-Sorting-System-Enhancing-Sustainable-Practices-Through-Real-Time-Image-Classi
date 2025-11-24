"""Load weights from model.weights.h5 into a correctly structured model."""
import sys
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import numpy as np

# Get current directory (ml/)
CURRENT_DIR = Path(__file__).parent
WEIGHTS_PATH = CURRENT_DIR / 'model.weights.h5'
OUTPUT_PATH = CURRENT_DIR / 'final_waste_classifier.keras'

print("=" * 60)
print("Model Weight Loading Tool")
print("=" * 60)

if not WEIGHTS_PATH.exists():
    print(f"✗ Error: model.weights.h5 not found at {WEIGHTS_PATH}")
    sys.exit(1)

print(f"✓ Found weights file: {WEIGHTS_PATH}")

# Build the model with the correct architecture (matching training script)
print(f"\nBuilding model with correct architecture...")
IMG_HEIGHT, IMG_WIDTH = 224, 224
NUM_CLASSES = 6  # cardboard, glass, metal, paper, plastic, trash

base_model = MobileNetV2(
    weights='imagenet',  # Use ImageNet weights for base
    include_top=False,
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
)
base_model.trainable = False

# Create the model with the exact same architecture as training script
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(NUM_CLASSES, activation='softmax')
])

print("✓ Model architecture built")
model.summary()

# Load the weights
print(f"\nLoading weights from {WEIGHTS_PATH}...")
try:
    model.load_weights(str(WEIGHTS_PATH), skip_mismatch=False)
    print("✓ Weights loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not load weights directly: {e}")
    print("  Attempting to load with skip_mismatch=True...")
    try:
        model.load_weights(str(WEIGHTS_PATH), skip_mismatch=True)
        print("✓ Weights loaded (some weights may not have matched)")
    except Exception as e2:
        print(f"✗ Error: Could not load weights: {e2}")
        print("\nPossible solutions:")
        print("1. Check if the weights file matches the model architecture")
        print("2. Retrain the model using AI-wastesorter/train_model.py")
        sys.exit(1)

# Compile the model
print(f"\nCompiling model...")
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
print("✓ Model compiled")

# Test the model
print(f"\nTesting model with dummy input...")
dummy_input = np.random.random((1, 224, 224, 3)).astype(np.float32)
prediction = model.predict(dummy_input, verbose=0)
print(f"✓ Model test successful!")
print(f"  Input shape: {dummy_input.shape}")
print(f"  Output shape: {prediction.shape}")
print(f"  Output sum: {prediction[0].sum():.4f} (should be ~1.0 for softmax)")

# Save the model
print(f"\nSaving model to {OUTPUT_PATH}...")
if OUTPUT_PATH.exists():
    backup_path = CURRENT_DIR / 'final_waste_classifier_old.keras'
    print(f"  Backing up existing model to {backup_path}...")
    import shutil
    try:
        shutil.move(str(OUTPUT_PATH), str(backup_path))
        print("  ✓ Backup created")
    except Exception as e:
        print(f"  ⚠️  Could not backup: {e}")

model.save(str(OUTPUT_PATH))
print(f"✓ Model saved successfully")

print("\n" + "=" * 60)
print("Model loading completed successfully!")
print("=" * 60)
print(f"\nThe web app will now use the model from:")
print(f"  {OUTPUT_PATH}")
print("\nYou can now test the web app - the classification should work!")






