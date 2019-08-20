# Generated by Django 2.2.4 on 2019-08-20 00:50

import analyses.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of analysis', max_length=30, unique=True)),
                ('description', models.CharField(help_text='Description', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Mesh',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='_None', max_length=100)),
                ('address', models.FileField(upload_to=analyses.models.analysis_directory_path)),
                ('NumFaces', models.IntegerField(default=1)),
                ('NumEdges', models.IntegerField(default=1)),
                ('analysis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mesh', to='analyses.Analysis')),
            ],
        ),
        migrations.CreateModel(
            name='Preform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of Preform', max_length=30)),
                ('thickness', models.FloatField(default=0.01, help_text='Thickness')),
                ('K11', models.FloatField(default=1e-10, help_text='Enter a number for K11')),
                ('K12', models.FloatField(default=0, help_text='Enter a number for K12')),
                ('K22', models.FloatField(default=2e-10, help_text='Enter a number for K22')),
                ('phi', models.FloatField(default=0.5, help_text='Enter a number for volume fraction')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preform', to='analyses.Analysis')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('typ', models.CharField(choices=[('1', 'Fill everywhere'), ('2', 'Fill the outlet')], default=0, max_length=30)),
                ('endtime', models.FloatField(default=1000, help_text='End time of analysis')),
                ('outputstep', models.FloatField(default=10000, help_text='Step size for writing output')),
                ('maxiterations', models.IntegerField(default=10000, help_text='Maximum number of iterations')),
                ('maxhaltsteps', models.IntegerField(default=10, help_text='Maximum number of consequtive steps with no apparant change in saturation')),
                ('minchangesaturation', models.FloatField(default=0.001, help_text='Minimum acceptable change of saturation')),
                ('timescaling', models.FloatField(default=5.0, help_text='Parameter to scale predicted filling time')),
                ('fillthreshold', models.FloatField(default=0.98, help_text='Threshold for counting filled CVs')),
                ('analysis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='step', to='analyses.Analysis')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('rotate', models.FloatField(default=0, help_text='Degree of rotation')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='section', to='analyses.Analysis')),
                ('preform', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preform', to='analyses.Preform')),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Step', models.IntegerField(default=0)),
                ('analysis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='analyses.Analysis')),
            ],
        ),
        migrations.CreateModel(
            name='Resin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of Resin', max_length=30)),
                ('viscosity', models.FloatField(default=0.02, help_text='Enter a number for viscosity')),
                ('analysis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resin', to='analyses.Analysis')),
            ],
        ),
        migrations.CreateModel(
            name='Nodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NodeNum', models.IntegerField()),
                ('x', models.FloatField(max_length=6, null=True)),
                ('y', models.FloatField(max_length=6, null=True)),
                ('z', models.FloatField(max_length=6, null=True)),
                ('FaceGroup', models.CharField(default='_None', max_length=50)),
                ('EdgeGroup', models.CharField(default='_None', max_length=50)),
                ('mesh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyses.Mesh')),
            ],
        ),
        migrations.CreateModel(
            name='Connectivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ElmNum', models.IntegerField(null=True)),
                ('N1', models.IntegerField(null=True)),
                ('N2', models.IntegerField(null=True)),
                ('N3', models.IntegerField(null=True)),
                ('mesh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyses.Mesh')),
            ],
        ),
        migrations.CreateModel(
            name='BC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('typ', models.CharField(choices=[('Pressure', 'Pressure'), ('Flow_Rate', 'Flow Rate'), ('Wall', 'Wall')], default=0, max_length=30)),
                ('value', models.FloatField(default=0, help_text='Value on Boundary Condition')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bc', to='analyses.Analysis')),
            ],
        ),
    ]
