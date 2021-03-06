# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


# Import Flask
from flask import Flask,jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/Hawaii.sqlite")
# reflect an existing databse into a new model 
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement
# Create out session(link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#  Create an app
app = Flask(__name__)

# Define static routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Precipitation by dates from previous year<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of previous year's temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"- When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"- When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.<br/>"

    )
#########################################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
#    * Query for the dates and precipitation observations from the last 12 months.
#         * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#         * Return the json representation of your dictionary.
    # last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # year_ago = dt.date(last_date) - dt.timedelta(days=366)
    prep = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > "2016-08-23").all()
   # Create a list of dicts with `date` and `prcp` as the keys and values
    prep_totals = []
    for rain in prep:
        prep_dict = {}
        prep_dict["date"] = rain[0]
        prep_dict["prcp"] = rain[1]
        prep_totals.append(prep_dict)

    return jsonify(prep_totals)

@app.route("/api/v1.0/stations")
def stations(): 
    """Return a JSON list of stations from the dataset."""
    # Query stations
    stations =  session.query(Station.name, Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data

    # Calculate the date 1 year ago from the last data point in the database
    # last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # year_ago = dt.date(last_date) - dt.timedelta(days=366)

    # Query tobs
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= "2016-08-23").all()
    # Convert the results into a list 
    temp_list=[]
    for tobs in temp:
        temp_dict = {}
        temp_dict["date"] = tobs[0]
        temp_dict["tobs"] = float(tobs[1])
        temp_list.append(temp_dict)
    return jsonify(temp_list)

@app.route("/api/v1.0/<start_date>")
def start(start_date):

    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""
    
    start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    return jsonify(start)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    """return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    return jsonify(start_end)

if __name__ == '__main__':
    app.run(debug=True)