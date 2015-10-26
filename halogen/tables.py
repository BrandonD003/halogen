import db_utils

tables = {'processor': [], 'core': []}

def initialize():
  # clear the tables
  tables['processor'] = {}
  tables['core'] = {}

  # get the processors from the db
  processors = db_utils.find('knobs', fields={'type': 'processor'})

  # header row
  tables['processor'] = [['name']]

  # add one row for each processor
  for p in processors:
    tables['processor'].append([p.name])

  # get the cores from the db
  cores = db_utils.find('knobs', fields={'type': 'core'})

  # header row
  tables['core'] = [['name']]

  # add one row for each core
  for c in cores:
    tables['core'].append([c.name])

def set_tables(p_cols, c_cols):
    # initialize() will add these
    if p_cols.count('name') != 0:
        p_cols.remove('name')
    if c_cols.count('name') != 0:
        c_cols.remove('name')

    # removes all columns except 'name'
    initialize()

    for col in p_cols:
        add_column('processor', col)

    for col in c_cols:
        add_column('core', col)

def remove_column(table, knob_name):
    # find the index of the matching header column
    i = tables[table][0].index(knob_name)

    # remove the column from all rows in table_data
    for row in tables[table]:
        row.pop(i)

def get_column(table, knob_name):
    # get all knobs
    knobs = db_utils.find('knobs', fields={'type': table})

    # build the new column
    new_col = [knob_name]
    new_col += map(lambda k: k.knobs.get(knob_name, ''), knobs)

    return new_col

def add_column(table, knob_name):
    new_col = get_column(table, knob_name)

    # append each column element to it's row
    map(lambda r,c: r.append(c), tables[table], new_col)
