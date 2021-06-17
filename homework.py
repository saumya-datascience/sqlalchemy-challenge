import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start_date><br/>"
        f"/api/v1.0/temp_start_end/<start_date>/<end_date>"
    )

@app.route("/api/v1.0/precipitation")
def preci():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query 
    prcps=session.query(Measurement.date, func.avg(Measurement.prcp)).group_by(Measurement.date)\
    .filter(Measurement.date>='2016-08-23').order_by(Measurement.date).all()

    

    session.close()

    # Convert list of tuples into dictionary
    precipitation_dict = {date: prcp for date, prcp in prcps}
    

    return jsonify(precipitation_dict)    

@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query to Return a JSON list of stations from the dataset.
    results=session.query(Station.station).all()
    #close Session
    session.close()

    # Convert the list of tuples into list
    station_list=list(np.ravel(results))

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")  
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for 
    # the most recent 12 months of data.

    recent_date=session.query(Measurement.date).filter_by(station='USC00519281')\
        .order_by(Measurement.date.desc()).first()
    tobs_for12months=session.query(Measurement.date,Measurement.tobs)\
        .filter(Measurement.date>='2016-08-18').all()
    #close Session
    session.close()  

    #convert the list of tupules into list
    tobs_list=[]
    for tob in tobs_for12months:
        tobs_list.append(tob.tobs)

    #Return a JSON list of temperature observations (TOBS) for that year. 
    return jsonify(tobs_for12months) 

@app.route("/api/v1.0/temp/<start_date>")
def only_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    avg_temp=session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start_date).all()
    lowest=session.query(Measurement.tobs).filter(Measurement.date>=start_date)\
    .order_by(Measurement.tobs).first()
    highest=session.query(Measurement.tobs).filter(Measurement.date>=start_date)\
    .order_by((Measurement.tobs).desc()).first()
    
    
    dict={"average temp":avg_temp[0][0],"lowest temp":lowest[0],"highest temp":highest[0]}
    print(dict)
    
    return jsonify(dict)


@app.route("/api/v1.0/temp_start_end/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    avg_temp=session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start_date,Measurement.date<=end_date).all()
    lowest=session.query(Measurement.tobs).filter(Measurement.date>=start_date,Measurement.date<=end_date)\
    .order_by(Measurement.tobs).first()
    highest=session.query(Measurement.tobs).filter(Measurement.date>=start_date,Measurement.date<=end_date)\
    .order_by((Measurement.tobs).desc()).first()
    dict={"average temp":avg_temp[0][0],"lowest temp":lowest[0],"highest temp":highest[0]}
          
    return jsonify(dict) 


if __name__ == '__main__':
    app.run(debug=True)
  



