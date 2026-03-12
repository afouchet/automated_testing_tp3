from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Form, FormResponse, Answer


def form_detail(request, slug):
    form = get_object_or_404(Form, slug=slug, is_active=True)
    questions = form.questions.all()

    if request.method == "POST":
        form_response = FormResponse.objects.create(form=form)
        errors = {}

        for question in questions:
            value = request.POST.get(f"question_{question.id}", "").strip()
            if question.is_required and not value:
                errors[question.id] = "Mandatory field"
            else:
                Answer.objects.create(
                    response=form_response,
                    question=question,
                    value=value,
                )

        if errors:
            form_response.delete()
            return render(request, "core/form_detail.html", {
                "form": form,
                "questions": questions,
                "errors": errors,
                "submitted_data": request.POST,
            })

        return redirect("form_success", slug=slug)

    return render(request, "core/form_detail.html", {
        "form": form,
        "questions": questions,
        "errors": {},
        "submitted_data": {},
    })


def form_success(request, slug):
    form = get_object_or_404(Form, slug=slug)
    return render(request, "core/form_success.html", {"form": form})
