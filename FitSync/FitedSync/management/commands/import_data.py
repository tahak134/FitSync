import csv
from django.core.management.base import BaseCommand, CommandError
from FitedSync.models import Exercise, FoodItem, WorkoutRoutine
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Populate database tables from CSV files.'

    def handle(self, *args, **kwargs):
        try:
            # Import Exercises
            # self.import_exercise_data()
            # self.stdout.write(self.style.SUCCESS('Successfully imported exercises data.'))
            
            # # Import Food Items
            # self.import_food_data()
            # self.stdout.write(self.style.SUCCESS('Successfully imported food items data.'))
            
            # Import Workout Routines
            self.import_workout_routines()
            self.stdout.write(self.style.SUCCESS('Successfully imported workout routines data.'))
        
        except Exception as e:
            raise CommandError(f'Error importing data: {e}')

    # def import_exercise_data(self):
    #     # Assuming 'combined_exercise_data.csv' is located in the base directory
    #     path = os.path.join(settings.BASE_DIR, 'FitedSync', 'combined_exercise_data.csv')
    #     with open(path, 'r') as file:
    #         reader = csv.DictReader(file)
    #         for row in reader:
    #             Exercise.objects.update_or_create(
    #                 title=row['Title'],
    #                 defaults={
    #                     'description': row['Description_URL'],
    #                     'image_url': row['Exercise_Image'],
    #                     'image_url_secondary': row['Exercise_Image1'],
    #                     'muscle_gp_details': row['muscle_gp_details'],
    #                     'equipment_details': row['equipment_details'],
    #                     'equipment': row['equipment'],
    #                     'muscle_group': row['muscle_group'],
    #                 }
    #             )

    # def import_food_data(self):
    #     # Assuming 'combined_food_data.csv' is located in the base directory
    #     path = os.path.join(settings.BASE_DIR,'FitedSync', 'combined_food_data.csv')
    #     with open(path, 'r') as file:
    #         reader = csv.DictReader(file)
    #         for row in reader:
    #             FoodItem.objects.update_or_create(
    #                 food = row['food'],
    #                 defaults={
    #                     'caloric_value': float(row['Caloric Value']),
    #                     'fat': float(row['Fat']),
    #                     'saturated_fats': float(row['Saturated Fats']),
    #                     'monounsaturated_fats': float(row['Monounsaturated Fats']),
    #                     'polyunsaturated_fats': float(row['Polyunsaturated Fats']),
    #                     'carbohydrates': float(row['Carbohydrates']),
    #                     'sugars': float(row['Sugars']),
    #                     'protein': float(row['Protein']),
    #                     'cholesterol': float(row['Cholesterol']),
    #                     'sodium': float(row['Sodium']),
    #                     'water': float(row['Water']),
    #                     'vitamin_a': float(row['Vitamin A']),
    #                     'vitamin_b1': float(row['Vitamin B1']),
    #                     'vitamin_b2': float(row['Vitamin B2']),
    #                     'vitamin_c': float(row['Vitamin C']),
    #                     'vitamin_d': float(row['Vitamin D']),
    #                     'vitamin_e': float(row['Vitamin E']),
    #                     'vitamin_k': float(row['Vitamin K']),
    #                     'calcium': float(row['Calcium']),
    #                     'iron': float(row['Iron']),
    #                     'nutrition_density': float(row['Nutrition Density']),
    #                 }
    #             )

    def import_workout_routines(self):
        # Assuming 'workout_routines.csv' is located in the base directory
        path = os.path.join(settings.BASE_DIR,'FitedSync', 'workout_routines.csv')
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                WorkoutRoutine.objects.update_or_create(
                    routine_id=row['Routine ID'],
                    defaults={
                        'name': row['Name'],
                        'description': row['Description'],
                        'duration': int(row['Duration(minutes)']),
                        'difficulty_level': row['Difficulty Level'],
                        'workout_type': row['Type'],
                        'equipment_needed': row['Equipment Needed'],
                        'sets': int(row['Sets']),
                        'repetitions': row['Repetitions'],
                        'exercises': row['Exercises'],
                        'target_muscle_groups': row['Target Muscle Groups'],
                        'notes': row['Notes'],
                    }
                )
