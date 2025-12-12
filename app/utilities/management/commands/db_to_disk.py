import os
import json
import datetime
from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand
from django.db import transaction


def export_all_models(export_dir=None, use_today=True, app_labels=None, model_names=None, indent=2):
    if export_dir is None:
        date_label = datetime.date.today().isoformat() if use_today else "dump"
        export_dir = os.path.join("model_exports", date_label)
    os.makedirs(export_dir, exist_ok=True)

    print(f"📁 Exporting to folder: {export_dir}")

    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = model.__name__

        # Skip models not in selected apps/models
        if app_labels and app_label not in app_labels:
            continue
        if model_names and model_name not in model_names:
            continue

        filename = f"{app_label}.{model_name}.json"
        filepath = os.path.join(export_dir, filename)

        queryset = model.objects.all().order_by(model._meta.pk.name)
        if queryset.exists():
            print(f"📝 Exporting {app_label}.{model_name} ({queryset.count()} rows)...")
            with open(filepath, "w", encoding="utf-8") as f:
                serializers.serialize("json", queryset, indent=indent, stream=f)
        else:
            print(f"⚠️  Skipping {app_label}.{model_name} (no data)")

    print("✅ Done exporting models.")


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
    help = "Export or import all models to/from JSON files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--import-dir",
            type=str,
            help="Directory to import from (if omitted, export will be done)",
        )
        parser.add_argument(
            "--no-today",
            action="store_true",
            help="Do not use today’s date for export dir (use 'dump' instead)",
        )
        parser.add_argument(
            "--apps",
            nargs="+",
            type=str,
            help="List of apps to export (space-separated)",
        )
        parser.add_argument(
            "--models",
            nargs="+",
            type=str,
            help="List of model class names to export (space-separated)",
        )

    def handle(self, *args, **options):
        if options["import_dir"]:
            import_all_models(options["import_dir"])
        else:
            export_all_models(
                use_today=not options["no_today"],
                app_labels=options.get("apps"),
                model_names=options.get("models"),
            )
