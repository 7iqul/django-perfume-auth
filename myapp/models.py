from django.db import models

class Perfume(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    size_ml = models.IntegerField()
    description = models.TextField(blank=True)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return self.name