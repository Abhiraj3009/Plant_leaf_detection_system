import os
import django

# 1. Setup Django environment inside a standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_project.settings')
django.setup()

# Import your model AFTER django.setup() is called
from plant_backend.models import PlantInfo

def seed_database():
    labels_file = 'labels.txt'
    
    if not os.path.exists(labels_file):
        print(f"❌ Error: Could not find '{labels_file}' in your root directory.")
        print("Please make sure labels.txt is sitting next to manage.py.")
        return

    print("🌱 Starting database seeding process...")
    
    with open(labels_file, 'r') as f:
        # Read lines, strip whitespace, and ignore empty lines
        folder_ids = [line.strip() for line in f.readlines() if line.strip()]

    created_count = 0
    skipped_count = 0

    for folder_id in folder_ids:
        # Generate a cleaner name for display purposes
        # Example: 'amelanchier_arborea' -> 'Amelanchier Arborea'
        clean_name = folder_id.replace('_', ' ').replace('-', ' ').title()
        
        # Check if it already exists to prevent duplicate crashing
        plant, created = PlantInfo.objects.get_or_create(
            folder_id=folder_id,
            defaults={
                'common_name': clean_name,       # Temporary fallback
                'botanical_name': clean_name,    # Temporary fallback
                'medicinal_benefits': f"Placeholder profile text for {clean_name}."
            }
        )
        
        if created:
            created_count += 1
        else:
            skipped_count += 1

    print("---")
    print(f"✅ Seeding Complete!")
    print(f"🆕 New Species Added: {created_count}")
    print(f"🔄 Existing Species Skipped: {skipped_count}")
    print(f"📊 Total Records Now in Database: {PlantInfo.objects.count()}")

if __name__ == '__main__':
    seed_database()