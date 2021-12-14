import pandas as pd

from statistic import Statistic
from .filter import Filter


class FilterableFilter(Filter):

    def __init__(self, csv_file, dataset_type):
        super(FilterableFilter, self).__init__()

        self.dataset_type = dataset_type

        df = pd.read_csv(csv_file, header=None, dtype=str)
        df.columns = ['dataset_type', 'patient_id', 'image_id', 'assignee', 'issue']
        df.drop(columns='assignee', inplace=True)

        mask = df['dataset_type'] == dataset_type
        self.df = df[mask].copy()

    def apply(self, filename, label_filepath, label_json) -> Statistic or None:
        patient_id = filename.split('_')[0]

        mask = (self.df['patient_id'] == patient_id) & (self.df['image_id'] == filename) & (self.df['issue'] == 'TRUE')
        row = self.df[mask]['issue']
        if len(row) > 0:
            return Statistic.from_key_value('dataset_filtered', 1)
        return None
