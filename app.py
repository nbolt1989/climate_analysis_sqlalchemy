# ---Climate App: Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed ---

# Import Flask and other dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    # I need to list out all paths
    return (
        f"<h1>Welcome to the homepage!</h1><br/>" 
        f"<strong>The available routes are:</strong><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br>"
        f'<br>'
        f'<strong>date format yyyy-mm-dd</strong><br>'
        f"/api/v1.0/searchdate/<start><br/>" 
        f'<strong>date format yyyy-mm-dd</strong><br>'
        f"/api/v1.0/daterange/<start>/<end><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
   #create a session link
    session = Session(engine)
    #go back twelve months like in my Jupyter nb
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    #query last 12 months of precipation data; same as Jupyter nb
    last12_precip = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()
    #close session
    session.close()
    # Create a dictionary from the row data and append to a list of measurements_data; this will be similar to the titanic passenger activity
    # Empty list to append a dict into
    measurement_data = []
    for date, prcp in last12_precip:
        measurement_dict = {}
        measurement_dict["Date"] = date
        measurement_dict["Precipitation"] = prcp
        measurement_data.append(measurement_dict)
    return jsonify(measurement_data)

    print("Server received request for 'Precipitation' page...")
    
@app.route('/api/v1.0/stations')
def stations():
    #create a session link
    session = Session(engine)
    #query a list of the stations
    stations = session.query(measurement.station).group_by(measurement.station).all()
    #close the session
    session.close()
    station_list = []
    for i in stations:
        station_dict = {}
        station_dict["Station"] = i
        station_list.append(station_dict)

    print(f"Welcome to the list of stations<br/>")
    return jsonify(station_list)


@app.route('/api/v1.0/tobs')
def temps():
    session = Session(engine)
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    #Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(measurement.station,measurement.date,measurement.tobs).\
    filter(measurement.date >= one_year_ago).\
    filter(measurement.station == 'USC00519281').all()
    session.close()
    stationtemp_list = []
    for a,b,c in results:
        stl_dict = {}
        stl_dict['Station'] = a
        stl_dict['Date']=b
        stl_dict['Temperature'] = c
        stationtemp_list.append(stl_dict)

    return jsonify(stationtemp_list)

@app.route('/api/v1.0/searchdate/<start>')
def start(start):
    session = Session(engine)
    high_low_avg = session.query(measurement.date,\
            func.min(measurement.tobs),\
            func.max(measurement.tobs),\
            func.avg(measurement.tobs)).\
            filter(func.strftime("%Y-%m-%d", measurement.date) >=start).\
            group_by(measurement.date).all()

    dates = []                       
    for a,b,c,d in high_low_avg:
        hla_date_dict = {}
        hla_date_dict["Date"] = a
        hla_date_dict["Low Temp"] = b
        hla_date_dict["Max Temp"] = c
        hla_date_dict["Avg Temp"] = d
        dates.append(hla_date_dict)
    session.close()
    return jsonify(dates)

@app.route('/api/v1.0/daterange/<start>/<end>')
def startend(start, end):
    session = Session(engine)
    range_high_low_avg = session.query(measurement.date,\
            func.min(measurement.tobs),\
            func.max(measurement.tobs),\
            func.avg(measurement.tobs)).\
            filter(func.strftime("%Y-%m-%d", measurement.date) >= start).\
            filter(func.strftime("%Y-%m-%d", measurement.date) <= end).\
            group_by(measurement.date).all()
    
    range_dates=[]
    for a,b,c,d in range_high_low_avg:
        range_date_dict = {}
        range_date_dict["Date"] = a
        range_date_dict["Low Temp"] = b
        range_date_dict["Max Temp"] = c
        range_date_dict["Avg Temp"] = d
        range_dates.append(range_date_dict)   
    session.close()
    return jsonify(range_dates)




# 4. Define main behavior
if __name__ == '__main__':
    app.run(debug=True)
