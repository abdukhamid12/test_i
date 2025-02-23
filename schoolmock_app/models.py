from django.db import models
from django.contrib.auth.models import User, AbstractUser

# class User(AbstractUser)

# Модель студента
class Profile(models.Model):
    TEACHER = 'teacher'
    STUDENT = 'student'
    ROLE = [
        (TEACHER, 'TEACHER'),
        (STUDENT, 'STUDENT'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="students")
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    school = models.CharField(max_length=255)
    classroom = models.CharField(max_length=10)  # or IntegerField based on your use case
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=30, choices=ROLE)

    def __str__(self):
        return f"{self.name} {self.surname}"
    
    def is_teacher(self):
        return self.role == self.TEACHER


# Модель теста
class Test(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    classroom = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    duration = models.IntegerField(default=60)  # Время теста в минутах
    is_finished = models.BooleanField(default=False)  # Поле для указания, завершен ли тест
    finished_at = models.DateTimeField(null=True, blank=True)  # Время завершения теста

    def __str__(self):
        return self.title
    
    if is_finished == finished_at:
        is_finished = True

# Модель вопроса
# Модель вопроса
from django.core.exceptions import ValidationError
from django.db import models

class Question(models.Model):
    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)  # Теперь текст можно оставить пустым
    difficulty = models.IntegerField(default=1)
    correct_answer = models.CharField(max_length=255)  # Используется для проверки открытых ответов
    image = models.ImageField(upload_to='questions/', blank=True, null=True)

    def clean(self):
        """Проверяем, что либо `text`, либо `image` заполнены."""
        if not self.text and not self.image:
            raise ValidationError("Вопрос должен содержать либо текст, либо изображение.")

    def save(self, *args, **kwargs):
        """Запускаем `clean()` перед сохранением."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text if self.text else "Вопрос с изображением"


# Варианты ответа на вопрос
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # Поле для указания правильного ответа

    def __str__(self):
        return self.text

# Ответы студентов
class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(null=True, blank=True)
    points_awarded = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer by {self.student} for {self.test}"
