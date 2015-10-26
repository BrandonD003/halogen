from flask import make_response, jsonify, render_template, request, Response
import json
import logging
import yaml

import forms
import tables
import charts
import db_utils
import halogen

benchmark_choices = tuple()
processor_choices = tuple()
stat_choices = {}

def initialize():
    global benchmark_choices
    global processor_choices
    global stat_choices
    benchmark_choices = halogen.get_benchmark_choices()
    processor_choices = halogen.get_processor_choices()
    stat_choices      = halogen.get_stat_choices()

def index():
    global benchmark_choices
    global processor_choices
    global stat_choices
    form = forms.StatForm()
    form.benchmarks.choices = benchmark_choices
    form.runs.choices = processor_choices

    return render_template('halogen.html', stat_choices=stat_choices, form=form)

def get_chart():
    stat_name, benchmarks, procs, normalize, average, hmean = halogen.process_chart_request(request)

    chart = charts.Chart(stat_name=stat_name, 
                         benchmarks=benchmarks, 
                         runs=procs, 
                         normalize=normalize,
                         average=average,
                         hmean=hmean)

    response              = make_response(chart.to_json())
    response.content_type = 'application/json'
    return response

def get_csv():
    stat_name, benchmarks, procs, normalize, average, hmean = halogen.process_chart_request(request)
    chart = charts.Chart(stat_name=stat_name, 
                         benchmarks=benchmarks, 
                         runs=procs, 
                         normalize=normalize,
                         average=average,
                         hmean=hmean)

    return Response(chart.to_csv(),
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                             "attachment;filename=test.csv"})

def save_tables():
    # print table, request.args.get('colName', None, type=str)

    p_cols = yaml.load(request.args.get('pCols'))
    c_cols = yaml.load(request.args.get('cCols'))
    tables.set_tables(p_cols=p_cols, c_cols=c_cols)

    # return an empty response
    response = jsonify({})
    return response

def get_col():
    # print table, request.args.get('colName', None, type=str)

    table = request.args.get('table', type=str)
    col = tables.get_column(table, request.args.get('colName', type=str))

    response              = make_response(json.dumps(col))
    response.content_type = 'application/json'
    return response

def knob_tables():
    return render_template('tables.html', tables=tables.tables)
