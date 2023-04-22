# Generated by Django 4.1.4 on 2023-03-11 17:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='EdiGrammar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GrammarRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tn_ancestors_pks', models.TextField(blank=True, default='', editable=False, verbose_name='Ancestors pks')),
                ('tn_ancestors_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Ancestors count')),
                ('tn_children_pks', models.TextField(blank=True, default='', editable=False, verbose_name='Children pks')),
                ('tn_children_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Children count')),
                ('tn_depth', models.PositiveIntegerField(default=0, editable=False, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Depth')),
                ('tn_descendants_pks', models.TextField(blank=True, default='', editable=False, verbose_name='Descendants pks')),
                ('tn_descendants_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Descendants count')),
                ('tn_index', models.PositiveIntegerField(default=0, editable=False, verbose_name='Index')),
                ('tn_level', models.PositiveIntegerField(default=1, editable=False, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Level')),
                ('tn_priority', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(9999)], verbose_name='Priority')),
                ('tn_order', models.PositiveIntegerField(default=0, editable=False, verbose_name='Order')),
                ('tn_siblings_pks', models.TextField(blank=True, default='', editable=False, verbose_name='Siblings pks')),
                ('tn_siblings_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Siblings count')),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('edigrammar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grammarview.edigrammar')),
                ('tn_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tn_children', to='grammarview.grammarrecord', verbose_name='Parent')),
            ],
            options={
                'verbose_name': 'Record',
                'verbose_name_plural': 'Record',
                'ordering': ['tn_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EdiGrammarItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('edigrammar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grammarview.edigrammar')),
            ],
        ),
    ]