"""
quizzes/views.py

Step 2 — quiz_generate + quiz_save
Step 3 — quiz_list, quiz_detail, quiz_delete
"""
import json
import re

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ai_assistant.gemini import gemini_client
from ai_assistant.views import build_user_context
from google.genai import types

from .models import Answer, Question, Quiz, QuizAttempt

# ── constants ────────────────────────────────────────────────────────────────

MAX_QUESTIONS = 20
VALID_TYPES   = {'multiple_choice', 'true_false'}
VALID_DIFF    = {'easy', 'medium', 'hard'}
VALID_SOURCES = {'notes', 'document', 'all'}

# ── helpers ───────────────────────────────────────────────────────────────────

def _strip_markdown_json(text: str) -> str:
    """
    Gemini sometimes wraps its JSON inside ```json ... ``` fences.
    Strip those fences before parsing.
    """
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def _build_quiz_prompt(context: str, num_questions: int,
                       difficulty: str, q_types: list) -> str:
    """
    Builds the strict JSON-only prompt sent to Gemini.
    """
    if len(q_types) == 1 and q_types[0] == 'true_false':
        type_instruction = 'All questions must be true_false type.'
    elif len(q_types) == 1 and q_types[0] == 'multiple_choice':
        type_instruction = 'All questions must be multiple_choice type.'
    else:
        type_instruction = (
            'Mix multiple_choice and true_false questions. '
            'Aim for roughly 70% multiple_choice and 30% true_false.'
        )

    return f"""You are a quiz generator. Return ONLY valid JSON. No markdown, no explanation, no text outside the JSON.

Generate a quiz with EXACTLY {num_questions} questions at {difficulty.upper()} difficulty.

{type_instruction}

Rules:
- multiple_choice: exactly 4 answer options, exactly 1 with "is_correct": true
- true_false: exactly 2 answer options ("True" and "False"), exactly 1 with "is_correct": true
- Only generate questions from the SOURCE MATERIAL below
- Include a brief "explanation" for each question (why the correct answer is right)
- Never include question numbers in the "text" field
- Return ONLY the JSON object, nothing else

Required JSON format:
{{
  "title": "A descriptive quiz title based on the content",
  "questions": [
    {{
      "text": "Question text here?",
      "type": "multiple_choice",
      "explanation": "Brief explanation of why the correct answer is right.",
      "answers": [
        {{"text": "Correct option", "is_correct": true}},
        {{"text": "Wrong option A", "is_correct": false}},
        {{"text": "Wrong option B", "is_correct": false}},
        {{"text": "Wrong option C", "is_correct": false}}
      ]
    }},
    {{
      "text": "True or False question?",
      "type": "true_false",
      "explanation": "Brief explanation.",
      "answers": [
        {{"text": "True",  "is_correct": true}},
        {{"text": "False", "is_correct": false}}
      ]
    }}
  ]
}}

SOURCE MATERIAL:
{context}

Remember: Return ONLY the JSON. No extra text."""


def _validate_quiz_json(data: dict, requested_count: int) -> list:
    """
    Validates the parsed quiz JSON structure.
    Returns a list of error strings (empty = valid).
    """
    errors = []

    if not isinstance(data, dict):
        return ['Response is not a JSON object.']

    if 'title' not in data or not str(data.get('title', '')).strip():
        errors.append('Missing or empty "title".')

    questions = data.get('questions')
    if not isinstance(questions, list) or len(questions) == 0:
        errors.append('"questions" must be a non-empty list.')
        return errors   # can't validate individual questions without the list

    if len(questions) > MAX_QUESTIONS:
        errors.append(
            f'Too many questions: {len(questions)} (max {MAX_QUESTIONS}).'
        )

    for i, q in enumerate(questions, 1):
        prefix = f'Question {i}'

        if not isinstance(q, dict):
            errors.append(f'{prefix}: must be an object.')
            continue

        text = q.get('text', '').strip()
        if not text:
            errors.append(f'{prefix}: empty question text.')

        q_type = q.get('type', '')
        if q_type not in VALID_TYPES:
            errors.append(
                f'{prefix}: invalid type "{q_type}". '
                f'Must be one of {VALID_TYPES}.'
            )

        answers = q.get('answers', [])
        if not isinstance(answers, list):
            errors.append(f'{prefix}: "answers" must be a list.')
            continue

        if q_type == 'multiple_choice':
            if len(answers) != 4:
                errors.append(
                    f'{prefix}: multiple_choice requires exactly 4 answers '
                    f'(got {len(answers)}).'
                )
        elif q_type == 'true_false':
            if len(answers) != 2:
                errors.append(
                    f'{prefix}: true_false requires exactly 2 answers '
                    f'(got {len(answers)}).'
                )

        correct_count = sum(
            1 for a in answers
            if isinstance(a, dict) and a.get('is_correct') is True
        )
        if correct_count != 1:
            errors.append(
                f'{prefix}: must have exactly 1 correct answer '
                f'(found {correct_count}).'
            )

        for j, ans in enumerate(answers, 1):
            if not isinstance(ans, dict):
                errors.append(f'{prefix}, Answer {j}: must be an object.')
                continue
            if not str(ans.get('text', '')).strip():
                errors.append(f'{prefix}, Answer {j}: empty answer text.')

    return errors


# ── views ─────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def quiz_generate(request):
    """
    AJAX POST — calls Gemini to generate a quiz JSON preview.
    Does NOT save to the database; that is done by quiz_save.

    Expected POST body (JSON):
        source        : "notes" | "document" | "all"
        source_ref    : optional string label shown in the quiz
        num_questions : int 1–20
        difficulty    : "easy" | "medium" | "hard"
        q_types       : ["multiple_choice"] | ["true_false"] | ["multiple_choice","true_false"]
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON request body.'}, status=400)

    # ── parse + sanitise inputs ───────────────────────────────────────────────
    source     = body.get('source', 'all')
    source_ref = str(body.get('source_ref', '')).strip()[:200]
    difficulty = body.get('difficulty', 'medium')
    raw_types  = body.get('q_types', ['multiple_choice', 'true_false'])

    if source not in VALID_SOURCES:
        return JsonResponse(
            {'error': f'Invalid source. Must be one of: {VALID_SOURCES}.'},
            status=400,
        )
    if difficulty not in VALID_DIFF:
        return JsonResponse(
            {'error': f'Invalid difficulty. Must be one of: {VALID_DIFF}.'},
            status=400,
        )

    try:
        num_questions = int(body.get('num_questions', 5))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'num_questions must be an integer.'}, status=400)

    if not 1 <= num_questions <= MAX_QUESTIONS:
        return JsonResponse(
            {'error': f'num_questions must be between 1 and {MAX_QUESTIONS}.'},
            status=400,
        )

    if not isinstance(raw_types, list) or not raw_types:
        return JsonResponse({'error': 'q_types must be a non-empty list.'}, status=400)

    q_types = [t for t in raw_types if t in VALID_TYPES]
    if not q_types:
        return JsonResponse(
            {'error': f'q_types must contain at least one of: {VALID_TYPES}.'},
            status=400,
        )

    # ── build context from user's data ───────────────────────────────────────
    # build_user_context already aggregates notes/tasks/resources/documents
    user_context = build_user_context(request.user)

    if user_context == 'The user has no data yet in Mind Nest.':
        return JsonResponse(
            {'error': 'You have no notes, resources, or documents yet. '
                      'Add some content first, then generate a quiz.'},
            status=400,
        )

    # ── call Gemini ───────────────────────────────────────────────────────────
    prompt = _build_quiz_prompt(user_context, num_questions, difficulty, q_types)

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[types.Content(
                role='user',
                parts=[types.Part(text=prompt)],
            )],
        )
        raw_text = response.text or ''
    except Exception as e:
        return JsonResponse(
            {'error': f'AI service error: {str(e)}'},
            status=502,
        )

    if not raw_text.strip():
        return JsonResponse(
            {'error': 'AI returned an empty response. Please try again.'},
            status=502,
        )

    # ── strip markdown fences + parse JSON ───────────────────────────────────
    cleaned = _strip_markdown_json(raw_text)

    try:
        quiz_data = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        return JsonResponse(
            {'error': f'AI returned invalid JSON: {exc}'},
            status=502,
        )

    # ── validate structure ────────────────────────────────────────────────────
    validation_errors = _validate_quiz_json(quiz_data, num_questions)
    if validation_errors:
        return JsonResponse(
            {'error': 'AI response failed validation.',
             'details': validation_errors},
            status=502,
        )

    # ── attach metadata for the save step ────────────────────────────────────
    quiz_data['_meta'] = {
        'difficulty':  difficulty,
        'source_type': source,
        'source_ref':  source_ref,
    }

    return JsonResponse({'quiz': quiz_data})


@login_required
@require_POST
def quiz_save(request):
    """
    AJAX POST — persists a previously generated (or client-validated) quiz.
    Wraps all DB writes in a transaction; on any error nothing is committed.

    Expected POST body (JSON):
        title         : str
        difficulty    : "easy" | "medium" | "hard"
        source_type   : "notes" | "document" | "manual"
        source_ref    : str (optional)
        time_limit    : int seconds or null
        questions     : [ { text, type, explanation, answers:[{text,is_correct}] } ]
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON request body.'}, status=400)

    # ── server-side re-validation (never trust the client) ───────────────────
    validation_errors = _validate_quiz_json(body, MAX_QUESTIONS)
    if validation_errors:
        return JsonResponse(
            {'error': 'Quiz data failed server-side validation.',
             'details': validation_errors},
            status=400,
        )

    # ── sanitise top-level fields (whitelist — no arbitrary field injection) ──
    title = str(body.get('title', '')).strip()[:200]
    if not title:
        return JsonResponse({'error': '"title" is required.'}, status=400)

    difficulty = body.get('difficulty', 'medium')
    if difficulty not in VALID_DIFF:
        difficulty = 'medium'

    source_type = body.get('source_type', 'notes')
    valid_source_types = {'notes', 'document', 'manual'}
    if source_type not in valid_source_types:
        source_type = 'notes'

    source_ref = str(body.get('source_ref', '')).strip()[:200]

    raw_time = body.get('time_limit')
    time_limit = None
    if raw_time is not None:
        try:
            time_limit = int(raw_time)
            if time_limit <= 0:
                time_limit = None
        except (ValueError, TypeError):
            time_limit = None

    questions_data = body.get('questions', [])

    # ── persist inside a single transaction ──────────────────────────────────
    try:
        with transaction.atomic():
            quiz = Quiz.objects.create(
                user        = request.user,   # always the logged-in user — never from body
                title       = title,
                difficulty  = difficulty,
                source_type = source_type,
                source_ref  = source_ref,
                time_limit  = time_limit,
                is_active   = True,
            )

            for order_idx, q_data in enumerate(questions_data, start=1):
                question = Question.objects.create(
                    quiz          = quiz,
                    text          = str(q_data['text']).strip(),
                    question_type = q_data['type'],
                    explanation   = str(q_data.get('explanation', '')).strip(),
                    order         = order_idx,
                )

                for ans_data in q_data['answers']:
                    Answer.objects.create(
                        question   = question,
                        text       = str(ans_data['text']).strip(),
                        is_correct = bool(ans_data.get('is_correct', False)),
                    )

    except Exception as exc:
        # Transaction is automatically rolled back on any exception.
        return JsonResponse(
            {'error': f'Failed to save quiz: {str(exc)}'},
            status=500,
        )

    return JsonResponse({
        'success': True,
        'quiz_id': quiz.pk,
        'title':   quiz.title,
        'message': f'Quiz "{quiz.title}" saved successfully with '
                   f'{quiz.question_count} questions.',
    })


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3 — Quiz List · Quiz Detail · Quiz Delete
# ═══════════════════════════════════════════════════════════════════════════════

@login_required
def quiz_list(request):
    """
    /quizzes/ — paginated list of the current user's quizzes.
    Only quizzes owned by request.user are returned.
    """
    quizzes = Quiz.objects.filter(user=request.user, is_active=True)

    # ── optional filters ──────────────────────────────────────────────────────
    difficulty = request.GET.get('difficulty', '')
    search     = request.GET.get('search', '')

    if difficulty in {'easy', 'medium', 'hard'}:
        quizzes = quizzes.filter(difficulty=difficulty)
    if search:
        quizzes = quizzes.filter(title__icontains=search)

    paginator = Paginator(quizzes, 9)
    page      = paginator.get_page(request.GET.get('page', 1))

    # ── aggregate stats for header cards ─────────────────────────────────────
    all_quizzes    = Quiz.objects.filter(user=request.user, is_active=True)
    total_quizzes  = all_quizzes.count()
    total_attempts = QuizAttempt.objects.filter(user=request.user).count()

    best_pct = None
    best_obj = QuizAttempt.objects.filter(user=request.user).order_by('-percentage').first()
    if best_obj:
        best_pct = round(best_obj.percentage, 1)

    context = {
        'quizzes':          page,
        'total_quizzes':    total_quizzes,
        'total_attempts':   total_attempts,
        'best_pct':         best_pct,
        'current_diff':     difficulty,
        'current_search':   search,
    }
    return render(request, 'quizzes/quiz_list.html', context)


@login_required
def quiz_detail(request, pk):
    """
    /quizzes/<pk>/ — detail page for a single quiz.
    Ownership is enforced: users can only see their own quizzes.
    """
    # user-scoped get_object_or_404 → 404 if wrong owner, not a data leak
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user, is_active=True)

    # Only this user's attempts, most recent first
    attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user)

    # Per-attempt stats
    attempt_count = attempts.count()
    best_attempt  = attempts.order_by('-percentage').first()
    avg_pct       = None
    if attempt_count:
        avg_pct = round(
            sum(a.percentage for a in attempts) / attempt_count, 1
        )

    context = {
        'quiz':           quiz,
        'attempts':       attempts[:10],      # latest 10 shown in table
        'attempt_count':  attempt_count,
        'best_attempt':   best_attempt,
        'avg_pct':        avg_pct,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
@require_POST
def quiz_delete(request, pk):
    """
    POST /quizzes/<pk>/delete/
    Soft-deletes (is_active=False) the quiz after ownership check.
    Hard-deleting is avoided so attempt history isn't orphaned unexpectedly.
    """
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    quiz.is_active = False
    quiz.save(update_fields=['is_active'])
    messages.success(request, f'Quiz "{quiz.title}" deleted.')
    return redirect('quizzes:quiz_list')


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4 — Quiz Take · Quiz Submit
# ═══════════════════════════════════════════════════════════════════════════════

@login_required
def quiz_take(request, pk):
    """
    GET /quizzes/<pk>/take/
    Renders the quiz-taking UI. All question/answer data is passed to the
    template as JSON so the JS state machine can drive one-at-a-time display
    without extra round-trips.
    Ownership is enforced: 404 if wrong user or inactive quiz.
    """
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user, is_active=True)

    questions = quiz.questions.prefetch_related('answers').all()
    if not questions.exists():
        messages.warning(request, 'This quiz has no questions yet.')
        return redirect('quizzes:quiz_detail', pk=pk)

    # Serialise questions + answers for the JS state machine.
    # We include answer IDs so the client can send them back on submit,
    # but we NEVER include is_correct — the server decides that.
    questions_data = []
    for q in questions:
        answers = []
        for a in q.answers.all():
            answers.append({
                'id':   a.pk,
                'text': a.text,
            })
        questions_data.append({
            'id':          q.pk,
            'text':        q.text,
            'type':        q.question_type,
            'answers':     answers,
        })

    context = {
        'quiz':           quiz,
        'questions_json': json.dumps(questions_data),
        'question_count': len(questions_data),
        'submit_url':     f'/quizzes/{pk}/submit/',
    }
    return render(request, 'quizzes/quiz_take.html', context)


@login_required
@require_POST
def quiz_submit(request, pk):
    """
    POST /quizzes/<pk>/submit/  (AJAX, JSON body)

    Expected body:
        {
          "answers": {
            "<question_id>": <answer_id>,   // may be null if skipped
            ...
          },
          "time_taken": <seconds int or null>
        }

    Security guarantees:
    - Quiz ownership verified before anything else.
    - Every question_id is verified to belong to THIS quiz.
    - Every answer_id is verified to belong to the corresponding question.
    - Score/percentage are computed server-side only.
    - One atomic transaction: partial attempt is never committed.
    - Duplicate question_ids in the payload are silently deduplicated (last wins).
    """
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user, is_active=True)

    # ── parse body ────────────────────────────────────────────────────────────
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    raw_answers  = body.get('answers', {})
    raw_time     = body.get('time_taken')

    if not isinstance(raw_answers, dict):
        return JsonResponse({'error': '"answers" must be an object.'}, status=400)

    # ── validate time_taken ───────────────────────────────────────────────────
    time_taken = None
    if raw_time is not None:
        try:
            time_taken = int(raw_time)
            if time_taken < 0:
                time_taken = None
        except (ValueError, TypeError):
            time_taken = None

    # ── load this quiz's questions + answers from the DB (single source of truth) ──
    questions = list(
        quiz.questions.prefetch_related('answers').order_by('order')
    )
    if not questions:
        return JsonResponse({'error': 'This quiz has no questions.'}, status=400)

    # Build lookup dicts keyed by pk for O(1) access
    question_map = {q.pk: q for q in questions}
    # answer_map: answer_id → Answer object, but only answers belonging to this quiz
    answer_map = {}
    for q in questions:
        for a in q.answers.all():
            answer_map[a.pk] = a

    # ── server-side scoring ───────────────────────────────────────────────────
    scored = []   # list of (question, chosen_answer_or_None, is_correct)
    errors = []

    for q in questions:
        raw_ans_id = raw_answers.get(str(q.pk))   # JS sends keys as strings

        chosen   = None
        correct  = False

        if raw_ans_id is not None:
            # Coerce to int
            try:
                ans_id = int(raw_ans_id)
            except (ValueError, TypeError):
                errors.append(f'Invalid answer id for question {q.pk}.')
                scored.append((q, None, False))
                continue

            # Verify the answer belongs to THIS question (not any other)
            if ans_id not in answer_map:
                errors.append(
                    f'Answer {ans_id} does not belong to this quiz.'
                )
                scored.append((q, None, False))
                continue

            chosen_answer = answer_map[ans_id]
            if chosen_answer.question_id != q.pk:
                errors.append(
                    f'Answer {ans_id} does not belong to question {q.pk}.'
                )
                scored.append((q, None, False))
                continue

            chosen  = chosen_answer
            correct = chosen_answer.is_correct

        scored.append((q, chosen, correct))

    if errors:
        return JsonResponse({'error': 'Invalid answers submitted.',
                             'details': errors}, status=400)

    # ── compute totals ────────────────────────────────────────────────────────
    total           = len(scored)
    correct_count   = sum(1 for _, _, c in scored if c)
    incorrect_count = total - correct_count
    percentage      = round((correct_count / total * 100), 2) if total else 0.0

    # ── persist in a single transaction ──────────────────────────────────────
    try:
        with transaction.atomic():
            attempt = QuizAttempt.objects.create(
                quiz       = quiz,
                user       = request.user,
                score      = correct_count,
                total      = total,
                percentage = percentage,
                time_taken = time_taken,
            )

            from .models import AttemptAnswer
            attempt_answers = [
                AttemptAnswer(
                    attempt    = attempt,
                    question   = q,
                    chosen     = chosen,
                    is_correct = is_correct,
                )
                for q, chosen, is_correct in scored
            ]
            AttemptAnswer.objects.bulk_create(attempt_answers)

    except Exception as exc:
        return JsonResponse(
            {'error': f'Failed to save attempt: {str(exc)}'},
            status=500,
        )

    from django.urls import reverse as _reverse
    return JsonResponse({
        'success':         True,
        'attempt_id':      attempt.pk,
        'score':           correct_count,
        'total':           total,
        'correct':         correct_count,
        'incorrect':       incorrect_count,
        'percentage':      percentage,
        'result_url':      _reverse('quizzes:quiz_result', args=[pk, attempt.pk]),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# Step 5 — Quiz Result
# ═══════════════════════════════════════════════════════════════════════════════

@login_required
def quiz_result(request, pk, attempt_pk):
    """
    GET /quizzes/<pk>/result/<attempt_pk>/

    Ownership enforced on two levels:
    1. The attempt must belong to request.user  → guards attempt access.
    2. The quiz must belong to request.user     → prevents URL-walking to
       another user's quiz via a shared attempt id.

    AttemptAnswers are split into three groups for the review section:
    - correct:   chosen answer was right
    - incorrect: chosen answer was wrong (but user did answer)
    - skipped:   user left the question unanswered (chosen is NULL)
    """
    # Two-level ownership check in a single, efficient query
    attempt = get_object_or_404(
        QuizAttempt,
        pk         = attempt_pk,
        user       = request.user,
        quiz__pk   = pk,
        quiz__user = request.user,   # ensures the quiz also belongs to this user
    )
    quiz = attempt.quiz

    # Fetch all attempt answers with related question + chosen answer
    attempt_answers = (
        attempt.answers
        .select_related('question', 'chosen')
        .prefetch_related('question__answers')
        .order_by('question__order')
    )

    correct_answers   = []
    incorrect_answers = []
    skipped_answers   = []

    for aa in attempt_answers:
        # Get the correct answer for this question (from DB, not from client)
        correct_ans = aa.question.answers.filter(is_correct=True).first()
        entry = {
            'attempt_answer': aa,
            'question':       aa.question,
            'chosen':         aa.chosen,
            'correct_answer': correct_ans,
            'explanation':    aa.question.explanation,
        }
        if aa.is_correct:
            correct_answers.append(entry)
        elif aa.chosen is None:
            skipped_answers.append(entry)
        else:
            incorrect_answers.append(entry)

    # grade label
    if attempt.percentage >= 90:
        grade = ('Excellent!', 'success', 'bi-trophy-fill')
    elif attempt.percentage >= 75:
        grade = ('Great Job!', 'primary', 'bi-star-fill')
    elif attempt.percentage >= 50:
        grade = ('Good Effort', 'warning', 'bi-emoji-smile')
    else:
        grade = ('Keep Practicing', 'danger', 'bi-arrow-repeat')

    context = {
        'quiz':               quiz,
        'attempt':            attempt,
        'correct_answers':    correct_answers,
        'incorrect_answers':  incorrect_answers,
        'skipped_answers':    skipped_answers,
        'grade_label':        grade[0],
        'grade_color':        grade[1],
        'grade_icon':         grade[2],
        'review_items':       incorrect_answers + skipped_answers,
    }
    return render(request, 'quizzes/quiz_result.html', context)
