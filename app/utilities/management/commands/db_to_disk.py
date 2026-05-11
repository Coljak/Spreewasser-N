import os
import json
import datetime
from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand
from django.db import transaction


BATCH_SIZE = 1000

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


def save_batch(batch, model_label):
    with transaction.atomic():
        for obj in batch:
            obj.save()

    print(f"✅ Saved batch of {len(batch)} for {model_label}")


def load_data_from_json(filepaths, batch_size=BATCH_SIZE):
    not_loaded = []
    not_loaded_length = len(filepaths)
    for filepath in filepaths:
        model_label = os.path.basename(filepath).replace(".json", "")

        print(f"📄 Loading {model_label} from {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:

                batch = []
                total = 0

                for obj in serializers.deserialize("json", f):
                    batch.append(obj)

                    if len(batch) >= batch_size:
                        save_batch(batch, model_label)
                        total += len(batch)
                        batch = []

                if batch:
                    save_batch(batch, model_label)
                    total += len(batch)

            print(f"✅ Imported {total} objects into {model_label}")

        except Exception as e:
            not_loaded.append(filepath)
            print(f"❌ Failed to import {model_label}: {e}")

    if not_loaded:
        if len(not_loaded) == not_loaded_length:
            print("⚠️  All imports failed. Please check the files and try again. The following files could not be imported:", not_loaded)
            return
        print("\n🔁 Retrying failed imports...")
        print(not_loaded)

        # Avoid infinite recursion
        if len(not_loaded) != len(filepaths):
            load_data_from_json(not_loaded, batch_size=batch_size)


def import_all_models(import_dir, app_labels=None, model_names=None):
    print(f"📥 Importing models from: {import_dir}")

    files = sorted(
        f for f in os.listdir(import_dir)
        if f.endswith(".json")
    )

    filtered_files = []

    for f in files:
        filename = f.replace(".json", "")
        app_label, model_name = filename.split(".", 1)

        if app_labels and app_label not in app_labels:
            continue

        if model_names and model_name not in model_names:
            continue

        filtered_files.append(f)

    filepaths = [
        os.path.join(import_dir, f)
        for f in filtered_files
    ]

    print(f"📂 Found {len(filtered_files)} files to import:")
    print(filtered_files)

    load_data_from_json(filepaths)


class Command(BaseCommand):
    help = "Export or import all models to/from JSON files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--import-dir",
            type=str,
            help="Directory to import from",
        )

        parser.add_argument(
            "--no-today",
            action="store_true",
            help="Use 'dump' instead of today's date",
        )

        parser.add_argument(
            "--apps",
            nargs="+",
            type=str,
            help="Apps to export/import",
        )

        parser.add_argument(
            "--models",
            nargs="+",
            type=str,
            help="Model class names to export/import",
        )

        parser.add_argument(
            "--batch-size",
            type=int,
            default=BATCH_SIZE,
            help="Batch size for imports",
        )

    def handle(self, *args, **options):

        app_labels = options.get("apps")
        model_names = options.get("models")

        if options["import_dir"]:
            import_all_models(
                import_dir=options["import_dir"],
                app_labels=app_labels,
                model_names=model_names,
            )

        else:
            export_all_models(
                use_today=not options["no_today"],
                app_labels=app_labels,
                model_names=model_names,
            )