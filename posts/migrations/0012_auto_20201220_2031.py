# Generated by Django 2.2.6 on 2020-12-20 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Введите ваш комментарий', max_length=200, verbose_name='Текст комментария'),
        ),
    ]