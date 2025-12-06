from django.shortcuts import render
from django.utils.html import strip_tags
# Create your views here.
import inspect
from django import forms
from toolbox import forms as forms_module
from toolbox import filters as filters_module
import csv

"""
Utility to generate a json/ dictionary for the help functions/icons in the toolbox
"""

def get_all_form_labels(forms_module, filters_module):
    """
    Returns a dictionary with form/filter class names as keys and 
    dicts of {field_name: label} as values.
    """
    all_forms = {}
    
    # Process Forms
    for name, obj in inspect.getmembers(forms_module, inspect.isclass):
        faulty = []
        try:
            if issubclass(obj, forms.BaseForm):
                form_instance = obj()
                all_forms[name] = {
                    fname: f.label if isinstance(f.label, str) else f.label for fname, f in form_instance.fields.items()
                }
        except:
            faulty.append(name)

    # Process Filters (django_filters)
    for name, obj in inspect.getmembers(filters_module, inspect.isclass):
        try:
            import django_filters
        except ImportError:
            continue
        try: 
            if issubclass(obj, django_filters.FilterSet):
                filter_instance = obj()
                all_forms[name] = {
                    fname: f.label if hasattr(f, 'label') else fname
                    for fname, f in filter_instance.form.fields.items()
                }
        except:
            faulty.append(name)

    return all_forms, faulty



def get_all_labels_as_csv(file_path="all_form_labels.csv"):
    """
    Collects all field names, labels, and help_texts from forms and filters
    and writes them to a CSV file with columns: form_name, field_name, label, help_text
    """
    all_forms, faulty = get_all_form_labels(forms_module, filters_module)

    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # write header
        writer.writerow(["form_name", "field_name", "label", "help_text"])

        for form_name, fields in all_forms.items():
            # Instantiate the form/filter to get help_texts
            form_class = getattr(forms_module, form_name, None) or getattr(filters_module, form_name, None)
            if form_class is None:
                continue

            # For filters, use filter.form.fields
            if 'django_filters' in str(form_class.__bases__):
                filter_instance = form_class()
                field_objs = filter_instance.form.fields
            else:
                form_instance = form_class()
                field_objs = form_instance.fields

            for fname, field in field_objs.items():
                label = strip_tags(str(field.label)) if field.label else fname
                help_text = strip_tags(field.help_text) if getattr(field, 'help_text', None) else ""
                writer.writerow([form_name, fname, label, help_text])

    print(f"CSV written to {file_path}")
    print(f"Faulty forms/filters: {faulty}")
