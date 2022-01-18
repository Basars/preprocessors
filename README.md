# Preprocessors

Preprocessors to remove DICOM masks and generate segmentations.

### Prepare Dependencies
```
pip install opencv-python pydicom matplotlib pandas
```

### Command Usage
```
usage: main.py [-h] --dcm-dir DCM_DIR 
                    --label-dir LABEL_DIR
                    --target-dir TARGET_DIR
                    --mode {inspector,mask,roi,spreadsheet,cvat}
                    [--filterable-csv-file FILTERABLE_CSV_FILE]
                    [--filterable-dataset-type {train,valid,test}]
                    [--filterable-keep-issues]
                    [--new-shape NEW_SHAPE]
                    [--crop-image CROP_IMAGE]
                    [--jobs JOBS]

This is a preprocessor to remove DICOM masks and generate segmentations and
its inspectors, masks and ROIs.

optional arguments:
  -h, --help            show this help message and exit
  --dcm-dir DCM_DIR     The DICOM root directory
  --label-dir LABEL_DIR
                        The JSON labels root directory
  --target-dir TARGET_DIR
                        The destination root directory for outputs
  --mode {inspector,mask,roi,spreadsheet,cvat}
                        inspector    Generate four-in-one images to compare masks, overlay 
                                     and noise-eliminated with original image
                        mask         Generate binary masks that will be used as Dataset
                                     for segmentation models
                        roi          Generate region-of-interest images that will be used 
                                     as Dataset for classification model
                        spreadsheet  Generate CSV files that contains encrypted
                                     patients identifiers and its file name
                        cvat         Generate a XML file that contains segmentation mask polygons
                                     to be uploaded on CVAT
  --filterable-csv-file FILTERABLE_CSV_FILE
                        The CSV file to be used for filtering broken datasets out
  --filterable-dataset-type {train,valid,test}
                        The type of dataset source directory for querying filterable CSV file
  --filterable-keep-issues
                        A flag to keep issued rows in filterable CSV file
  --new-shape NEW_SHAPE
                        WxH. Resize the output image with desired width and height - e.g.) 224x224
  --crop-image CROP_IMAGE
                        X:Y,W:H. Crop the output image to desired rectangle - e.g.) 90:0,480:480
  --jobs JOBS           Number of workers
```
```
usage: assign.py [-h] --csv-file CSV_FILE 
                      --source-dirs SOURCE_DIRS
                      --target-dir TARGET_DIR

This is an assigner for assigning dataset validation job fairly.

optional arguments:
  -h, --help            show this help message and exit
  --csv-file CSV_FILE   The assignees CSV file
  --source-dirs SOURCE_DIRS
                        dir1,dir2,dir3,..  The source directories to be assigned to
  --target-dir TARGET_DIR
                        The destination directory where the assigned directory will be located
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

### CSV Formats
#### Filterable CSV File
```csv
filterable-dataset-type,patient_id,image_id,assignee,issue

train,00000001,00000001_0001,John,TRUE
valid,00000002,00000002_0001,James,FALSE
test,00000003,00000003_0001,Alice,FALSE
```
`TRUE` means the row have an issue, and the image will be truncated in the result.

#### Assignees CSV File
```csv
John,James,Alice
,,
00000001,00000002,00000003
00000004,00000005,
,00000006,
```
Proper assignees CSV file is required to separate the dataset fairly.
```
Result:
- John
    - 00000001
        - *.jpg
    - 00000004
        - *.jpg
- James
    - 00000002
        - *.jpg
    - 00000005
        - *.jpg
    - 00000006
        - *.jpg
- Alice
    - 00000003
        - *.jpg
```