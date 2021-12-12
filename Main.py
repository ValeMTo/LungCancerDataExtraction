import pylidc as pl
import nrrd
import numpy

import logging
import six
import radiomics

import sys
import os
import itk

import SimpleITK as sitk

from csv import writer

#TODO: change pylidc library
"""
def resampleMask(imagepath, maskpath, resMaskPath):
    rif = sitk.ResampleImageFilter()
    rif.SetReferenceImage(imagepath)
    rif.SetOutputPixelType(maskpath.GetPixelID())
    rif.SetInterpolator(sitk.sitkNearestNeighbor)
    resMask = rif.Execute(maskpath)

    sitk.WriteImage(resMask, resMaskPath, True)  # True enables compression when saving the resampled mask
"""
#TODO: substitute the function in the executable part
def extractMask(maskPath, pid, numSlice):
    scans = pl.query(pl.Scan).filter(pl.Scan.patient_id == pid)
    print(scans.count())
    scan = scans.first()

    print(scan.patient_id,
          scan.pixel_spacing,
          scan.slice_thickness,
          scan.slice_spacing)

    # The input come from base and path in scan class in pylidc library
    ann = pl.query(pl.Annotation).first()

    booleanMask = ann.boolean_mask()  # numpy.ndarray
    booleanMask = booleanMask.astype('int8')
    bbox = ann.bbox()  # tuple


    mask = numpy.zeros((512, 512, numSlice))
    mask[bbox[0].start:bbox[0].stop, bbox[1].start:bbox[1].stop, bbox[2].start:bbox[2].stop] = booleanMask
    nrrd.write(maskPath, mask)


def convertDicomToNRRD(dirName, outFileName):
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

extractor = radiomics.featureextractor.RadiomicsFeatureExtractor()

dirName = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\manifest-1639326440222\\LIDC-IDRI\\LIDC-IDRI-0350\\1.3.6.1.4.1.14519.5.2.1.6279.6001.402240049299350560004923763412\\1.3.6.1.4.1.14519.5.2.1.6279.6001.121108220866971173712229588402"
imagePath = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\conversionNRRD\\image.nrrd"
convertDicomToNRRD(dirName, imagePath)

pid = 'LIDC-IDRI-0350'
#tmpPath = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\conversionNRRD\\tmp.nrrd"
maskPath = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\conversionNRRD\\label.nrrd"
extractMask(maskPath, pid, len(os.listdir(dirName))-1)

image = itk.imread(imagePath)
print(type(image))
mask = itk.imread(maskPath)
boundingBox, correctedMask =radiomics.imageoperations.checkMask(image, mask, correctMask=True)
itk.imwrite(correctedMask, maskPath)


#resampleMask(imagePath, tmpPath, maskPath)

print('Extraction parameters:\n\t', extractor.settings)
print('Enabled filters:\n\t', extractor.enabledImagetypes)
print('Enabled features:\n\t', extractor.enabledFeatures)

result = extractor.execute(imagePath, maskPath)

file = open('featureExtraction.csv', 'w')
writer = writer(file)

print('calculating features')
print('Result type:', type(result))
for key, value in six.iteritems(result):
    data = [str(key), str(value)]
    writer.writerow(data)
print('saved features')
file.close()

