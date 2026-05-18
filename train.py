import os
import tensorflow as tf
from dataset import load_datasets
from model import build_leaf_model

def main():
    print("=" * 50)
    print("      LEAFSNAP MUTLI-SOURCE TRAINING PIPELINE       ")
    print("=" * 50)

    # 1. Load the preprocessed 80/10/10 data streams
    train_ds, val_ds, test_ds, class_names = load_datasets()
    num_classes = len(class_names)
    print(f"\n[INFO] Data pipeline verified successfully.")
    print(f"[INFO] Total distinct plant species to classify: {num_classes}")

    # 2. Build the model architecture layout
    model = build_leaf_model(num_classes)

    # 3. Compile the network configurations
    print("\n[INFO] Compiling model configurations...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # 4. Set up deep learning callbacks
    # EarlyStopping stops training early if validation loss stops improving, saving time and preventing overfitting
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=2,
            restore_best_weights=True,
            verbose=1
        )
    ]

    # 5. Execute the core training loop
    print("\n[INFO] Initiating neural network training loop...")
    epochs = 5  # Set to 5 epochs; early stopping will kick in if it plateaus early
    
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks
    )

    # 6. Evaluate final performance against the completely unseen Test Set
    print("\n" + "="*40)
    print("   RUNNING FINAL TEST SET EVALUATION   ")
    print("="*40)
    test_loss, test_acc = model.evaluate(test_ds, verbose=1)
    print(f"\n[FINAL METRICS] Test Loss: {test_loss:.4f}")
    print(f"[FINAL METRICS] Test Accuracy: {test_acc * 100:.2f}%")

    # 7. Export the trained brain weights and class labels sheet
    print("\n[INFO] Exporting final model parameters and asset tracking sheets...")
    model_output_name = "leafsnap_final_model.keras"
    labels_output_name = "labels.txt"
    
    model.save(model_output_name)
    
    with open(labels_output_name, "w") as f:
        for name in class_names:
            f.write(f"{name}\n")
            
    print(f"[SUCCESS] Deep learning weights saved as: '{model_output_name}'")
    print(f"[SUCCESS] Categorical index sheet saved as: '{labels_output_name}'")
    print("\nPipeline execution finished successfully! Ready for web deployment integration.")

if __name__ == "__main__":
    main()