# Generated by Django 5.1.3 on 2024-11-11 19:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('questions', '0002_alter_choice_question_questiongroupobjectpermission_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='questions.question'
            ),
        ),
    ]