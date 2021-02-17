# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 14:48:39 2021

@author: chris
"""

import numpy as np
import pandas as pd
from matplotlib import rcParams
from matplotlib import pyplot as plt 
import seaborn as sns
from scipy.stats import zscore

# allow output to span multiple output lines in the console
pd.set_option('display.max_columns', 500)

# switch to seaborn default stylistic parameters
# see the very useful https://seaborn.pydata.org/tutorial/aesthetics.html
sns.set()
sns.set_context('talk')

# change default plot size
rcParams['figure.figsize'] = 10,8
# Covid Data
covidDF = pd.read_csv('https://raw.githubusercontent.com/chrisweilacker/CovidMachineLearningProject/master/global_covid19_mortality_rates.csv', index_col=0)
# 2016 Data for Both Sexes is in Column Both Sexes
obesityDF = pd.read_csv('https://raw.githubusercontent.com/chrisweilacker/CovidMachineLearningProject/master/obesity-data.csv', skiprows=3)
# Demographics Data which includes the percentage of population over 65 per country.
demoDF = pd.read_csv('https://raw.githubusercontent.com/chrisweilacker/CovidMachineLearningProject/master/DEMO_Global.csv')

# Create our DataFrame with the necessary data from all three datasets
df = covidDF.merge(obesityDF[['Country', 'Both sexes']], how='inner') #Copy in the whole Covid Data and the Obesity Data
# Modify name of Both Sexes to Obesity and get just the number
df.rename(columns={'Both sexes': 'Obesity'}, inplace=True)
obNumber = df['Obesity'].str.split(" ", n = 1, expand = True) 
df['Obesity'] = obNumber[0]

#Drop Rows with no Obesity Data
df.drop(df.loc[df['Obesity']=='No'].index, inplace=True)
#Drop Rows with no Covid Data
df.drop(df.loc[df['Mortality Ratio']==0].index, inplace=True)
df.rename(columns={'Mortality Ratio': 'Covid-19 Mortality Ratio'}, inplace=True)
# Convert Obesity data to float
df['Obesity'] = pd.to_numeric(df['Obesity'], downcast="float")

#Drop the outlier Yemen which has an 8.75 Std Deviation on its Covied 19 mortality
df.drop(df.loc[df['Country']=='Yemen'].index,inplace=True)


# Get the Pop 65 and Over and Tot Pop Data to Calculate Percent 65 and Over
df = df.merge(demoDF[['Country', 'Value']][(demoDF['Time']==2017) & (demoDF['Indicator']=='Population aged 65 years or older ')], how='inner') #Copy in the 65 and Over Data
df.rename(columns={'Value': 'Pop65Over'}, inplace=True)
df = df.merge(demoDF[['Country', 'Value']][(demoDF['Time']==2017) & (demoDF['Indicator']=='Total population ')], how='inner') #Copy in the 65 and Over Data
df.rename(columns={'Value': 'TotPop'}, inplace=True)

# Create Perc 65 and Over
df['Perc65Over'] = (100 * df['Pop65Over']/df['TotPop'])

corr = df[['Covid-19 Mortality Ratio', 'Perc65Over', 'Obesity']].corr()
#It seems that there is a correlation between both Perc 65 and Over, Obesity and Covid-19 Mortality Ratio
#Though the Perc65 and Over seems to be stronger than Obesity, but the data hasnt been normalized yet.
#We may later want to bring in another dimension such as functionality of the countries health system
# depending on what the ML algorithm can do.
corr.style.background_gradient(cmap='coolwarm')

# We might need to create a categorical column for mortality whether it is high risk or low risk
# and see if an ML algorithm such as KNN can use the obesity and Over 65 Population to 
# categorize the data would be more accurate.
df['HighRisk'] = zscore(df['Covid-19 Mortality Ratio']) > 1
df['NormCovid19Mortality'] = zscore(df['Covid-19 Mortality Ratio'])

#Some visualizations of the Data so far.
df.plot.scatter(x='Perc65Over', y='Obesity', c='NormCovid19Mortality', colormap='viridis')
plt.xlabel('Perc65Over')
