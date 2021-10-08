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
            name='ContratantesRol',
            fields=[
                ('idcontratantes_rol', models.AutoField(primary_key=True, serialize=False)),
                ('desc_rol', models.CharField(max_length=30)),
                ('fk_contratante', models.IntegerField()),
                ('valor_rol', models.CharField(blank=True, max_length=16, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogSeguridad',
            fields=[
                ('idlog_seguridad', models.AutoField(primary_key=True, serialize=False)),
                ('fk_cta_usuario', models.SmallIntegerField()),
                ('fecha_transaccion', models.DateField()),
                ('hora_transac', models.DateField()),
                ('fk_tipo_operacion', models.SmallIntegerField()),
                ('desc_operacion', models.TextField()),
                ('valor_dato', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CtaUsuario',
            fields=[
                ('idcta_usuario', models.AutoField(primary_key=True, serialize=False)),
                ('codigo_cta', models.CharField(max_length=15)),
                ('clave', models.TextField(blank=True, null=True)),
                ('intentos_fallidos', models.IntegerField()),
                ('fecha_ult_cambio', models.DateField(blank=True, null=True)),
                ('respuesta_secreta', models.TextField(blank=True, null=True)),
                ('fk_status_cuenta', models.SmallIntegerField()),
                ('dias_cambio', models.IntegerField()),
                ('fk_pregunta_secreta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pregunta', to='app.tablasconfiguracion')),
                ('fk_publico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.publico')),
                ('fk_rol_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rol_usuario', to='app.tablasconfiguracion')),
            ],
        ),
    ]
