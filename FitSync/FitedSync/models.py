from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user.set_username(username)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class FitnessGoal(models.Model):
    GOAL_CHOICES = [
        ('LOSE_WEIGHT', 'Lose weight'),
        ('MAINTAIN_WEIGHT', 'Maintain weight'),
        ('GAIN_WEIGHT', 'Gain weight'),
        ('GAIN_MUSCLE', 'Gain muscle'),
        ('MODIFY_DIET', 'Modify my diet')
    ]
    
    name = models.CharField(max_length=30, choices=GOAL_CHOICES, unique=True)

    def __str__(self):
        return self.name
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True)
    target_weight = models.FloatField(null=True, blank=True)

    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sedentary'),
            ('lightly_active', 'Lightly Active'),
            ('moderately_active', 'Not Very Active'),
            ('very_active', 'Very Active'),
            ('extra_active', 'Extra Active'),
        ],
        default='moderately_active'
    )
    fitness_goals = models.ManyToManyField(FitnessGoal, blank=True)

    # Daily calorie goal field
    daily_calorie_goal = models.PositiveIntegerField(null=True, blank=True)  # Calculated daily calorie goal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.username}'s Profile"

class Exercise(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    muscle_group = models.CharField(max_length=100)
    equipment = models.CharField(max_length=100)
    equipment_details = models.CharField(max_length=200, blank=True, null=True)
    muscle_gp_details = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField()
    image_url_secondary = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class CustWorkout(models.Model):
    difficulty_level_choices = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('All Levels', 'All Levels'),
    ]
    name = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    difficulty_level = models.CharField(max_length=20, choices=difficulty_level_choices)

class CustWorkoutLog(models.Model):
    date = models.DateField()
    routine_name = models.CharField(max_length=255)
    duration_minutes = models.IntegerField()
    calories_burned = models.FloatField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
       

class CustWorkoutExercise(models.Model):
    workout = models.ForeignKey(CustWorkout, on_delete=models.CASCADE, related_name="workout_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    repetitions = models.PositiveIntegerField()

    class Meta:
        unique_together = ('workout', 'exercise')
    
class WorkoutRoutine(models.Model):
    ROUTINE_TYPE_CHOICES = [
        ('Strength Training', 'Strength Training'),
        ('HIIT', 'HIIT'),
        ('Yoga', 'Yoga'),
        ('Dance', 'Dance'),
        ('Cardio', 'Cardio'),
        ('Core Training', 'Core Training'),
        ('Circuit Training', 'Circuit Training'),
        ('Plyometrics', 'Plyometrics'),
    ]

    difficulty_level_choices = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('All Levels', 'All Levels'),
    ]

    routine_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    difficulty_level = models.CharField(max_length=20, choices=difficulty_level_choices)
    workout_type = models.CharField(max_length=20, choices=ROUTINE_TYPE_CHOICES)
    equipment_needed = models.CharField(max_length=100, blank=True, null=True)
    sets = models.PositiveIntegerField()
    repetitions = models.CharField(max_length=50)
    exercise = models.ManyToManyField(Exercise, related_name="workout_routines")
    exercises = models.TextField(max_length=100)
    target_muscle_groups = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)

    def calculate_calories(self, user_weight, duration):
        total_calories = 0
        for workout_exercise in self.workoutexercise_set.all():
            # Example calorie formula (calories per set, multiplied by exercise duration)
            calories_burned = (workout_exercise.sets * workout_exercise.reps * user_weight * 0.1) * (duration / 60)
            total_calories += calories_burned
        return total_calories

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Workout Routine"
        verbose_name_plural = "Workout Routines"

class ExerciseLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    date = models.DateField()
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    sets = models.IntegerField(null=True, blank=True)
    reps = models.IntegerField(null=True, blank=True)

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(WorkoutRoutine, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
            return f"{self.workout.name} - {self.exercise.name}"


class WorkoutLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    routine_name = models.CharField(max_length=255)
    duration_minutes = models.IntegerField()
    calories_burned = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.routine_name} on {self.date}"


class UserDailyLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField(null=True, blank=True)
    total_calories_consumed = models.FloatField(default=0)
    total_calories_burned = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - Log for {self.date}"


class FoodItem(models.Model):
    # Food item information
    food_name = models.CharField(max_length=255)

    # Nutritional information
    caloric_value = models.FloatField()
    fat = models.FloatField()
    saturated_fats = models.FloatField()
    monounsaturated_fats = models.FloatField()
    polyunsaturated_fats = models.FloatField()
    carbohydrates = models.FloatField()
    sugars = models.FloatField()
    protein = models.FloatField()
    cholesterol = models.FloatField()
    sodium = models.FloatField()
    water = models.FloatField()

    # Vitamins and minerals
    vitamin_a = models.FloatField(null=True, blank=True)
    vitamin_b1 = models.FloatField(null=True, blank=True)
    vitamin_b2 = models.FloatField(null=True, blank=True)
    vitamin_c = models.FloatField(null=True, blank=True)
    vitamin_d = models.FloatField(null=True, blank=True)
    vitamin_e = models.FloatField(null=True, blank=True)
    vitamin_k = models.FloatField(null=True, blank=True)

    # Minerals
    calcium = models.FloatField(null=True, blank=True)
    iron = models.FloatField(null=True, blank=True)

    # Nutrition density
    nutrition_density = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.food

class MealLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.CharField(
        max_length=50, 
        choices=[('breakfast', 'breakfast'), 
                 ('lunch', 'lunch'), 
                 ('dinner', 'dinner'), 
                 ('snacks', 'snacks')]
    )
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Quantity in grams or serving size")
    food_name = models.CharField(max_length=255)
    
    # Calculated fields
    calories = models.FloatField(editable=False, null=True)
    protein = models.FloatField(editable=False, null=True)
    carbohydrates = models.FloatField(editable=False, null=True)
    fat = models.FloatField(editable=False, null=True)

    def save(self, *args, **kwargs):
        # Automatically calculate nutrient values based on the food item and quantity
        self.calories = (self.food_item.caloric_value * self.quantity) / 100
        self.protein = (self.food_item.protein * self.quantity) / 100
        self.carbohydrates = (self.food_item.carbohydrates * self.quantity) / 100
        self.fat = (self.food_item.fat * self.quantity) / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.meal_type} on {self.date}"

class Meal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.CharField(max_length=50)  # e.g., Breakfast, Lunch, Dinner
    meal_logs = models.ManyToManyField(MealLog, related_name='meals')

    def __str__(self):
        return f"{self.user.username} - {self.meal_type} on {self.date}"


class Goal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=50, choices=[('Weight Loss', 'Weight Loss'), ('Caloric Intake', 'Caloric Intake')])
    target_value = models.FloatField()
    current_value = models.FloatField()
    date_set = models.DateField()
    date_achieved = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Goal: {self.goal_type}"

    
class CalorieBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    calories_consumed = models.FloatField()
    calories_burned = models.FloatField()

    @property
    def net_calories(self):
        return self.calories_consumed - self.calories_burned

    def __str__(self):
        return f"{self.user.username} - Calorie Balance on {self.date}"


