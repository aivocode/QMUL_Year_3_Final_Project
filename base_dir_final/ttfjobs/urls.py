from django.urls import path
from . import views, views_tests


app_name = 'ttfjobs'


urlpatterns = [
#GUEST:
    #GUEST CONTENT:
    path('', views.home, name='home'),
    path('features', views.features, name='features'),
    path('pricing', views.pricing, name='pricing'),
    path('demo', views.demo, name='demo'),
    path('about', views.about, name='about'),
    ##

    #GUEST > EMPLOYER
    path('employer', views.employer, name='employer'),
    path('employer-register', views.employer_register, name='employer_register'),
    path('employer-login', views.employer_login, name='employer_login'),
    ##

    #GUEST > CANDIDATE:
    path('candidate', views.candidate, name='candidate'),
    path('candidate-register', views.candidate_register, name='candidate_register'),
    path('candidate-login', views.candidate_login, name='candidate_login'),
    ##
##


#EMPLOYER, CANDIDATES (GLOBAL):
    #GLOBAL SHARED:
    path('all-logout', views.all_logout, name='all_logout'),
    path('delete-message/<int:message_id>/', views.delete_message, name="delete_message"),
    ##
##


#EMPLOYER:
    #EMPLOYER DASHBOARD:
    path('employer-dashboard', views.employer_dashboard, name='employer_dashboard'),
    ##

    #EMPLOYER PROFILE:
    path('employer-profile', views.employer_profile, name='employer_profile'),
    path('employer-profile-edit', views.employer_profile_edit, name='employer_profile_edit'),
    ##

    #EMPLOYER REFERRAL:
    path('employer-referral', views.employer_referral, name='employer_referral'),
    ##

    #EMPLOYER CHAT:
    path('employer-chat', views.employer_chat, name='employer_chat'),
    path('employer-chat-message-create/<int:user_id>/', views.employer_chat_message_create, name='employer_chat_message_create'),
    path('employer-chat-messages-view<int:candidate_user_id>/', views.employer_chat_messages_view, name='employer_chat_messages_view'),
    path('employer-chat-message-view/<int:message_id>/', views.employer_chat_message_view, name='employer_chat_message_view'),
    path('employer-chat-archive', views.employer_chat_archive, name='employer_chat_archive'),
    path('employer-chat-archive-message/<int:archived_id>/', views.employer_chat_archive_message, name='employer_chat_archive_message'),

    ##

    #EMPLOYER CANDIDATES:
    path('employer-candidates', views.employer_candidates, name='employer_candidates'),
    path('employer-tests/assign-courses/<int:candidate_id>/', views.employer_courses_assignment, name='employer_courses_assignment'),
    path('employer-tests/view-courses/<int:candidate_id>/',views.employer_courses_results,name='employer_courses_results'),
    path('employer-tests/view-results/<int:candidate_id>/submitted-data/<int:submitted_test_id>/', views.employer_test_submitted_data, name='employer_test_submitted_data'),
    path('employer-tests/assign-test/<int:candidate_id>/', views.employer_tests_assignment, name='employer_tests_assignment'),
    path('employer-tests/view-results/<int:candidate_id>/', views.employer_test_results, name='employer_test_results'),
    ##

    #EMPLOYER COURSES:
    path('employer-courses', views.employer_courses, name='employer_courses'),
    path('employer-courses/create/', views.employer_courses_create, name='employer_course_create'),
    path('employer-courses/update/<int:course_id>/', views.employer_courses_update, name='employer_course_update'),
    ##

    #EMPLOYER TESTS:
    path('employer-tests', views.employer_tests, name='employer_tests'),
    path('employer-tests-create', views_tests.CreateTestView.as_view(), name='employer_tests_create'),
    path('employer-tests-edit/<int:pk>/', views_tests.UpdateTestView.as_view(), name='employer_tests_edit'),
##
    

#CANDIDATE:
    #CANDIDATE DASHBOARD:
    path('candidate-dashboard', views.candidate_dashboard, name='candidate_dashboard'),
    ##

    #CANDIDATE PROFILE:
    path('candidate-profile', views.candidate_profile, name='candidate_profile'),
    path('candidate-profile-edit', views.candidate_profile_edit, name='candidate_profile_edit'),
    ##

    #CANDIDATE CHAT:
    path('candidate-chat', views.candidate_chat, name='candidate_chat'),
    path('candidate-chat-message-create/<int:user_id>/', views.candidate_chat_message_create, name='candidate_chat_message_create'),
    path('candidate-chat-message-view/<int:message_id>/', views.candidate_chat_message_view, name='candidate_chat_message_view'),
    path('candidate-chat-message-view-sent/<int:message_id>/', views.candidate_chat_message_view_sent, name='candidate_chat_message_view_sent'),
    path('candidate-chat-archive', views.candidate_chat_archive, name='candidate_chat_archive'),
    path('candidate-chat-archive-message/<int:archived_id>/', views.candidate_chat_archive_message, name='candidate_chat_archive_message'),
    ##

    #CANDIDATE COURSES:
    path('candidate-courses', views.candidate_courses, name='candidate_courses'),
    path('candidate-courses/take/<int:course_id>/', views.candidate_take_course, name='candidate_take_course'),
    ##
    
    #CANDIDATE TESTS:
    path('candidate-tests', views.candidate_tests, name='candidate_tests'),
    path('candidate-tests/test/<int:test_id>/', views.candidate_take_test, name='candidate_take_test'),
    ##

    #CANDIDATE ACHIEVEMENTS:
    path('candidate-achievements', views.candidate_achievements, name='candidate_achievements'),
    ##
##
]
