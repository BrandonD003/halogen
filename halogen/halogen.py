from flask import request 
import logging
import ordereddict
import yaml

import forms
import db_utils

def select_procs(stat_name, proc_names):
  '''
  turn a list of processor names into a list of names to access the stats_db with.
  if <stat_name> is a core stat, turn each processor name into '<proc_name> <core_name>'
  for each core in the processor. 
  if <stat_name> is a process stat, turn each processor name into '<proc_name> process_0'
  '''
  # find the type of stat
  stat_type = stat_name.split('.')[0]

  # list of names to access the stats db with
  db_names = []

  if stat_type == 'processor':
    return proc_names
  elif stat_type == 'core':
      for p in proc_names:
        # find how many cores p has
        row = db_utils.find_one('knobs', fields={'type': 'processor', 'name': p})
        if row is None:
            logging.error('problem finding {0} in the knobs db'.format(p))
            continue
        for core_name in row.knobs['core_names']:
            # <processor_name> <core_name>
            db_names.append(p + ' ' + core_name)
      return db_names
  elif stat_type == 'process':
      # right now only 1 process per processor is supported
      for p in proc_names:
        # <processor_name> process_0
        db_names.append(p + ' process_0')
      return db_names
  else:
      logging.error('unknown stat type: {0}'.format(stat_type))
      return proc_names

def select_benchmarks(names):
    '''
    return <names> but with '<suite>.all' replaced with all benchmarks from <suite>
    and 'all' replaced with all benchmarks.
    '''
    if names is None:
        return []

    bm_list = []
    for name in names:
        # add all benchmarks from a suite
        if '.all' in name:
            # strip '.all' from the end of name
             suite = name.rstrip('.all')
            rows = db_utils.find('benchmarks', fields={'suite': suite})
            # add benchmarks matching suite
            bm_list += [b.name for b in rows]

        # add all benchmarks
        elif name == 'all':
            rows = db_utils.find('benchmarks', fields={})
            return [b.name for b in rows]

        # add an individual benchmark by name
        elif bm_list.count(name) == 0:
            bm_list.append(name)
    return bm_list

def process_chart_request(request):
    stat_name  = request.args.get('statName', None, type=str)
    benchmarks = select_benchmarks(yaml.load(request.args.get('benchmarks')))
    procs      = select_procs(stat_name, yaml.load(request.args.get('runs')))

    if request.args.get('normalize') == 'true':
        normalize = True
    else:
         normalize = False

    if request.args.get('average') == 'true':
        average = True
    else:
        average = False

    if request.args.get('hmean') == 'true':
        hmean = True
    else:
        hmean = False

        logging.debug('statName: ' + stat_name)
        logging.debug('benchmarks: ' + str(benchmarks))
        logging.debug('procs: ' + str(procs))
        logging.debug('normalize: ' + str(normalize))
        logging.debug('average: ' + str(average))
        logging.debug('hmean: ' + str(hmean))
        logging.debug(request.args)

    return (stat_name, benchmarks, procs, normalize, average, hmean)

def get_stat_choices():
    ''' 
    return a (nested) dict of stats: {display_name: submit_name}
    '''
    # use the last core and processor stats
        core_stats    = db_utils.find('stats', fields={'type': 'core'})[0].stats
        proc_stats    = db_utils.find('stats', fields={'type': 'processor'})[0].stats
        process_stats = db_utils.find('stats', fields={'type': 'process'})[0].stats
        stat_choices  = {'core': core_stats, 'processor': proc_stats, 'process': process_stats}

    # replace the stat value with the submit_name (hierarchical name joined by '.')
    def replace_value(d, name=None):
        for k,v in d.items():
            if name is None:
                new_name = k
            else:
                new_name = name + '.' + k

            if isinstance(v, dict):
                d[k] = replace_value(v, new_name)
            else:
                d[k] = new_name
        return d

    # order each dict/sub-dict
    def order(d):
        for k,v in d.items():
            if isinstance(v, dict):
                d[k] = order(v)
        return ordereddict.OrderedDict(sorted(d.items()))

    return order(replace_value(stat_choices))

def get_processor_choices():
    ''' 
    returns a sorted tuple list of processor types ((<knob0.id>, <knob0.name>), (<knob1.id>, <knob1.name>), ...)
    '''
    # get all knobs
    rows = db_utils.find('knobs', fields={'type': 'processor'})

    # make them into tuples of (pid, display_name)
    processors = tuple([(r.name, r.name) for r in sorted(rows, key=lambda row: row.name)])

    logging.debug(processors)
    return processors

def get_benchmark_choices():
    '''
    returns a nested tuple list of suites and benchmarks.
    ((<suite_name0>, (<bm0.name>, <bm0.name>), (<bm1.name>, <bm1.name>), ...), (<suite_name1>, ...))
    '''
    suites = db_utils.distinct('benchmarks', field='suite')
    benchmarks = (('all', 'all'),)
    for suite in suites:
        bms = db_utils.find('benchmarks', fields={'suite': suite})
        # first tuple of each suite is for selecting the whole suite
        bm_tuple = ((suite + '.all', 'all'),)
        # for each benchmar, append (b.name, b.name)
        bm_tuple += tuple([(b.name, b.name) for b in bms])
        # add the suite to the master list of benchmarks
        benchmarks += ((suite, (bm_tuple)),)

    # logging.debug(benchmarks)
    return benchmarks
