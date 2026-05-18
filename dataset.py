import os
import tensorflow as tf
from tensorflow.keras import layers

DATA_DIR = os.path.join("processed_data")
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

def load_datasets():
    if not os.path.exists(DATA_DIR):
        print(f"ERROR: Run preprocess.py first to generate the '{DATA_DIR}' folder!")
        exit()

    print("Loading Train Set...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATA_DIR, "train"),
        shuffle=True, image_size=IMG_SIZE, batch_size=BATCH_SIZE
    )

    print("Loading Validation Set...")
    val_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATA_DIR, "validation"),
        shuffle=False, image_size=IMG_SIZE, batch_size=BATCH_SIZE
    )

    print("Loading Test Set...")
    test_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATA_DIR, "test"),
        shuffle=False, image_size=IMG_SIZE, batch_size=BATCH_SIZE
    )

    class_names = train_ds.class_names

    # Data Augmentation Layer applied strictly to training stream
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.15),
    ])

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y)).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, test_ds, class_names