from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, AttemptAnswer


class AnswerInline(admin.TabularInline):
    model  = Answer
    extra  = 4
    fields = ('text', 'is_correct')


class QuestionInline(admin.StackedInline):
    model       = Question
    extra       = 0
    fields      = ('text', 'question_type', 'explanation', 'order')
    show_change_link = True


class AttemptAnswerInline(admin.TabularInline):
    model      = AttemptAnswer
    extra      = 0
    fields     = ('question', 'chosen', 'is_correct')
    readonly_fields = ('question', 'chosen', 'is_correct')
    can_delete = False


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'difficulty', 'source_type', 'question_count',
                     'attempt_count', 'is_active', 'created_at')
    list_filter   = ('difficulty', 'source_type', 'is_active')
    search_fields = ('title', 'user__username', 'source_ref')
    readonly_fields = ('created_at',)
    inlines       = [QuestionInline]

    def question_count(self, obj):
        return obj.question_count
    question_count.short_description = 'Questions'

    def attempt_count(self, obj):
        return obj.attempt_count
    attempt_count.short_description = 'Attempts'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'quiz', 'question_type', 'order')
    list_filter   = ('question_type', 'quiz__difficulty')
    search_fields = ('text', 'quiz__title')
    ordering      = ('quiz', 'order')
    inlines       = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display  = ('text', 'question', 'is_correct')
    list_filter   = ('is_correct',)
    search_fields = ('text', 'question__text')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display    = ('user', 'quiz', 'score', 'total', 'percentage',
                       'time_taken', 'completed_at')
    list_filter     = ('quiz__difficulty',)
    search_fields   = ('user__username', 'quiz__title')
    readonly_fields = ('score', 'total', 'percentage', 'time_taken', 'completed_at')
    inlines         = [AttemptAnswerInline]


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display  = ('attempt', 'question', 'chosen', 'is_correct')
    list_filter   = ('is_correct',)
    search_fields = ('attempt__user__username', 'question__text')
