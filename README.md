# Preprocessors

Preprocessors to remove DICOM masks and generate segmentations.

### Command Usage
```
usage: main.py [-h] --dcm-dir DCM_DIR 
                    --label-dir LABEL_DIR 
                    --target-dir TARGET_DIR 
                    --mode {inspector,segments}

optional arguments:
  -h, --help            show this help message and exit
  --dcm-dir DCM_DIR     The DICOM root directory
  --label-dir LABEL_DIR
                        The JSON labels root directory
  --target-dir TARGET_DIR
                        The destination root directory for outputs
  --mode {inspectors,segments}
```

### Dataset Hierarchy
```
Dataset:
- {LABEL_DIR}
    - *
        - ENDO
            - *.json
- {DCM_DIR}
    - *
        - ENDO
            - *.dcm
```