"""Reconstruct model from config.json and weights.h5 files."""
import sys
from pathlib import Path
import json

import tensorflow as tf
from tensorflow import keras

# Get current directory (ml/)
CURRENT_DIR = Path(__file__).parent
CONFIG_PATH = CURRENT_DIR / 'config.json'
WEIGHTS_PATH = CURRENT_DIR / 'model.weights.h5'
METADATA_PATH = CURRENT_DIR / 'metadata.json'
OUTPUT_PATH = CURRENT_DIR / 'final_waste_classifier.keras'

print("=" * 60)
print("Model Reconstruction Tool")
print("=" * 60)

# Check if files exist
if not CONFIG_PATH.exists():
    print(f"✗ Error: config.json not found at {CONFIG_PATH}")
    sys.exit(1)

if not WEIGHTS_PATH.exists():
    print(f"✗ Error: model.weights.h5 not found at {WEIGHTS_PATH}")
    sys.exit(1)

print(f"✓ Found config.json")
print(f"✓ Found model.weights.h5")
if METADATA_PATH.exists():
    print(f"✓ Found metadata.json")
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
        print(f"  Keras version: {metadata.get('keras_version', 'unknown')}")
        print(f"  Date saved: {metadata.get('date_saved', 'unknown')}")

print(f"\nLoading model configuration...")
try:
    # Try method 1: Load using Keras model_from_json
    print("Attempting method 1: Loading from JSON config...")
    try:
        with open(CONFIG_PATH, 'r') as f:
            config_str = f.read()
        
        print(f"  Config file size: {len(config_str)} characters")
        
        # Try loading as JSON first to see structure
        config = json.loads(config_str)
        print(f"✓ Configuration loaded as JSON")
        print(f"  Config type: {type(config)}")
        if isinstance(config, dict):
            print(f"  Config keys: {list(config.keys())[:10]}...")  # Show first 10 keys
        
        # Try reconstructing model from config
        print(f"\nReconstructing model from config...")
        model = keras.models.model_from_json(config_str)
        print(f"✓ Model architecture reconstructed")
        
        # Load weights
        print(f"\nLoading weights from {WEIGHTS_PATH}...")
        model.load_weights(str(WEIGHTS_PATH))
        print(f"✓ Weights loaded successfully")
        
    except Exception as e1:
        print(f"  ✗ Method 1 failed: {e1}")
        
        # Try method 2: Direct load using keras.load_model if config is a SavedModel format
        print("\nAttempting method 2: Trying direct Keras load...")
        try:
            # Try loading the entire directory as a SavedModel
            if CURRENT_DIR.exists() and (CURRENT_DIR / 'model.weights.h5').exists():
                # Build model architecture manually from the config
                print("  Building model architecture manually...")
                from tensorflow.keras.applications import MobileNetV2
                from tensorflow.keras import layers, models
                
                base_model = MobileNetV2(
                    weights=None,  # We'll load weights from file
                    include_top=False,
                    input_shape=(224, 224, 3)
                )
                base_model.trainable = False
                
                model = models.Sequential([
                    base_model,
                    layers.GlobalAveragePooling2D(),
                    layers.Dropout(0.3),
                    layers.Dense(128, activation='relu'),
                    layers.Dropout(0.2),
                    layers.Dense(6, activation='softmax')  # 6 classes
                ])
                
                print("✓ Model architecture built")
                print("  Loading weights...")
                model.load_weights(str(WEIGHTS_PATH))
                print("✓ Weights loaded")
            else:
                raise Exception("Weights file not found")
        except Exception as e2:
            print(f"  ✗ Method 2 failed: {e2}")
            raise Exception(f"All loading methods failed. Last error: {e2}")
    
    # Compile the model (necessary for inference)
    print(f"\nCompiling model...")
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print(f"✓ Model compiled")
    
    # Display model summary
    print(f"\nModel Summary:")
    print("-" * 60)
    model.summary()
    print("-" * 60)
    
    # Test the model
    print(f"\nTesting model with dummy input...")
    import numpy as np
    dummy_input = np.random.random((1, 224, 224, 3)).astype(np.float32)
    prediction = model.predict(dummy_input, verbose=0)
    print(f"✓ Model test successful!")
    print(f"  Input shape: {dummy_input.shape}")
    print(f"  Output shape: {prediction.shape}")
    print(f"  Output sum: {prediction[0].sum():.4f} (should be ~1.0 for softmax)")
    
    # Save the reconstructed model
    print(f"\nSaving reconstructed model to {OUTPUT_PATH}...")
    # Backup old model if it exists
    if OUTPUT_PATH.exists():
        backup_path = CURRENT_DIR / 'final_waste_classifier_old.keras'
        print(f"  Backing up existing model to {backup_path}...")
        import shutil
        shutil.move(str(OUTPUT_PATH), str(backup_path))
    
    model.save(str(OUTPUT_PATH))
    print(f"✓ Model saved successfully to {OUTPUT_PATH}")
    
    print("\n" + "=" * 60)
    print("Model reconstruction completed successfully!")
    print("=" * 60)
    print(f"\nThe web app will now use the reconstructed model from:")
    print(f"  {OUTPUT_PATH}")
    
except json.JSONDecodeError as e:
    print(f"✗ Error: Invalid JSON in config.json: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

