from flask import Flask, jsonify
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(bind=engine)

app = Flask(__name__)

### Routes
'''
* `/api/v1.0/precipitation`

  * Query for the dates and precipitation observations from the last year.

  * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.

  * Return the json representation of your dictionary.
'''
@app.route("/api/v1.0/precipitation")
def precipitation():
    last_year_prcp = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date > '2016-08-23').all()
    prcp_dict = dict(last_year_prcp)
    return jsonify(prcp_dict)



'''
* `/api/v1.0/stations`

  * Return a json list of stations from the dataset.
'''
@app.route("/api/v1.0/stations")
def stations():
    all_stations = session.query(Station.name).all()
    stations_list = [station[0] for station in all_stations]
    stations_dict = {'stations': stations_list}
    return jsonify(stations_dict)


'''
* `/api/v1.0/tobs`

  * Return a json list of Temperature Observations (tobs) for the previous year
'''
@app.route("/api/v1.0/temperature")
def temperature():
    last_year_tobs = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date > '2016-08-23').all()
    tobs_dict = dict(last_year_tobs)
    return jsonify(tobs_dict)


'''
* `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

  * Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

  * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

  * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
'''
def calc_temps_range(start_date, end_date):
    summary_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    return summary_stats[0]

def temp_summary_dict(summary_stats):
    TMIN = summary_stats[0]
    TAVG = summary_stats[1]
    TMAX = summary_stats[2]
    response_dict = {'TMIN': TMIN,
                    'TAVG': TAVG,
                    'TMAX': TMAX}
    return response_dict

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    response_dict = calc_temps_range(start, end)
    summary_stats = calc_temps_range(start, end)
    response_dict = temp_summary_dict(summary_stats)
    return jsonify(response_dict)


def calc_temps_start(start_date):
    summary_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).all()
    return summary_stats[0]


@app.route('/api/v1.0/<start>')
def start(start):
    summary_stats = calc_temps_start(start)
    response_dict = temp_summary_dict(summary_stats)
    return jsonify(response_dict)


if __name__ == "__main__":
    app.run()
