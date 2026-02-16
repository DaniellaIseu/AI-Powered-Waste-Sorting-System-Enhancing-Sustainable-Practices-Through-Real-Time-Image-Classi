import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt

print("TensorFlow version:", tf.__version__)

# Configuration
IMG_HEIGHT, IMG_WIDTH = 224, 224
BATCH_SIZE = 32
NUM_EPOCHS = 20
DATA_PATH = "dataset/Trashnet dataset"

# Model output paths - save to ml/ directory for web app to use
BASE_DIR = Path(__file__).parent.parent
ML_DIR = BASE_DIR / 'ml'
ML_DIR.mkdir(parents=True, exist_ok=True)

FINAL_MODEL_PATH = ML_DIR / 'final_waste_classifier.keras'
BEST_MODEL_PATH = BASE_DIR / 'AI-wastesorter' / 'best_model.h5'
TFLITE_MODEL_PATH = BASE_DIR / 'AI-wastesorter' / 'waste_classifier.tflite'
HISTORY_PLOT_PATH = BASE_DIR / 'AI-wastesorter' / 'training_history.png'

# Check if data path exists
if not os.path.exists(DATA_PATH):
    print(f"Error: Data path '{DATA_PATH}' does not exist!")
    exit(1)

print("Dataset structure looks good. Starting training process...")

# Data Augmentation and Generators
train_datagen = ImageDataGenerator(
    rescale=1./255,           # Normalize pixel values
    validation_split=0.2,     # Use 20% for validation
    rotation_range=20,        # Random rotation
    width_shift_range=0.2,    # Random horizontal shift
    height_shift_range=0.2,   # Random vertical shift
    horizontal_flip=True,     # Random horizontal flip
    zoom_range=0.2,           # Random zoom
    shear_range=0.2,          # Random shear
    fill_mode='nearest'       # Fill in missing pixels
)

print("Creating data generators...")

# Training data generator
train_generator = train_datagen.flow_from_directory(
    DATA_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

# Validation data generator
validation_generator = train_datagen.flow_from_directory(
    DATA_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# Get class names and indices
class_names = list(train_generator.class_indices.keys())
num_classes = len(class_names)
print(f"Class names: {class_names}")
print(f"Number of classes: {num_classes}")

print(f"Training samples: {train_generator.samples}")
print(f"Validation samples: {validation_generator.samples}")

# Build the Model using Transfer Learning with MobileNetV2
print("Building the model...")

# Load pre-trained MobileNetV2 without the top layer
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
)

# Freeze the base model initially
base_model.trainable = False

# Create new model on top
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),  # Increased dropout for better regularization
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(num_classes, activation='softmax')
])

# Compile the model
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("Model architecture:")
model.summary()

# Callbacks for better training
checkpoint = ModelCheckpoint(
    str(BEST_MODEL_PATH),
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# Train the model
print("Starting training...")
history = model.fit(
    train_generator,
    epochs=NUM_EPOCHS,
    validation_data=validation_generator,
    callbacks=[checkpoint, early_stop],
    verbose=1
)

# Load the best model saved during training
model.load_weights(str(BEST_MODEL_PATH))

# Evaluate the final model
print("Evaluating the model...")
train_loss, train_accuracy = model.evaluate(train_generator)
val_loss, val_accuracy = model.evaluate(validation_generator)

print(f"Final Training Accuracy: {train_accuracy:.4f}")
print(f"Final Validation Accuracy: {val_accuracy:.4f}")

# Plot training history
def plot_training_history(history):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot accuracy
    ax1.plot(history.history['accuracy'], label='Training Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    
    # Plot loss
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(str(HISTORY_PLOT_PATH))
    plt.show()

plot_training_history(history)

# Save the final model to ml/ directory for web app to use
print(f"\nSaving final model to {FINAL_MODEL_PATH}...")
model.save(str(FINAL_MODEL_PATH))
print(f"✓ Model saved as '{FINAL_MODEL_PATH}'")

# Also save as .h5 in the AI-wastesorter directory for backup
backup_h5_path = BASE_DIR / 'AI-wastesorter' / 'waste_classifier.h5'
model.save(str(backup_h5_path))
print(f"✓ Backup model saved as '{backup_h5_path}'")

# Convert to TensorFlow Lite for mobile deployment
print(f"\nConverting to TensorFlow Lite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open(str(TFLITE_MODEL_PATH), 'wb') as f:
    f.write(tflite_model)
print(f"✓ TensorFlow Lite model saved as '{TFLITE_MODEL_PATH}'")

print("\n" + "="*60)
print("Training completed successfully!")
print("="*60)
print(f"✓ Final model saved to: {FINAL_MODEL_PATH}")
print(f"✓ Backup .h5 model: {backup_h5_path}")
print(f"✓ TensorFlow Lite model: {TFLITE_MODEL_PATH}")
print(f"✓ Training history plot: {HISTORY_PLOT_PATH}")
print("\nThe web app will now use the model from the ml/ directory!")
print("Next step: Integrate the .tflite model into your Flutter app!")