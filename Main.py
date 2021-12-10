from configparser import ConfigParser

import pylidc as pl
import nrrd
import numpy

import logging
import six
import radiomics

import sys
import os
import itk
#https://itk.org/ITKExamples/src/IO/GDCM/ReadDICOMSeriesAndWrite3DImage/Documentation.html for conversion

#TODO: change pylidc library

""""
parser = argparse.ArgumentParser(description="Read DICOM Series And Write 3D Image.")
parser.add_argument(
    "dicom_directory",
    nargs="?",
    help="If DicomDirectory is not specified, current directory is used",
)
parser.add_argument("output_image", nargs="?")
parser.add_argument("series_name", nargs="?")
args = parser.parse_args()

# current directory by default
dirName = "."
if args.dicom_directory:
    dirName = args.dicom_directory
"""

#TODO: move config functions to another file
def createConfigureFile(user):
    config_object = ConfigParser()

    config_object["dicom"]={
        "path": "",
        "warn": "true"
    }

    with open('C:\\Users\\'+str(user)+'\\pylidc.conf', 'w') as conf:
        config_object.write(conf)

    print("The config file is created")

def changePathDicom(user, newPath):
    config_object = ConfigParser()
    config_object.read('C:\\Users\\'+str(user)+'\\pylidc.conf')

    dicomInfo = config_object["dicom"]
    dicomInfo["path"] = newPath

    with open('C:\\Users\\'+str(user)+'\\pylidc.conf', 'w') as conf:
        config_object.write(conf)

    print("The config file has been modified")

def convertDicomToNRRD(dirName):
    PixelType = itk.ctype("signed short")
    Dimension = 3

    ImageType = itk.Image[PixelType, Dimension]

    namesGenerator = itk.GDCMSeriesFileNames.New()
    namesGenerator.SetUseSeriesDetails(True)
    namesGenerator.AddSeriesRestriction("0008|0021")
    namesGenerator.SetGlobalWarningDisplay(False)
    namesGenerator.SetDirectory(dirName)

    seriesUID = namesGenerator.GetSeriesUIDs()

    if len(seriesUID) < 1:
        print("No DICOMs in: " + dirName)
        sys.exit(1)

    print("The directory: " + dirName)
    print("Contains the following DICOM Series: ")
    for uid in seriesUID:
        print(uid)

    seriesFound = False
    for uid in seriesUID:
        seriesIdentifier = uid
        """"
        if args.series_name:
            seriesIdentifier = args.series_name
            seriesFound = True
        """
        print("Reading: " + seriesIdentifier)
        fileNames = namesGenerator.GetFileNames(seriesIdentifier)

        reader = itk.ImageSeriesReader[ImageType].New()
        dicomIO = itk.GDCMImageIO.New()
        reader.SetImageIO(dicomIO)
        reader.SetFileNames(fileNames)
        reader.ForceOrthogonalDirectionOff()

        writer = itk.ImageFileWriter[ImageType].New()
        outFileName = os.path.join(dirName, seriesIdentifier + ".nrrd")
        """"
        if args.output_image:
            outFileName = args.output_image
        """
        writer.SetFileName(outFileName)
        writer.UseCompressionOn()
        writer.SetInput(reader.GetOutput())
        print("Writing: " + outFileName)
        writer.Update()

        if seriesFound:
            break

#Setting up logging
radiomics.setVerbosity(logging.WARNING)

#TODO: analyse with DEBUG and INFO verbosity
logger = radiomics.logger
logger.setLevel(logging.WARNING)

handler = logging.FileHandler(filename='testLog.txt', mode = 'w')
formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


#TODO: add input (treat DICOM images)
# Getting data

# Instantiate data

#TODO: parameter file. The following code extracts data by default options
#parameter of first order: pyradiomics -> radiomic feature -> first order statistics && gray level co-occurrence matrix (GMLM) features
# Do i need a filter?
# Try all filters and add the option to use them as requested

createConfigureFile("valer")
changePathDicom("valer", "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\manifest-1638790098115\\LIDC-IDRI")

pid = 'LIDC-IDRI-0306'
scans = pl.query(pl.Scan).filter(pl.Scan.patient_id == pid)
print(scans.count())

scan = scans.first()

print(scan.patient_id,
      scan.pixel_spacing,
      scan.slice_thickness,
      scan.slice_spacing)

ann = pl.query(pl.Annotation).first()
vol = ann.scan.to_volume()

mask = ann.boolean_mask()
bbox = ann.bbox()

maskReady = numpy.array(mask.shape, dtype = numpy.bool_)

itkVol = itk.GetImageFromArray(maskReady.astype(numpy.bool_))
imageType = itk.Image[itk.B, 3]

writerType = itk.ImageFileWriter[imageType]
writer = writerType.New()
filename = 'C:\\NECSTCamp\\LungCancerDataExtraction\\data\\manifest-1638790098115\LIDC-IDRI\\LIDC-IDRI-0306\\01-01-2000-NA-CT LUNG SCREEN-56413\\NA-18860\\testdata.nrrd'
writer.SetFileName(filename)
writer.SetInput(itkVol)
writer.Update()

extractor = radiomics.featureextractor.RadiomicsFeatureExtractor()

print('Extraction parameters:\n\t', extractor.settings)
print('Enabled filters:\n\t', extractor.enabledImagetypes)
print('Enabled features:\n\t', extractor.enabledFeatures)

dirName = "C:\\NECSTCamp\LungCancerDataExtraction\data\dicom"
imagePath = convertDicomToNRRD(dirName)


result = extractor.execute(imagePath, filename)
print('Result type:', type(result))
print('calculated features')
for key, value in six.iteritems(result):
    print('\t', key, ':', value)



#TODO: save the data on a cvs file
#TODO: Visualize features - matrix and graphics

