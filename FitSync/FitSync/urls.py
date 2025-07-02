from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from FitedSync.views import *

router = routers.DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'workout-routines', WorkoutRoutineViewSet, basename='workout-routine')
router.register(r'cust-workout-routines', CustWorkoutViewSet, basename='cust-workout-routine')
router.register(r'users', UserViewSet, basename='user')
router.register(r'foods', FoodViewSet)
router.register(r'daily-logs', UserDailyLogViewSet, basename='daily-log')
router.register(r'exercise-logs', ExerciseLogViewSet, basename='exercise-log')
router.register(r'workout-logs', WorkoutLogViewSet, basename='workout-log')
router.register(r'cust-workout-logs', CustWorkoutLogViewSet, basename='cust-workout-log')
router.register(r'meals', MealViewSet)
router.register(r'users/calorie-data/', CalorieDataViewSet, basename='calorie-data'),


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('FitedSync.urls')),
]