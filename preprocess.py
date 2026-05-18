import os
import shutil
import random
from pathlib import Path

# Fix the path to point precisely where LeafSnap keeps its segmented folders
FIELD_DIR = Path("leafsnap-dataset/leafsnap-dataset/dataset/images/field")
SEG_DIR = Path("leafsnap-dataset/leafsnap-dataset/dataset/segmented/field") # Updated path!

# Output folder for organized data
OUTPUT_DIR = Path("processed_data")

# Splitting ratios
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

def split_and_copy_images(source_folders, output_root):
    print("Starting data preprocessing and distribution...")
    
    # We move the random seed outside the inner loop 
    # This prevents identical shuffling indexing between field and segmented
    random.seed(42) 
    
    # Reset output directory if it exists to ensure a clean split
    if output_root.exists():
        print(f"Clearing old execution data from {output_root}...")
        shutil.rmtree(output_root)
        
    for source_dir in source_folders:
        if not source_dir.exists():
            print(f"ERROR: Source path missing: {source_dir}")
            continue
            
        print(f"Processing source folder: {source_dir.name}...")
        
        # Iterate through every plant species folder
        for species_folder in source_dir.iterdir():
            if not species_folder.is_dir():
                continue
                
            species_name = species_folder.name
            images = list(species_folder.glob("*.*")) # Grab all image files
            
            # Mix the specific folder's files up cleanly
            random.shuffle(images)
            
            total_imgs = len(images)
            if total_imgs == 0:
                continue
                
            # Calculate indices for splits
            train_end = int(total_imgs * TRAIN_RATIO)
            val_end = train_end + int(total_imgs * VAL_RATIO)
            
            # Divide image file lists
            train_imgs = images[:train_end]
            val_imgs = images[train_end:val_end]
            test_imgs = images[val_end:]
            
            # Helper logic to copy files into their new sub-folders
            for split_name, split_list in [('train', train_imgs), ('validation', val_imgs), ('test', test_imgs)]:
                target_dir = output_root / split_name / species_name
                target_dir.mkdir(parents=True, exist_ok=True)
                
                for img_path in split_list:
                    unique_name = f"{source_dir.name}_{img_path.name}"
                    shutil.copy(img_path, target_dir / unique_name)

    print(f"\nPreprocessing Complete! Combined data structured inside: '{output_root}/'")

if __name__ == "__main__":
    split_and_copy_images([FIELD_DIR, SEG_DIR], OUTPUT_DIR)