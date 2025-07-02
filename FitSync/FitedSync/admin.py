from django.contrib import admin
from .models import CustomUser, WorkoutLog, MealLog, Goal, CalorieBalance

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'weight', 'height', 'daily_calorie_goal')
    search_fields = ('username', 'fitness_goals')
    list_filter = ('username',)
    ordering = ('username',)

admin.site.register(CustomUser, UserProfileAdmin)

# The rest of your admin classes for Workout, Meal, Progress, etc., remain the same.


# Workout Admin
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'routine_name', 'date', 'duration_minutes', 'calories_burned')
    search_fields = ('user__username', 'routine_name')
    list_filter = ('date', 'routine_name')
    ordering = ('-date',)

admin.site.register(WorkoutLog, WorkoutAdmin)

# Meal Admin
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'date', 'food_item', 'calories', 'protein', 'carbohydrates', 'fat')
    search_fields = ('user__username', 'meal_type', 'food_item')
    list_filter = ('meal_type', 'date')
    ordering = ('-date',)

admin.site.register(MealLog, MealAdmin)

# Goal Admin
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_type', 'target_value', 'current_value', 'date_set', 'date_achieved')
    search_fields = ('user__username', 'goal_type')
    list_filter = ('goal_type', 'date_set', 'date_achieved')
    ordering = ('-date_set',)

admin.site.register(Goal, GoalAdmin)

# Calorie Balance Admin
class CalorieBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'calories_consumed', 'calories_burned', 'net_calories')
    search_fields = ('user__username',)
    list_filter = ('date',)
    ordering = ('-date',)

admin.site.register(CalorieBalance, CalorieBalanceAdmin)
