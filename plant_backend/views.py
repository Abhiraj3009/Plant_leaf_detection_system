import os
import numpy as np
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings

# Try importing ML frameworks safely
try:
    import tensorflow as tf
    from cv2 import dnn  # accurate openCV or keras loader depending on how you trained it
except ImportError:
    pass

from .models import PlantInfo

# Load the model ONCE when the server starts up so it's super fast
MODEL_PATH = os.path.join(settings.BASE_DIR, 'leafsnap_final_model.keras') # ◄ Check exact filename extension
model = None

if os.path.exists(MODEL_PATH):
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(MODEL_PATH)
        print("🎯 ML Model loaded into Django successfully!")
    except Exception as e:
        print(f"❌ Error loading ML model: {e}")

# Load labels from labels.txt into a Python list
LABELS_PATH = os.path.join(settings.BASE_DIR, 'labels.txt')
with open(LABELS_PATH, 'r') as f:
    class_labels = [line.strip() for line in f.readlines() if line.strip()]


def test_prediction_view(request):
    if request.method == 'POST' and request.FILES.get('leaf_image'):
        file = request.FILES['leaf_image']
        
        # 1. Save uploaded file temporarily to media/processed directory
        file_name = default_storage.save(f"tmp/{file.name}", file)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        try:
            # 2. Preprocess image exactly how your train.py did it
            # (Assuming standard 224x224 RGB input - update dimensions if you used 128x128 or grayscale)
            img = tf.keras.utils.load_img(file_path, target_size=(224, 224))
            img_array = tf.keras.utils.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)  # Make batch shape (1, 224, 224, 3)
            #img_array = img_array / 255.0                  # Rescale normalization
            
            # 3. Run model prediction
            if model:
                predictions = model.predict(img_array)
                predicted_class_idx = np.argmax(predictions[0])
                confidence = round(float(np.max(predictions[0])) * 100, 2)
                
                # Get folder label string from our index array
                predicted_folder_id = class_labels[predicted_class_idx]
                
                # 4. Fetch additional descriptive metadata from PostgreSQL
                try:
                    plant_db_record = PlantInfo.objects.get(folder_id=predicted_folder_id)
                    common_name = plant_db_record.common_name
                except PlantInfo.DoesNotExist:
                    common_name = "Species matches, but no DB text profile exists yet."
            else:
                predicted_folder_id = "Model file not found or loaded"
                common_name = "N/A"
                confidence = 0.0

        except Exception as e:
            print(f"Prediction crash log: {e}")
            predicted_folder_id = f"Processing Error: {e}"
            common_name = "Error"
            confidence = 0.0
        finally:
            # Clean up the file after prediction so your computer doesn't get cluttered
            if os.path.exists(file_path):
                os.remove(file_path)

        # Send results back to the template screen
        return render(request, 'upload.html', {
            'prediction': predicted_folder_id,
            'common_name': common_name,
            'confidence': confidence
        })

    return render(request, 'upload.html')