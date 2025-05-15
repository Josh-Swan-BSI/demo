from flask import Flask, render_template, request, abort
import pandas as pd
from visualisations import dashboard
import logging
import datetime

'''
AUTHOR: Josh Swan
DATE: 07-06-2023

This file is the main file for loading the OPSS flask application. Here the routes of the website are managed and the data
for the visualisations are loaded in. 
'''

#INITIALISE THE APP
app = Flask(__name__)
SECRET_TOKEN = "5018ca65a141dfe18fbe375c453ff51bce6f33da4cd11fef51d5d11f51553f13"

@app.before_request
def check_access_token():

    # Skip token check for static files
    if request.path.startswith('/static/') or request.path.startswith("/dash/"):
        return

    # Check for token in request headers or query parameters
    token = request.headers.get('X-Access-Token') or request.args.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden

# Create a separate logger for errors
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)

# Error Logging configuration
error_handler = logging.FileHandler('./logs/OPSS_app.log')
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# Create a separate logger for usage
usage_logger = logging.getLogger('usage_logger')
usage_logger.setLevel(logging.INFO)

# Usage Logging configuration
usage_handler = logging.FileHandler('./logs/OPSS_usage.log')
usage_handler.setLevel(logging.INFO)
usage_formatter = logging.Formatter('%(asctime)s %(message)s')
usage_handler.setFormatter(usage_formatter)
usage_logger.addHandler(usage_handler)

@app.errorhandler(500)
def internal_error(exception):
    # Log the full exception traceback to the error log
    error_logger.error(f"An error occurred: {exception}", exc_info=True)
    return render_template('500.html'), 500

@app.before_request
def log_request_info():
    # Filter requests to log only website routes (exclude static files and other background requests)
    if request.endpoint not in ['static'] and not request.path.startswith('/dash/'):
        # Get client IP address
        user_ip = request.remote_addr
        # Get the accessed URL
        requested_url = request.url
        # this only logs the IP address from the portal, not the user's device IP address
        usage_logger.info(f"User with IP: {user_ip} accessed {requested_url} at {datetime.datetime.now(datetime.timezone.utc)}")


# WEBSITE ROUTES
"""All routes point back to the main layout template as at the time of writing they were placeholders for other page links.
They are purely aesthetic and serve no real purpose as they are left over from a previous more developed version"""
@app.route('/')
def home():
    return render_template('new_layout.html', dash_url='/dash/')
@app.route('/standards')
def standards():
    return render_template('new_layout.html', dash_url='/dash/')
@app.route('/services')
def services():
    return render_template('new_layout.html', dash_url='/dash/')
@app.route('/sectors')
def sectors():
    return render_template('new_layout.html', dash_url='/dash/')
@app.route('/topics')
def topics():
    return render_template('new_layout.html', dash_url='/dash/')
@app.route('/about')
def about():
    return render_template('new_layout.html', dash_url='/dash/')

# LOAD DATA FROM CSV
def load_data():
    try:
        # table 1 data
        df = pd.read_csv(r"./data/Phase_2C_meta_table_gov(compressed)_v2.csv", encoding="utf-8")

        # #Cleaning dates by removing timestamps
        df['Published'] = pd.to_datetime(df['Published'], format="%d/%m/%Y", dayfirst=True)
        df['Published'] = df['Published'].dt.date

        #data that powers the sunburst
        references = pd.read_csv(r"./data/next_version_dataset_more_version11(compressed).csv", encoding="utf-8").astype(str)
        # references = pd.read_csv(r"C:\repos\OPSS_DevOps\data\filtered_records.csv", encoding="utf-8").astype(str)

        # 0 width spaces are added to make standards unique so they occupy their own segment in the sunburst
        def add_zero_width_space(text, index):
            zero_width_space = '\u200B' # this might be causing an error?
            return text + zero_width_space * index

        references['standard'] = references.groupby('standard').cumcount().apply(lambda x: add_zero_width_space('', x)) + references[
            'standard']

        references["standard"] = references["standard"].str.replace("(inaccessible)", "")
        references["parent"] = references["parent"].str.replace("(inaccessible)", "")

        df["Identifier"] = df["Identifier"].str.replace("(inaccessible)", "")

        return [df, references]

    except Exception as e:
        print("Error loading data: ", e)
        return [pd.DataFrame(), pd.DataFrame()]

#RUN THE APP,
if __name__ == "__main__": # <-- don't do this on the python anywhere!
    data = load_data()
    df = data[0]
    references = data[1]

    dash_app = dashboard(app, df, references, routes="/dash/")
    app.run(debug=True, port=5001) # this line is only enabled on localhost testing