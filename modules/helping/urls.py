# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from django.urls import path
from modules.helping.views import save_Q,showhelps,helpsdelete,helpsedit,show_questions,questionask,landingshow, sending 
from modules.helping import views


urlpatterns = [
    path('Save/', save_Q , name="Savequestions"),
    path('ver/', showhelps , name="Showhelps"),
    path('edithelp/<int:id>',helpsedit, name="edithelp"),
    path('deletehelp/<int:id>',helpsdelete, name="deletehelp"),
    path('showQuestions/',show_questions,name="show_questions"),
    path('showAnswers/<int:id>',questionask,name="showanswers"),
    path('landingshow/',landingshow,name="landingshow"),
    path('sending/',sending,name="sending"),
    path('helpSecurity/', views.helpSecurity, name="helpSecurity"),   
    path('myHelp/', views.myHelp, name="myHelp"),   
]