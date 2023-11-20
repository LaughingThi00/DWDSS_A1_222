# import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd
from pandas import *
from datetime import datetime

def calGrowth(df: DataFrame):
    # Making x and y
    x_train = df['Earnings Date'].values.copy()
    y_train = df['EPS Estimate'].values.copy()

    # Flip the dimensions
    x_train = np.flip(x_train)
    y_train = np.flip(y_train)

    # Convert datetime.date into int
    for i in range(x_train.shape[0]):
        dt = datetime.combine(x_train[i], datetime.min.time())
        sec = int(dt.timestamp())
        x_train[i] = sec
    
    # Reshape x
    x_train = x_train.reshape((-1,1))

    # create a linear regression object
    model = LinearRegression()

    # fit the model to the data
    model.fit(x_train, y_train)

    # plot the data and regression line
    plt.scatter(x_train, y_train)
    plt.plot(x_train, model.predict(x_train), color='red')
    plt.xlabel('X values')
    plt.ylabel('Y values')
    plt.title('Linear Regression')
    plt.show()

    # Recalculate the growth rate
    x1 = df['Earnings Date'].values[0]
    x1Number = int(datetime.combine(x1, datetime.min.time()).timestamp())
    x1Number = np.array(x1Number).reshape((1,1))
    x2 = x1.replace(year = x1.year + 1)
    x2Number = int(datetime.combine(x2, datetime.min.time()).timestamp())
    x2Number = np.array(x2Number).reshape((1,1))
    y1 = model.predict(x1Number)
    y2 = model.predict(x2Number)
    slope = (y2[0] - y1[0])/y1[0]

    # return the growth rate
    return slope