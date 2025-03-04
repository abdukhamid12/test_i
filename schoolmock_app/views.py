from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseNotFound
from .models import Test, Question, AnswerOption, StudentAnswer
from .serializers import *
from .forms import *
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user

# ViewSet для управления тестами

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    @csrf_exempt
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        test = self.get_object()

        # Check if the test is already finished
        if test.is_finished:
            return Response({'error': 'Test is already finished.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the logged-in user
        student = get_user(request)
        if not student:
            return Response({'error': 'Student information is required.'}, status=status.HTTP_400_BAD_REQUEST)

        answers = request.data.get('answers', [])
        if not answers:
            return Response({'error': 'No answers provided.'}, status=status.HTTP_400_BAD_REQUEST)

        total_points = 0
        response_data = []
        print(student)
        print(answers)
        # Use a transaction to ensure atomicity
        try:
            # with transaction.atomic():
            for ans in answers:
                question_id = ans.get('question_id')
                answer_id = ans.get('answer_id')
                print(question_id)
                print(answer_id)
                if not question_id or not answer_id:
                    return Response({'error': 'Invalid answer data.'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    question = Question.objects.get(id=question_id)
                    if not question.text and not question.image:
                        return Response({'error': f'Question with id {question_id} has no text or image.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    correct_answer = AnswerOption.objects.filter(question=question, is_correct=True).first()

                    # Проверка правильности ответа
                    points_awarded = 0
                    if correct_answer and int(answer_id) == correct_answer.id:
                        points_awarded = question.difficulty  # Используем сложность вопроса как множитель

                    print(student.id)
                    print(test.id)
                    print(question.id)
                    print(answer_id)
                    print(points_awarded)
                    print(ans.get('text_answer', 'None'))
                    # Save student's answer
                    StudentAnswer.objects.create(
                        student=student,
                        test=test,
                        question=question,
                        answer_option_id=answer_id,
                        points_awarded=points_awarded,
                        text_answer=ans.get('text_answer', 'None')
                    )

                    total_points += points_awarded
                    response_data.append({
                        'question_id': question.id,
                        'points_awarded': points_awarded
                    })


                except Question.DoesNotExist:
                    return Response({'error': f'Question with id {question_id} does not exist.'},
                                    status=status.HTTP_400_BAD_REQUEST)


            if test.is_finished == test.finished_at:
                test.is_finished = True
                test.save()
            else:
                test.is_finished = False

        except Exception as e:
            return Response({'error': 'An error occurred while processing answers.', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'answers submitted', 'total_points': total_points, 'details': response_data},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def test_by_id(self, request):
        test_id = request.query_params.get('test_id')
        test_test = Test.objects.filter(id=test_id).first()

        if not test_test:
            return Response({'error': 'Invalid test ID'}, status=status.HTTP_404_NOT_FOUND)

        # Добавляем duration в ответ
        serializer = self.get_serializer(test_test)
        data = serializer.data
        data['duration'] = test_test.duration * 60  # Переводим минуты в секунды

        return Response(data)


def test(request):
    return render(request, 'test.html',)

def home(request):
    return render(request, 'index.html',)