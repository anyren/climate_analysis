import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect db tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

def year_calc():
    session = Session(bind=engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    session.close()
    date_format = '%Y-%m-%d'
    dtObj = dt.datetime.strptime(recent_date,date_format)
    start_year = dtObj - relativedelta(years=1)
    start_year = start_year.strftime(date_format)
    return((recent_date,start_year))
    

# Flask routes
app = Flask(__name__)

@app.route("/")
#List all available routes.
def home():
    return ("Climate API Homepage</br>"
        "Available routes:</br>"
        "/api/v1.0/precipitation</br>"
        "/api/v1.0/stations</br>"
        "/api/v1.0/tobs</br>"
        "/api/v1.0/startdate</br>"
        "/api/v1.0/startdate/enddate</br>"
    )

@app.route("/api/v1.0/precipitation")
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
def precip():
    session = Session(bind=engine)
    recent_date,start_year = year_calc()
    precip = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date <= recent_date).filter(Measurement.date > start_year)
    session.close()
    precip_data = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        precip_data.append(precip_dict)
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def station():
    session = Session(bind=engine)
    station = session.query(Station.station,Station.name).all()
    session.close()
    station_data = []
    for station, name in station:
        station_dict = {}
        station_dict["station_id"] = station
        station_dict["name"] = name
        station_data.append(station_dict)
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most active station for the previous year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
def temp():
    session = Session(bind=engine)
    recent_date,start_year = year_calc()
    tobs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date <= recent_date).filter(Measurement.date > start_year)
    session.close()
    temp_data = []
    for date, temp in tobs:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = temp
        temp_data.append(temp_dict)
    return jsonify(temp_data)

#@app.route("/api/v1.0/<start>")
#@app.route("/api/v1.0/<start>/<end>")
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).


if __name__ == ("__main__"):
    app.run(debug=True)