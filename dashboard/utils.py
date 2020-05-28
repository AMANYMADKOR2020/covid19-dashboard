import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import re
import os
from collections import Counter
import requests 
from pandas import DataFrame as df

r = requests.get('http://coronavirus-tracker-api.herokuapp.com/v2/locations')

r=df(r.json()['locations'])
analytics_dict = {
    "no_of_population": 0,
    "no_of_confirmed" :0,
    "no_of_deaths" :0,
    "no_of_recovered" :0
}
def init_jobs(queries):
    global analytics_dict
    analytics_dict = {
    "no_of_population": 0,
    "no_of_confirmed" :0,
    "no_of_deaths" :0,
    "no_of_recovered" :0
}
    confirmed = []
    recovered =[]
    deaths = []
    for x in r['latest']:
        confirmed.append(x['confirmed'])
        recovered.append(x['recovered'])
        deaths.append(x['deaths'])
    r['confirmed'] = df(confirmed)
    r['recovered'] = df(recovered)
    r['deaths'] = df(deaths)
   # if .str.upper()  
    no_Population=float(r.loc[r['country'].str.upper() ==queries.upper()]['country_population'])
    no_confirmed=float(r.loc[r['country'].str.upper() ==queries.upper()]['confirmed'])
    no_recovered=float(r.loc[r['country'].str.upper() ==queries.upper()]['recovered'])
    no_deaths=float(r.loc[r['country'].str.upper() ==queries.upper()]['deaths'])
    analytics_dict = {
    "no_of_population": no_Population,
    "no_of_confirmed" :no_confirmed,
    "no_of_deaths" :no_deaths,
    "no_of_recovered" :no_recovered

}

    
def get_analytics_dict():
    global analytics_dict
    no_of_confirmed = analytics_dict['no_of_confirmed']
    no_of_deaths = analytics_dict['no_of_deaths']
    no_of_recovered = analytics_dict['no_of_recovered']
    no_of_population = analytics_dict['no_of_population']
    print (analytics_dict) 
    return {
    "no_of_population": no_of_population,
    "no_of_confirmed" :no_of_confirmed,
    "no_of_deaths" :no_of_deaths,
    "no_of_recovered" :no_of_recovered
    }
    
