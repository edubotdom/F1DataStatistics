# Generated by Django 3.1.2 on 2020-12-29 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anyo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anyo', models.CharField(max_length=5, verbose_name='Años competidos en la categoría')),
            ],
        ),
        migrations.CreateModel(
            name='Nacionalidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30, verbose_name='Nombre de la nacionalidad')),
            ],
        ),
        migrations.CreateModel(
            name='Piloto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(verbose_name='Nombre')),
                ('fechaNacimiento', models.DateField(verbose_name='Fecha de nacimiento')),
                ('victorias', models.IntegerField(verbose_name='Número de victorias')),
                ('podios', models.IntegerField(verbose_name='Número de podios')),
                ('poles', models.IntegerField(verbose_name='Número de poles')),
                ('campeonatos', models.IntegerField(verbose_name='Número de campeonatos del mundo de pilotos ganados')),
                ('temporadas', models.IntegerField(verbose_name='Número de temporadas disputadas')),
                ('carreras', models.IntegerField(verbose_name='Número de carreras disputadas')),
                ('puntos', models.DecimalField(decimal_places=10, max_digits=15, verbose_name='Número de puntos obtenidos durante su carrera deportiva')),
                ('retiros', models.IntegerField(verbose_name='Número de retiros durante su carrera deportiva')),
                ('anyos_competidos', models.ManyToManyField(to='main.Anyo', verbose_name='Años competidos en la categoría')),
                ('nacionalidad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.nacionalidad', verbose_name='Nombre de la nacionalidad')),
            ],
        ),
        migrations.CreateModel(
            name='Escuderia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(verbose_name='Nombre')),
                ('victorias', models.IntegerField(verbose_name='Número de victorias')),
                ('poles', models.IntegerField(verbose_name='Número de poles')),
                ('temporadas', models.IntegerField(verbose_name='Número de temporadas disputadas')),
                ('carreras', models.IntegerField(verbose_name='Número de carreras disputadas')),
                ('campeonatos', models.IntegerField(verbose_name='Número de campeonatos del mundo de constructores ganados')),
                ('puntos', models.DecimalField(decimal_places=10, max_digits=15, verbose_name='Número de puntos obtenidos durante su carrera deportiva')),
                ('anyos_competidos', models.ManyToManyField(to='main.Anyo', verbose_name='Años competidos en la categoría')),
                ('nacionalidad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.nacionalidad', verbose_name='Nombre de la nacionalidad')),
                ('pilotos', models.ManyToManyField(to='main.Piloto')),
            ],
        ),
    ]
