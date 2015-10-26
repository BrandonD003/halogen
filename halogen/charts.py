import logging
import json
import db_utils

class Series():
    def __init__(self, name, data=None, labels=None):
        self.name               = name
        self.data               = data[:]
        self.labels             = labels[:]

    def add_average(self):
        if len(self.data) == 0:
            return
        avg = reduce(lambda x, y: x + y, self.data)/float(len(self.data))
        self.data.append(avg)
        self.labels.append(avg)

    def add_hmean(self):
        # ignore 0 values because it likely means the run didn't complete
        data = [x for x in self.data if x > 0]
        if len(data) == 0:
            return
        hmean = float(len(data))/reduce(lambda x, y: x + 1.0/y, data)
        self.data.append(hmean)
        self.labels.append(hmean)

    def to_json(self):
        data_list = []
        for i in xrange(len(self.data)):
            data_list.append({'y': self.data[i], 'label': self.labels[i]})
        return {'name': self.name, 'data': data_list}

        
class Chart():
    def __init__(self, stat_name, benchmarks, runs, normalize, average, hmean):
        self.stat_name          = stat_name
        self.benchmarks         = benchmarks

        self.stat               = ''
        self.stat_long          = ''
        self.x_axis_title       = ''
        self.series             = []

        self.build(runs)

        if average:
            self.add_average()
        elif hmean:
            self.add_hmean()

        if normalize:
            self.normalize()

    def build(self, runs):
        # remove the hierarchy from stat_name and just use the final piece
        self.stat                   = self.stat_name.split('.')[-1]
        self.stat_long              = self.stat_name
        self.x_axis_title           = 'benchmarks'

        # split stat_name at the first '.'
        (type, name) = self.stat_name.split('.', 1)

        # create a Series for each entry
        for entry in runs:
            # series data, elements aligned to self.benchmarks
            data = []

            # append the stat value for each benchmark. 0 if not found
            for benchmark in self.benchmarks:
                # query the db
                row = db_utils.find_one('stats', fields={'name': entry, 
                                                         'type': type, 
                                                         'benchmark': benchmark})

                # append 0 and continue if a row wasn't found
                if not row:
                    data.append(0)
                    continue

                # append the stat value
                data.append(db_utils.get_stat(row.stats, name))

            # create a new Series for this runs entry and append to self.series
            self.series.append(Series(name=entry, data=data, labels=data))

        # logging.debug("Building chart. stat_name: {0}, benchmarks: {1}, runs: {2}, series: {3}".format(self.stat_name, self.benchmarks, runs, self.series))

    def add_average(self):
        for i in xrange(len(self.series)):
            self.series[i].add_average()
        self.benchmarks.append('average')

    def add_hmean(self):
        for i in xrange(len(self.series)):
            self.series[i].add_hmean()
        self.benchmarks.append('hmean')

    def normalize(self):
        for i in reversed(xrange(len(self.series))):
            for j in xrange(len(self.benchmarks)):
                self.series[i].data[j] = self.series[i].data[j] / self.series[0].data[j]

    def to_json(self):
        return json.dumps({
                'stat': self.stat,
                'stat_long': self.stat_long,
                'series': [s.to_json() for s in self.series],
                'benchmarks': self.benchmarks,
                'x_axis_title': self.x_axis_title
                })

    def to_csv(self):
        csv = ''
        # use series names as column headings
        for s in self.series:
            csv += ', ' + s.name
        csv += '\n'

        # add one row per benchmark
        for i, b in enumerate(self.benchmarks):
            csv += b
            for s in self.series:
                csv += ', ' + str(s.data[i])
            csv += '\n'

        return csv

