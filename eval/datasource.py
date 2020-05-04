from abc import ABC, abstractmethod
import logging
import json

logger = logging.getLogger('datasource')
fhdlr = logging.FileHandler('write.log', mode='w')
fhdlr.terminator=''
logger.addHandler(fhdlr)


class DataSource(ABC):

    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def dump(self):
        pass


class FuncLatencyDatasource(DataSource):
    def __init__(self, write_file, append=True, write_size=None):
        self.write_size = write_size or 1000
        self.write_cd = self.write_size
        self.write_file = write_file
        self.entries = []
        if append:
            try:
                self.entries = json.load(write_file)
            except:
                print(f"Failed to load json file {write_file}")
        #  if not append:
        #      with open(self.write_file, 'w') as f:
        #          f.write(','.join(self.columns) + '\n')

        print('Func Latency Datasource initialized. Writing to {}'.format(write_file))
        print('write-size: {}, appending: {}'.format(self.write_size, append))

    def update(self, event):
        print(event.delta)
        self.entries.append(event.delta)

    def dump(self, filename=None):
        filename = filename or self.write_file or 'output.csv'
        with open(self.write_file, mode='w') as f:
            json.dump(self.entries, f)
            #  for row in self.entries:
            #      f.write(','.join(row) + '\n')
        self.entries = []
        return 'Entries Dumped'
