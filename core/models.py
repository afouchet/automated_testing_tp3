from django.db import models
from django.contrib.auth.models import User


class Form(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ("text", "Text"),
        ("textarea", "Textarea"),
        ("email", "Email"),
    ]

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="questions")
    label = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default="text")
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.form.title} — {self.label}"


class FormResponse(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="responses")
    submitted_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
