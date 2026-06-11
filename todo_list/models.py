from django.db import models


class Meta:
        verbose_name = "ToDo Item"

class ToDoItem(models.Model):
    title = models.CharField(max_length=250)
    done = models.BooleanField(default=False)


def __str__(self)-> str:
    return self.title