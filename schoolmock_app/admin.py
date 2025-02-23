from django.contrib import admin
from django.db.models import Sum
from .models import *

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    max_num = 4
    extra = 1  # Number of empty forms to display for new options
    fields = ('text', 'is_correct')  # Include the is_correct field

@admin.register(Profile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'surname', 'school', 'classroom', 'created_at', 'updated_at')
    search_fields = ('user', 'name', 'surname', 'school', 'classroom', 'created_at', 'updated_at')

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'classroom', 'start_date', 'duration', 'is_finished')
    list_filter = ('teacher', 'classroom', 'is_finished')
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'difficulty', 'image',)
    list_filter = ('test', 'image')

    inlines = [AnswerOptionInline]  # Allow adding multiple answer options inline

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'question', 'get_answer_text', 'points_awarded', 'total_points')
    list_filter = ('test', 'student')

    def get_answer_text(self, obj):
        """Display the text of the selected answer option."""
        if obj.answer_option:
            return obj.answer_option.text  # Return the selected answer option text
        return obj.text_answer  # Fallback to the text answer for open-ended questions
    get_answer_text.short_description = 'Answer'

    def total_points(self, obj):
        """Calculate total points for each student in the specific test."""
        return (
            StudentAnswer.objects.filter(student=obj.student, test=obj.test)
            .aggregate(total=Sum('points_awarded'))['total'] or 0  # Default to 0 if no answers
        )
    total_points.short_description = 'Total Points'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Select related fields for optimized query performance
        qs = qs.select_related('student', 'test', 'question', 'answer_option')
        return qs

class TestAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Только пользователи с ролью 'teacher' имеют доступ
        if hasattr(request.user, 'students') and request.user.students.is_teacher():
            return True
        return False

    def has_add_permission(self, request):
        # Только учителя могут добавлять тесты
        if hasattr(request.user, 'students') and request.user.students.is_teacher():
            return True
        return False

    def has_change_permission(self, request, obj=None):
        # Только учителя могут редактировать тесты
        if hasattr(request.user, 'students') and request.user.students.is_teacher():
            return True
        return False