import tensorflow as tf 
from tensorflow.keras.models import Sequential 
from tensorflow.keras import layers, models
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Check for GPU availability
gpus = tf.config.list_physical_devices('GPU')
if gpus: 
    print("GPU is available and will be used")
else: 
    print("GPU is not available and will not be used")

# Set paths for training and validation data
training_dir = 'images/images/train'
validation_dir = 'images/images/validation'

# Image augmentation for training data
training_data = ImageDataGenerator(
    rescale=1./255, 
    rotation_range=40,
    width_shift_range=0.2, 
    height_shift_range=0.2, 
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Only rescaling for validation data
validation_data = ImageDataGenerator(rescale=1./255)

# Load images through directory with batch size 64 (no need to repeat)
training_generator = training_data.flow_from_directory(
    training_dir, target_size=(64, 64), batch_size=64, class_mode='categorical'
)

validation_generator = validation_data.flow_from_directory(
    validation_dir, target_size=(64,64), batch_size=64, class_mode='categorical'
)

# Building the model
model = models.Sequential()

model.add(layers.Conv2D(32, (3,3), activation='relu', padding='same', input_shape=(64,64,3)))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2,2), padding='same'))

model.add(layers.Conv2D(64, (3,3), activation='relu', padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2, 2), padding='same'))

model.add(layers.Conv2D(128, (3,3), activation='relu', padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2, 2), padding='same'))

model.add(layers.Conv2D(256, (3,3), activation='relu', padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2,2), padding='same'))

model.add(layers.Conv2D(512, (3,3), activation='relu', padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2,2), padding='same'))

# Regularization to prevent overfitting
model.add(layers.Flatten())
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(512, activation='relu'))
model.add(layers.BatchNormalization())
model.add(layers.Dropout(0.5))

# Output layer
model.add(layers.Dense(7, activation='softmax'))

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

# Load the saved model from the checkpoint file
model = tf.keras.models.load_model('best_model.keras')

# Callbacks for early stopping and model checkpoint
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
checkpoint = ModelCheckpoint('best_model.keras', monitor='val_accuracy', save_best_only=True)

# Recalculate steps per epoch and validation steps based on the data
steps_per_epoch = training_generator.samples // training_generator.batch_size
validation_steps = validation_generator.samples // validation_generator.batch_size

# Resume training from epoch 17
train = model.fit(training_generator, 
                  initial_epoch=16,  # Start from epoch 17
                  epochs=45,  # Continue until epoch 45
                  validation_data=validation_generator, 
                  validation_steps=validation_steps, 
                  callbacks=[early_stopping, checkpoint])

# Save the final model
model.save('CNN_Model_final.keras')