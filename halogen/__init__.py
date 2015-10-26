from flask import Flask
import argparse
import logging

import views
import db_utils

def initialize():

    # parse arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-d', '--debug', 
                           action='store_true',
                           help='dump debug messages to logfile')
    argparser.add_argument('--logfile', 
                           help='file to dump log messages', 
                           default='halogen.log')
    argparser.add_argument('--db', 
                           required=True,
                           help='database name to use')
    args = argparser.parse_args()

    # enable logging debug messages
    level=logging.INFO
    if args.debug:
        DEBUG = True
        level=logging.DEBUG

    logging.basicConfig(level=level,
                        format='%(asctime)s [%(levelname)s] %(funcName)s :: %(message)s')

    db_utils.initialize(args.db)

    views.initialize()
    tables.initialize()
    tables.set_tables(p_cols=['core_names'], c_cols=[])

    return args

def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    app.config.from_object('halogen.settings')
    app.add_url_rule(
        '/', view_func=views.index, methods=['GET'])
    app.add_url_rule(
        '/get_chart/', view_func=views.get_chart, methods=['GET'])
    app.add_url_rule(
        '/get_csv/', view_func=views.get_csv, methods=['GET'])
    app.add_url_rule(
        '/halogen/tables/', view_func=views.knob_tables, methods=['GET'])
    app.add_url_rule(
        '/save_tables/', view_func=views.save_tables, methods=['GET'])
    app.add_url_rule(
        '/get_col/', view_func=views.get_col, methods=['GET'])

    def is_dict(d):
        return isinstance(d, dict)
    app.jinja_env.tests['is_dict'] = is_dict

    return app


def run_server():
    args = initialize()
    app = create_app()
    if args.debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')
