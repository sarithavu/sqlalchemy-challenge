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

    # Convert the results to a dictionary
    precipitation_dict = precipitation_data.set_index('date')['prcp'].to_dict()

    print(precipitation_dict)

    # Return the JSON representation of the dictionary
    return jsonify({ 'date': 'prcp' })

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Retrieve stations from the dataset
    
    # Return a JSON list of stations
    return jsonify([ 'station1', 'station2' ])

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the most-active station for temperature observations
    # Return a JSON list of temperature observations
    return jsonify([ { 'date': 'temp' } ])

# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_range(start, end=None):
    # Calculate TMIN, TAVG, and TMAX for the specified date range
    # Return a JSON list of the calculated values
    return jsonify({ 'TMIN': 0, 'TAVG': 0, 'TMAX': 0 })

if __name__ == "__main__":
    app.run(debug=True)