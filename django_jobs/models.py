from django.db import models
from datetime import date


class Company(models.Model):
    """The short model for Company."""
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Jobs(models.Model):
    """The Model which contains data about the job."""
    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    link = models.URLField()

    class Meta:
        verbose_name_plural = "Jobs"

    def __str__(self):
        return self.title



