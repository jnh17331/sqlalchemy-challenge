# Dependencies
import sqlalchemy
from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# Database Setup
#################################################


# Creates an engine for the sql file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Sets up our base
Base = automap_base()
Base.prepare(engine, reflect=True)

# Reflect the tables
Base.classes.keys()

# Save references to each table
Measurement  = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def main():
        return (
            f"Welcome to my Hawaii Climate App :)</br>"
            f"Routes:</br>"
            f"/api/v1.0/precipitation</br>"
            f"/api/v1.0/stations</br>"
            f"/api/v1.0/tobs</br>"
            f"/api/v1.0/start</br>"
            f"/api/v1.0/start/end</br>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Gets the range of days in the previous year    
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Queries the data to get precipitation measurements for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).order_by(Measurement.date).all()

    # Puts the results of the query into a dictonary
    results_dict = dict(results)

    # Closes the session
    session.close()

    # Returns the dictionary as a json
    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():

    # Queries the stations from the data; then groups and orders the stations by id
    stations = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station)\
                      .order_by(func.count(Measurement.id).desc()).all()

    # Puts the results of the query into a dictonary
    stations_dict = dict(stations)

    # Closes the session
    session.close()

    # Returns the dictionary as a json
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():

    # Queries the data for the most active station and observed temp then filters the queried data for the most recent year
    temp_obs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23')\
                      .filter(Measurement.station == 'USC00519281').all()

    # Creates a dictionary and appends the queried data to that dictionary
    tobs_list = []
    for date, tobs in temp_obs:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)

    # Closes the session
    session.close()

    # Returns the dictionary as a json
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):

    # Gets the min value, mean value, and max value of an observed temp from a specified date from the sql data
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    # Creates a dictionary and appends the queried data to that dictionary
    tobsall = []
    for min, avg, max in result:
            tobs_dict = {}
            tobs_dict["Min"] = min
            tobs_dict["Average"] = avg
            tobs_dict["Max"] = max
            tobsall.append(tobs_dict)
        
    # Closes the session
    session.close()

    # Returns the list of the queried data
    return jsonify(tobsall)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    # Gets the start and end date and puts them as a date in datetime
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()

    # Queries the sql data for the min, avg, and max temp of the start and end date
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                    .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


    # Creates a dictionary and appends the queried data to that dictionary
    tobsall = []
    for min_temp, avg_temp, max_temp in result:
            tobs_dict = {}
            tobs_dict["Min"] = min_temp
            tobs_dict["Average"] = avg_temp
            tobs_dict["Max"] = max_temp
            tobsall.append(tobs_dict)

    # Closes the session
    session.close()

    # Returns the list
    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)