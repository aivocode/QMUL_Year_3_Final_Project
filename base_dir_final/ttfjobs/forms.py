from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet

#GUEST > EMPLOYER, CANDIDATE


class UserCreationFormExtended(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name",
                  "email", "password1", "password2")

    # REMOVE ANNOYING HELPTEXT:
    def __init__(self, *args, **kwargs):
        super(UserCreationFormExtended, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
    ##

    def save(self, commit=True):
        user = super(UserCreationFormExtended, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# GUEST > EMPLOYER:
class EmployerAuthenticationFormExtended(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.groups.filter(name='employer').exists():
            raise forms.ValidationError(
                "Login details don't belong to Employer.")


# GUEST > EMPLOYER:
# EMPLOYER:
class EmployerProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    company_name = forms.CharField(required=True)

    class Meta:
        model = EmployerProfile
        fields = ['picture', 'company_name']


# EMPLOYER:
class EmployerCreateReferral(forms.ModelForm):
    referral_code = forms.CharField(required=True)

    def clean_referral_code(self):
        referral_code = self.cleaned_data['referral_code']
        if EmployerProfile.objects.filter(referral_code=referral_code).exists():
            raise ValidationError("Referral code entered is already taken.")
        else:
            return referral_code

    class Meta:
        model = EmployerProfile
        fields = ['referral_code']


#EMPLOYER, CANDIDATE
class UserEditForm(forms.ModelForm):
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    # REMINDER: DON'T CREATE BLANK DATABASE FIELDS OUTSIDE FRONTEND INTERFACE OR BLANK FIELDS VALIDATION FAILS IN VIEWS.PY
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken by you or others.")
        else:
            return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already taken by you or others.")
        else:
            return email
    ##

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


# GUEST > CANDIDATE:
class CandidateAuthenticationFormExtended(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.groups.filter(name='candidate').exists():
            raise forms.ValidationError(
                "Login details don't belong to Candidate.")


# GUEST > CANDIDATE:
# CANDIDATE:
class CandidateProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    referral_code = forms.CharField(required=True)
    interests = forms.ModelMultipleChoiceField(queryset=Interests.objects.all(
    ), widget=forms.CheckboxSelectMultiple, required=True)

    def clean_referral_code(self):
        referral_code = self.cleaned_data['referral_code']
        if EmployerProfile.objects.filter(referral_code=referral_code).exists():
            return referral_code
        else:
            raise ValidationError(
                "Referral code entered is invalid. Please contact your inviter.")

    class Meta:
        model = CandidateProfile
        fields = ['picture', 'referral_code', 'interests']


class CandidateProfileFormEdit(forms.ModelForm):
    picture = forms.ImageField(required=False)
    interests = forms.ModelMultipleChoiceField(queryset=Interests.objects.all(
    ), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = CandidateProfile
        fields = ['picture', 'interests']


# UNSORTED:
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'message')


class ReplyMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message',)


class SearchForm(forms.Form):
    query = forms.CharField(label="Search input:", widget=forms.TextInput(
        attrs={'placeholder': 'Enter email, first name or last name'}), required=False,)
    interests = forms.ModelMultipleChoiceField(label="Filter by interests:", queryset=Interests.objects.all(
    ), widget=forms.CheckboxSelectMultiple, required=False)


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'short_description', 'interests']
        widgets = {'interests': forms.CheckboxSelectMultiple, }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'correct']


class BaseAnswerFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_answers = 0
        if self.is_valid():
            for data in self.cleaned_data:
                if data['correct']:
                    correct_answers += 1
            if correct_answers == 0:
                raise forms.ValidationError(
                    'You need to select at least 1 correct answer')
            if correct_answers > 1:
                raise forms.ValidationError(
                    'Only one correct answer can per question')


AnswerFormset = inlineformset_factory(
    Question,
    Answer,
    formset=BaseAnswerFormSet,
    min_num=4,
    form=AnswerForm,
    extra=0,
    can_delete=False,
)


class BaseQuestionFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = AnswerFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='bookimage-%s-%s' % (
                form.prefix,
                AnswerFormset.get_default_prefix()),
        )

    def is_valid(self):
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):
        result = super().save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result


QuestionFormSet = inlineformset_factory(
    Test,
    Question,
    form=QuestionForm,
    formset=BaseQuestionFormSet,
    extra=0,
    min_num=10,
    can_delete=False
)


class TestAssignmentForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ('tests_assigned',)
        widgets = {'tests_assigned': forms.CheckboxSelectMultiple,}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        submitted_tests = self.instance.user.submittedtest_set.values_list('test__id', flat=True)
        qs = self.fields['tests_assigned'].queryset.exclude(id__in=submitted_tests)
        self.fields['tests_assigned'].queryset = qs


class CourseAssignmentForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ('courses_assigned',)
        widgets = {
            'courses_assigned': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        submitted_courses = self.instance.user.submittedcourse_set.values_list(
            'course__id', flat=True
        )
        qs = self.fields['courses_assigned'].queryset.exclude(
            id__in=submitted_courses)
        self.fields['courses_assigned'].queryset = qs


class TestGeneratedForm(forms.Form):
    def __init__(self, test, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for question in test.question_set.all():
            choices = []
            answers = question.answer_set.values_list('text', flat=True)
            for answer in answers:
                choices.append(
                    [answer, answer],
                )

            field_name = 'question_{question_id}'.format(
                question_id=question.id)
            self.fields[field_name] = forms.ChoiceField(
                label=question.question, choices=choices, widget=forms.RadioSelect()
            )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ('created_by', 'created_at',)
        widgets = {
            'interests': forms.CheckboxSelectMultiple,
        }
