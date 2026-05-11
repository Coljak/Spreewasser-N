import os
import json
import datetime

from django.apps import apps
from django.core import serializers
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction


BATCH_SIZE = 1000
EXPORT_PART_SIZE = 500_000


# =========================================================
# EXPORT
# =========================================================

def write_queryset_to_parts(
    queryset,
    filepath_base,
    part_size=EXPORT_PART_SIZE,
    indent=None,
):
    """
    Writes queryset into:
      model.part1.json
      model.part2.json
      ...
    """

    total_written = 0
    part_number = 1

    current_count = 0
    first_in_file = True

    filepath = f"{filepath_base}.part{part_number}.json"
    f = open(filepath, "w", encoding="utf-8")

    print(f"📝 Writing {filepath}")

    f.write("[")

    for obj in queryset.iterator(chunk_size=5000):

        if current_count >= part_size:
            f.write("]")
            f.close()

            print(
                f"✅ Finished part {part_number} "
                f"({current_count} rows)"
            )

            part_number += 1
            current_count = 0
            first_in_file = True

            filepath = f"{filepath_base}.part{part_number}.json"
            f = open(filepath, "w", encoding="utf-8")

            print(f"📝 Writing {filepath}")

            f.write("[")

        serialized = serializers.serialize(
            "json",
            [obj],
            indent=indent,
        )[1:-1]  # remove outer []

        if not first_in_file:
            f.write(",")

        f.write(serialized)

        first_in_file = False
        current_count += 1
        total_written += 1

        if total_written % 100_000 == 0:
            print(f"   ⏳ Exported {total_written:,} rows...")

    f.write("]")
    f.close()

    print(
        f"✅ Finished part {part_number} "
        f"({current_count} rows)"
    )

    print(f"✅ Total exported: {total_written:,} rows")


def export_all_models(
    export_dir=None,
    use_today=True,
    app_labels=None,
    model_names=None,
    indent=None,
    part_size=EXPORT_PART_SIZE,
):
    if export_dir is None:
        date_label = (
            datetime.date.today().isoformat()
            if use_today
            else "dump"
        )

        export_dir = os.path.join(
            settings.APP_DATA_DIR,
            "model_exports",
            date_label,
        )

    os.makedirs(export_dir, exist_ok=True)

    print(f"📁 Exporting to folder: {export_dir}")

    for model in apps.get_models():

        app_label = model._meta.app_label
        model_name = model.__name__

        if app_labels and app_label not in app_labels:
            continue

        if model_names and model_name not in model_names:
            continue

        queryset = model.objects.all().order_by(
            model._meta.pk.name
        )

        count = queryset.count()

        if count == 0:
            print(
                f"⚠️ Skipping {app_label}.{model_name} "
                f"(no data)"
            )
            continue

        print(
            f"📝 Exporting {app_label}.{model_name} "
            f"({count:,} rows)"
        )

        filepath_base = os.path.join(
            export_dir,
            f"{app_label}.{model_name}"
        )

        write_queryset_to_parts(
            queryset=queryset,
            filepath_base=filepath_base,
            part_size=part_size,
            indent=indent,
        )

    print("✅ Done exporting models.")


# =========================================================
# IMPORT
# =========================================================

def save_batch(batch, model_label):

    with transaction.atomic():
        for obj in batch:
            obj.save()

    print(
        f"✅ Saved batch of {len(batch)} "
        f"for {model_label}"
    )


def load_data_from_json(
    filepaths,
    batch_size=BATCH_SIZE,
):
    not_loaded = []

    for filepath in filepaths:

        filename = os.path.basename(filepath)

        model_label = filename.split(".part")[0]

        print(f"📄 Loading {filename}")

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

            print(
                f"✅ Imported {total:,} objects "
                f"into {model_label}"
            )

        except Exception as e:

            not_loaded.append(filepath)

            print(
                f"❌ Failed to import "
                f"{filename}: {e}"
            )

    if not_loaded:

        print("\n🔁 Retrying failed imports...")

        if len(not_loaded) != len(filepaths):
            load_data_from_json(
                not_loaded,
                batch_size=batch_size,
            )


def import_all_models(
    import_dir,
    app_labels=None,
    model_names=None,
    batch_size=BATCH_SIZE,
):
    print(f"📥 Importing models from: {import_dir}")
    if 'app_data' in import_dir.split(os.sep):
            import_dir = import_dir.split('app_data', 1)[1].lstrip(os.sep)
    if 'model_imports' in import_dir.split(os.sep):
        import_dir = import_dir.split('model_imports', 1)[1].lstrip(os.sep)

    files = sorted(
        f for f in os.listdir(import_dir)
        if f.endswith(".json")
    )

    filtered_files = []

    for f in files:

        # Example:
        # app.Model.part1.json

        base = f.rsplit(".part", 1)[0]

        app_label, model_name = base.split(".", 1)

        if app_labels and app_label not in app_labels:
            continue

        if model_names and model_name not in model_names:
            continue

        filtered_files.append(f)

    filepaths = [
        os.path.join(
            settings.APP_DATA_DIR,
            'model_imports',
            import_dir, 
            f
            )
        for f in filtered_files
    ]

    print(f"📂 Found {len(filepaths)} files")

    load_data_from_json(
        filepaths,
        batch_size=batch_size,
    )


# =========================================================
# COMMAND
# =========================================================

class Command(BaseCommand):

    help = "Export/import all models"

    def add_arguments(self, parser):

        parser.add_argument(
            "--import-dir",
            type=str,
        )

        parser.add_argument(
            "--no-today",
            action="store_true",
        )

        parser.add_argument(
            "--apps",
            nargs="+",
            type=str,
        )

        parser.add_argument(
            "--models",
            nargs="+",
            type=str,
        )

        parser.add_argument(
            "--batch-size",
            type=int,
            default=BATCH_SIZE,
        )

        parser.add_argument(
            "--part-size",
            type=int,
            default=EXPORT_PART_SIZE,
            help="Rows per export file",
        )

    def handle(self, *args, **options):

        if options["import_dir"]:

            import_all_models(
                import_dir=options["import_dir"],
                app_labels=options.get("apps"),
                model_names=options.get("models"),
                batch_size=options["batch_size"],
            )

        else:

            export_all_models(
                use_today=not options["no_today"],
                app_labels=options.get("apps"),
                model_names=options.get("models"),
                part_size=options["part_size"],
            )