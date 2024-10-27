# Generated by Django 4.1.4 on 2023-03-19 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grammarview', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grammarrecord',
            name='bformat',
            field=models.CharField(blank=True, default=None, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='decimals',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='format',
            field=models.CharField(blank=True, default=None, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='is_field',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='length',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='mandatory',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='maxrepeat',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='minlength',
            field=models.CharField(default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='grammarrecord',
            name='subfields',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
