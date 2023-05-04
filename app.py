  
from multiprocessing import Condition
from random import choices
from wsgiref.validate import validator
from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SubmitField,SelectField, IntegerField, BooleanField, RadioField)
from wtforms.validators import DataRequired, InputRequired, Length
import jsonify
import numpy as np
import pickle as pickle
import numpy as np
import sklearn
import math
from sklearn.preprocessing import StandardScaler
import os
import scrapper 

import mysql.connector



app = Flask(__name__)

# sceret key for form
app.config['SECRET_KEY'] = 'any secret string'

model = pickle.load(open('random_forest_regression_models.pkl', 'rb'))


car_type_options = [('','Select Type'),('truck','Truck'),('pickup','Pickup'),('mini-van','Mini-van'),('sedan','Sedan'),('hatchback','Hatchback'),('offroad','Offroad'),('SUV','SUV'),('convertible','Convertible'),
('van','Van'),('coupe','Coupe'),('wagon','Wagon'),('bus','Bus'),('other','Other')]

transmission_options = [('','Select Transmission'),('automatic','Automatic'),('manual','Manual')]

make_options = [('','Select Make'),('ford','Ford'),('toyota','Toyota'),('honda','Honda'),('chevrolet','Chevrolet'),('dodge','Dodge'),('chrysler','Chrysler'),('subaru','Subaru'),('mercedes-benz','Mercedes-benz'),
('lincoln','Lincoln'),('jeep','Jeep'),('buick','Buick'),('acura','Acura'),('volvo','Volvo'),('infiniti','Infiniti'),('bmw','BMW'),('volkswagen','Volkswagen'),('mazda','Mazda'),('porsche','Porsche'),
('lexus','Lexus'),('kia','Kia'),('gmc','GMC'),('ram','RAM'),('nissan','Nissan'),('audi','Audi'),('mitsubishi','Mitsubishi'),('fiat','Fiat'),('cadillac','Cadillac'),('rover','Rover'),('jaguar','Jaguar'),
('mini','Mini'),('alfa-romeo','Alfa-Romeo'),('pontiac','Pontiac'),('saturn','Saturn'),('harley-davidson','Harley-Davidson'),('mercury','Mercury'),('tesla','Tesla'),('datsun','Datsun'),
('aston-martin','Aston-Martin'),('land rover','Land Rover'),('ferrari','Ferrari')]

year_options = [('','Select Year'),('2022','2022'),('2021','2021'),('2020','2020'),('2019','2019'),('2018','2018'),('2017','2017'),('2016','2016'),('2015','2015'),('2014','2014'),('2013','2013'),
('2012','2012'),('2011','2011'),('2010','2010'),('2009','2009'),('2008','2008'),('2007','2007'),('2006','2006'),('2005','2005'),('2004','2004'),('2003','2003'),('2002','2002'),('2001','2001'),
('2000','2000')]


cars=[('','Select Car Name'),
("jetta s","jetta s"),("jetta s turbo","jetta s turbo"),
("jetta 1.4t s","jetta 1.4t s"),("jetta se","jetta se"),
("jetta se 1.8l","jetta se 1.8l"),("jetta se 1.8l turbo","jetta se 1.8l turbo"),
("jetta se 1.8l turbo","jetta se 1.8l turbo"),("jetta se 2,5l","jetta se 2,5l"),
("jetta sport","jetta sport"),
("passat 1.8t s","passat 1.8t s"),("passat s","passat s"),
("passat 1.8t se","passat 1.8t se"),
("passat se tdi","passat se tdi"),("passat cc sport","passat cc sport"),
("passat 2.0t","passat 2.0t"),("passat 3.6l","passat 3.6l"),
("atlas","atlas"),
("atlas cross sport","atlas cross sport"),("atlas sel","atlas sel"),
("atlas se","atlas se"),
("atlas se 4motion","atlas se 4motion")
]

config = {
    'user': 'root',
    'password': 'rishabh1234',
    'host': '34.174.102.104',
    'database':'scrapper'
}


# Create Form Class
class myform(FlaskForm):
    year = SelectField(" ",choices=year_options, validators = [DataRequired()])
    transmission = SelectField("  ",choices=transmission_options, validators = [DataRequired()])
    make =  SelectField("  ",choices=make_options, validators = [DataRequired()]) # Manufatcurer
    fuel_type =  SelectField(" ",choices=[('','Select Fuel Type '),('gas', 'Gas'), ('diesel', 'Diesel'),('hybrid', 'Hybrid'),('electric','Electric')], validators = [DataRequired()])
    car_type =  SelectField(" ", choices=car_type_options,validators = [DataRequired()]) # CAR TYPE
    car_condition =  SelectField("  ",choices=[('','Select Condition'),('good', 'Good'), ('fair', 'Fair'), ('like new', 'Like New'),('salvage', 'Salvage')], validators = [DataRequired()]) 
    car_model = SelectField("  ",choices=cars, validators = [DataRequired()])
    details = SelectField(" ",choices=cars, validators = [DataRequired()])
    submit = SubmitField("Get Estimate")



standard_to = StandardScaler()
@app.route('/',methods=['GET', 'POST'])
def Home():
    # Model Feat
    year = None
    transmission = None
    car_age= None
    fuel = None
    condition = None
    type = None
    manufacturer = None
    

    transmission_type = None
    fuel_type = None
    car_condition = None
    car_type=None
    prediction=0
    price =0
    make = None
    form = myform()
    #car_condition1=None
    scrap_price=" "
    modell=None
 

    if request.method == 'POST':

        # 1 year
        year = int(form.year.data)

        transmission_type = form.transmission.data
        fuel_type = form.fuel_type.data
        car_condition = form.car_condition.data
        #car_condition1 = form.car_condition1.data
        car_type = form.car_type.data
        make = form.make.data
        details = form.details.data

        # now we establish our connection
        cnxn = mysql.connector.connect(**config)
        cursor = cnxn.cursor()
        sql="SELECT * FROM cars where year = %s and make=%s and transmission=%s and cond=%s and type=%s "
        cursor.execute(sql,(str(year),str(make),str(transmission_type),str(car_condition),str(car_type)))
        res = cursor.fetchall()
        if res!=[]:
            for i in res:
                scrap_price = i[5]
        else:
            scrap_price = scrapper.scrap(year,transmission_type,make,car_type,fuel_type,details)
            sql = "INSERT INTO cars(year,make,transmission,cond,type,price) values(%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(str(year),str(make),str(transmission_type),str(car_condition),str(car_type),str(scrap_price)))
            # print("Added")
            
            cnxn.commit()
        cnxn.close()

        
        #print('type:', car_condition1)

        # 2 Car Age
        car_age = 2022 - year

        # 3 transmisiiom
        if transmission_type == 'automatic':
            transmission = 0

        else:
            transmission = 1

        # 4 condition
        if car_condition == 'excellent':
            condition = 0
    
        elif  car_condition == 'good':
            condition = 1

        elif  car_condition == 'fair':
            condition = 2

        elif  car_condition == 'like new':
            condition = 3

        elif  car_condition == 'new':
            condition = 4

        elif  car_condition == 'salvage':
            condition = 5

        # 5 fuel
        if fuel_type == 'gas':
            fuel = 0
            
        elif fuel_type == 'diesel':
            fuel = 1

        elif fuel_type == 'hybrid':
            fuel = 2

        elif fuel_type == 'electric':
            fuel = 3  

        # 6 car type

        if car_type == 'truck':
            type = 0
            
        elif car_type == 'pickup':
            type = 1
            
        elif car_type == 'mini-van':
            type = 2
                 
        elif car_type == 'sedan':
            type = 3
               
        elif car_type == 'hatchback':
            type = 4
              
        elif car_type == 'offroad':
            type = 5

        elif car_type == 'SUV':
            type = 6
               
        elif car_type == 'convertible':
            type = 7
            
        elif car_type == 'van':
            type = 8
            
        elif car_type == 'coupe':
            type = 9
            
        elif car_type == 'wagon':
            type = 10
            
        elif car_type == 'other':
            type = 11
            
        elif car_type == 'bus':
            type = 12
       
        # Manufacuturer

        if make == 'ford':
            manufacturer = 0
        elif make == 'toyota':
            manufacturer = 1
        elif make == 'honda':
            manufacturer = 2
        elif make == 'chevrolet':
            manufacturer = 3
        elif make == 'dodge':
            manufacturer = 4
        elif make == 'chrysler':
            manufacturer = 5
        elif make == 'subaru':
            manufacturer = 6
        elif make == 'mercedes-benz':
            manufacturer = 7
        elif make == 'lincoln':
            manufacturer = 8
        elif make == 'jeep':
            manufacturer = 9
        elif make == 'buick':
            manufacturer = 10
        elif make == 'acura':
            manufacturer = 11
        elif make == 'volvo':
            manufacturer = 12
        elif make == 'infiniti':
            manufacturer = 13
        elif make == 'bmw':
            manufacturer = 14
        elif make == 'volkswagen':
            manufacturer = 15
        elif make == 'mazda':
            manufacturer = 16  
        elif make == 'porsche':
            manufacturer = 17 
        elif make == 'lexus':
            manufacturer = 18 
        elif make == 'kia':
            manufacturer = 19
        elif make == 'gmc':
            manufacturer = 20
        elif make == 'hyundai':
            manufacturer = 21
        elif make == 'ram':
            manufacturer = 22
        elif make == 'nissan':
            manufacturer = 23
        elif make == 'audi':
            manufacturer = 24
        elif make == 'mitsubishi':
            manufacturer = 25
        elif make == 'fiat':
            manufacturer = 26
        elif make == 'cadillac':
            manufacturer = 27
        elif make == 'rover':
            manufacturer = 28
        elif make == 'jaguar':
            manufacturer = 29
        elif make == 'mini':
            manufacturer = 30
        elif make == 'alfa-romeo':
            manufacturer = 31
        elif make == 'pontiac':
            manufacturer = 32
        elif make == 'saturn':
            manufacturer = 33
        elif make == 'harley-davidson':
            manufacturer = 34
        elif make == 'mercury':
            manufacturer = 35
        elif make == 'tesla':
            manufacturer = 36
        elif make == 'datsun':
            manufacturer = 37
        elif make == 'aston-martin':
            manufacturer = 38
        elif make == 'land rover':
            manufacturer = 39
        elif make == 'ferrari':
            manufacturer = 40


         # Car Model
        if details == 'jetta s':
            modell=1
        elif details == 'jetta s':
            modell=2
        elif details == 'jetta s turbo':
            modell=3
        elif details == 'jetta 1.4t s':
            modell = 4
        elif details == 'jetta se':
            modell=5
        elif details == 'jetta se 1.8l':
            modell=6
        elif details== 'jetta se 1.8l turbo':
            modell=7
        elif details == 'jetta se 2,5l':
            modell=8,
        elif details == 'jetta sport':
            modell=9,
        elif  details== 'passat 1.8t s':
            modell=10
        elif details == 'passat s':
            modell=11
        elif details == 'passat 1.8t se':
            modell=12
        elif details == 'passat se tdi':
            modell=13
        elif details == 'passat cc sport':
            modell=14
        elif details == 'passat 2.0t':
            modell=15
        elif details == 'passat 3.6l':
            modell=16
        elif details == 'atlas':
            modell=17
        elif details ==  'atlas cross sport':
            modell=18
        elif details == 'atlas sel awd':
            modell=19
        elif details == 'atlas se 4motion':
            modell=20
        elif details == 'atlas sel':
            modell=21
        elif details  == 'atlas se':
            modell=22
        else:
            modell=0
        
        prediction=model.predict([[year, transmission, car_age, fuel, condition,type,manufacturer,modell]])
        #price = round(prediction[0], 0)
        price = math.trunc(prediction[0])
        


    return render_template('index.html', form = form, output_scrap = scrap_price,output=price)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
    # app.run(port=5000, debug=True)
