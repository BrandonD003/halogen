import logging
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def initialize(db_name):
    global Session
    global Base
    engine = create_engine('sqlite:///' + db_name)
    Session = sessionmaker(bind=engine)

    # create tables
    Base.metadata.create_all(engine)

def get_session():
    return Session()

def get_stat(stat_data, stat_name):
    def _get_stat(stat_data, stat_tokens):
        data = stat_data.get(stat_tokens[0], 0)
        if isinstance(data, dict):
            return _get_stat(data, stat_tokens[1:])
        elif data == 'inf':
            return 0.0
        else:
            return data
    return _get_stat(stat_data, stat_name.split('.'))

def find_one(db_name, fields={}):
    session = get_session()
    rows = session.query(db[db_name]).filter_by(**fields)
    if rows.count() is 0:
        return None
    # return the last row
    return rows[-1]

def count_rows(db_name, fields={}):
    session = get_session()
    return session.query(db[db_name]).filter_by(**fields).count()
    
def remove_row(db_name, fields={}):
    session = get_session()
    n = session.query(db[db_name]).filter_by(**fields).delete()
    session.commit()
    logging.info('removed {0} rows from stats with name {1}'.format(n, fields['name']))
    
def find(db_name, fields={}):
    session = get_session()
    return session.query(db[db_name]).filter_by(**fields)
    
def distinct(db_name, field):
    session = get_session()
    query = session.query(db[db_name]).distinct()
    return set([q.__dict__[field] for q in query])


def print_item(item):
    if item is None:
        print ''
        return

    s = ''
    for (key, value) in item.__dict__.items():
        s+= str(key) + ': ' + str(value) + '\n'
    print s


def add_row(db_name, fields, allow_duplicate=False):
    '''
    adds a new row to a database.

    db_name: database to add a new row to
    fields: dict describing the columns and values of the new row
    allow_duplicate: when False, a new row won't be added
        if there's already a row described by fields

    return: id of row
    '''

    session = get_session()

    # check for duplicates
    if not allow_duplicate:
        row = find_one(db_name, fields)
        if row is not None:
            logging.debug('Found duplicate in \'{0}\'. Returning id {1}'.format(db_name, row.id))
            return row.id

    row = db[db_name](**fields)
    session.add(row)
    session.commit()
    
    logging.debug('adding new row to \'{0}\'. Returning id {1}'.format(db_name, row.id))

    return row.id

def add_knob(fields, knob_name=None):

    # return row name if this knob is already in the db
    row = find_one('knobs', fields={'type': fields['type'], 'knobs': fields['knobs']})
    if row is not None:
        return str(row.name)

    # next_id is the count of this type of knob in <knobs>
    next_id = count_rows(db_name='knobs', fields={'type': fields['type']}) + 1
    if knob_name is None:
        # <type>_<id>
        knob_name = fields['type'] + '_' + str(next_id)

    add_row(db_name='knobs', fields={'type': fields['type'], 'name': knob_name, 'knobs': fields['knobs']})
    logging.info('adding new knob (name: {0} type: {1})'.format(knob_name, fields['type']))
    return knob_name

def insert(db_name, **kwargs):
    session = get_session()

    obj = db[db_name](**kwargs)
    session.add(obj)
    session.commit()


class Knob(Base):
    __tablename__       = 'knobs'
    id                  = Column(Integer, primary_key=True)
    type                = Column(String)
    name                = Column(String)
    knobs               = Column(PickleType)

class Benchmark(Base):
    __tablename__       = 'benchmarks'
    id                  = Column(Integer, primary_key=True)
    name                = Column(String)
    suite               = Column(String)

class Stat(Base):
    __tablename__       = 'stats'
    id                  = Column(Integer, primary_key=True)
    name                = Column(String)
    type                = Column(String)
    benchmark           = Column(String)
    stats               = Column(PickleType)

# add all classes here so we can access them with a string
db = {}
db['benchmarks']  = Benchmark
db['stats']       = Stat
db['knobs']       = Knob

benchmarks = {
    'spec2006': ['perlbench', 'bzip2', 'gcc', 'mcf', 'milc', 'namd',
        'go', 'soplex', 'povray', 'hmmer', 'sjeng', 'libquantum', 
        'h264ref', 'lbm', 'omnetpp', 'astar', 'sphinx3', 'xalancbmk'],
    'splash2': ['barnes', 'fmm', 'ocean-contig', 'ocean-non-contig', 'raytrace',
        'water-nsquared', 'water-spatial', 'fft', 'lu-contig', 'lu-non-contig',
        'radix']}

def add_benchmark(name):
    for suite in benchmarks:
        if name in benchmarks[suite]:
            add_row(db_name='benchmarks', fields={'suite': suite, 'name': name})

def build_benchmark_table():
    for suite in benchmarks:
        for name in benchmarks[suite]:
            add_row(db_name='benchmarks', fields={'suite': suite, 'name': name})
            print 'Successfully added {0} to suite {1}'.format(name, suite)

