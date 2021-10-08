# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from modules.academic import views

urlpatterns = [
   path('', views.index, name='academic'),
   #Pruebas de sprint 2
   path('test/', views.prueba, name="academic_test"),
   path('evaluaciones/', views.evaluaciones, name="evaluaciones"),
   #contenidos AJAX
   path('contenidoProgramas/', views.getContentProgramas, name="contenidoProgramas"),
   path('contenidoProcesos/', views.getContentProcesos, name="contenidoProcesos"),
   path('contenidoUnidades/', views.getContentUnidades, name="contenidoUnidades"),
   path('contenidoCursos/', views.getContentCursos, name="contenidoCursos"),
   path('contenidoTopicos/', views.getContentTopicos, name="contenidoTopicos"),
   path('comboOption/', views.getComboContent, name="contenidoCombo"),
   #modales
   path('modalAddCategoria/', views.getModalCategorias, name="modalAddCategoria"),
   path('modalAddPrograma/', views.getModalProgramas, name="modalAddPrograma"),
   path('modalAddProceso/', views.getModalProcesos, name="modalAddProceso"),
   path('modalAddUnidad/', views.getModalUnidades, name="modalAddUnidad"),
   path('modalAddCurso/', views.getModalCursos, name="modalAddCurso"),
   path('modalAddTopico/', views.getModalTopico, name="modalAddTopico"),
   path('modalAddActividad/', views.getModalActividad, name="modalAddActividad"),
   path('modalChooseActivity/', views.getModalChooseActivities, name="modalChooseActivity"),
   path('modalNewTest/', views.getModalNewTest, name="modalNewTest"),
   path('modalNewLesson/', views.getModalNewLesson, name="modalNewLesson"),
   path('modalNewHomework/', views.getModalNewHomework, name="modalNewHomework"),
   path('modalNewForum/', views.getModalNewForum, name="modalNewForum"),
   #urls serias
   path('<str:programa>/', views.programa, name="programa"),
   path('<str:programa>/<str:proceso>/', views.proceso, name="proceso"),
   path('<str:programa>/<str:proceso>/<str:unidad>/', views.unidad, name="unidad"),
   path('<str:programa>/<str:proceso>/<str:unidad>/<str:curso>/', views.curso, name="curso"),
   path('<str:programa>/<str:proceso>/<str:unidad>/<str:curso>/<str:topico>/', views.topico, name="topico"),
   path('<str:programa>/<str:proceso>/<str:unidad>/<str:curso>/<str:topico>/<int:idActividad>/', views.actividad, name="actividad"),
   #demas paginas
   re_path(r'^.*\.*', views.pages, name='pages'),
]
