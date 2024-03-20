from flask import Flask, render_template, request
from data_processing import *
from api_operations import validate_search_query
from apikeys import EXPANDED_APIKEY

app = Flask(__name__)

plots_list = []


@app.route(rule="/", methods=['POST', 'GET'])
def start_menu():
    if request.method == 'POST' and 'search_query' in request.form.keys():
        if request.form['search_query'] != '' and request.form['button'] == 'validate':
            search_query = request.form['search_query']
            records_found = validate_search_query(EXPANDED_APIKEY, search_query)
            if records_found:
                return render_template('index.html',
                                       message=f'Records found: {records_found}', search_query=search_query)
            return render_template('index.html',
                                   message='0 records found or bad request, please check your search syntax',
                                   search_query=search_query)
        if request.form['search_query'] != '' and request.form['button'] == 'run':
            plots_list.clear()
            search_query = request.form['search_query']
            safe_filename, plots = run_button_main_function(EXPANDED_APIKEY, search_query)
            for plot in plots:
                plots_list.append(plot)
            return render_template('index.html',
                                   filename=safe_filename,
                                   search_query=search_query,
                                   plot=plots_list[0])
    if request.method == 'POST' and 'filename' in request.form.keys():
        plots_list.clear()
        file = request.form['filename']
        if file == '':
            return render_template('index.html', search_query='')
        plots = visualize_excel(f'downloads/{file}')
        for plot in plots:
            plots_list.append(plot)
        return render_template('index.html', plot=plots_list[0])
    if request.method == 'POST' and 'button' in request.form.keys():
        visualizations = {
            "grant_funding_by_year": plots_list[0],
            "top_grant_receivers": plots_list[1],
            "top_funders": plots_list[2],
            "top_countries": plots_list[3],
            "average_grant_volume_per_year": plots_list[4],
            "top_grants_by_associated_wos_records": plots_list[5]
        }
        if request.form['button'] in visualizations.keys():
            for k, v in visualizations.items():
                if request.method == 'POST' and request.form['button'] == k:
                    return render_template('index.html', plot=v)
    return render_template('index.html', search_query='')


app.run(debug=True)
