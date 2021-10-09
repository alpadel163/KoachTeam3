# Generated by Django 3.2.7 on 2021-09-17 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EscalaEvaluacion',
            fields=[
                ('idescala_evaluacion', models.SmallAutoField(primary_key=True, serialize=False)),
                ('desc_escala', models.TextField()),
                ('maxima_puntuacion', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='TipoRecursos',
            fields=[
                ('idtipo_recurso', models.SmallAutoField(primary_key=True, serialize=False)),
                ('ruta_icono', models.TextField()),
                ('desc_recurso', models.TextField()),
                ('tipo', models.CharField(blank=True, max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EscalaCalificacion',
            fields=[
                ('idescala_calificacion', models.SmallAutoField(primary_key=True, serialize=False)),
                ('desc_calificacion', models.TextField()),
                ('puntos_maximo', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('fk_calificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tablasconfiguracion')),
            ],
        ),
        migrations.CreateModel(
            name='Cursos',
            fields=[
                ('idcurso', models.SmallAutoField(primary_key=True, serialize=False)),
                ('desc_curso', models.TextField(db_collation='utf8mb3_swedish_ci')),
                ('abrev_curso', models.CharField(db_collation='utf8mb3_swedish_ci', max_length=7)),
                ('codigo_curso', models.CharField(db_collation='utf8mb3_swedish_ci', max_length=15)),
                ('disponible_desde', models.DateField()),
                ('fk_categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tablasconfiguracion')),
                ('fk_estruc_programa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.estructuraprograma')),
            ],
        ),
        migrations.CreateModel(
            name='ActividadEvaluaciones',
            fields=[
                ('idactividad_evaluaciones', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.TextField()),
                ('fk_curso_actividad', models.SmallIntegerField(null=True)),
                ('nro_repeticiones', models.IntegerField(blank=True, null=True)),
                ('calificacion_aprobar', models.IntegerField()),
                ('fk_escala_calificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.escalacalificacion')),
            ],
        ),
    ]