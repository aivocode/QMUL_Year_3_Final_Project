from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from .forms import *


class CreateTestView(CreateView):
    form_class = TestForm
    template_name = "employer/employer-tests-create.html"
    model = Test

    def get_all_forms(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_formset = QuestionFormSet()
        context = {'form': form, 'questions_formset': questions_formset,}
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        return form_kwargs

    def form_valid(self, form, questions_formset):
        test = form.save(commit=False)
        test.created_by = self.request.user
        test.save()
        form.save_m2m()
        questions_formset.instance = test
        questions = questions_formset.save()
        return HttpResponseRedirect(reverse('ttfjobs:employer_tests'))

    def get(self, request, *args, **kwargs):
        self.object = None
        forms = self.get_all_forms()
        return self.render_to_response(self.get_context_data(**forms))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_formset = QuestionFormSet(request.POST)
        if form.is_valid() and questions_formset.is_valid():
            return self.form_valid(form, questions_formset)
        return self.form_invalid(form, questions_formset)


    def form_invalid(self, form, questions_formset):
        return self.render_to_response(self.get_context_data(form=form, questions_formset=questions_formset))


class UpdateTestView(UpdateView):
    form_class = TestForm
    template_name = "employer/employer-tests-edit.html"
    model = Test

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        forms = self.get_all_forms()
        return self.render_to_response(self.get_context_data(**forms))

    def get_all_forms(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_formset = QuestionFormSet(instance=self.object, queryset=self.object.question_set.all())
        context = {'form': form, 'questions_formset': questions_formset,}
        return context

    def form_invalid(self, form, questions_formset):
        return self.render_to_response(self.get_context_data(form=form, questions_formset=questions_formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()

        form = self.get_form(form_class)
        questions_formset = QuestionFormSet(request.POST, instance=self.object)
        if form.is_valid() and questions_formset.is_valid():
            return self.form_valid(form, questions_formset)
        return self.form_invalid(form, questions_formset)

    def form_valid(self, form, questions_formset):
        # Save test
        test = form.save(commit=False)
        test.created_by = self.request.user
        test.save()
        form.save_m2m()
        # Save questions and answers
        questions_formset.instance = test
        questions = questions_formset.save()
        return HttpResponseRedirect(reverse('ttfjobs:employer_tests'))
