let timer;
let timeLeft = 0; // Переводим минуты в секунды
let testId = null;
let currentQuestionIndex = 0;
let answeredQuestions = new Set(); // To track answered questions

// Capture student details
let studentName, studentSurname, studentSchool, studentClass;

async function enterTest() {
    const testInput = document.getElementById('test-id');
    if (!testInput) {
        console.error('Input element with ID "test-id" not found.');
        return;
    }

    testId = testInput.value; // testId должен быть доступен глобально
    console.log("Test ID:", testId); // Проверка, что testId получен

    try {
        const response = await fetch(`/api/tests/test_by_id?test_id=${testId}`);
        if (!response.ok) {
            throw new Error("Тест с таким ID не найден");
        }

        const test = await response.json();
        console.log("Test data:", test); // Проверяем, что API вернул данные

        loadTest(test);
        timeLeft = test.duration; // Теперь duration приходит в секундах
        startTimer();
    } catch (error) {
        alert(error.message);
    }
}

function loadTest(test) {
    document.getElementById('test-room').style.display = 'none';
    document.getElementById('test-container').style.display = 'block';

    const container = document.getElementById('questions-container');
    container.innerHTML = ''; // Очистка контейнера перед загрузкой новых вопросов

    test.questions.forEach((question, index) => {
        const questionElem = document.createElement('div');
        questionElem.classList.add('question');

        // Проверяем, есть ли текст вопроса
        if (question.text) {
            questionElem.innerHTML += `<p>${index + 1}. ${question.text}</p>`;
        }

        // Проверяем, есть ли изображение у вопроса
        if (question.image) {
            const imgElem = document.createElement('img');
            imgElem.src = question.image;
            imgElem.style.width = '90%'; // Увеличиваем ширину до 90% контейнера
            imgElem.style.maxWidth = '500px'; // Ограничение по ширине, чтобы не было слишком огромным
            imgElem.style.height = 'auto'; // Авто высота, чтобы сохранить пропорции
            imgElem.style.maxHeight = '300px'; // Ограничение по высоте, чтобы не было слишком длинным
            imgElem.style.objectFit = 'cover'; // Заполняет область без искажений
            imgElem.style.display = 'block';
            imgElem.style.margin = '10px auto';

            // Проверяем, загрузилось ли изображение
            imgElem.oncontextmenu = function () {
                return false;
            };

            // Запрещаем перетаскивание изображения
            imgElem.ondragstart = function () {
                return false;
            };

            imgElem.onload = function () {
                questionElem.prepend(imgElem);
            };

            imgElem.onerror = function () {
                imgElem.remove();
            };
        }


        if (question.options.length > 0) {
            // Вопрос с вариантами ответов (множественный выбор)
            question.options.forEach(option => {
                const optionElem = document.createElement('div');
                optionElem.classList.add('option');
                optionElem.innerHTML = `
                    <input type="radio" name="question_${question.id}" value="${option.id}" hidden>
                    <label>${option.text}</label>
                `;
                optionElem.onclick = () => {
                    const radioButton = optionElem.querySelector('input[type="radio"]');
                    radioButton.checked = true;
                    markAnswered(index);
                    if (index < test.questions.length - 1) {
                        showQuestion(currentQuestionIndex + 1);
                    } else {
                        toggleSubmitButton();
                    }
                };
                questionElem.appendChild(optionElem);
            });
        } else {
            // Открытый вопрос (без вариантов ответов)
            const inputElem = document.createElement('input');
            inputElem.type = 'text';
            inputElem.name = `question_${question.id}`;
            inputElem.placeholder = 'Введите ваш ответ';
            inputElem.oninput = () => {
                if (inputElem.value.trim() !== '') {
                    markAnswered(index);
                } else {
                    answeredQuestions.delete(index);
                }
                toggleSubmitButton();
            };
            questionElem.appendChild(inputElem);
        }

        container.appendChild(questionElem);
    });

    createPagination(test.questions.length);
    showQuestion(currentQuestionIndex);
}

function createPagination(totalQuestions) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = ''; // Clear previous pagination
    for (let i = 0; i < totalQuestions; i++) {
        const button = document.createElement('button');
        button.className = 'page-button';
        button.innerText = i + 1;
        button.onclick = () => showQuestion(i);
        pagination.appendChild(button);
    }
}

function showQuestion(index) {
    const questions = document.querySelectorAll('.question');
    questions.forEach((question, i) => {
        question.style.display = (i === index) ? 'block' : 'none';
    });
    currentQuestionIndex = index;
    updatePagination();
    toggleSubmitButton();
}

function markAnswered(index) {
    answeredQuestions.add(index);
    updatePagination();
}

function updatePagination() {
    const paginationButtons = document.querySelectorAll('.page-button');
    paginationButtons.forEach((button, i) => {
        button.classList.toggle('answered', answeredQuestions.has(i));
    });
}

function toggleSubmitButton() {
    const totalQuestions = document.querySelectorAll('.question').length;
    document.getElementById('submit-button').style.display = (answeredQuestions.size === totalQuestions) ? 'block' : 'none';
}

function startTimer() {
    timer = setInterval(() => {
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        document.getElementById('timer').innerText = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        if (timeLeft <= 0) {
            clearInterval(timer);
            submitTest();
        }
    }, 1000);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


async function submitTest() {
    const answers = [];
    const questions = document.querySelectorAll('.question');

    questions.forEach((questionElem) => {
        const questionId = questionElem.querySelector('[name^="question_"]').name.split('_')[1];
        const isMultipleChoice = questionElem.querySelector('input[type="radio"]');

        if (isMultipleChoice) {
            // Multiple-choice question
            const selectedOption = questionElem.querySelector('input[type="radio"]:checked');
            if (selectedOption) {
                answers.push({ question_id: questionId, answer_id: selectedOption.value });
            }
        } else {
            // Open-ended question
            const textAnswer = questionElem.querySelector('input[type="text"]').value;
            if (textAnswer.trim()) {
                answers.push({ question_id: questionId, text_answer: textAnswer.trim() });
            }
        }
    });

    // Include student details in the submission
    const studentDetails = {
        name: studentName,
        surname: studentSurname,
        school: studentSchool,
        class: studentClass
    };

    const csrftoken = getCookie('csrftoken');

    // Отправляем ответы на сервер
    const response = await fetch(`/api/tests/${testId}/submit_answer/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        credentials: 'include',
        body: JSON.stringify({
            student_details: studentDetails,
            answers: answers
        })
    });

    const result = await response.json();
    console.log(result);  // Проверяем, что пришло от сервера

    if (result && result.total_points !== undefined) {
        Swal.fire({
            title: "Тест завершён!",
            text: `Ваш результат: ${result.total_points} баллов.`,
            icon: "success",
            confirmButtonText: "Ок",
            background: "#fefefe",
            color: "#333",
            timer: 5000,
            timerProgressBar: true
        });
    } else {
        Swal.fire({
            title: "Ошибка",
            text: "Не удалось получить ваш балл. Попробуйте ещё раз.",
            icon: "error",
            confirmButtonText: "Ок",
            background: "#fefefe",
            color: "#333"
        });
    }

    setTimeout(() => {
        window.location.href = '/';
    }, 5000);
}


document.addEventListener('contextmenu', function (event) {
    event.preventDefault();
});
