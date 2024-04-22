import json
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile-pictures')
    company_name = models.CharField(max_length=128)
    referral_code = models.CharField(max_length=128)


class Interests(models.Model):
    option = models.CharField(max_length=64)
    def __str__(self):
        return self.option


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128)
    message = models.TextField()
    has_been_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['has_been_read', '-created_at']

    def __str__(self):
        return f'{self.sender} - {self.receiver} - {self.message}'


class ArchivedMessage(models.Model):
    archived_by = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)


class Test(models.Model):
    title = models.CharField(max_length=256)
    short_description = models.TextField()
    interests = models.ManyToManyField(Interests)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.TextField()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=256)
    correct = models.BooleanField(default=False)


class SubmittedTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    submitted_data = JSONField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.test.title

    def get_data(self):
        data = []
        question_prefix = 'question_'
        submitted_data = json.loads(self.submitted_data)
        for key, value in submitted_data.items():
            question_id = key.replace(question_prefix, '')
            question = Question.objects.get(id=question_id)
            data.append({'question': question.question,'answer': value,})
        return data


    def get_score(self):
        if not self.score:
            question_prefix = 'question_'
            data = json.loads(self.submitted_data)
            score = 0
            for key, value in data.items():
                question_id = key.replace(question_prefix, '')
                question = Question.objects.get(id=question_id)
                if question.answer_set.filter(text=value, correct=True):
                    score += 2
            self.score = score
            self.save()
        return self.score


class Course(models.Model):
    title = models.CharField(max_length=256)
    short_description = models.TextField()
    interests = models.ManyToManyField(Interests)
    page_one = models.TextField()
    page_two = models.TextField()
    page_three = models.TextField()
    page_four = models.TextField()
    page_five = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class SubmittedCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.test.title


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='pictures')
    referral_code = models.CharField(max_length=128)
    employer = models.ForeignKey(EmployerProfile, on_delete=models.SET_NULL, null=True)
    interests = models.ManyToManyField(Interests)
    tests_assigned = models.ManyToManyField(Test, blank=True)
    courses_assigned = models.ManyToManyField(Course, blank=True)

    def get_total_score(self):
        submitted_tests = SubmittedTest.objects.filter(submitted_by=self.user)
        score = 0
        for test in submitted_tests:
            score += test.get_score()
        return score

    def get_level_number(self):
        level = 0
        total_score = self.get_total_score()
        if len(str(total_score)) == 2:
            level =  str(total_score)[0]
        elif len(str(total_score)) == 3:
            level = 10
        return int(level)

    def get_progress_percentage(self):
        return self.get_total_score()

    def is_test_taken(self):
        return SubmittedTest.objects.filter(submitted_by=self.user)

    def is_course_taken(self):
        return SubmittedCourse.objects.filter(submitted_by=self.user)

    # def is_five_course_taken(self):
    #     count = SubmittedCourse.objects.filter(submitted_by=self.user).count()

    #     return SubmittedCourse.objects.filter(submitted_by=self.user)

    def is_progress_halfway_through(self):
        level_number = self.get_level_number()
        return level_number >= 5
