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
    def __init__(self, write_file, append=True):
        self.write_file = write_file
        self.entries = []
        #  if not append:
        #      with open(self.write_file, 'w') as f:
        #          f.write(','.join(self.columns) + '\n')

        print('FuncLatency Datasource initialized. Writing to {}'.format(write_file))
        print('appending: {}'.format(append))
        if append:
            try:
                with open(write_file, 'r') as f:
                    self.entries = json.load(f)
                print(f'{len(self.entries)} Entries loaded from file')
            except Exception as e:
                print(e)
                print(f"Failed to load json file {write_file}")

    def update(self, event):
        self.entries.append(event.delta)

    def dump(self, filename=None):
        filename = filename or self.write_file or 'output.json'
        with open(self.write_file, mode='w') as f:
            json.dump(self.entries, f)
            #  for row in self.entries:
            #      f.write(','.join(row) + '\n')
        print(f'{len(self.entries)} Entries written to file')
        self.entries = []
        return 'Entries Dumped'
