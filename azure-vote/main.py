from flask import Flask, request, render_template
import os
import random
import redis
import socket
import sys
import logging
#from applicationinsights.logging import LoggingHandler
from datetime import datetime

# App Insights
# TODO: Import required libraries for App Insights
from applicationinsights import TelemetryClient
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
#from opencensus.ext.azure.trace_exporter import AzureExporter
#from opencensus.trace.samplers import ProbabilitySampler
#from opencensus.trace.tracer import Tracer
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.log_exporter import AzureEventHandler

# Logging
#logger = # TODO: Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string='InstrumentationKey=c902824f-d43b-42f6-8b71-ca0bf9dc4d08'))
logger.setLevel(logging.INFO)


# Metrics
#exporter = # TODO: Setup exporter
#exporter = metrics_exporter.new_metrics_exporter(
#  enable_standard_metrics=True,
#  connection_string='InstrumentationKey=c902824f-d43b-42f6-8b71-ca0bf9dc4d08')

# Tracing
#tracer = # TODO: Setup tracer
tracer = TelemetryClient('InstrumentationKey=c902824f-d43b-42f6-8b71-ca0bf9dc4d08;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/')
tracer.track_trace('My trace with context')
tracer.flush()
#tracer = Tracer(
#    exporter=AzureExporter(
#        connection_string='InstrumentationKey=c902824f-d43b-42f6-8b71-ca0bf9dc4d08'),
#    sampler=ProbabilitySampler(1.0),
#)

app = Flask(__name__)

# Requests
#middleware = # TODO: Setup flask middleware
#middleware = FlaskMiddleware(
#    app,
#    exporter=AzureExporter(connection_string="InstrumentationKey=c902824f-d43b-42f6-8b71-ca0bf9dc4d08"),
#    sampler=ProbabilitySampler(rate=1.0),
#)
# Load configurations from environment or config file
app.config.from_pyfile('config_file.cfg')

if ("VOTE1VALUE" in os.environ and os.environ['VOTE1VALUE']):
    button1 = os.environ['VOTE1VALUE']
else:
    button1 = app.config['VOTE1VALUE']

if ("VOTE2VALUE" in os.environ and os.environ['VOTE2VALUE']):
    button2 = os.environ['VOTE2VALUE']
else:
    button2 = app.config['VOTE2VALUE']

if ("TITLE" in os.environ and os.environ['TITLE']):
    title = os.environ['TITLE']
else:
    title = app.config['TITLE']

# Redis Connection
r = redis.Redis()

# Change title to host name to demo NLB
if app.config['SHOWHOST'] == "true":
    title = socket.gethostname()

# Init Redis
if not r.get(button1): r.set(button1,0)
if not r.get(button2): r.set(button2,0)

@app.route('/', methods=['GET', 'POST'])
def index():
#    with tracer.span(name='hello'):
#        print('Hello, World!')
  

    if request.method == 'GET':

        # Get current values
        vote1 = r.get(button1).decode('utf-8')
        # TODO: use tracer object to trace cat vote
        #tracer.span(name='Cat Vote')
        logger.info('Cat Vote')
        #print('Cat votes = ' + vote1)

        vote2 = r.get(button2).decode('utf-8')
        # TODO: use tracer object to trace dog vote
        #tracer.span(name='Dog vote')
        logger.info('Dog vote')
        #print('Dog votes = ' + vote2)

        # Return index with values
        return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

    elif request.method == 'POST':
        vote = request.form['vote']
        vote1 = r.get(button1).decode('utf-8')
        vote2 = r.get(button2).decode('utf-8')

        if vote == 'reset':
            # Empty table and return results
            r.set(button1,0)
            r.set(button2,0)
            return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

        if vote == 'Cats':    
            r.incr(vote,1)            
            properties = {'custom_dimensions': {'Cats Vote': vote1}}
            # TODO: use logger object to log cat vote
            logger.info('Cat vote')
            #tracer.span('Cat vote')
            print('Cat votes = ' + vote1)
            return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

        if vote == 'Dogs': 
            r.incr(vote,1)            
            properties = {'custom_dimensions': {'Dogs Vote': vote2}}
            # TODO: use logger object to log dog vote
            logger.info('Dog vote')
            #tracer.span('Dog vote')
            print('Dog votes = ' + vote2)
            return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

        else:

            # Insert vote result into DB
            #vote = request.form['vote']
            #r.incr(vote,1)

            # Get current values
            #vote1 = r.get(button1).decode('utf-8')
            #vote2 = r.get(button2).decode('utf-8')

            # Return results
            return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

if __name__ == "__main__":
    # comment line below when deploying to VMSS
    # app.run() # local
    # uncomment the line below before deployment to VMSS
    app.run(host='0.0.0.0', threaded=True, debug=True) # remote
