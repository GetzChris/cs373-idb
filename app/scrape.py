import json
import os
import requests
import time
from collections import defaultdict
from functools import reduce
from py_bing_search import PyBingSearch

apikey = 'wtprucmwrgk6bd92rq7tun97'
edmund_url = 'http://api.edmunds.com/api/vehicle/v2/'
end_url = '?fmt=json&view=full&api_key=' + apikey
bing = PyBingSearch('Np5rmrL6fIPP3jpDqVi+Li/rJ1Joih4Q6wP69HrjQro=')

model_id = 1
make_id = 1

models_list = []
makes_list = []
make_ids = {}
makes_models_dict = defaultdict(list)

makes_json = requests.get(edmund_url + 'makes' + end_url).json()

def add_model(make,model,year,make_id):
  print('adding model '+model)
  try:
    global model_id
    global models_list
    global makes_models_dict
    time.sleep(.6)
    car = requests.get(edmund_url + '{}/{}/{}'.format(make,model,year) + end_url).json()
    style = car['styles'][0]
    eid = style['id']
    time.sleep(.6)
    car_json = requests.get(edmund_url + 'styles/{}'.format(eid) + end_url).json()
    query = car['make'] + ' ' + car['model']
    result = bing.search(query, limit=1, format='json')
    car_dict = {'id':model_id,'make':make,'make_id':make_id,'model':model,'year':year,'price':car_json['price']['baseMSRP'],'horsepower':car_json['engine']['horsepower']}
    car_dict['img_url'] = result
    makes_models_dict[make].append(car_dict)
    models_list.append(car_dict)
    model_id += 1
  except Exception as e:
    pass

def add_make(make):
  print('adding_make' + make)
  global make_ids
  global makes_list
  global makes_models_dict

  make_json = {}
  make_json['id'] = make_ids[make]
  make_json['name'] = make
  make_json['num_models'] = len(makes_models_dict[make])
  cars = makes_models_dict[make]
  total = reduce( (lambda t, car: t + car['price']), cars, 0)
  make_json['avg_price'] = float(total)/len(cars)
  total = reduce( (lambda t, car: t + car['horsepower']), cars, 0)
  expensive_car = reduce((lambda m, car:m if m['price'] > car['price'] else car),cars)
  make_json['max_car_id'] = expensive_car['id']
  url_name = reduce(lambda r,x:  r + x.capitalize() + '-', make['name'].split('-'),'')
  url = 'http://www.carlogos.org/uploads/car-logos/{}logo-1.jpg'.format(url_name)
  response = requests.get(url)
  if(response.status_code == 404):
    url = bing.search(make['name'] + " logo", limit=1, format='json')
  make_json['img_url'] = url
  make_json['avg_horsepower'] = float(total)/len(cars)
  makes_list.append(make_json)

for make in makes_json['makes']:
  for model in make['models']:
    years = model['years']
    last = len(years) - 1
    car = years[last]
    if car['year'] > 2014:
      add_model(make['niceName'],model['niceName'],years[last]['year'],make_id)
  make_ids[make['niceName']] = make_id
  make_id+=1

with open('cars_list.json', 'w') as outfile:
    json.dump(models_list, outfile)

for make in makes_models_dict:
  add_make(make)

with open('makes_list.json', 'w') as outfile:
  json.dump(makes_list, outfile)