import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import numpy as np
import os
import matplotlib.pyplot as plt

print("TensorFlow version:", tf.__version__)

# Configuration
IMG_HEIGHT, IMG_WIDTH = 224, 224
BATCH_SIZE = 32
NUM_EPOCHS = 20
DATA_PATH = "dataset/Trashnet dataset"

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
    'best_model.h5',
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
model.load_weights('best_model.h5')

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
    plt.savefig('training_history.png')
    plt.show()

plot_training_history(history)

# Save the final model
model.save('waste_classifier.h5')
print("Model saved as 'waste_classifier.h5'")

# Convert to TensorFlow Lite for mobile deployment
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('waste_classifier.tflite', 'wb') as f:
    f.write(tflite_model)
print("TensorFlow Lite model saved as 'waste_classifier.tflite'")

print("Training completed successfully!")
print("Next step: Integrate the .tflite model into your Flutter app!")