import json

from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
from .models import *

from django.db.models import Q
from django.contrib.auth import login, logout

from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test



#GUEST:
#GUEST CONTENT:
def home(request):
    return render(request, 'guest/home.html')

def features(request):
    return render(request, 'guest/features.html')

def pricing(request):
    return render(request, 'guest/pricing.html')

def demo(request):
    return render(request, 'guest/demo.html')

def about(request):
    return render(request, 'guest/about.html')
##


#GUEST > EMPLOYER:
def employer(request):
    return render(request, 'guest/employer.html')

@csrf_exempt
def employer_register(request):
    user_creation_form_extended = UserCreationFormExtended()
    employer_profile_form = EmployerProfileForm()
    if request.method == "POST":
        user_creation_form_extended = UserCreationFormExtended(request.POST)
        employer_profile_form = EmployerProfileForm(request.POST, request.FILES)
        if user_creation_form_extended.is_valid() and employer_profile_form.is_valid():
            user = user_creation_form_extended.save()
            employer_profile = employer_profile_form.save(False)
            employer_profile.user = user
            employer_profile.save()
            employer_group = Group.objects.get_or_create(name='employer')
            employer_group[0].user_set.add(user)
            login(request, user)
            return redirect("ttfjobs:employer_dashboard")
    return render(request, 'guest/employer-register.html', {"user_creation_form_extended": user_creation_form_extended, "employer_profile_form": employer_profile_form})

@csrf_exempt
def employer_login(request):
    authentication_form = EmployerAuthenticationFormExtended()
    if request.method == "POST":
        authentication_form = EmployerAuthenticationFormExtended(
            data=request.POST)
        if authentication_form.is_valid():
            user = authentication_form.get_user()
            login(request, user)
            return redirect("ttfjobs:employer_dashboard")
    return render(request, 'guest/employer-login.html', {"authentication_form": authentication_form})
##


#GUEST > CANDIDATE:
def candidate(request):
    return render(request, 'guest/candidate.html')

@csrf_exempt
def candidate_register(request):
    user_creation_form_extended = UserCreationFormExtended()
    candidate_profile_form = CandidateProfileForm()
    if request.method == "POST":
        user_creation_form_extended = UserCreationFormExtended(request.POST)
        candidate_profile_form = CandidateProfileForm(request.POST, request.FILES)
        if user_creation_form_extended.is_valid() and candidate_profile_form.is_valid():
            user = user_creation_form_extended.save()
            candidate_profile = candidate_profile_form.save(False)
            referral_code = candidate_profile_form.cleaned_data['referral_code']
            employer = None
            if EmployerProfile.objects.filter(referral_code=referral_code).exists():
                employer = EmployerProfile.objects.get(referral_code=referral_code)
                candidate_profile.employer = employer
            candidate_profile.user = user
            candidate_profile.save()
            candidate_profile_form.save_m2m()
            candidate_group = Group.objects.get_or_create(name='candidate')
            candidate_group[0].user_set.add(user)
            login(request, user)
            return redirect("ttfjobs:candidate_dashboard")
    return render(request, 'guest/candidate-register.html', {"user_creation_form_extended": user_creation_form_extended, "candidate_profile_form": candidate_profile_form})

@csrf_exempt
def candidate_login(request):
    authentication_form = CandidateAuthenticationFormExtended()
    if request.method == "POST":
        authentication_form = CandidateAuthenticationFormExtended(data=request.POST)
        if authentication_form.is_valid():
            user = authentication_form.get_user()
            login(request, user)
            return redirect("ttfjobs:candidate_dashboard")
    return render(request, 'guest/candidate-login.html', {"authentication_form": authentication_form})
##
##



#EMPLOYER, CANDIDATE (GLOBAL):
#GLOBAL SHARED:
def all_logout(request):
    logout(request)
    return redirect("ttfjobs:home")

@login_required
def delete_message(request, message_id):
    try:
        message = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).get(id=message_id)
    except:
        raise Http404('No message matched the given query')
    if ArchivedMessage.objects.filter(message=message, archived_by=request.user).exists():
        raise Http404('No message matched the given query')
    if request.method == "POST":
        ArchivedMessage.objects.create(archived_by=request.user, message=message,)
        if getattr(request.user, 'employerprofile', None):
            return HttpResponseRedirect(reverse('ttfjobs:employer_chat'))
        else:
            return HttpResponseRedirect(reverse('ttfjobs:candidate_chat'))
    return render(request, 'global/delete_message.html', {'message': message,})
##



#EMPLOYER:
#EMPLOYER CHECK:
def check_if_employer(user):
    return user.groups.filter(name='employer').exists()
##


#EMPLOYER DASHBOARD:
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_dashboard(request):
    user = User.objects.get(id=request.user.id)
    last_login = user.last_login
    if user.employerprofile.referral_code:
        referral_status = "Created"
    else:
        referral_status = "Not created"
    candidates = request.user.employerprofile.candidateprofile_set.all()
    tests_count = Test.objects.filter(created_by=request.user).count()
    course_count = Course.objects.filter(created_by=request.user).count()
    return render(request, 'employer/employer-dashboard.html', {"last_login": last_login, "referral_status": referral_status, "candidates": candidates, "tests_count": tests_count, "course_count": course_count})
##


#EMPLOYER PROFILE:
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_profile(request):
    user = User.objects.get(id=request.user.id)
    employer_profile = EmployerProfile.objects.get(user_id=request.user.id)
    return render(request, 'employer/employer-profile.html', {"user": user, "employer_profile": employer_profile})

@csrf_exempt
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_profile_edit(request):
    user_edit_form = UserEditForm()
    employer_profile_form = EmployerProfileForm()
    employer_profile_form.fields['picture'].required = False
    employer_profile_form.fields['company_name'].required = False
    user = User.objects.get(id=request.user.id)
    employer_profile = EmployerProfile.objects.get(user_id=request.user.id)
    if request.method == "POST":
        user_edit_form = UserEditForm(request.POST)
        employer_profile_form = EmployerProfileForm(request.POST, request.FILES)
        employer_profile_form.fields['picture'].required = False
        employer_profile_form.fields['company_name'].required = False
        if user_edit_form.is_valid():
            # CHECK FOR EMPTY FORM FIELDS:
            if request.POST['username']:
                user.username = request.POST['username']
            if request.POST['first_name']:
                user.first_name = request.POST['first_name']
            if request.POST['last_name']:
                user.last_name = request.POST['last_name']
            if request.POST['email']:
                user.email = request.POST['email']
            if request.FILES.get('picture'):
                employer_profile.picture = request.FILES.get('picture')
            if request.POST['company_name']:
                employer_profile.company_name = request.POST['company_name']
            ##
            user.save()
            employer_profile.save()
            return redirect("ttfjobs:employer_profile")
    return render(request, 'employer/employer-profile-edit.html', {"user_edit_form": user_edit_form, "employer_profile_form": employer_profile_form})
##


#EMPLOYER REFERRAL:
@csrf_exempt
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_referral(request):
    employer_create_referral = EmployerCreateReferral()
    employer_profile = EmployerProfile.objects.get(user_id=request.user.id)
    if request.method == "POST":
        employer_create_referral = EmployerCreateReferral(request.POST)
        if employer_create_referral.is_valid():
            employer_profile.referral_code = request.POST['referral_code']
            employer_profile.save()
    if employer_profile.referral_code:
        referral_code = employer_profile.referral_code
        response = "Referral code has been created."
        copy_referral = True
    else:
        referral_code = ""
        response = "Referral code has not been created yet."
        copy_referral = False
    return render(request, 'employer/employer-referral.html', {"employer_create_referral": employer_create_referral, "referral_code": referral_code, "response": response, "copy_referral": copy_referral})
##


#EMPLOYER CHAT:
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_chat(request):
    candidates = request.user.employerprofile.candidateprofile_set.all()
    sent_messages = Message.objects.exclude(archivedmessage__archived_by=request.user,).filter(sender=request.user)
    form = SearchForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data.get('query')
        interests = form.cleaned_data.get('interests')
        if query:
            candidates = candidates.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user__email__icontains=query))
        if interests:
            candidates = candidates.filter(interests__in=interests)
    return render(request, 'employer/employer-chat.html', {'candidates': candidates, 'form': form, 'sent_messages': sent_messages,})

@login_required(login_url="ttfjobs:employer_login")
def employer_chat_message_create(request, user_id):
    candidate = User.objects.get(id=user_id)
    form = MessageForm()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = candidate
            message.save()
            messages.success(request, 'Message sent successfully')
            return HttpResponseRedirect(reverse('ttfjobs:employer_chat'))        
    return render(request, 'employer/employer-chat-message-create.html', {"candidate": candidate, "form": MessageForm})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_chat_messages_view(request, candidate_user_id):
    if not request.user.employerprofile.candidateprofile_set.filter(user__id=candidate_user_id).exists():
        raise Http404('No matching profile')
    candidate_messages = Message.objects.filter(receiver=request.user, sender=candidate_user_id)
    candidate_messages.update(has_been_read=True)
    candidate = User.objects.get(id=candidate_user_id)
    return render(request, 'employer/employer-chat-messages-view.html', {"candidate_messages": candidate_messages, "candidate": candidate})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_chat_message_view(request, message_id):
    message = Message.objects.get(id=message_id)
    receiver = User.objects.get(id=message.receiver_id)
    return render(request, 'employer/employer-chat-message-view.html', {"message": message, "receiver": receiver})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_chat_archive(request):
    archived_messages = ArchivedMessage.objects.filter(archived_by=request.user)
    return render(request, 'employer/employer-chat-archive.html', {"archived_messages": archived_messages})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_chat_archive_message(request, archived_id):
    message = get_object_or_404(ArchivedMessage, id=archived_id, archived_by=request.user)
    return render(request, 'employer/employer-chat-archive-message.html', {"message": message})
##


#EMPLOYER CANDIDATES:
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_candidates(request):
    employer_candidates = request.user.employerprofile.candidateprofile_set.all()
    return render(request, 'employer/employer-candidates.html', {'candidates': employer_candidates,})
##


#EMPLOYER TESTS:
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_tests(request):
    tests = Test.objects.filter(created_by=request.user)
    return render(request, 'employer/employer-tests.html', {'tests': tests,})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_tests_assignment(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    if not request.user.employerprofile.candidateprofile_set.filter(id=candidate_id).exists():
        raise Http404('No message matched the given query')
    employers_all_tests = request.user.test_set.all()
    form = TestAssignmentForm(instance=candidate, data=request.POST or None,)
    if form.is_valid():
        form.save()
        messages.success(request, 'Succesfully assigned tests')
        return HttpResponseRedirect(reverse('ttfjobs:employer_candidates'))
    return render(request, 'employer/employer-candidates-test-assignment.html', {'candidate': candidate, 'form': form,})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_test_results(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    if not request.user.employerprofile.candidateprofile_set.filter(id=candidate_id).exists():
        raise Http404('No message matched the given query')
    submitted_tests = SubmittedTest.objects.filter(submitted_by=candidate.user)
    awaiting_tests = candidate.tests_assigned.exclude(id__in=submitted_tests.values_list('test__id', flat=True))
    return render(request, 'employer/employer-candidates-test-results.html', {'candidate': candidate, 'submitted_tests': submitted_tests, 'awaiting_tests': awaiting_tests,})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_courses_assignment(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    if not request.user.employerprofile.candidateprofile_set.filter(id=candidate_id).exists():
        raise Http404('No message matched the given query')
    employers_all_tests = request.user.test_set.all()
    form = CourseAssignmentForm(instance=candidate, data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Succesfully assigned courses')
        return HttpResponseRedirect(reverse('ttfjobs:employer_candidates'))
    return render(request, 'employer/employer-candidates-courses-assignment.html', {'candidate': candidate, 'form': form,})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_courses_results(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    if not request.user.employerprofile.candidateprofile_set.filter(id=candidate_id).exists():
        raise Http404('No message matched the given query')
    submitted_courses = SubmittedCourse.objects.filter(submitted_by=candidate.user)
    awaiting_courses = candidate.courses_assigned.exclude(id__in=submitted_courses.values_list('course__id', flat=True))
    return render(request, 'employer/employer-candidates-courses-results.html', {'candidate': candidate, 'submitted_courses': submitted_courses, 'awaiting_courses': awaiting_courses,})

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_test_submitted_data(request, candidate_id, submitted_test_id):
    submitted_test = get_object_or_404(SubmittedTest, id=submitted_test_id)
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    if not request.user.employerprofile.candidateprofile_set.filter(id=candidate_id).exists():
        raise Http404('No message matched the given query')
    return render(request, 'employer/employer-test-submitted-data.html', {'submitted_test': submitted_test,})
##


##EMPLOYER COURSES:
@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_courses(request):
    courses = request.user.course_set.all()
    return render(request, 'employer/employer-courses.html', {'courses': courses,},)

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_courses_create(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        course = form.save(commit=False)
        course.created_by = request.user
        course.save()
        form.save_m2m()
        messages.success(request, 'Course created successfully')
        return HttpResponseRedirect(reverse('ttfjobs:employer_courses'))
    return render(request, 'employer/employer-courses-create.html', {'form': form,},)

@login_required(login_url="ttfjobs:employer_login")
@user_passes_test(check_if_employer)
def employer_courses_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.created_by != request.user:
        raise Http404('No course matched the given query')
    form = CourseForm(data=request.POST or None, instance=course)
    if form.is_valid():
        course = form.save()
        messages.success(request, 'Course updated successfully')
        return HttpResponseRedirect(reverse('ttfjobs:employer_courses'))
    return render(request, 'employer/employer-courses-create.html',{'form': form,},)
##



#CANDIDATE:
#CANDIDATE CHECK:
def check_if_candidate(user):
    return user.groups.filter(name='candidate').exists()
##


#CANDIDATE DASHBOARD:
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_dashboard(request):
    user = User.objects.get(id=request.user.id)
    last_login = user.last_login
    submitted_courses_ids = SubmittedCourse.objects.filter(submitted_by=request.user).values_list('course_id', flat=True)
    submitted_tests_ids = SubmittedTest.objects.filter(submitted_by=request.user).values_list('test_id', flat=True)
    incoming_messages_count = Message.objects.exclude(archivedmessage__archived_by=request.user).exclude(has_been_read=True).filter(receiver=request.user,).count()
    assigned_course_count = request.user.candidateprofile.courses_assigned.exclude(id__in=submitted_courses_ids).count()
    assigned_tests_count = request.user.candidateprofile.tests_assigned.exclude(id__in=submitted_tests_ids).count()
    return render(request, 'candidate/candidate-dashboard.html', {"last_login": last_login, "incoming_messages_count": incoming_messages_count, "assigned_tests_count": assigned_tests_count, "assigned_course_count": assigned_course_count})
##


#CANDIDATE PROFILE:
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_profile(request):
    user = User.objects.get(id=request.user.id)
    candidate_profile = CandidateProfile.objects.get(user_id=request.user.id)
    return render(request, 'candidate/candidate-profile.html', {"user": user, "candidate_profile": candidate_profile})

@csrf_exempt
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_profile_edit(request):
    user_edit_form = UserEditForm()
    candidate_profile_form_edit = CandidateProfileFormEdit()
    user = User.objects.get(id=request.user.id)
    candidate_profile = CandidateProfile.objects.get(user_id=request.user.id)
    if request.method == "POST":
        user_edit_form = UserEditForm(request.POST)
        candidate_profile_form_edit = CandidateProfileFormEdit(request.POST, request.FILES, instance=candidate_profile)
        if user_edit_form.is_valid() and candidate_profile_form_edit.is_valid():
            # CHECK FOR EMPTY FORM FIELDS:
            if request.POST['username']:
                user.username = request.POST['username']
            if request.POST['first_name']:
                user.first_name = request.POST['first_name']
            if request.POST['last_name']:
                user.last_name = request.POST['last_name']
            if request.POST['email']:
                user.email = request.POST['email']
            user.save()
            if request.FILES.get('picture'):
                candidate_profile.picture = request.FILES.get('picture')
                candidate_profile.save()
            if request.POST.get('interests'):
                candidate_profile_form_edit.save(False)
                candidate_profile_form_edit.save_m2m()
            ##
            return redirect("ttfjobs:candidate_profile")
    return render(request, 'candidate/candidate-profile-edit.html', {"user_edit_form": user_edit_form, "candidate_profile_form_edit": candidate_profile_form_edit})
##


#CANDIDATE CHAT:
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_chat(request):
    chat_messages = Message.objects.exclude(archivedmessage__archived_by=request.user).filter(receiver=request.user)
    try:
        employer = request.user.candidateprofile.employer
    except:
        employer = None
    sent_messages = Message.objects.exclude(archivedmessage__archived_by=request.user,).filter(sender=request.user)
    return render(request, 'candidate/candidate-chat.html', {"chat_messages": chat_messages, "employer": employer, "sent_messages": sent_messages})

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_chat_message_view(request, message_id):
    message = get_object_or_404(Message, receiver=request.user, id=message_id)
    message.has_been_read = True
    message.save()
    form = ReplyMessageForm(request.POST or None)
    if form.is_valid():
        new_message = form.save(commit=False)
        new_message.sender = request.user
        new_message.subject = message.subject
        new_message.receiver = message.sender
        new_message.save()
        messages.success(request, "Succesfully sent message")
        return HttpResponseRedirect(reverse('ttfjobs:candidate_chat'))
    return render(request, 'candidate/candidate-chat-message-view.html', {'chat_message': message, 'form': form,},)

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_chat_message_view_sent(request, message_id):
    message = Message.objects.get(id=message_id)
    receiver = User.objects.get(id=message.receiver_id)
    return render(request, 'candidate/candidate-chat-message-view-sent.html', {"message": message, "receiver": receiver})

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_chat_message_create(request, user_id):
    employer = User.objects.get(id=user_id)
    message_form = MessageForm()
    if request.method == "POST":
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sender = request.user
            message.receiver = employer
            message.save()
            messages.success(request, 'Message sent successfully.')
            return HttpResponseRedirect(reverse('ttfjobs:candidate_chat'))        
    return render(request, 'candidate/candidate-chat-message-create.html', {"employer": employer, "message_form": message_form})

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_chat_archive(request):
    archived_messages = ArchivedMessage.objects.filter(archived_by=request.user)
    return render(request, 'candidate/candidate-chat-archive.html', {'archived_messages': archived_messages,})

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_chat_archive_message(request, archived_id):
    message = get_object_or_404(ArchivedMessage, id=archived_id, archived_by=request.user)
    return render(request, 'candidate/candidate-chat-archive-message.html', {'message': message,})
##


#CANDIDATE COURSES:
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_courses(request):
    submitted_courses_ids = SubmittedCourse.objects.filter(submitted_by=request.user).values_list('course_id', flat=True)
    #HIDE SUBMITTED COURSES:
    assigned_courses = request.user.candidateprofile.courses_assigned.exclude(id__in=submitted_courses_ids)
    return render(request, 'candidate/candidate-courses.html', {'assigned_courses': assigned_courses,},)

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_take_course(request, course_id):
    candidate_profile = request.user.candidateprofile
    if not candidate_profile.courses_assigned.filter(id=course_id):
        raise Http404('No message matched the given query')
    if SubmittedCourse.objects.filter(submitted_by=request.user, course__id=course_id).exists():
        raise Http404('Course has been submitted')
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        SubmittedCourse.objects.create(course=course, submitted_by=request.user,)
        messages.success(request, 'Course submmited successfully')
        return HttpResponseRedirect(reverse('ttfjobs:candidate_courses'))
    return render(request, 'candidate/candidate-take-course.html', {'course': course,},)
##


#CANDIDATE TESTS:
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_tests(request):
    submitted_tests_ids = SubmittedTest.objects.filter(submitted_by=request.user).values_list('test_id', flat=True)
    #HIDE SUBMITTED TESTS:
    assigned_tests = request.user.candidateprofile.tests_assigned.exclude(id__in=submitted_tests_ids)
    return render(request, 'candidate/candidate-tests.html', {'assigned_tests': assigned_tests,},)

@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_take_test(request, test_id):
    candidate_profile = request.user.candidateprofile
    if not candidate_profile.tests_assigned.filter(id=test_id):
        raise Http404('No message matched the given query')
    if SubmittedTest.objects.filter(submitted_by=request.user, test__id=test_id).exists():
        raise Http404('Test been submitted')
    test = Test.objects.get(id=test_id)
    form = TestGeneratedForm(data=request.POST or None, test=test)
    if form.is_valid():
        SubmittedTest.objects.create(test=test, submitted_data=json.dumps(form.cleaned_data), submitted_by=request.user,)
        messages.success(request, 'Test submitted successfully')
        return HttpResponseRedirect(reverse('ttfjobs:candidate_tests'))
    return render(request, 'candidate/candidate-take-test.html', {'test': test, 'form': form,},)
##


#CANDIDATE ACHIEVEMENTS:
@login_required(login_url="ttfjobs:candidate_login")
@user_passes_test(check_if_candidate)
def candidate_achievements(request):
    submitted_tests = SubmittedTest.objects.filter(submitted_by=request.user)
    submitted_courses = SubmittedCourse.objects.filter(submitted_by=request.user)
    return render(request, 'candidate/candidate-achievements.html', {'submitted_tests': submitted_tests, 'submitted_courses': submitted_courses,},)
##
