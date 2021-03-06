import json
import os
import cv2
import time
import shutil
import multiprocessing
import numpy as np

from statistic import Statistic
from concurrent.futures import ThreadPoolExecutor


class Mode:

    def __init__(self, name, root_dcm_dir, root_label_dir, root_dst_dir, pipes, filters):
        self._name = name
        self._root_dcm_dir = root_dcm_dir
        self._root_label_dir = root_label_dir
        self._root_dst_dir = root_dst_dir
        self._pipes = pipes
        self._make_patient_dir = True
        self._filters = filters
        self._overwritable_labels = None
        self._overwritable_dir = '/tmp/preprocessors-overwritable'

    @property
    def name(self):
        return self._name

    @property
    def root_dcm_dir(self):
        return self._root_dcm_dir

    @property
    def root_label_dir(self):
        return self._root_label_dir

    @property
    def root_dst_dir(self):
        return self._root_dst_dir

    @property
    def overwritable_labels(self):
        return self._overwritable_labels

    @property
    def overwritable_dir(self):
        return self._overwritable_dir

    def set_overwritable_labels(self, overwritable_labels):
        self._overwritable_labels = overwritable_labels
        if overwritable_labels is not None:
            if not os.path.exists(self.overwritable_dir):
                os.makedirs(self.overwritable_dir, exist_ok=True)

    def finish(self):
        pass

    def apply_pipelines(self, image) -> Statistic or np.ndarray:
        statistics = []
        for pipe in self._pipes:
            ret = pipe.apply(image)
            if isinstance(ret, Statistic):
                statistics.append(ret)
                break
            elif isinstance(ret, np.ndarray):
                image = ret
            else:
                statistics.append(Statistic.from_key_value(f'invalid_pipe_result ({pipe.name})', 1))
                break
        if len(statistics) > 0:
            return Statistic(*statistics)
        return image

    def pipelines(self, target_filepath, image) -> Statistic or None:
        result = self.apply_pipelines(image)
        if isinstance(result, Statistic):
            return result
        cv2.imwrite(target_filepath, result)
        return None

    def run(self, dst_dir, filename, dcm_filepath, label_filepath) -> Statistic or None:
        raise NotImplementedError('mode#run is not implemented.')

    def run_segmentation_pair(self, dcm_dir, label_dir, dst_dir):
        if not os.path.exists(dst_dir) and self._make_patient_dir:
            os.makedirs(dst_dir, exist_ok=True)
        dcm_files = [f for f in os.listdir(dcm_dir)
                     if not os.path.isdir(f) and f.lower().endswith('.dcm') and not f.startswith('.')]
        label_files = [f for f in os.listdir(label_dir)
                       if not os.path.isdir(f) and f.lower().endswith('.json') and not f.startswith('.')]

        files = dcm_files if len(dcm_files) > len(label_files) else label_files
        print(f"Starting to generate {len(files)} segmentation inspector files...")
        statistic = Statistic()
        errors = []
        for filename in files:
            original_filename = filename
            filename = filename.split('.')[0]

            dcm_filepath = os.path.join(dcm_dir, '{}.dcm'.format(filename))
            json_filepath = os.path.join(label_dir, '{}.json'.format(filename))

            dcm_existence = os.path.exists(dcm_filepath)
            json_existence = os.path.exists(json_filepath)
            if not dcm_existence or not json_existence:
                statistic.increase('not_existed', 1)
                if not dcm_existence:
                    print(f"'{dcm_filepath}' is not existed despite its label is existed. "
                          f"The original filename was '{original_filename}'")
                else:
                    print(f"'{json_filepath} is not existed despite its DICOM file is existed. "
                          f"The original filename was '{original_filename}'")
                continue

            with open(json_filepath, 'r', encoding='euc-kr') as f:
                label_json = json.load(f)

            overwritten = False
            if self.overwritable_labels is not None and filename in self.overwritable_labels:
                label = self.overwritable_labels[filename]

                # overwrite json dicts
                if 'phase_id' not in label['image']:
                    label['image']['phase_id'] = label_json['image']['phase_id']
                label_json = label
                # overwrites the json file to tmp directory
                json_filepath = os.path.join(self.overwritable_dir, '{}.json'.format(filename))
                with open(json_filepath, 'w', encoding='euc-kr') as f:
                    json.dump(label_json, f, indent=4, sort_keys=True)
                overwritten = True
                print('{} have been overwritten'.format(filename))

            has_issue = False
            for f in self._filters:
                error = f.apply(filename, json_filepath, label_json)
                if error is not None:
                    errors.append(error)
                    has_issue = True
                    break

            if has_issue:
                continue

            error = self.run(dst_dir, filename, dcm_filepath, json_filepath)
            if error is not None:
                errors.append(error)
                continue

            if overwritten:
                statistic.increase('overwritten', 1)
            else:
                statistic.increase('success', 1)
        if os.path.exists(dst_dir) and len(os.listdir(dst_dir)) == 0:
            shutil.rmtree(dst_dir)
        return Statistic(statistic, *errors)

    def run_job(self, chunk: list):
        statistics = []
        for dcm_subdir, label_subdir in chunk:
            assert dcm_subdir == label_subdir

            dcm_dir = os.path.join(self.root_dcm_dir, dcm_subdir, 'ENDO')
            label_dir = os.path.join(self.root_label_dir, label_subdir, 'ENDO')
            if not os.path.exists(dcm_dir) or not os.path.exists(label_dir):
                print(f"'{dcm_dir}' does not contain endoscopic images")
                statistics.append(Statistic.from_key_value('no_endoscopic_dir', 1))
                continue
            dst_dir = os.path.join(self.root_dst_dir, dcm_subdir)
            statistics.append(self.run_segmentation_pair(dcm_dir, label_dir, dst_dir))
        return Statistic(*statistics)

    def parse_and_preprocess_dirs(self, jobs=-1):
        if jobs == -1:
            n_threads = multiprocessing.cpu_count()
        elif jobs is None:
            n_threads = 1
        else:
            n_threads = jobs

        print('Current mode: {}'.format(self.name))
        print('Gathering DICOM and labels sorted directories...')
        dcm_subdirs = sorted([subdir
                              for subdir in os.listdir(self.root_dcm_dir)
                              if os.path.isdir(os.path.join(self.root_dcm_dir, subdir))])
        label_subdirs = sorted([subdir
                                for subdir in os.listdir(self.root_label_dir)
                                if os.path.isdir(os.path.join(self.root_label_dir, subdir))])
        print("{} DICOMs and {} labels have been gathered.".format(len(dcm_subdirs), len(label_subdirs)))
        assert len(dcm_subdirs) == len(label_subdirs)

        pairs = list(zip(dcm_subdirs, label_subdirs))
        if len(pairs) < n_threads:
            n_threads = len(pairs)
            chunk_size = 1
        else:
            chunk_size = int(len(pairs) / n_threads + 1)

        print('{} threads will be joined for the job.'.format(n_threads))

        start_time = time.time()
        futures = []
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            for i in range(n_threads):
                from_index = i * chunk_size
                to_index = min(len(pairs), (i + 1) * chunk_size)
                chunk = pairs[from_index:to_index]
                future = executor.submit(self.run_job, chunk)
                futures.append(future)
        end_time = time.time()

        statistics = []
        for future in futures:
            statistics.append(future.result())

        self.finish()
        print("All jobs have finished.")
        print(f"Total {(end_time - start_time):.2f} seconds have elapsed")
        statistic = Statistic(*statistics)
        return statistic
