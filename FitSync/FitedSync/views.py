from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import CustomUser, Exercise, WorkoutRoutine, FoodItem, UserDailyLog, MealLog, ExerciseLog, CustWorkout, Meal
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)        

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        print("Serializer validated data:", serializer.validated_data)
        serializer.save()

class CalorieDataViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CalorieDataSerializer

    def get(self, request):
        user_id = self.request.query_params.get('userId')

        # Aggregate data for Meal Logs
        meal_logs = (
            MealLog.objects.filter(user_id=user_id)
            .values('date')
            .annotate(consumed=Sum('calories'))
        )

        # Aggregate data for Exercise Logs
        exercise_logs = (
            ExerciseLog.objects.filter(user_id=user_id)
            .values('date')
            .annotate(burned=Sum('calories_burned'))
        )

        workout_logs = (
            WorkoutLog.objects.filter(user_id=user_id)
            .values('date')
            .annotate(burned=Sum('calories_burned'))
        )

        # Combine data by date
        data = {}
        for log in meal_logs:
            date = log['date']
            if date not in data:
                data[date] = {'date': date, 'consumed': 0, 'burned': 0}
            data[date]['consumed'] = log['consumed']

        for log in exercise_logs:
            date = log['date']
            if date not in data:
                data[date] = {'date': date, 'consumed': 0, 'burned': 0}
            data[date]['burned'] = log['burned']

        for log in workout_logs:
            date = log['date']
            if date not in data:
                data[date] = {'date': date, 'consumed': 0, 'burned': 0}
            data[date]['burned'] = log['burned']

        # Convert to list for serialization
        response_data = list(data.values())
        return Response(response_data)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                password = request.data.get('password')
                if password:
                    user.set_password(password)  # Hash the new password
                    user.save()  # Save the user instance again to apply the password change
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        exercises = Exercise.objects.filter(title__icontains=query)
        serializer = self.get_serializer(exercises, many=True)
        return Response(serializer.data)
        
class CustWorkoutViewSet(viewsets.ModelViewSet):
    queryset = CustWorkout.objects.all()
    serializer_class = CustWorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return CustWorkout.objects.filter(user=self.request.user)
    
    def get_routine_with_exercises(routine_id):
        routine = get_object_or_404(CustWorkout.objects.prefetch_related('workout_exercises__exercise'), id=routine_id)
        return {
        "id": routine.id,
        "name": routine.name,
        "user": routine.user.id,
        "duration": routine.duration,
        "difficulty_level": routine.difficulty_level,
        "workout_exercises": [
            {
                "id": we.id,
                "exercise": we.exercise.id if we.exercise else None,
                "sets": we.sets,
                "repetitions": we.repetitions,
            }
            for we in routine.workout_exercises.all() if we.exercise
        ],
    }

    @action(detail=True, methods=['post'])
    def log_workout(self, request, pk=None):
        custom_workout = self.get_object()
        user = request.user
        weight = request.data.get('weight')
        
        if not weight:
            return Response({"error": "Weight is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            weight = float(weight)
        except ValueError:
            return Response({"error": "Invalid weight value"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate calories burned (you may want to adjust this calculation)
        calories_burned = custom_workout.calculate_calories(weight)

        log = ExerciseLog.objects.create(
            user=user,
            custom_workout=custom_workout,
            duration_minutes=custom_workout.duration,
            calories_burned=calories_burned,
            date=datetime.now().date()
        )

        serializer = ExerciseLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkoutRoutineViewSet(viewsets.ModelViewSet):
    queryset = WorkoutRoutine.objects.all()
    serializer_class = WorkoutRoutineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        logger.debug(f"Accessing workout-routines list view with request: {request.method}")
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in workout-routines list view: {str(e)}")
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None, *args, **kwargs):
        logger.debug(f"Accessing workout-routine detail view for pk: {pk}")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Workout routine not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in workout-routine detail view: {str(e)}")
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        logger.debug("Getting workout-routines queryset")
        return WorkoutRoutine.objects.all()

    @action(detail=True, methods=['post'])
    def log_workout(self, request, pk=None):
        try:
            workout = self.get_object()
            user = request.user
            duration = request.data.get('duration', workout.duration)
            
            log = ExerciseLog.objects.create(
                user=user,
                workout_routine=workout,
                duration_minutes=duration,
                calories_burned=workout.calculate_calories(user.weight, duration),
                date=datetime.now().date()
            )
            
            serializer = ExerciseLogSerializer(log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error logging workout: {str(e)}")
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FoodViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        foods = FoodItem.objects.filter(food_name__icontains=query)
        serializer = self.get_serializer(foods, many=True)
        return Response(serializer.data)

class UserDailyLogViewSet(viewsets.ModelViewSet):
    serializer_class = UserDailyLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserDailyLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def today(self, request):
        log = UserDailyLog.objects.filter(
            user=request.user,
            date=datetime.now().date()
        ).first()
        if not log:
            log = UserDailyLog.objects.create(
                user=request.user,
                date=datetime.now().date()
            )
        serializer = self.get_serializer(log)
        return Response(serializer.data)

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    @action(detail=False, methods=['get'])
    def get_daily_meal_summary(self, request):
        
        user = request.user
        date = request.query_params.get('date')

        if not user.is_authenticated:
            return Response({"error": "User must be authenticated."}, 
                            status=status.HTTP_401_UNAUTHORIZED)

        if not date:
            return Response({"error": "date is a required query parameter."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            meal_logs = MealLog.objects.filter(user=user, date=date).select_related('food_item')
            data = [
                {
                    'id': log.id,
                    'meal_type': log.meal_type,
                    'quantity': log.quantity,
                    'calories': log.calories,
                    'protein': log.protein,
                    'carbohydrates': log.carbohydrates,
                    'fat': log.fat,
                    'food_item': {
                        'id': log.food_item.id,
                        'food_name': log.food_item.food_name,
                        'caloric_value': log.food_item.caloric_value,
                        'protein': log.food_item.protein,
                        'carbohydrates': log.food_item.carbohydrates,
                        'fat': log.food_item.fat,
                    }
                }
                for log in meal_logs
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a meal and its associated meal logs.
        """
        data = request.data
        user = request.user
        date = data.get('date')
        meal_type = data.get('meal_type')
        food_items_data = data.get('food_items', [])

        if not date or not meal_type or not food_items_data:
            return Response({"error": "date, meal_type, and food_items are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create or retrieve the meal entry
            meal, created = Meal.objects.get_or_create(
                user=user,
                date=date,
                meal_type=meal_type
            )

            # Clear any existing logs for the meal (to avoid duplicates)
            meal.meal_logs.clear()

            # Create meal logs for each food item and associate them with the meal
            for food_data in food_items_data:
                food_item_id = food_data.get('food_item')
                quantity = food_data.get('quantity')
                food_name = food_data.get('food_name')

                if not food_item_id or not quantity:
                    return Response({"error": "Each food item must include food_item and quantity."},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Get the FoodItem instance
                food_item = FoodItem.objects.get(id=food_item_id)

                # Calculate nutritional values
                calories = food_item.caloric_value * quantity
                protein = food_item.protein * quantity
                carbohydrates = food_item.carbohydrates * quantity
                fat = food_item.fat * quantity

                # Create a new MealLog instance
                meal_log = MealLog.objects.create(
                    user=user,
                    date=date,
                    meal_type=meal_type,
                    food_item=food_item,
                    quantity=quantity,
                    calories=calories,
                    protein=protein,
                    carbohydrates=carbohydrates,
                    food_name=food_name,
                    fat=fat
                )

                # Associate the MealLog with the Meal
                meal.meal_logs.add(meal_log)

            # Calculate the total nutrition from the meal logs associated with this meal
            meal_logs = meal.meal_logs.all()
            meal.total_calories = meal_logs.aggregate(Sum('calories'))['calories__sum'] or 0
            meal.total_protein = meal_logs.aggregate(Sum('protein'))['protein__sum'] or 0
            meal.total_carbs = meal_logs.aggregate(Sum('carbohydrates'))['carbohydrates__sum'] or 0
            meal.total_fat = meal_logs.aggregate(Sum('fat'))['fat__sum'] or 0
            meal.save()

            # Serialize the updated meal instance
            serializer = MealSerializer(meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except FoodItem.DoesNotExist:
            return Response({"error": "Invalid food item."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExerciseLogViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        today = datetime.now().date()
        return ExerciseLog.objects.filter(user=user, date=today)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Get query parameters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # If start_date is not provided, default to 7 days ago
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # If end_date is not provided, default to today
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Filter queryset by date range
        queryset = queryset.filter(date__range=[start_date, end_date])

        # Group by exercise and aggregate data
        exercise_summary = queryset.values('exercise__title').annotate(
            total_duration=Sum('duration_minutes'),
            total_calories=Sum('calories_burned')
        )

        return Response(exercise_summary)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise ValidationError({"detail": f"Error creating exercise log: {str(e)}"})

class WorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        today = datetime.now().date()
        return WorkoutLog.objects.filter(user=user, date=today)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Get query parameters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # If start_date is not provided, default to 7 days ago
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # If end_date is not provided, default to today
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Filter queryset by date range
        queryset = queryset.filter(date__range=[start_date, end_date])

        # Group by exercise and aggregate data
        workout_summary = queryset.values('routine_name').annotate(
            total_duration=Sum('duration_minutes'),
            total_calories=Sum('calories_burned')
        )

        return Response(workout_summary)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise ValidationError({"detail": f"Error creating workout log: {str(e)}"})
        
class CustWorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = CustWorkoutLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        today = datetime.now().date()
        return CustWorkoutLog.objects.filter(user=user, date=today)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Get query parameters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # If start_date is not provided, default to 7 days ago
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # If end_date is not provided, default to today
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Filter queryset by date range
        queryset = queryset.filter(date__range=[start_date, end_date])

        # Group by exercise and aggregate data
        cust_workout_summary = queryset.values('routine_name').annotate(
            total_duration=Sum('duration_minutes'),
            total_calories=Sum('calories_burned')
        )

        return Response(cust_workout_summary)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise ValidationError({"detail": f"Error creating custom workout log: {str(e)}"})