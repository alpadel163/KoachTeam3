from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.db.models import query
from django.db.models.aggregates import Count
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django import template
from modules.app import Methods
from core import settings
from pathlib import Path
import uuid
import base64
import datetime
from django.core.paginator import Paginator

from django.utils.dateparse import parse_datetime

import json
from django.core.files.storage import FileSystemStorage
import os

from ..app.models import TablasConfiguracion, Estructuraprograma


from ..security.models import ExtensionUsuario

from .models import ActividadEvaluaciones, Cursos, ActividadConferencia, ActividadLeccion, ActividadTarea, EscalaEvaluacion, EvaluacionesPreguntas, EvaluacionesBloques, Paginas, PreguntasOpciones, ExamenActividad,ExamenRespuestas,ExamenResultados
from modules.app import models

# Create your views here.
@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'academic'
    #Vista del gestor
    html_template = (loader.get_template('academic/gestor.html'))
    #Vista del profesor
    #html_template = (loader.get_template('academic/index.html'))
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def createLessons(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            # try:
            if request.body:
                data = json.load(request)
                if data["method"] == "Delete":
                    pagina = Paginas.objects.get(pk=data["id"])
                    leccion = pagina.fk_estructura_programa
                    pagina.delete()
                    #update order
                    paginas = leccion.paginas_set.all().order_by('ordenamiento')
                    for idx, value in enumerate(paginas, start=1):
                        value.ordenamiento = idx
                        value.save()
                    return JsonResponse({"message":"Deleted"})
                elif data["method"] == "Sort":
                    for item in data["order"]:
                        tempPage = Paginas.objects.get(pk=item["pk"])
                        tempPage.ordenamiento = item["order"]
                        tempPage.save()
                    return JsonResponse({"message":"Perfect"})
                elif data["method"] == "Update":
                    pass
                elif data["method"] == "Create":
                    leccion = ActividadLeccion.objects.get(pk=data["id"]).fk_estructura_programa
                    paginas = leccion.paginas_set.all().order_by('ordenamiento')
                    ordenamiento = paginas.count()
                    for idx, value in enumerate(paginas, start=1):
                        value.ordenamiento = idx
                        value.save()
                    pagina = Paginas()
                    pagina.titulo = ""
                    pagina.contenido = ""
                    pagina.ordenamiento = ordenamiento + 1
                    pagina.fk_estructura_programa = leccion
                pagina.save()
                return JsonResponse({"message":"Perfect"})
            else:
                html_template = (loader.get_template('academic/createLessons.html'))
                return HttpResponse(html_template.render(context, request))
            # except:
            #     return JsonResponse({"message":"error"}, status=500)
    lessonId=request.GET.get('id')
    context = {}
    leccion=ActividadLeccion.objects.get(fk_estructura_programa=lessonId)
    context['segment'] = 'academic'
    context['lesson'] = leccion
    return render(request, 'academic/createLessons.html', context)

@login_required(login_url="/login/")
def createQuestions(request):
    preguntaId=request.GET.get('id')
    #la modificacion es para que los busque por el id de estructuras programa (me facilita la vida)
    pregunta=ActividadEvaluaciones.objects.get(fk_estructura_programa=preguntaId)
    escalas = EscalaEvaluacion.objects.all()
    
    escalaEvaluacion=pregunta.fk_escala_evaluacion
    escalaBloque=pregunta.fk_escala_bloque

    escalaBloque=pregunta.fk_escala_bloque

    listaPreguntas=None
    boque=None

    if(Estructuraprograma.objects.get(pk=preguntaId).fk_categoria.valor_elemento=='activityExpert'):
     bloque=EvaluacionesBloques.objects.filter(fk_actividad_evaluaciones=pregunta.idactividad_evaluaciones)
     
    else:
     bloque=EvaluacionesBloques.objects.get(fk_actividad_evaluaciones=pregunta.idactividad_evaluaciones)
     listaPreguntas=EvaluacionesPreguntas.objects.filter(fk_evaluaciones_bloque=bloque).order_by('orden')



     

    
    context = {
        'pregunta':pregunta,
        "tipoPreguntas" : TablasConfiguracion.obtenerHijos('PregEvalua'),   
        'modelo':pregunta , 
        'escalas':escalas,
        'bloque':bloque,
        'escalaEvaluacion':escalaEvaluacion,
        'listaPreguntas':listaPreguntas,
        'escalaBloque':escalaBloque

    }
    context['segment'] = 'academic'
    if(Estructuraprograma.objects.get(pk=preguntaId).fk_categoria.valor_elemento=='activityExpert'):
     return render(request, 'academic/createExpert.html', context)

    return render(request, 'academic/createQuestions.html', context)

@login_required(login_url="/login/")
def reviewExamen(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            
                context = {}
                data = json.load(request)["data"]

                
                if data["method"] == "Show":
                        examen=ExamenActividad.objects.get(pk=data['testId'])
                        resultados=ExamenResultados.objects.filter(fk_Examen=examen.pk)
                        respuestas=ExamenRespuestas.objects.filter(fk_Examen=examen.pk)
                        actividad=ActividadEvaluaciones.objects.annotate(num_child=Count('bloque_actividad', distinct=True) ).get(pk=data['ActivityId'])
                        
                        
                        context = {
                        'examen':examen,
                        'resultados':resultados,
                        'respuestas':respuestas,
                        'actividad':actividad,

                        }
                        html_template = (loader.get_template('academic/ExamenRespuestas.html'))
                        return HttpResponse(html_template.render(context, request))
                   

@login_required(login_url="/login/")
def contenidoExamen(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            
                context = {}
                data = json.load(request)["data"]

                
                if data["method"] == "Show":
                        actividad=ActividadEvaluaciones.objects.annotate(num_child=Count('bloque_actividad', distinct=True) ).get(pk=data['ActivityId'])
                        
                        
                        context = {
                        'actividad':actividad,

                        }
                        html_template = (loader.get_template('academic/contenidoExamen.html'))
                        return HttpResponse(html_template.render(context, request))
                   
                if data["method"] == "Get":
                        actividad=ActividadEvaluaciones.objects.annotate(num_child=Count('bloque_actividad', distinct=True) ).get(pk=data['ActivityId'])
                        BloquesPreguntas=actividad.bloque_actividad.all()
                        findpregunta = list(BloquesPreguntas.values())
                        
                         
                        # pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                        # findpregunta = list(pregunta.values())
                        # childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                        # listaChilds = list(childs.values())
                        return JsonResponse({"data":findpregunta}, safe=False)
                     

                if data["method"] == "Update":
                    bloque=EvaluacionesBloques.objects.get(pk=int(data["idViejo"]))
                    
                    bloque.comentario=data['textoBloque']
                    bloque.titulo_bloque=data['tituloBloque']
                    bloque.save()



                if data["method"] == "Create":
                    actividad=ActividadEvaluaciones.objects.annotate(num_child=Count('bloque_actividad', distinct=True) ).get(pk=data['ActivityId'])
                    Examen=ExamenActividad.objects.create()

                    Examen.usuario=ExtensionUsuario.objects.get(user=request.user).Publico
                    Examen.estadoExamen=2
                    Examen.nro_repeticiones=1
                    Examen.fechaInicio=datetime.datetime.now() 
                    Examen.fk_Actividad=actividad


                    Examen.save()
                    return JsonResponse({"id": Examen.pk})     


                if data["method"] == "Save":
                   respuestas=data["respuestas"] 

                   if respuestas:
                        total=0
                        examen=ExamenActividad.objects.get(pk=data['examenId'])
                        actividad=ActividadEvaluaciones.objects.get(pk=data['ActivityId'])

                        for block in actividad.bloque_actividad.all():
                            resultado=ExamenResultados()
                            resultado.bloque=block
                            resultado.puntuacionBloques=float(0.00)
                            resultado.fk_Examen=examen
                            resultado.save()

                        for resp in respuestas:
                            opcionRespuesta=ExamenRespuestas.objects.create()
                            opcion=PreguntasOpciones.objects.get(pk=resp['opcionID'])
                            opcionRespuesta.fk_Opcion=opcion
                            opcionRespuesta.fk_Examen=examen
                            pregunta=EvaluacionesPreguntas.objects.get(pk=resp['idPregunta'])

                            opcionRespuesta.fk_pregunta=pregunta

                            if(resp['tipoPregunta']==5):
                                opcionRespuesta.respuetaCorrecta=resp['isCorrect']
                            if(resp['tipoPregunta']==4):
                                opcionRelacionada=PreguntasOpciones.objects.get(pk=resp['idRelacional'])
                                opcionRespuesta.fk_OpcionRelacionada=opcionRelacionada
                            opcionRespuesta.save()

                            resultado=ExamenResultados.objects.filter(fk_Examen=examen).get(bloque__pk=resp['bloques'])
                            if(resp['tipoPregunta']==1):
                                if(opcion.respuetaCorrecta):
                                 resultado.puntuacionBloques= resultado.puntuacionBloques+pregunta.puntos_pregunta
                                 examen.PuntuacionFinal=examen.PuntuacionFinal+pregunta.puntos_pregunta

                            if(resp['tipoPregunta']==2):
                             resultado.puntuacionBloques= resultado.puntuacionBloques+opcion.puntos_porc
                             examen.PuntuacionFinal=examen.PuntuacionFinal+opcion.puntos_porc

                            if(resp['tipoPregunta']==3):
                                if(opcion.respuetaCorrecta):
                                    resultado.puntuacionBloques= resultado.puntuacionBloques+pregunta.puntos_pregunta
                                    examen.PuntuacionFinal=examen.PuntuacionFinal+pregunta.puntos_pregunta

                            if(resp['tipoPregunta']==4):
                                opcionRelacionada=PreguntasOpciones.objects.get(pk=resp['idRelacional'])
                                if(opcionRelacionada.indiceAsociacion==opcion.indiceAsociacion):
                                    resultado.puntuacionBloques= resultado.puntuacionBloques+opcion.puntos_porc
                                    examen.PuntuacionFinal=examen.PuntuacionFinal+opcion.puntos_porc

                            if(resp['tipoPregunta']==5):
                             if(opcion.respuetaCorrecta):
                                 resultado.puntuacionBloques= resultado.puntuacionBloques+opcion.puntos_porc
                                 examen.PuntuacionFinal=examen.PuntuacionFinal+opcion.puntos_porc

                            if(resp['tipoPregunta']==6):
                             resultado.puntuacionBloques= resultado.puntuacionBloques+opcion.puntos_porc
                             examen.PuntuacionFinal=examen.PuntuacionFinal+opcion.puntos_porc
                            resultado.save()
                            examen.save()
                        
                   examen.estadoExamen=3
                   examen.fechaTermino=datetime.datetime.now() 
                   examen.nro_repeticiones=examen.nro_repeticiones+1
                   examen.save()


                            

                        
                       
                        


                   
                            





                        






                        
                          



             
                return JsonResponse({"message": "Perfect"})     
           
           
    context = {}
    html_template = (loader.get_template('academic/contenidoExamen.html'))
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def takeExam(request):
    preguntaId=request.GET.get('id')
    #la modificacion es para que los busque por el id de estructuras programa (me facilita la vida)
    pregunta=ActividadEvaluaciones.objects.get(fk_estructura_programa=preguntaId)
    escalas = EscalaEvaluacion.objects.all()
    user=ExtensionUsuario.objects.get(user=request.user)


    examen=ExamenActividad.objects.filter(fk_Actividad=pregunta).filter(usuario=user.Publico)
    print(examen)


    
    escalaEvaluacion=pregunta.fk_escala_evaluacion
    escalaBloque=pregunta.fk_escala_bloque

    escalaBloque=pregunta.fk_escala_bloque

    listaPreguntas=None
    boque=None

    if(Estructuraprograma.objects.get(pk=preguntaId).fk_categoria.valor_elemento=='activityExpert'):
     bloque=EvaluacionesBloques.objects.filter(fk_actividad_evaluaciones=pregunta.idactividad_evaluaciones)
     
    else:
     bloque=EvaluacionesBloques.objects.get(fk_actividad_evaluaciones=pregunta.idactividad_evaluaciones)
     listaPreguntas=EvaluacionesPreguntas.objects.filter(fk_evaluaciones_bloque=bloque).order_by('orden')



     

    
    context = {
        'pregunta':pregunta,
        "tipoPreguntas" : TablasConfiguracion.obtenerHijos('PregEvalua'),   
        'modelo':pregunta , 
        'escalas':escalas,
        'bloque':bloque,
        'escalaEvaluacion':escalaEvaluacion,
        'listaPreguntas':listaPreguntas,
        'escalaBloque':escalaBloque,
        'examen':examen

    }
    context['segment'] = 'academic'
    if(Estructuraprograma.objects.get(pk=preguntaId).fk_categoria.valor_elemento=='activityExpert'):
     return render(request, 'academic/takeExam.html', context)

    return render(request, 'academic/takeExam.html', context)

@login_required(login_url="/login/")
def SeeTest(request):
    Id=request.GET.get('id')
    examen=ExamenActividad.objects.get(pk=Id)
    
    pregunta=ActividadEvaluaciones.objects.get(pk=examen.fk_Actividad.pk)
    escalas = EscalaEvaluacion.objects.all()
    user=ExtensionUsuario.objects.get(user=request.user)


    print(examen)


    
    escalaEvaluacion=pregunta.fk_escala_evaluacion
    escalaBloque=pregunta.fk_escala_bloque

    escalaBloque=pregunta.fk_escala_bloque

    listaPreguntas=None
    boque=None

    if(Estructuraprograma.objects.get(pk=pregunta.fk_estructura_programa.pk).fk_categoria.valor_elemento=='activityExpert'):
     bloque=EvaluacionesBloques.objects.filter(fk_actividad_evaluaciones=pregunta.idactividad_evaluaciones)
     
    else:
     bloque=EvaluacionesBloques.objects.get(fk_actividad_evaluaciones=pregunta.idactividad_evaluaciones)
     listaPreguntas=EvaluacionesPreguntas.objects.filter(fk_evaluaciones_bloque=bloque).order_by('orden')



     

    
    context = {
        'pregunta':pregunta,
        "tipoPreguntas" : TablasConfiguracion.obtenerHijos('PregEvalua'),   
        'modelo':pregunta , 
        'escalas':escalas,
        'bloque':bloque,
        'escalaEvaluacion':escalaEvaluacion,
        'listaPreguntas':listaPreguntas,
        'escalaBloque':escalaBloque,
        'examen':examen

    }
    context['segment'] = 'academic'
    if(Estructuraprograma.objects.get(pk=pregunta.fk_estructura_programa.pk).fk_categoria.valor_elemento=='activityExpert'):
     return render(request, 'academic/SeeTest.html', context)

    return render(request, 'academic/SeeTest.html', context)

    


#    if "delete" in data:
#                     question = EvaluacionesPreguntas.objects.get(pk=data["id"])
#                     question.delete()
#                     return JsonResponse({"message": "Deleted"})
#                 elif "idFind" in data:
#                     question = EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
#                     findQuestion = list(question.values())
#                     return JsonResponse({"data":findQuestion[0]}, safe=False)
#                 elif "idViejo" in data:
#                     question = EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
#                 else:
#                     question = EvaluacionesPreguntas()
#                 question.texto_pregunta.data = data["textoPregunta"]
#                 question.puntos_pregunta.data = data["puntosPregunta"]
#                 question.fk_actividad_evaluaciones.data = data["fk_actividad_evaluaciones"]
#                 question. fk_tipo_pregunta_evaluacion.data = data["tipoPregunta"]
#                 question.save()


@login_required(login_url="/login/")
def TestList(request):
    examenes=ExamenActividad.objects.all()
     
    paginator = Paginator(examenes, 10)
    
    msg=None
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
  


            
    context = { 'msg':msg,
     'ExamenList':page_obj ,
    }
    context['segment'] = 'academic'

    
    return render(request, 'academic/TestList.html', context)

@login_required(login_url="/login/")
def MyTest(request):
    examenes=ExamenActividad.objects.all()
    examenes.filter(usuario=ExtensionUsuario.objects.get(user=request.user).Publico)
     
    paginator = Paginator(examenes, 10)
    
    msg=None
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
  


            
    context = { 'msg':msg,
     'ExamenList':page_obj ,
    }
    context['segment'] = 'academic'

    
    return render(request, 'academic/TestList.html', context)


@login_required(login_url="/login/")
def saveQuestions(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                context = {}
                data = json.load(request)["data"]
                
                if data['tipoPregunta']==1:
                 pregunta=EvaluacionesPreguntas.objects.create()
                 bloque=EvaluacionesBloques.objects.get(pk=data['fatherId'])
                 pregunta.fk_evaluaciones_bloque=bloque
                 pregunta.texto_pregunta=data['textoPregunta']
                 pregunta.puntos_pregunta=data['puntosPregunta']
                 pregunta.fk_tipo_pregunta_evaluacion=data['tipoPregunta']
                 pregunta.save

                 hijos = data["hijos"]
                 if hijos:
                     print('jeje')
                        # if "idViejo" in data:
                        #     childs = EscalaCalificacion.objects.filter(fk_escala_evaluacion=newScaleGe)
                        #     childs.delete()
                        # for newScalePa in hijos:
                        #     newSP = EscalaCalificacion()
                        #     newSP.desc_calificacion=newScalePa["descriptionCalif"]
                        #     newSP.puntos_maximo=newScalePa["max_points"] 
                        #     newSP.fk_calificacion_id=newScalePa["quack"]
                        #     newSP.fk_escala_evaluacion= newScaleGe
                        #     newSP.save()    

             
                return JsonResponse({"message": "Perfect"})      
            except:
                return JsonResponse({"message": "Error"})
                
    context = {}
    html_template = (loader.get_template('academic/createQuestions.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getContentProgramas(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            if request.body:
                data = json.load(request)    
                lista = {}
                edit=True
                delete=True
                categorias = TablasConfiguracion.obtenerHijos("CatPrograma")
                if data["query"] == "" or data["query"] == None:
                    for categoria in categorias:
                        lista[categoria.desc_elemento]=categoria.estructuraprograma_set.all().filter(valor_elemento="Program")
                else:
                    for categoria in categorias:
                        lista[categoria.desc_elemento]=categoria.estructuraprograma_set.all().filter(valor_elemento="Program", descripcion__icontains=data["query"])
                context = {"data" : lista, "edit": edit, "delete":delete, "query":data["query"]}
                html_template = (loader.get_template('academic/contenidoProgramas.html'))
                return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getContentProcesos(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            if request.body:
                data = json.load(request)    
                edit=True
                delete=True
                programa=Estructuraprograma.objects.get(valor_elemento="Program", url=data["url"])
                if data["query"] == "" or data["query"] == None:
                    lista = programa.estructuraprograma_set.all()
                else:
                    lista = programa.estructuraprograma_set.all().filter(valor_elemento="Process", descripcion__icontains=data["query"])
                context = {"data":lista, "programa":programa, "edit": edit, "delete":delete, "query":data["query"]}
                html_template = (loader.get_template('academic/contenidoProcesos.html'))
                return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getContentUnidades(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            if request.body:
                data = json.load(request)    
                edit=True
                delete=True
                programa=Estructuraprograma.objects.get(valor_elemento="Program", url=data["url"])
                proceso=Estructuraprograma.objects.get(valor_elemento="Process", url=data["urlProceso"])
                if data["query"] == "" or data["query"] == None:
                    lista = proceso.estructuraprograma_set.all()
                else:
                    lista = proceso.estructuraprograma_set.all().filter(valor_elemento="Unit", descripcion__icontains=data["query"])
                context = {"data":lista, "programa":programa, "proceso":proceso ,"edit": edit, "delete":delete, "query":data["query"]}
                html_template = (loader.get_template('academic/contenidoUnidades.html'))
                return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getContentCursos(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            if request.body:
                data = json.load(request)    
                edit=True
                delete=True
                programa=Estructuraprograma.objects.get(valor_elemento="Program", url=data["url"])
                proceso=Estructuraprograma.objects.get(valor_elemento="Process", url=data["urlProceso"])
                unidad=Estructuraprograma.objects.get(valor_elemento="Unit", url=data["urlUnidad"])
                if data["query"] == "" or data["query"] == None:
                    lista = unidad.estructuraprograma_set.all()
                else:
                    lista = unidad.estructuraprograma_set.all().filter(valor_elemento="Course", descripcion__icontains=data["query"])
                context = {"data":lista, "programa":programa, "proceso":proceso, "unidad":unidad ,"edit": edit, "delete":delete, "query":data["query"]}
                html_template = (loader.get_template('academic/contenidoCursos.html'))
                return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getContentTopicos(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            if request.body:
                data = json.load(request)    
                take=True
                go=True
                see=True
                edit=True
                add=True
                delete=True
                programa=Estructuraprograma.objects.get(valor_elemento="Program", url=data["url"])
                proceso=Estructuraprograma.objects.get(valor_elemento="Process", url=data["urlProceso"])
                unidad=Estructuraprograma.objects.get(valor_elemento="Unit", url=data["urlUnidad"])
                curso=Estructuraprograma.objects.get(valor_elemento="Course", url=data["urlCurso"])
                if data["query"] == "" or data["query"] == None:
                    lista = curso.estructuraprograma_set.all()
                else:
                    lista = curso.estructuraprograma_set.all().filter(valor_elemento="Topic", descripcion__icontains=data["query"])
                context = {"data":lista, "programa":programa, "proceso":proceso, "unidad":unidad, "curso":curso ,"add":add,"edit": edit,"take": take,"see": see, "delete":delete, "go":go, "query":data["query"]}
                html_template = (loader.get_template('academic/contenidoTopicos.html'))
                return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getContentLecciones(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            if request.body:
                data = json.load(request)    
                take=True
                go=True
                see=True
                edit=True
                add=True
                delete=True
                leccionId = data["id"]
                leccion = ActividadLeccion.objects.get(pk=leccionId)
                actividad = leccion.fk_estructura_programa
                if data["query"] == "" or data["query"] == None:
                    lista = actividad.paginas_set.all().order_by("ordenamiento")
                else:
                    lista = actividad.paginas_set.all().filter(titulo__icontains=data["query"]).order_by("ordenamiento")
                context = {"data":lista, "lesson":leccion ,"add":add,"edit": edit,"take": take,"see": see, "delete":delete, "go":go, "query":data["query"]}
                html_template = (loader.get_template('academic/contenidoLecciones.html'))
                return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getModalCategorias(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            try:
                if request.body:
                    data = json.load(request)
                    config = TablasConfiguracion.objects.filter(valor_elemento="CatPrograma")
                    padre = list(config.values())[0]
                    if data["method"] == "Delete":
                        category = TablasConfiguracion.objects.get(id_tabla=data["id"])
                        category.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        category = TablasConfiguracion.objects.get(id_tabla=data["id"])
                    elif data["method"] == "Create":
                        category = TablasConfiguracion()
                        category.tipo_elemento=0 
                        category.permite_cambios=1
                        category.valor_elemento=None
                        category.mostrar_en_combos=1
                        category.maneja_lista=0
                        category.fk_tabla_padre_id=padre["id_tabla"]
                    category.desc_elemento = data["data"]["descriptionCat"]
                    category.save()
                    return JsonResponse({"message":"Perfect"})
                else:
                    html_template = (loader.get_template('components/modalAddCategoria.html'))
                    return HttpResponse(html_template.render(context, request))
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalProgramas(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Find":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])    
                        categorias = TablasConfiguracion.obtenerHijos(valor="CatPrograma")
                        context = {"categorias": categorias, "modelo": modelo}
                        html_template = (loader.get_template('components/modalAddPrograma.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        programa = Estructuraprograma.objects.get(pk=data["id"])
                        programa.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        programa = Estructuraprograma.objects.get(pk=data["id"])
                    elif data["method"] == "Create":
                        programa = Estructuraprograma()
                        programa.valor_elemento = "Program"
                        programa.fk_estructura_padre_id=None
                    programa.descripcion = data["data"]["descriptionProgram"]
                    programa.resumen = data["data"]["resumenProgram"]
                    programa.url = data["data"]["urlProgram"]
                    programa.fk_categoria_id = data["data"]["categoryProgram"]
                    programa.peso_creditos = data["data"]["creditos"]
                    programa.save()
                    return JsonResponse({"message":"Perfect"})
                else:
                    categorias = TablasConfiguracion.obtenerHijos(valor="CatPrograma")
                    context = {"categorias": categorias, "modelo": modelo}
                    html_template = (loader.get_template('components/modalAddPrograma.html'))
                    return HttpResponse(html_template.render(context, request))
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalProcesos(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Find":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])    
                        programs = Estructuraprograma.objects.filter(valor_elemento="Program")
                        context = {"programs": programs, "modelo": modelo}
                        html_template = (loader.get_template('components/modalAddProceso.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        proceso = Estructuraprograma.objects.get(pk=data["id"])
                        proceso.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        proceso = Estructuraprograma.objects.get(pk=data["id"])
                    elif data["method"] == "Create":
                        proceso = Estructuraprograma()
                        proceso.valor_elemento = "Process"
                    proceso.fk_estructura_padre_id=data["data"]["padreProcess"]
                    proceso.descripcion = data["data"]["descriptionProcess"]
                    proceso.resumen = data["data"]["resumenProcess"]
                    proceso.url = data["data"]["urlProcess"]
                    proceso.fk_categoria_id = Estructuraprograma.objects.get(pk=data["data"]["padreProcess"]).fk_categoria_id
                    proceso.peso_creditos = data["data"]["creditos"]
                    proceso.save()
                    return JsonResponse({"message":"Perfect"})
                else:
                    programs = Estructuraprograma.objects.filter(valor_elemento="Program")
                    context = {"programs": programs, "modelo": modelo}
                    html_template = (loader.get_template('components/modalAddProceso.html'))
                    return HttpResponse(html_template.render(context, request))
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalUnidades(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Find":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])
                        modeloPadre = Estructuraprograma.objects.get(pk=modelo.fk_estructura_padre_id)
                        programs = Estructuraprograma.objects.filter(valor_elemento="Program")
                        processes = Estructuraprograma.objects.filter(valor_elemento="Process")
                        context = {"programs": programs, "processes":processes, "modelo": modelo, "modeloPadre": modeloPadre}
                        html_template = (loader.get_template('components/modalAddUnidad.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        unidad = Estructuraprograma.objects.get(pk=data["id"])
                        unidad.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        unidad = Estructuraprograma.objects.get(pk=data["id"])
                    elif data["method"] == "Create":
                        unidad = Estructuraprograma()
                        unidad.valor_elemento = "Unit"
                    unidad.fk_estructura_padre_id=data["data"]["padreUnit"]
                    unidad.descripcion = data["data"]["descriptionUnit"]
                    unidad.resumen = data["data"]["resumenUnit"]
                    unidad.url = data["data"]["urlUnit"]
                    unidad.fk_categoria_id = Estructuraprograma.objects.get(pk=data["data"]["padreUnit"]).fk_categoria_id
                    unidad.peso_creditos = data["data"]["creditos"]
                    unidad.save()
                    return JsonResponse({"message":"Perfect"})
                else:
                    programs = Estructuraprograma.objects.filter(valor_elemento="Program")
                    processes = Estructuraprograma.objects.filter(valor_elemento="Process")
                    context = {"programs": programs, "processes":processes, "modelo": modelo}
                    html_template = (loader.get_template('components/modalAddUnidad.html'))
                    return HttpResponse(html_template.render(context, request))
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalCursos(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Show":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])
                        units = Estructuraprograma.objects.filter(valor_elemento="Unit",fk_estructura_padre_id=modelo.fk_estructura_padre_id)
                        tipoDuracion = TablasConfiguracion.obtenerHijos(valor="Duracion")
                        status = TablasConfiguracion.obtenerHijos(valor="EstCurso")
                        
                        context = {"units":units,"tipoDuracion":tipoDuracion, "status":status}
                        html_template = (loader.get_template('components/modalAddCurso.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Find":
                        modeloCurso = Cursos.objects.get(fk_estruc_programa=data["id"])
                        modelo = Estructuraprograma.objects.get(pk=data["id"])
                        modeloPadre = Estructuraprograma.objects.get(pk=modelo.fk_estructura_padre_id)
                        units = Estructuraprograma.objects.filter(valor_elemento="Unit",fk_estructura_padre=modeloPadre.fk_estructura_padre)
                        tipoDuracion = TablasConfiguracion.obtenerHijos(valor="Duracion")
                        status = TablasConfiguracion.obtenerHijos(valor="EstCurso")
                        context = {"units":units, "modeloCurso":modeloCurso, "modelo": modelo, "tipoDuracion":tipoDuracion, "status":status}
                        html_template = (loader.get_template('components/modalAddCurso.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        curso = Estructuraprograma.objects.get(pk=data["id"])
                        curso.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        curso = Estructuraprograma.objects.get(pk=data["id"])
                        curso_char = curso.cursos
                    elif data["method"] == "Create":
                        curso = Estructuraprograma()
                        curso_char = Cursos()
                        curso.valor_elemento = "Course"
                    curso.fk_estructura_padre_id=data["data"]["padreCourse"]
                    curso.descripcion = data["data"]["titleCourse"]
                    curso.resumen = data["data"]["resumenCourse"]
                    curso.url = data["data"]["urlCourse"]
                    curso.fk_categoria_id = Estructuraprograma.objects.get(pk=data["data"]["padreCourse"]).fk_categoria_id
                    curso.peso_creditos = data["data"]["creditos"]
                    curso_char.abrev_curso = data["data"]["urlCourse"]
                    curso_char.codigo_curso = data["data"]["codeCourse"]
                    curso_char.disponible_desde = data["data"]["disponibleCourse"]
                    curso_char.fk_estatus_curso_id = data["data"]["statusCourse"]
                    curso_char.tipo_evaluacion = False
                    if "checkExpertCB" in data["data"]:
                        curso_char.tipo_evaluacion = True
                    if "durationCourse" in data["data"]:
                        curso_char.duracion = data["data"]["durationCourse"]
                    else:
                        curso_char.duracion = None
                    if "timeCourse" in data["data"]:
                        curso_char.fk_tipo_duracion_id = data["data"]["timeCourse"]
                    else:
                        curso_char.fk_tipo_duracion_id = None
                    curso.save()
                    curso_char.fk_estruc_programa = curso
                    curso_char.save()
                    return JsonResponse({"message":"Perfect"})
                # else:
                
            except:
                return JsonResponse({"message":"error"}, status=500)


@login_required(login_url="/login/")
def getModalTopico(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Show":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])
                        courses = Estructuraprograma.objects.filter(valor_elemento="Course",fk_estructura_padre_id=modelo.fk_estructura_padre_id)
                        context = {"courses":courses}
                        html_template = (loader.get_template('components/modalAddTopico.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Find":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])
                        modeloPadre = Estructuraprograma.objects.get(pk=modelo.fk_estructura_padre_id)
                        courses = Estructuraprograma.objects.filter(valor_elemento="Course",fk_estructura_padre=modeloPadre.fk_estructura_padre)
                        context = {"courses": courses, "modelo": modelo}
                        html_template = (loader.get_template('components/modalAddTopico.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        topico = Estructuraprograma.objects.get(pk=data["id"])
                        topico.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        topico = Estructuraprograma.objects.get(pk=data["id"])
                    elif data["method"] == "Create":
                        topico = Estructuraprograma()
                        topico.valor_elemento = "Topic"
                    topico.fk_estructura_padre_id=data["data"]["padreTopic"]
                    topico.descripcion = data["data"]["descriptionTopic"]
                    topico.resumen = data["data"]["resumenTopic"]
                    topico.url = data["data"]["urlTopic"]
                    topico.fk_categoria_id = Estructuraprograma.objects.get(pk=data["data"]["padreTopic"]).fk_categoria_id
                    topico.peso_creditos = None
                    topico.save()
                    return JsonResponse({"message":"Perfect"})
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalActividad(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Show":
                        html_template = (loader.get_template('components/modalAddActividad.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Find":
                        modelo = Estructuraprograma.objects.get(pk=data["id"])
                        context = {"modelo": modelo}
                        html_template = (loader.get_template('components/modalAddActividad.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        actividad = Estructuraprograma.objects.get(pk=data["id"])
                        actividad.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        actividad = Estructuraprograma.objects.get(pk=data["id"])
                    elif data["method"] == "Create":
                        actividad = Estructuraprograma()
                        actividad.valor_elemento = "Activity"
                    actividad.fk_estructura_padre_id=data["padreActivity"]
                    actividad.descripcion = data["data"]["descriptionActivity"]
                    actividad.resumen = data["data"]["resumenActivity"]
                    actividad.url = data["data"]["urlActivity"]
                    actividad.fk_categoria_id = TablasConfiguracion.obtenerHijos(valor="Tipo Actividad").filter(desc_elemento=data["tipoActividad"])[0].pk
                    actividad.peso_creditos = None
                    actividad.save()
                    return JsonResponse({"message":"Perfect"})
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalPagina(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Show":
                        html_template = (loader.get_template('components/modalAddPagina.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Find":
                        modelo = Paginas.objects.get(pk=data["id"])
                        context = {"modelo": modelo}
                        html_template = (loader.get_template('components/modalAddPagina.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        pagina = Paginas.objects.get(pk=data["id"])
                        pagina.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        pagina = Paginas.objects.get(pk=data["id"])
                    elif data["method"] == "Create":
                        pagina = Paginas()
                    pagina.titulo = data["data"]["titlePage"]
                    if data["data"]["summernote"] != "<p><br></p>":
                        pagina.contenido = data["data"]["summernote"]
                    pagina.save()
                    return JsonResponse({"message":"Perfect"})
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getPreviewLeccion(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Find":
                        modelo = Paginas.objects.get(pk=data["id"])
                        context = {"modelo":modelo.contenido}
                        html_template = (loader.get_template('academic/previewLeccion.html'))
                        return HttpResponse(html_template.render(context, request))
                    return JsonResponse({"message":"Perfect"})
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalResourcesBank(request):
    context = {}
    html_template = (loader.get_template('components/modalBancoRecursos.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getModalChooseActivities(request):
    context = {}
    html_template = (loader.get_template('components/modalEscogerActividad.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getModalChooseTypeQuestion(request):
    context = {}
    html_template = (loader.get_template('components/modalTypeQuestion.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getModalAddBlock(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
            
                context = {}
                data = json.load(request)["data"]

                if "delete" in data:
                    bloque=EvaluacionesBloques.objects.get(pk=data["id"])
                    actividad = bloque.fk_actividad_evaluaciones

                    bloque.delete()
                     #update order
                    bloques = actividad.bloque_actividad.order_by('orden')
                    for idx, value in enumerate(bloques, start=1):
                        value.orden = idx
                        value.save()
                    return JsonResponse({"message": "Deleted"})
                if "idFind" in data:
                    
                    bloque=EvaluacionesBloques.objects.filter(pk=data["idFind"])
                    findBloque = list(bloque.values())
                    
                    return JsonResponse({"data":findBloque[0]}, safe=False)
                
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddBlock.html'))
                        return HttpResponse(html_template.render(context, request))

                if data["method"] == "Update":
                    bloque=EvaluacionesBloques.objects.get(pk=int(data["idViejo"]))
                    
                    bloque.comentario=data['textoBloque']
                    bloque.titulo_bloque=data['tituloBloque']
                    bloque.save()



                if data["method"] == "Create":
                    actividad=ActividadEvaluaciones.objects.annotate(num_child=Count('bloque_actividad', distinct=True) ).get(pk=data['ActivityId'])
                    actividad.pointUse=actividad.pointUse+actividad.fk_escala_bloquemaxima_puntuacion
                    actividad.save()
                    bloque=EvaluacionesBloques.objects.create()

                    newOrden=actividad.num_child+1
                    bloque.orden=newOrden
                    print('aquitoy')

                    bloque.fk_actividad_evaluaciones=actividad
                    bloque.comentario=data['textoBloque']
                    bloque.titulo_bloque=data['tituloBloque']
                    print('eeeee')

                    bloque.save()


             
                return JsonResponse({"message": "Perfect"})     
            except:
                return JsonResponse({"message": "Error"}) 
           
    context = {}
    html_template = (loader.get_template('components/modalAddBlock.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getModalNewTest(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                        data = json.load(request)
                        tipoDuracion = TablasConfiguracion.obtenerHijos(valor="Duracion")
                        escalas = EscalaEvaluacion.objects.all()
                        if data["method"] == "Show":
                            context = {"escalas":escalas, "tipoDuracion":tipoDuracion}
                            html_template = (loader.get_template('components/modalAddTest.html'))
                            return HttpResponse(html_template.render(context, request))
                        elif data["method"] == "Find":
                            modelo = ActividadEvaluaciones.objects.get(fk_estructura_programa=data["id"])
                            context = {"modelo": modelo, "escalas":escalas, "tipoDuracion":tipoDuracion}
                            html_template = (loader.get_template('components/modalAddTest.html'))
                            return HttpResponse(html_template.render(context, request))
                        elif data["method"] == "Delete":
                            actividad = Estructuraprograma.objects.get(pk=data["id"])
                            actividad.delete()
                            return JsonResponse({"message":"Deleted"})
                        elif data["method"] == "Update":
                            actividad = Estructuraprograma.objects.get(pk=data["id"])
                            test = ActividadEvaluaciones.objects.get(fk_estructura_programa=data["id"])
                        elif data["method"] == "Create":
                            actividad = Estructuraprograma()
                            test = ActividadEvaluaciones()
                            actividad.valor_elemento = "Activity"
                            actividad.pointUsed = 0
                            actividad.fk_estructura_padre_id=data["padreActivity"]
                        
                        actividad.descripcion = data["data"]["descriptionActivity"]
                        actividad.resumen = data["data"]["resumenActivity"]
                        actividad.url = data["data"]["urlActivity"]
                        actividad.peso_creditos = None
                        actividad.fk_categoria_id = TablasConfiguracion.obtenerHijos(valor="Tipo Actividad").get(desc_elemento="Test").pk
                        if "checkExpertCB" in data["data"]:
                            actividad.fk_categoria_id = TablasConfiguracion.obtenerHijos(valor="Tipo Actividad").get(desc_elemento="Expert test").pk
                            scale=EscalaEvaluacion.objects.get(pk=int(data["data"]["Blockqualification"]))
                            test.fk_escala_bloque = scale
                        else:   
                            test.nro_repeticiones = data["data"]["repeats"]
                            test.calificacion_aprobar = data["data"]["minApp"]

                        if "durationActivity" in data["data"]:
                            test.duracion = data["data"]["durationActivity"]
                        else:
                            test.duracion = None
                        if "timeActivity" in data["data"]:
                            test.fk_tipo_duracion_id = data["data"]["timeActivity"]
                        else:
                            test.fk_tipo_duracion_id = None
                    
                        test.fk_escala_evaluacion_id = data["data"]["qualification"]
                        actividad.save()
                        test.fk_estructura_programa = actividad
                        test.save()
                        if data["method"] == "Create":
                            if not "checkExpertCB" in data["data"]:
                                bloque=EvaluacionesBloques.objects.create()
                                bloque.titulo_bloque=actividad.descripcion
                                #bloque.titulo_bloque='Test'
                                
                                bloque.orden=1
                                bloque.comentario=''
                                bloque.fk_actividad_evaluaciones=test
                                bloque.fk_escala_bloque=None   
                                bloque.save()
                        return JsonResponse({"message":"Perfect"})
            except:
                 return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalNewLesson(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    status = TablasConfiguracion.obtenerHijos(valor="EstLeccion")
                    if data["method"] == "Show":
                        context = {"status":status}
                        html_template = (loader.get_template('components/modalAddLesson.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Find":
                        modelo = ActividadLeccion.objects.get(fk_estructura_programa=data["id"])
                        context = {"modelo": modelo, "status":status}
                        html_template = (loader.get_template('components/modalAddLesson.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        actividad = Estructuraprograma.objects.get(pk=data["id"])
                        actividad.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        actividad = Estructuraprograma.objects.get(pk=data["id"])
                        lesson = ActividadLeccion.objects.get(fk_estructura_programa=data["id"])
                    elif data["method"] == "Create":
                        actividad = Estructuraprograma()
                        lesson = ActividadLeccion()
                        actividad.valor_elemento = "Activity"
                        actividad.fk_estructura_padre_id=data["padreActivity"]
                    actividad.descripcion = data["data"]["descriptionActivity"]
                    actividad.resumen = data["data"]["resumenActivity"]
                    actividad.url = data["data"]["urlActivity"]
                    actividad.peso_creditos = None
                    actividad.fk_categoria_id = TablasConfiguracion.obtenerHijos(valor="Tipo Actividad").get(desc_elemento="Lesson").pk
                    lesson.disponible_desde = data["data"]["disponibleLesson"]
                    lesson.estatus_id = data["data"]["estatusLesson"]
                    actividad.save()
                    lesson.fk_estructura_programa = actividad
                    lesson.save()
                    return JsonResponse({"message":"Perfect"})
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalNewHomework(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            try:
                if request.body:
                    data = json.load(request)
                    if data["method"] == "Show":
                        html_template = (loader.get_template('components/modalAddHomework.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Find":
                        modelo = ActividadTarea.objects.get(fk_estructura_programa=data["id"])
                        context = {"modelo": modelo}
                        html_template = (loader.get_template('components/modalAddHomework.html'))
                        return HttpResponse(html_template.render(context, request))
                    elif data["method"] == "Delete":
                        actividad = Estructuraprograma.objects.get(pk=data["id"])
                        actividad.delete()
                        return JsonResponse({"message":"Deleted"})
                    elif data["method"] == "Update":
                        actividad = Estructuraprograma.objects.get(pk=data["id"])
                        homework = ActividadTarea.objects.get(fk_estructura_programa=data["id"])
                    elif data["method"] == "Create":
                        actividad = Estructuraprograma()
                        homework = ActividadTarea()
                        actividad.valor_elemento = "Activity"
                        actividad.fk_categoria_id = TablasConfiguracion.obtenerHijos(valor="Tipo Actividad").get(desc_elemento="Homework").pk
                        actividad.fk_estructura_padre_id=data["padreActivity"]
                    actividad.descripcion = data["data"]["descriptionActivity"]
                    actividad.resumen = data["data"]["resumenActivity"]
                    actividad.url = data["data"]["urlActivity"]
                    actividad.peso_creditos = None
                    actividad.save()
                    homework.fk_estructura_programa = actividad
                    homework.fecha_entrega = data["data"]["entregaHomework"]
                    homework.save()
                    return JsonResponse({"message":"Perfect"})
            except:
                return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalNewForum(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            modelo = {}
            # try:
            if request.body:
                data = json.load(request)
                if data["method"] == "Show":
                    html_template = (loader.get_template('components/modalAddForum.html'))
                    return HttpResponse(html_template.render(context, request))
                elif data["method"] == "Find":
                    modelo = ActividadConferencia.objects.get(fk_estructura_programa=data["id"])
                    context = {"modelo": modelo}
                    html_template = (loader.get_template('components/modalAddForum.html'))
                    return HttpResponse(html_template.render(context, request))
                elif data["method"] == "Delete":
                    actividad = Estructuraprograma.objects.get(pk=data["id"])
                    actividad.delete()
                    return JsonResponse({"message":"Deleted"})
                elif data["method"] == "Update":
                    actividad = Estructuraprograma.objects.get(pk=data["id"])
                    forum = ActividadConferencia.objects.get(fk_estructura_programa=data["id"])
                elif data["method"] == "Create":
                    actividad = Estructuraprograma()
                    forum = ActividadConferencia()
                    actividad.valor_elemento = "Activity"
                    actividad.fk_categoria_id = TablasConfiguracion.obtenerHijos(valor="Tipo Actividad").get(desc_elemento="Forum").pk
                    actividad.fk_estructura_padre_id=data["padreActivity"]
                actividad.descripcion = data["data"]["descriptionActivity"]
                actividad.resumen = data["data"]["resumenActivity"]
                actividad.url = data["data"]["urlActivity"]
                actividad.peso_creditos = None
                forum.fecha_hora = data["data"]["datetimeForum"]
                forum.enlace = data["data"]["linkForum"]
                forum.id_conferencia = data["data"]["idForum"]
                forum.clave = data["data"]["keyForum"]
                # forum.fk_publico
                actividad.save()
                forum.fk_estructura_programa = actividad
                forum.save()
                return JsonResponse({"message":"Perfect"})
            # except:
            #     return JsonResponse({"message":"error"}, status=500)

@login_required(login_url="/login/")
def getModalQuestion(request): 
    context = {
        "tipoPreguntas" : TablasConfiguracion.obtenerHijos('PregEvalua'),
    }
    html_template = (loader.get_template('components/modalAddQuestion.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def getModalNewSimple(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            
                context = {}
                data = json.load(request)["data"]

                if "delete" in data:
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["id"])
                    pregunta.delete()
                    return JsonResponse({"message": "Deleted"})
                if "idFind" in data:
                    print(data)
                    pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                    findpregunta = list(pregunta.values())
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                    listaChilds = list(childs.values())
                    return JsonResponse({"data":findpregunta[0], "childs":listaChilds}, safe=False)
                
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddSimple.html'))
                        return HttpResponse(html_template.render(context, request))

                if data["method"] == "Update":
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                  
                    pregunta.orden=pregunta.orden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']


                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)-float(pregunta.puntos_pregunta)+float(data['puntosPregunta'])
                    actividad.pointUse=float(actividad.pointUse)+float(bloque.pointUse)
                    bloque.save()
                    actividad.save()


                    pregunta.puntos_pregunta=data['puntosPregunta']

                    
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Simple')
                    pregunta.save()
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idViejo"])
                    
                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 
                                 childs.delete()
                            selectetedOp=int(data['select2'])     
                            for newOpcion in hijos:
                                
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']   
                                 Opcion.idLista=newOpcion['id']    
                                 Opcion.respuetaCorrecta=True if newOpcion['id']==selectetedOp else False
                                 Opcion.save()

                if data["method"] == "Create":
                    pregunta=EvaluacionesPreguntas.objects.create()

                    print(data)
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                    newOrden=bloque.num_child+1
                    pregunta.orden=newOrden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']


                    pregunta.puntos_pregunta=data['puntosPregunta']
                   
                    bloque.pointUse=float(bloque.pointUse)+float(pregunta.puntos_pregunta)
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(bloque.pointUse)+float(actividad.pointUse)
                    bloque.save()
                    actividad.save()


                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Simple')
                    pregunta.save()

                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                        
                                 childs.delete()
                            selectetedOp=int(data['select2'])     
                            for newOpcion in hijos:
                                
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']   
                                 Opcion.idLista=newOpcion['id']    
                                 Opcion.respuetaCorrecta=True if newOpcion['id']==selectetedOp else False
                                 Opcion.save()

             
                return JsonResponse({"message": "Perfect"})     
            
           
   
    context = {}
    html_template = (loader.get_template('components/modalAddSimple.html'))
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def getModalNewExpert(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
         
                context = {}
                data = json.load(request)["data"]

                if "delete" in data:
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["id"])
                    pregunta.delete()
                    return JsonResponse({"message": "Deleted"})
                if "idFind" in data:
                    
                    pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                    findpregunta = list(pregunta.values())
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                    listaChilds = list(childs.values())
                    return JsonResponse({"data":findpregunta[0], "childs":listaChilds}, safe=False)
                
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddQuestionExpert.html'))
                        return HttpResponse(html_template.render(context, request))

                if data["method"] == "Update":
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                  
                    pregunta.orden=pregunta.orden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    
                    bloque.pointUse=float(bloque.pointUse)-float(pregunta.puntos_pregunta)+float(data['puntosPregunta'])
                    
                    bloque.save()
                   


                    pregunta.puntos_pregunta=data['puntosPregunta']
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Expert')
                    pregunta.save()
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idViejo"])
                    
                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 
                                 childs.delete()
            
                            for newOpcion in hijos:
                                
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']   
                                 Opcion.idLista=newOpcion['id']    
                                 Opcion.puntos_porc=float(newOpcion['value'])  

                                 Opcion.save()
             
                
                if data["method"] == "Create":
                 
                    pregunta=EvaluacionesPreguntas.objects.create()
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
            
                    
                    newOrden=bloque.num_child+1
                    pregunta.orden=newOrden
                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']

                    pregunta.puntos_pregunta=data['puntosPregunta']
                    bloque.pointUse=float(bloque.pointUse)+float(pregunta.puntos_pregunta)
                    
                    bloque.save()
                   
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Expert')
                    pregunta.save()

                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 childs =None
                                 childs.delete()
                         
                            for newOpcion in hijos:
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.idLista=newOpcion['id']    

                                 Opcion.texto_opcion=newOpcion['OpcionText']    
                                 Opcion.puntos_porc=float(newOpcion['value'])  
                                 Opcion.save()

             
                return JsonResponse({"message": "Perfect"})     
           
           
   
    context = {}
    html_template = (loader.get_template('components/modalAddSimple.html'))
    return HttpResponse(html_template.render(context, request))    
    
@login_required(login_url="/login/")
def getModalNewMultiple(request):

    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                context = {}
                data = json.load(request)["data"]
                if "delete" in data:
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["id"])
                    pregunta.delete()
                    return JsonResponse({"message": "Deleted"})
                
               
                if "idFind" in data:
                    print(data)
                    pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                    findpregunta = list(pregunta.values())
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                    listaChilds = list(childs.values())
                    return JsonResponse({"data":findpregunta[0], "childs":listaChilds}, safe=False)
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddMultiple.html'))
                        return HttpResponse(html_template.render(context, request))
                if data["method"] == "Update":
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                  
                    pregunta.orden=pregunta.orden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)-float(pregunta.puntos_pregunta)+float(data['puntosPregunta'])
                    actividad.pointUse=float(actividad.pointUse)+float(bloque.pointUse)
                    bloque.save()
                    actividad.save()


                    pregunta.puntos_pregunta=data['puntosPregunta']
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Multiple')
                    pregunta.save()
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idViejo"])
                    
                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 
                                 childs.delete()
            
                            for newOpcion in hijos:
                                
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']   
                                 Opcion.idLista=newOpcion['id']    
                                 Opcion.puntos_porc=float(newOpcion['value'])  

                                 Opcion.save()
                
                if data["method"] == "Create":
                    pregunta=EvaluacionesPreguntas.objects.create()
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                    newOrden=bloque.num_child+1
                    pregunta.orden=newOrden
                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']

                    pregunta.puntos_pregunta=data['puntosPregunta']
                    bloque.pointUse=float(bloque.pointUse)+float(pregunta.puntos_pregunta)
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(bloque.pointUse)+float(actividad.pointUse)
                    bloque.save()
                    actividad.save()
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Multiple')
                    pregunta.save()

                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 childs =None
                                 childs.delete()
                         
                            for newOpcion in hijos:
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.idLista=newOpcion['id']    

                                 Opcion.texto_opcion=newOpcion['OpcionText']    
                                 Opcion.puntos_porc=float(newOpcion['value'])  
                                 Opcion.save()

             
                return JsonResponse({"message": "Perfect"})      
            except:
                return JsonResponse({"message": "Error"})
   
    context ={}
    html_template = (loader.get_template('components/modalAddMultiple.html'))
    return HttpResponse(html_template.render(context, request))
    
@login_required(login_url="/login/")
def getModalNewCompletion(request):

     if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                context = {}
                data = json.load(request)["data"]
                print(data)
                if "delete" in data:
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["id"])
                    pregunta.delete()
                    return JsonResponse({"message": "Deleted"})
                
               
                if "idFind" in data:
                    print(data)
                    pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                    findpregunta = list(pregunta.values())
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                    listaChilds = list(childs.values())
                    return JsonResponse({"data":findpregunta[0], "childs":listaChilds}, safe=False)
                
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddCompletion.html'))
                        return HttpResponse(html_template.render(context, request))
                if data["method"] == "Update":
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                  
                    pregunta.orden=pregunta.orden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    pregunta.indicePalabra=data['indiceRespuesta']
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)-float(pregunta.puntos_pregunta)+float(data['puntosPregunta'])
                    actividad.pointUse=float(actividad.pointUse)+float(bloque.pointUse)
                    bloque.save()
                    actividad.save()
                    pregunta.puntos_pregunta=data['puntosPregunta']
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Completation')
                    pregunta.save()
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idViejo"])
                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 
                                 childs.delete()
            
                            for newOpcion in hijos:
                                
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']   
                                 Opcion.idLista=newOpcion['id']    

                                 Opcion.respuetaCorrecta=int(newOpcion['isCorrect']) 

                                 Opcion.save()
                
                if data["method"] == "Create":
                    pregunta=EvaluacionesPreguntas.objects.create()
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                    newOrden=bloque.num_child+1
                    pregunta.orden=newOrden
                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.puntos_pregunta=data['puntosPregunta']
                    bloque.pointUse=float(bloque.pointUse)+float(pregunta.puntos_pregunta)
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(bloque.pointUse)+float(actividad.pointUse)
                    bloque.save()
                    actividad.save()
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    pregunta.indicePalabra=data['indiceRespuesta']
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Completation')
                    pregunta.save()

                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                        
                         
                            for newOpcion in hijos:
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']   
                                 Opcion.idLista=newOpcion['id']    

                                 Opcion.respuetaCorrecta=int(newOpcion['isCorrect'])  

                                 Opcion.save()

             
                return JsonResponse({"message": "Perfect"})      
            except:
                return JsonResponse({"message": "Error"})
   
        context = {}
        html_template = (loader.get_template('components/modalAddCompletion.html'))
        return HttpResponse(html_template.render(context, request))
    
@login_required(login_url="/login/")
def getModalNewAssociation(request):
    
     if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                context = {}
                data = json.load(request)["data"]
                print(data)
                if "delete" in data:
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["id"])
                    pregunta.delete()
                    return JsonResponse({"message": "Deleted"})
                
               
                if "idFind" in data:
                    print(data)
                    pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                    findpregunta = list(pregunta.values())
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                    childsA = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"] ).filter(columnaPregunta=1)
                    childsB = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"]).filter(columnaPregunta=2)

                    listaChilds = list(childs.values())
                    listaChildsA = list(childsA.values())
                    listaChildsB = list(childsB.values())

                    return JsonResponse({"data":findpregunta[0], "childs":listaChilds, "childsA":listaChildsA, "childsB":listaChildsB}, safe=False)
                
                
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddAssociation.html'))
                        return HttpResponse(html_template.render(context, request))
                if data["method"] == "Update":
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                  
                    pregunta.orden=pregunta.orden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)-float(pregunta.puntos_pregunta)+float(data['puntosPregunta'])
                    actividad.pointUse=float(actividad.pointUse)+float(bloque.pointUse)
                    bloque.save()
                    actividad.save()
                    
                    pregunta.puntos_pregunta=data['puntosPregunta']
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Association')
                    pregunta.save()
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idViejo"])
                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 
                                 childs.delete()
            
                            for newOpcion in hijos:
                                 OpcionA=PreguntasOpciones()
                                 OpcionA.fk_evaluacion_pregunta=pregunta
                                 OpcionA.texto_opcion=newOpcion['OpcionTextA']    
                                 OpcionA.indiceAsociacion=int(newOpcion['id'])  
                                 OpcionA.puntos_porc=float(newOpcion['value'])  
                                    

                                 OpcionA.columnaPregunta=1


                                 OpcionB=PreguntasOpciones()
                                 OpcionB.fk_evaluacion_pregunta=pregunta
                                 OpcionB.texto_opcion=newOpcion['OpcionTextB']    
                                 OpcionB.indiceAsociacion=int(newOpcion['id'])  
                                 OpcionB.puntos_porc=float(newOpcion['value'])  
                                 OpcionB.columnaPregunta=2


                                 OpcionA.save()
                                 OpcionB.save()
                
                if data["method"] == "Create":
                    pregunta=EvaluacionesPreguntas.objects.create()
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                    newOrden=bloque.num_child+1
                    pregunta.orden=newOrden
                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.puntos_pregunta=data['puntosPregunta']
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)+float(pregunta.puntos_pregunta)
                    actividad.pointUse=float(bloque.pointUse)+float(actividad.pointUse)
                    bloque.save()
                    actividad.save()
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    


                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('Association')
                    pregunta.save()

                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                         
                            for newOpcion in hijos:
                                 OpcionA=PreguntasOpciones()
                                 OpcionA.fk_evaluacion_pregunta=pregunta
                                 OpcionA.texto_opcion=newOpcion['OpcionTextA']    
                                 OpcionA.indiceAsociacion=int(newOpcion['id'])  
                                 OpcionA.puntos_porc=float(newOpcion['value'])  
                                    

                                 OpcionA.columnaPregunta=1


                                 OpcionB=PreguntasOpciones()
                                 OpcionB.fk_evaluacion_pregunta=pregunta
                                 OpcionB.texto_opcion=newOpcion['OpcionTextB']    
                                 OpcionB.indiceAsociacion=int(newOpcion['id'])  
                                 OpcionB.puntos_porc=float(newOpcion['value'])  
                                 OpcionB.columnaPregunta=2


                                 OpcionA.save()
                                 OpcionB.save()

             
                return JsonResponse({"message": "Perfect"})      
            except:
                return JsonResponse({"message": "Error"})
   
        context = {}
        html_template = (loader.get_template('components/modalAddAssociation.html'))
        return HttpResponse(html_template.render(context, request))
    
@login_required(login_url="/login/")
def getModalNewTof(request):
    
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                context = {}
                data = json.load(request)["data"]
                if "delete" in data:
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["id"])
                    pregunta.delete()
                    return JsonResponse({"message": "Deleted"})
                
               
                if "idFind" in data:
                    print(data)
                    pregunta=EvaluacionesPreguntas.objects.filter(pk=data["idFind"])
                    findpregunta = list(pregunta.values())
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idFind"])
                    listaChilds = list(childs.values())
                    return JsonResponse({"data":findpregunta[0], "childs":listaChilds}, safe=False)
                
                
                if data["method"] == "Show":
                        context = {}
                        html_template = (loader.get_template('components/modalAddTof.html'))
                        return HttpResponse(html_template.render(context, request))
                if data["method"] == "Update":
                    pregunta=EvaluacionesPreguntas.objects.get(pk=data["idViejo"])
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                  
                    pregunta.orden=pregunta.orden

                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.titulo_pregunta=data['tituloPregunta']
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)-float(pregunta.puntos_pregunta)+float(data['puntosPregunta'])
                    actividad.pointUse=float(actividad.pointUse)+float(bloque.pointUse)
                    bloque.save()
                    actividad.save()


                    pregunta.puntos_pregunta=data['puntosPregunta']
                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('True or False')
                    pregunta.save()
                    childs = PreguntasOpciones.objects.filter(fk_evaluacion_pregunta=data["idViejo"])
                    
                    hijos = data["hijos"]
                    if hijos:
                            print(hijos)
                        
                            if "idViejo" in data:
                                 
                                 childs.delete()
            
                            for newOpcion in hijos:
                                
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']    
                                 Opcion.puntos_porc=float(newOpcion['value'])  
                                 Opcion.respuetaCorrecta=int(newOpcion['trueFalse'])  
                                 Opcion.idLista=newOpcion['id']    


                                 Opcion.save()
                
                if data["method"] == "Create":
                    pregunta=EvaluacionesPreguntas.objects.create()
                    bloque=EvaluacionesBloques.objects.annotate(num_child=Count('bloque_pregunta', distinct=True) ).get(pk=data['fatherId'])
                    newOrden=bloque.num_child+1
                    pregunta.orden=newOrden
                    pregunta.fk_evaluaciones_bloque=bloque
                    pregunta.texto_pregunta=data['textoPregunta']
                    pregunta.puntos_pregunta=data['puntosPregunta']
                    actividad=ActividadEvaluaciones.objects.get(pk=bloque.fk_actividad_evaluaciones.pk)
                    actividad.pointUse=float(actividad.pointUse)-float(bloque.pointUse)
                    bloque.pointUse=float(bloque.pointUse)+float(pregunta.puntos_pregunta)
                    actividad.pointUse=float(bloque.pointUse)+float(actividad.pointUse)
                    bloque.save()
                    actividad.save()
                    pregunta.titulo_pregunta=data['tituloPregunta']

                    pregunta.fk_tipo_pregunta_evaluacion=Methods.OrigenPreguntaTipo('True or False')
                    pregunta.save()

                    hijos = data["hijos"]
                    if hijos:
                         
                            for newOpcion in hijos:
                                 Opcion=PreguntasOpciones()
                                 Opcion.fk_evaluacion_pregunta=pregunta
                                 Opcion.texto_opcion=newOpcion['OpcionText']    
                                 Opcion.puntos_porc=float(newOpcion['value'])  
                                 Opcion.respuetaCorrecta=int(newOpcion['trueFalse'])  
                                 Opcion.idLista=newOpcion['id']    

                                 Opcion.save()

             
                return JsonResponse({"message": "Perfect"})      
            except:
                return JsonResponse({"message": "Error"})
   
    context = {}
    html_template = (loader.get_template('components/modalAddTof.html'))
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def programa(request, programa):
    program = Estructuraprograma.objects.get(url=programa)
    context = {"programa" : program}
    context['segment'] = 'academic'
    #Vista del gestor
    html_template = (loader.get_template('academic/procesos.html'))
    #Vista del profesor
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def proceso(request, programa, proceso):
    program = Estructuraprograma.objects.get(url=programa)
    process = Estructuraprograma.objects.get(url=proceso)
    context = {"programa" : program, "proceso":process}
    #Vista del gestor

    html_template = (loader.get_template('academic/unidades.html'))
    #Vista del profesor
    return HttpResponse(html_template.render(context, request))
@login_required(login_url="/login/")
def unidad(request, programa, proceso, unidad):
    program = Estructuraprograma.objects.get(url=programa)
    process = Estructuraprograma.objects.get(url=proceso)
    unit = Estructuraprograma.objects.get(url=unidad)
    context = {"programa" : program, "proceso":process, "unidad":unit}
    #Vista del gestor

    html_template = (loader.get_template('academic/cursos.html'))
    #Vista del profesor
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def curso(request, programa, proceso, unidad, curso):
    program = Estructuraprograma.objects.get(url=programa)
    process = Estructuraprograma.objects.get(url=proceso)
    unit = Estructuraprograma.objects.get(url=unidad)
    course = Estructuraprograma.objects.get(url=curso)
    context = {"programa" : program, "proceso":process, "unidad":unit, "curso":course}
    #Vista del gestor
    html_template = (loader.get_template('academic/topicos.html'))
    #Vista del profesor
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def actividad(request):
    return

@login_required(login_url="/login/")
def getComboContent(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {}
            try:
                if request.body:
                    data=json.load(request)
                    if data["id"] == "null" or data["id"] == None:
                        hijos=None
                    else:
                        padre = Estructuraprograma.objects.get(pk=data["id"])
                        hijos = padre.estructuraprograma_set.all()
                    context = {"subEstructuraProg":hijos, "valor":data["valor"]}
                    html_template = (loader.get_template('registration/ComboOptions.html'))
                    return HttpResponse(html_template.render(context, request))
            except:
                return JsonResponse({"message":"error"}, status=500)
    
@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
