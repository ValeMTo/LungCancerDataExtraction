
from __future__ import print_function

import SimpleITK

import os
from subprocess import call
import tempfile
import radiomics
import six
import logging
import pydicom
import glob

def dcmImageToNRRD(inputDICOMImageDir, tempDir):
  scanNRRDFile = os.path.join(tempDir, "image.nrrd")
  print(scanNRRDFile)
  if not os.path.isfile(scanNRRDFile):
    call(['plastimatch', 'convert', '--input',
          inputDICOMImageDir, '--output-img', scanNRRDFile])
  return scanNRRDFile

def dcmSEGToNRRDs(inputSEG, tempDir):
  segmentsDir = os.path.join(tempDir, 'Segments')
  if not os.path.isdir(segmentsDir):
    os.mkdir(segmentsDir)
  call(['segimage2itkimage', '--inputDICOM',
        inputSEG, '--outputDirectory', segmentsDir])
  return glob.glob(os.path.join(segmentsDir, "*nrrd"))

class DICOMMetadataAccessor:
  def __init__(self, dcmFileName):
    self.dcm = pydicom.read_file(dcmFileName)

  def getInstanceUID(self):
    return self.dcm.SOPInstanceUID

  def getSeriesDescription(self):
    return self.dcm.SeriesDescription

  def getSeriesInstanceUID(self):
    return self.dcm.SeriesInstanceUID

class SEGMetadataAccessor(DICOMMetadataAccessor):
  def __init__(self, segFileName):
    DICOMMetadataAccessor.__init__(self, segFileName)

    if self.dcm.SOPClassUID != '1.2.840.10008.5.1.4.1.1.66.4':
      raise ValueError(
        "SEGMetadataAccessor: DICOM object is not Segmentation!")

  def getSegmentSegmentationTypeCode(self, segmentNumber):
    try:
      return self.dcm.SegmentSequence[segmentNumber].SegmentedPropertyTypeCodeSequence[0]
    except BaseException:
      return None

  def getTrackingIdentifier(self, segmentNumber):
    try:
      return self.dcm.SegmentSequence[segmentNumber].TrackingIdentifier
    except BaseException:
      return None

  def getTrackingUniqueIdentifier(self, segmentNumber):
    try:
      return self.dcm.SegmentSequence[segmentNumber].TrackingUID
    except BaseException:
      return None

  def getSegmentDescription(self, segmentNumber):
    try:
      return self.dcm.SegmentSequence[segmentNumber].SegmentDescription
    except BaseException:
      return None

  def getSegmentAnatomicLocationCode(self, segmentNumber):
    try:
      return self.dcm.SegmentSequence[segmentNumber].AnatomicRegionSequence[0]
    except BaseException:
      return None

#Setting up logging
radiomics.setVerbosity(logging.WARNING)

#TODO: analyse with DEBUG and INFO verbosity
logger = radiomics.logger
logger.setLevel(logging.WARNING)

handler = logging.FileHandler(filename='testLog.txt', mode = 'w')
formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


#TODO: add input (treat DICOM images). Need inputDICOMImageDir, inputSEG, outputDir

#----------------------------------------------------INPUTS---------------------------------------------------------------------------------
#Path to the directory with the input DICOM series.
inputDICOMImageDir = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\manifest-1638790098115\\LIDC-IDRI\\LIDC-IDRI-0306\\01-01-2000-NA-CT-LUNG-SCREEN-56413\\NA-18860"
#Path to the input segmentation defined as a DICOM Segmentation object.
inputSEG=""
#Path to the directory for saving the resulting DICOM file.
#outputDir=""


#Creates a temporary directory in the most secure manner possible.
# There are no race conditions in the directory’s creation.
# The directory is readable, writable, and searchable only by the creating user ID.
tempDir = tempfile.mkdtemp()

logger.info("Temporary directory: " + tempDir)
print("Temporary directory: " + tempDir)

# Using Plastimatch for DICOM image volume reconstruction.
print("Using Plastimatch for DICOM image volume reconstruction.")
print(inputDICOMImageDir)
inputImage = dcmImageToNRRD(inputDICOMImageDir, tempDir)
print(inputImage)

# convert segmentation into segments
inputSegments = dcmSEGToNRRDs(inputSEG, tempDir)
if len(inputSegments) == 0:
  print("No segments found. Cannot compute features.")
  logger.error("No segments found. Cannot compute features.")

# Path to the dictionary mapping pyradiomics feature names to the IBSI defined features.
featuresDir = os.path.join(tempDir, 'Features')
if not os.path.isdir(featuresDir):
  featuresDictPath=tempfile.mkdtemp()

# initialize Metadata for the individual features
featuresDictPath = os.path.join(featuresDictPath, "featuresDict.tsv")

#?????????????????????
#m = TID1500Metadata(featuresDictPath)

# find a valid DICOM file in the input image DICOM directory
dicomImage = None
for f in os.listdir(inputDICOMImageDir):
    try:
        pydicom.read_file(os.path.join(inputDICOMImageDir, f))
        dicomImage = os.path.join(inputDICOMImageDir, f)
        break
    except BaseException:
        continue

if dicomImage is None:
    logger.error(
        "Input DICOM image directory does not seem to contain any valid DICOM files!")
    print("Input DICOM image directory does not seem to contain any valid DICOM files!")

imageMetadataAccessor = DICOMMetadataAccessor(
os.path.join(inputDICOMImageDir, f))
segmentationMetadataAccessor = SEGMetadataAccessor(inputSEG)

#????????????????????????????????????????
#pyradiomicsVersion = None

for inputSegment in inputSegments:
    logger.debug("Processing segmentation file %s", inputSegment)
    print("Processing segmentation file %s", inputSegment)
    segmentNumber = os.path.split(inputSegment)[-1].split('.')[0]

    try:
        logger.debug("Initializing extractor")
        print("Initializing extractor")
        extractionSettings = {
            "geometryTolerance": float(1e-6),  # Default 1e-6
            "correctMask": False
        }
        #TODO: define parameters
        #Actually using default parameters
        extractor = featureextractor.RadiomicsFeatureExtractor()

        #params = []
        #if args.parameters is not None:
        #    params = [args.parameters]
        #extractor = featureextractor.RadiomicsFeatureExtractor(*params, **extractionSettings)

    except Exception:
        logger.error(
            'Initialization of the pyradimics feature extraction failed.', exc_info=True)
        print('Initialization of the pyradimics feature extraction failed.', exc_info=True)

    featureVector = extractor.execute(
        inputImage, inputSegment, int(segmentNumber))

    if len(featureVector) == 0:
        logger.error("No features extracted!")
        print("No features extracted!")

    #TODO: save the data on a cvs file instead of printing on stdout
    print('Extraction parameters:\n\t', extractor.settings)
    print('Enabled filters:\n\t', extractor.enabledImagetypes)
    print('Enabled features:\n\t', extractor.enabledFeatures)

    print('Result type:', type(featureVector))
    print('calculated features')
    for key, value in six.iteritems(featureVector):
        print('\t', key, ':', value)


#TODO: parameter file. The following code extracts data by default options
#parameter of first order: pyradiomics -> radiomic feature -> first order statistics && gray level co-occurrence matrix (GMLM) features
# Do i need a filter?
# Try all filters and add the option to use them as requested

#TODO: Visualize features - matrix and graphics
