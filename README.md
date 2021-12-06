# Preprocessors

Preprocessors to remove DICOM masks and generate segmentations.

### Prepare Dependencies
```
pip install opencv-python pydicom matplotlib
```

### Command Usage
```
usage: main.py [-h] --dcm-dir DCM_DIR 
                    --label-dir LABEL_DIR 
                    --target-dir TARGET_DIR 
                    --mode {inspectors,masking,roi} 
                    [--jobs JOBS]

This is a preprocessor to remove DICOM masks and generate segmentations and its inspectors.

optional arguments:
  -h, --help            show this help message and exit
  --dcm-dir DCM_DIR     The DICOM root directory
  --label-dir LABEL_DIR
                        The JSON labels root directory
  --target-dir TARGET_DIR
                        The destination root directory for outputs
  --mode {inspectors,masking,roi}
  --jobs JOBS           Number of workers
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