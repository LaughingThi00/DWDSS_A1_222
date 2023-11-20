from django.shortcuts import render
from django.http import JsonResponse
from api.models import Stock, Sector, Price
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import viewsets, permissions, status
import json

from api.GetData import *
from api.CalGrowth import *
from Global import *

from api.serializers import StockSerializer, SectorSerializer, PriceSerializer

class StockView(APIView):
    def get(self, request, pk):
        return
    
    def post(self, request):
        # Taking the type of request
        cmd = request.data.get('type')
        if cmd == 'clean':
            deleteTable = request.data.get('data')
            name = request.data.get('name')
            cleanCMD(deleteTable, name)
            response = {
                'type': cmd,
                'data': deleteTable,
                'status': 'success'
            }
            return Response(response,status = status.HTTP_200_OK)
        elif cmd == 'update':
            ticker = request.data.get('data')    
            serializer = updateCMD(ticker)
            if serializer.is_valid():
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        elif cmd == 'draw':
            ticker = request.data.get('data')    
            datadict = drawCMD(ticker)
            return Response(datadict, status = status.HTTP_200_OK)
        elif cmd == 'list':
            ans = listCMD()
            return Response(ans, status = status.HTTP_200_OK)
        else: pass
    

# ---------------------------------------- Additional method
def cleanCMD(deleteTable, name):
    if deleteTable == 'stock':
        objects = Stock.objects.filter(ticker = name)
    elif deleteTable == 'sector':
        objects = Sector.objects.all()
    objects.delete()
    

def updateCMD(ticker) -> StockSerializer:
    # Checking if Stock table is having the ticker, if yes then clean
    objStock = Stock.objects.filter(ticker=ticker)
    if objStock.exists():
        objStock.delete()
    # Insert data into Stock table
    df = get_earnings_history(ticker)
    growth = calGrowth(df)
    sector_name = get_company_info(ticker, 'sector')
    datadict = {
        'ticker' : ticker,
        'sector_name' : sector_name,
        'stock_growth' : growth,
    }
    serializer = StockSerializer(data = datadict)
    if serializer.is_valid():
        serializer.save()
    # Insert data into Price table
    df = get_ticker_hst(ticker, PERIOD)
    tickerStock = Stock.objects.get(ticker = ticker)
    for index, row in df.iterrows():
        price = Price(ticker = tickerStock, price = row['Close'], date = row['Date'])
        price.save()
    # Update data in the Sector table
    sectorName = get_company_info(ticker, 'sector')
    totalGrowth = 0
    numStockInSector = Stock.objects.filter(sector_name = sectorName).count()
    for obj in Stock.objects.filter(sector_name = sectorName):
        totalGrowth += obj.stock_growth
    objSector = Sector.objects.filter(sector_name = sectorName)
    if objSector.exists():
        sectorGrowth = totalGrowth*1.0 / numStockInSector
        objSector.update(sector_growth = sectorGrowth)
    else:
        sector = Sector(sector_name = sectorName, sector_growth = totalGrowth)
        sector.save()
    # Return a Stock Serilizer
    return serializer


def drawCMD(ticker) -> StockSerializer:
    # Checking if there is already a ticker in the Stock table, if not then update
    objectTicker = Stock.objects.filter(ticker = ticker)
    if not objectTicker.exists():
        updateCMD(ticker)
    # Taking the ticker hst from database
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])
    ticker_id = Stock.objects.get(ticker = ticker).id
    for obj in Price.objects.filter(ticker_id = ticker_id):
        new_row = {
            'Date': obj.date,
            'Open': 0,
            'High': 0,
            'Low': 0,
            'Close': obj.price,
            'Volume': 0,
            'Adj Close': 0
        }
        df.loc[len(df)] = new_row
    name = 'Final.csv'
    df.to_csv(DIR + f'{name}', index = False, header = True)
    # Taking growth from Sector table and export
    objectTicker = Stock.objects.get(ticker = ticker)
    growth = Sector.objects.get(sector_name = objectTicker.sector_name).sector_growth
    data = [growth]
    dfGrowth = pd.DataFrame(data, columns = ['Recomended Growth'])
    name = 'FinalGrowth.csv'
    dfGrowth.to_csv(DIR + f'{name}', index = False, header = True)
    # Into the DB
    datadict = {
        'ticker' : ticker,
        'sector_name' : objectTicker.sector_name,
        'sector_growth' : growth,
    }
    return datadict


def listCMD() -> dict:
    ans = {
        'data': []
    }
    for obj in Stock.objects.all():
        tDict = {
            'stock': obj.ticker,
            'sector': obj.sector_name
        }
        ans['data'].append(tDict)
    return ans
