# Import the dependencies.


import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite+pysqlite:///" + r"C:\Users\sarit\OneDrive\Desktop\Class_Folder\mygithub\sqlalchemy-challenge\SurfsUp\Resources\hawaii.sqlite")


# reflect an existing database into a new model

Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Define the home page route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )        

#Define the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Perform your precipitation analysis here
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    twelve_months_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(months=12)
    twelve_months_ago_date = twelve_months_ago.date()
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= twelve_months_ago_date).all()
    print(precipitation_data)


    # Convert the results to a dictionary
    precipitation_dict = {date: value for date, value in precipitation_data}

    #print(precipitation_dict)

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():

    # Retrieve stations from the dataset

    total_stations = session.query(func.count(func.distinct(Station.station))).all()
    
    results = session.query(Station.station, Station.name, func.count(Measurement.id).label('num_rows')) \
                 .select_from(Station) \
                 .join(Measurement, Station.station== Measurement.station) \
                 .group_by(Station.station, Station.name) \
                 .order_by(func.count(Measurement.id).desc()) \
                 .all()

    results_list = [(result.station, result.num_rows) for result in results]
    print(results_list)
    
    # Return a JSON list of stations
    return jsonify(results_list)

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the most-active station for temperature observations
    
      most_active_station = session.query(Station.station, Station.name, func.count(Measurement.id).label('num_rows')) \
                 .select_from(Station) \
                 .join(Measurement, Station.station== Measurement.station) \
                 .group_by(Station.station, Station.name) \
                 .order_by(func.count(Measurement.id).desc()) \
                 .first()[0]
      most_recent_date = session.query(func.max(Measurement.date)).scalar()
      twelve_months_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(months=12)
      twelve_months_ago_date = twelve_months_ago.date()

# Query the TOBS data for the specific station within the last 12 months
      tobs_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= twelve_months_ago_date,
        Measurement.date <= most_recent_date
    ).all()
      
      tobs_data_dict = {date: value for date, value in tobs_data}
      
    # Return a JSON list of temperature observations
      return jsonify(tobs_data_dict)
    

# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes
@app.route('/api/v1.0/<start>')
def temperature_start(start):
    # Convert the start date to a datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query database to calculate TMIN, TAVG, and TMAX from the start date to the end of the dataset
    temperature_stats = session.query(func.min(Measurement.tobs).label('TMIN'),
                                      func.avg(Measurement.tobs).label('TAVG'),
                                      func.max(Measurement.tobs).label('TMAX'))\
                               .filter(Measurement.date >= start_date)\
                               .all()

    # Extract the calculated values
    result = {'TMIN': temperature_stats[0][0],
              'TAVG': temperature_stats[0][1],
              'TMAX': temperature_stats[0][2]}

    # Return a JSON response with the calculated values
    return jsonify(result)

@app.route('/api/v1.0/<start>/<end>')
def temperature_range(start, end=None):
      # Convert the start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    
    # Query database to calculate TMIN, TAVG, and TMAX between the given start and end dates
    temperature_stats = session.query(func.min(Measurement.tobs).label('TMIN'),
                                      func.avg(Measurement.tobs).label('TAVG'),
                                      func.max(Measurement.tobs).label('TMAX'))\
                               .filter(Measurement.date >= start_date)\
                               .filter(Measurement.date <= end_date)\
                               .all()
    
    # Extract the calculated values
    result = {'TMIN': temperature_stats[0][0],
              'TAVG': temperature_stats[0][1],
              'TMAX': temperature_stats[0][2]}
    
    # Return a JSON response with the calculated values
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)