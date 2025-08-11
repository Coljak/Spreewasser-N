"""
This management command exports the ENTIRE database.
It creates one  JSON file per model in the directory 'model_exports'.
The process may take a while.
"""


import os
import sys
import django
import json
from django.core.management.base import BaseCommand
import datetime
from django.apps import apps
from django.core import serializers



def export_all_models(export_dir=None, use_today=True, indent=2):
    # Step 2: Create output directory
    if export_dir is None:
        date_label = datetime.date.today().isoformat() if use_today else "dump"
        export_dir = os.path.join("model_exports", date_label)
    os.makedirs(export_dir, exist_ok=True)
    print(f"📁 Exporting to folder: {export_dir}")

    # Step 3: Loop through all models
    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = model.__name__
        filename = f"{app_label}.{model_name}.json"
        filepath = os.path.join(export_dir, filename)

        queryset = model.objects.all().order_by(model._meta.pk.name)
        if queryset.exists():
            print(f"📝 Exporting {app_label}.{model_name} ({queryset.count()} rows)...")
            with open(filepath, "w", encoding="utf-8") as f:
                serializers.serialize("json", queryset, indent=indent, stream=f)
        else:
            print(f"⚠️  Skipping {app_label}.{model_name} (no data)")

    print("✅ Done exporting all models.")

class Command(BaseCommand):
    help = 'Export the entire database as JSON file per model'

    def handle(self, *args, **kwargs):
        export_all_models()

        self.stdout.write(self.style.SUCCESS('Successfully exported database'))