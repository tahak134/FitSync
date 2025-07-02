from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CalorieDataSerializer(serializers.Serializer):
    date = serializers.DateField()
    consumed = serializers.FloatField()
    burned = serializers.FloatField()


class FitnessGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessGoal
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    fitness_goals = FitnessGoalSerializer(many=True, required=False)
    
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    birthDate = serializers.DateField(source='date_of_birth')
    currentWeight = serializers.FloatField(source='weight')
    goalWeight = serializers.FloatField(source='target_weight')
    sex = serializers.CharField(source='gender')
    height = serializers.FloatField()
    confirm_password = serializers.CharField(write_only=True)
    daily_calorie_goal = serializers.FloatField()

    class Meta:
        model = CustomUser
        fields = [
            'firstName', 'lastName', 'birthDate', 'currentWeight', 'goalWeight',
            'height', 'sex', 'activity_level', 'email', 'password', 'fitness_goals', 'confirm_password', 'daily_calorie_goal'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        # Validate password and confirm_password match
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # Pop fitness goals from validated data and save separately
        fitness_goals = validated_data.pop('fitness_goals', [])
        
        # Create the user instance
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            date_of_birth=validated_data['date_of_birth'],
            gender=validated_data['gender'],
            height=validated_data['height'],
            weight=validated_data['weight'],
            target_weight=validated_data['target_weight'],
            activity_level=validated_data['activity_level'],
            daily_calorie_goal=validated_data['daily_calorie_goal'],
        )
        
        # Add fitness goals to user profile
        for goal in fitness_goals:
            fitness_goal, _ = FitnessGoal.objects.get_or_create(name=goal['name'])
            user.fitness_goals.add(fitness_goal)
        
        return user

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all(), write_only=True, source='exercise')

    class Meta:
        model = WorkoutExercise
        fields = ['exercise', 'exercise_id', 'sets', 'reps', 'duration_minutes']

class CustWorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all())
    sets = serializers.IntegerField()
    repetitions = serializers.IntegerField()

    class Meta:
        model = CustWorkoutExercise
        fields = ['exercise', 'sets', 'repetitions']

class CustWorkoutSerializer(serializers.ModelSerializer):
    # This field will represent the exercises, including sets and reps.
    workout_exercises = CustWorkoutExerciseSerializer(many=True)

    class Meta:
        model = CustWorkout
        fields = ['id', 'user', 'name', 'workout_exercises', 'duration', 'difficulty_level']

    def create(self, validated_data):
        workout_exercises_data = validated_data.pop('workout_exercises')
        # Create the CustWorkout instance first
        workout = CustWorkout.objects.create(**validated_data)

        # Now create WorkoutExercise instances for each exercise, sets, and reps
        for exercise_data in workout_exercises_data:
            exercise = exercise_data.pop('exercise')
            CustWorkoutExercise.objects.create(workout=workout, exercise=exercise, **exercise_data)

        return workout

    def update(self, instance, validated_data):
        workout_exercises_data = validated_data.pop('workout_exercises', None)

        # Update the other fields first
        instance.name = validated_data.get('name', instance.name)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.difficulty_level = validated_data.get('difficulty_level', instance.difficulty_level)
        instance.save()

        # Update or create the exercises, sets, and reps
        if workout_exercises_data is not None:
            # First, clear existing workout exercises
            instance.workout_exercises.all().delete()

            # Now, add the new workout exercises
            for exercise_data in workout_exercises_data:
                exercise = exercise_data.pop('exercise')
                WorkoutExercise.objects.create(custom_workout=instance, exercise=exercise, **exercise_data)

        return instance
    
class WorkoutRoutineSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(source='workoutexercise_set', many=True)
    calories_burned = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutRoutine
        fields = ['id', 'name', 'description', 'duration', 'difficulty_level', 'workout_type', 'equipment_needed', 'exercises', 'exercise', 'target_muscle_groups', 'notes', 'calories_burned']

    def create(self, validated_data):
        exercises_data = validated_data.pop('workoutexercise_set')
        workout_routine = WorkoutRoutine.objects.create(**validated_data)
        for exercise_data in exercises_data:
            WorkoutExercise.objects.create(workout=workout_routine, **exercise_data)
        return workout_routine

    def update(self, instance, validated_data):
        exercises_data = validated_data.pop('workoutexercise_set', [])
        instance = super().update(instance, validated_data)
        
        instance.workoutexercise_set.all().delete()
        for exercise_data in exercises_data:
            WorkoutExercise.objects.create(workout=instance, **exercise_data)
        
        return instance

    def get_calories_burned(self, obj):
        user_weight = self.context['request'].user.weight
        duration = self.context['request'].data.get('duration', obj.duration)
        return obj.calculate_calories(user_weight, duration)

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'

class UserDailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDailyLog
        fields = '__all__'

class MealLogSerializer(serializers.ModelSerializer):
    food_name = serializers.SerializerMethodField()  # Dynamically get food name from food_item
    calories = serializers.FloatField(read_only=True)
    protein = serializers.FloatField(read_only=True)
    carbohydrates = serializers.FloatField(read_only=True)
    fat = serializers.FloatField(read_only=True)

    class Meta:
        model = MealLog
        fields = '__all__'

    def get_food_name(self, obj):
        if obj.food_item:
            return obj.food_item.food_name
        return None

    def create(self, validated_data):
        food_name = validated_data.pop('food_name', None)
        if food_name:
            food_item = FoodItem.objects.filter(name=food_name).first()
            validated_data['food_item'] = food_item
        return super().create(validated_data)


class MealSerializer(serializers.ModelSerializer):
    meal_logs = MealLogSerializer(many=True, read_only=True)  # Nested MealLog serializer

    class Meta:
        model = Meal
        fields = '__all__'


class ExerciseLogSerializer(serializers.ModelSerializer):
    exercise = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all())  # Accepts ID as input

    class Meta:
        model = ExerciseLog
        fields = ['id', 'user', 'exercise', 'date', 'duration_minutes', 'calories_burned', 'sets', 'reps']
        read_only_fields = ['id', 'user']  # Auto-populated fields

    def create(self, validated_data):
        user= self.context['request'].user  # Get the user from the request context
        exercise = validated_data['exercise']
        duration_minutes = validated_data.get('duration_minutes')
        sets = validated_data.get('sets', 1)
        reps = validated_data.get('reps', 10)
        date = validated_data.get('date')
        calories_burned = validated_data.get('calories_burned')

        # Create and save the ExerciseLog
        exercise_log = ExerciseLog.objects.create(
            user=user,
            exercise=exercise,
            duration_minutes=duration_minutes,
            sets=sets,
            reps=reps,
            date=date,
            calories_burned=calories_burned
        )
        return exercise_log

class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = ['id', 'user', 'date', 'routine_name', 'duration_minutes', 'calories_burned']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        date = validated_data.get('date')
        routine_name = validated_data['routine_name']
        duration_minutes = validated_data.get('duration_minutes') 
        calories_burned = validated_data.get('calories_burned')

        workout_log = WorkoutLog.objects.create(
            user=user,
            date=date,
            routine_name=routine_name,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned
        )
        return workout_log

class CustWorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustWorkoutLog
        fields = ['id', 'user', 'date', 'routine_name', 'duration_minutes', 'calories_burned']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        date = validated_data.get('date')
        routine_name = validated_data['routine_name']
        duration_minutes = validated_data.get('duration_minutes') 
        calories_burned = validated_data.get('calories_burned')

        cust_workout_log = CustWorkoutLog.objects.create(
            user=user,
            date=date,
            routine_name=routine_name,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned
        )
        return cust_workout_log
    
class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

class CalorieBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalorieBalance
        fields = '__all__'