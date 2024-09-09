from django.db import models
from .developer import Developer
from .project import Project

class DeveloperProject(models.Model):
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date_claimed = models.DateTimeField()

    def __str__(self):
        return f'{self.developer} - {self.project}'