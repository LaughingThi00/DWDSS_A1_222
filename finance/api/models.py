from django.db import models

# Create your models here.
class Sector(models.Model):
    sector_name = models.CharField(max_length=100, null=False)
    sector_growth = models.FloatField(null=True)

class Stock(models.Model):
    ticker = models.CharField(max_length=100, null=False)
    sector_name = models.CharField(max_length=100, null=True)
    stock_growth = models.FloatField(null=True)

class Price(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE, null = False)
    price = models.FloatField(null=False)
    date = models.DateField(null=False)