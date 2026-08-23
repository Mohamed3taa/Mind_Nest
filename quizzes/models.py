from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Quiz(models.Model):

    class Difficulty(models.TextChoices):
        EASY   = 'easy',   'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD   = 'hard',   'Hard'

    class SourceType(models.TextChoices):
        NOTES    = 'notes',    'Notes'
        DOCUMENT = 'document', 'Document'
        MANUAL   = 'manual',   'Manual'

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty  = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
    )
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.NOTES,
    )
    # Human-readable reference, e.g. "Note: Python Basics" or "Document: lecture.pdf"
    source_ref  = models.CharField(max_length=200, blank=True)
    # Optional time limit in seconds (None = no limit)
    time_limit  = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Time limit in seconds. Leave blank for no limit.',
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f'{self.title} ({self.user.username})'

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def attempt_count(self):
        return self.attempts.count()

    @property
    def best_score(self):
        """Returns the highest percentage achieved across all attempts."""
        best = self.attempts.order_by('-percentage').first()
        return round(best.percentage, 1) if best else None

    @property
    def average_score(self):
        """Returns the mean percentage across all attempts."""
        attempts = self.attempts.all()
        if not attempts.exists():
            return None
        avg = sum(a.percentage for a in attempts) / attempts.count()
        return round(avg, 1)


class Question(models.Model):

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        TRUE_FALSE      = 'true_false',      'True / False'

    quiz          = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text          = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    # Shown on the results page after the user answers
    explanation   = models.TextField(blank=True)
    order         = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f'Q{self.order}: {self.text[:60]}'

    @property
    def correct_answer(self):
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    """
    Multiple Choice : exactly 4 answers, exactly 1 with is_correct=True.
    True / False    : exactly 2 answers ('True' / 'False'), 1 with is_correct=True.
    """
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text       = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f'[{mark}] {self.text[:60]}'


class QuizAttempt(models.Model):
    quiz         = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    # Number of correctly answered questions
    score        = models.PositiveIntegerField(default=0)
    # Total questions at the time of the attempt (snapshot)
    total        = models.PositiveIntegerField(default=0)
    # Percentage 0.0 – 100.0
    percentage   = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    # How long the user took in seconds (None = timer not used)
    time_taken   = models.PositiveIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'

    def __str__(self):
        return (
            f'{self.user.username} — {self.quiz.title} '
            f'({self.score}/{self.total}, {self.percentage:.1f}%)'
        )


class AttemptAnswer(models.Model):
    """
    Records which answer the user picked for each question in an attempt.
    'chosen' is NULL if the user skipped the question.
    """
    attempt    = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempt_answers')
    chosen     = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chosen_in',
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        # One record per question per attempt
        unique_together = ('attempt', 'question')
        verbose_name = 'Attempt Answer'
        verbose_name_plural = 'Attempt Answers'

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f'[{mark}] {self.question.text[:40]}'
