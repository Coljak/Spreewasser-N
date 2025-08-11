"""
This imports each table that is in the specified folder.
It takes files that are named <app_name>.<model_name>.json.
Run the command with 'python manage.py process_folder /path/to/my/folder'.
It takes absolute paths, such as 

python manage.py process_folder ./data
python manage.py process_folder ~/Documents/myproject

"""


import os
from django.core.management.base import BaseCommand, CommandError
import datetime
from django.apps import apps
from django.core import serializers
from django.db import transaction



def import_all_models(import_dir):
    print(f"📥 Importing models from: {import_dir}")
    files = sorted(f for f in os.listdir(import_dir) if f.endswith(".json"))

    for file in files:
        path = os.path.join(import_dir, file)
        model_label = file.replace(".json", "")
        print(f"📄 Loading {model_label} from {file}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                objects = list(serializers.deserialize("json", f))
                with transaction.atomic():
                    for obj in objects:
                        obj.save()
            print(f"✅ Imported {len(objects)} objects into {model_label}")
        except Exception as e:
            print(f"❌ Failed to import {model_label}: {e}")

class Command(BaseCommand):
    help = 'Import data to database from JSON files per model. Naming convention is <app_name>.<model_name>.json'

    def add_arguments(self, parser):
        parser.add_argument('import_dir', type=str, help='Directory containing JSON files to import')

    def handle(self, *args, **kwargs):
        import_dir = kwargs['import_dir']
        if not os.path.isdir(import_dir):
            raise CommandError(f"The specified directory does not exist: {import_dir}")
        else:
            import_all_models(import_dir)
            self.stdout.write(self.style.SUCCESS('Successfully exported database'))



        