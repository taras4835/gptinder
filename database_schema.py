import os
import sys
import django
from django.apps import apps
from django.db.models import ForeignKey, ManyToManyField

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
gptinder_back_path = os.path.join(project_path, 'gptinder_back')
sys.path.append(project_path)
sys.path.append(gptinder_back_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gptinder_back.gptinder.settings')
django.setup()

def generate_er_diagram():
    """Generate ER diagram for all models in the project"""
    
    print("```mermaid")
    print("erDiagram")
    
    processed_models = set()
    relationship_pairs = set()  # To avoid duplicate relationships
    
    # First pass: Add all models
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.') or app_config.name in ['admin', 'contenttypes', 'sessions', 'auth']:
            continue
            
        for model in app_config.get_models():
            model_name = model.__name__
            processed_models.add(model_name)
            
            fields_str = []
            for field in model._meta.fields:
                if not isinstance(field, ForeignKey):
                    field_type = field.get_internal_type()
                    nullable = "NULL" if field.null else "NOT NULL"
                    if field.primary_key:
                        pk = "PK"
                    else:
                        pk = ""
                    
                    # Convert Django field types to more generic database types
                    if field_type == 'CharField' or field_type == 'TextField':
                        db_type = "string"
                    elif field_type in ['IntegerField', 'AutoField', 'BigAutoField']:
                        db_type = "integer"
                    elif field_type in ['FloatField', 'DecimalField']:
                        db_type = "float"
                    elif field_type in ['BooleanField', 'NullBooleanField']:
                        db_type = "boolean"
                    elif field_type in ['DateField', 'DateTimeField']:
                        db_type = "datetime"
                    elif field_type == 'JSONField':
                        db_type = "json"
                    elif field_type == 'ImageField':
                        db_type = "file"
                    else:
                        db_type = field_type.lower().replace("field", "")
                    
                    fields_str.append(f"    {field.name} {db_type} {pk}")
            
            print(f"    {model_name} {{")
            print("\n".join(fields_str))
            print("    }")
    
    # Second pass: Add relationships
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.') or app_config.name in ['admin', 'contenttypes', 'sessions', 'auth']:
            continue
            
        for model in app_config.get_models():
            model_name = model.__name__
            
            # Process ForeignKey relationships
            for field in model._meta.fields:
                if isinstance(field, ForeignKey):
                    related_model = field.remote_field.model.__name__
                    
                    # Ensure both models are in our processed list
                    if related_model in processed_models:
                        rel_pair = f"{model_name}_{related_model}_{field.name}"
                        if rel_pair not in relationship_pairs:
                            relationship_pairs.add(rel_pair)
                            print(f"    {related_model} ||--o{{ {model_name} : \"{field.name}\"")
            
            # Process ManyToMany relationships
            for field in model._meta.many_to_many:
                related_model = field.remote_field.model.__name__
                
                # Ensure both models are in our processed list
                if related_model in processed_models:
                    rel_pair = f"{model_name}_{related_model}_{field.name}"
                    rev_pair = f"{related_model}_{model_name}_{field.name}"
                    
                    # Check if we've already processed this relationship in reverse
                    if rel_pair not in relationship_pairs and rev_pair not in relationship_pairs:
                        relationship_pairs.add(rel_pair)
                        print(f"    {model_name} }}|--o{{ {related_model} : \"{field.name}\"")
    
    print("```")

if __name__ == "__main__":
    generate_er_diagram() 