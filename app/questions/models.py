from django.db import models


# Create your models here.
class Question(models.Model):
    value = models.TextField(max_length=200)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    value = models.TextField(max_length=200)
