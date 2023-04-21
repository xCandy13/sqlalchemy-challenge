import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startyyyy-mm-dd<br/>"
        f"/api/v1.0/startyyyy-mm-dd/endyyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate most recent 12 months
    recent = session.query(measurement).order_by(measurement.date.desc()).first()
    one_year = dt.datetime.strptime(recent.date, '%Y-%m-%d')-dt.timedelta(days=365)

    """Return a JSON representation of our precipitation analysis (last 12 months of data)
    with 'date' as the key and 'prcp' as the value"""
    # Query precipitation data
    Precipitation = session.query(measurement.date, func.max(measurement.prcp))\
                    .filter(measurement.date >= one_year)\
                    .filter(measurement.date <= recent.date)\
                    .group_by(measurement.date)\
                    .order_by(measurement.date)\
                    .all()

    session.close()

    # Create a dictionary
    precip_analysis = []
    for date, prcp in Precipitation:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_analysis.append(precip_dict)

    return jsonify(precip_analysis)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station IDs"""
    # Query stations
    station_list = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_list))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most active station
    Active = session.query(measurement.station, func.count(measurement.station))\
            .group_by(measurement.station)\
            .order_by(func.count(measurement.station).desc())\
            .all()
    most_active = Active[0][0]
    
    # Calculate most recent 12 months
    recent = session.query(measurement).order_by(measurement.date.desc()).first()
    one_year = dt.datetime.strptime(recent.date, '%Y-%m-%d')-dt.timedelta(days=365)

    """Return a JSON representation of our temperatures for the most active station
    (last 12 months of data) with 'date' as the key and 'tobs' as the value"""
    # Query temperature data
    Temperature = session.query(measurement.date, measurement.tobs)\
                        .filter(measurement.date>=one_year)\
                        .filter(measurement.date<=recent.date)\
                        .filter(measurement.station == most_active).all()

    session.close()

    # Create a dictionary
    temp_analysis = []
    for date, tobs in Temperature:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_analysis.append(temp_dict)

    return jsonify(temp_analysis)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, max, and average temperature after a specified start date"""
    # Query stations
    calcs = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
                        .filter(measurement.date>=start)\
                        .all()
    
    session.close()

    # Convert list of tuples into normal list
    [TMIN,TMAX,TAVG] = list(np.ravel(calcs[0]))

    return jsonify({"TMIN":TMIN,"TMAX":TMAX, "TAVG":TAVG})


@app.route("/api/v1.0/<start>/<end>")
def starttoend(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, max, and average temperature after a specified start date
    and before a specified end date"""
    # Query stations
    calcs = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
                        .filter(measurement.date>=start)\
                        .filter(measurement.date<=end)\
                        .all()
    
    session.close()

    # Convert list of tuples into normal list
    [TMIN,TMAX,TAVG] = list(np.ravel(calcs[0]))

    return jsonify({"TMIN":TMIN,"TMAX":TMAX, "TAVG":TAVG})


if __name__ == "__main__":
    app.run(debug=True)
