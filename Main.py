import pylidc as pl
import nrrd
import numpy

import six
import radiomics

import sys
import os
import itk

from csv import writer

pid = "LIDC-IDRI-0003"
dirName = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\manifest-1639521588960\\LIDC-IDRI\\LIDC-IDRI-0003\\1.3.6.1.4.1.14519.5.2.1.6279.6001.101370605276577556143013894866\\1.3.6.1.4.1.14519.5.2.1.6279.6001.170706757615202213033480003264"
imagePath = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\conversionNRRD\\image.nrrd"
maskPath = "C:\\NECSTCamp\\LungCancerDataExtraction\\data\\conversionNRRD\\label.nrrd"

def extractMask(imagePath, maskPath,pid, numSlice):
    scans = pl.query(pl.Scan).filter(pl.Scan.patient_id == pid)
    scan = scans.first()

    ann = pl.query(pl.Annotation).first()

    booleanMask = ann.boolean_mask()
    bbox = ann.bbox()
    booleanMask = booleanMask.astype('int8')
    booleanMask = numpy.swapaxes(booleanMask,0,1)


    mask = numpy.zeros((512, 512, numSlice))

    padding = [-7, 8, 29] #LIDC-IDRI-0003
    mask[bbox[1].start+padding[1]:bbox[1].stop+padding[1], bbox[0].start+padding[0]:bbox[0].stop+padding[0], bbox[2].start+padding[2]:bbox[2].stop++padding[2]] = booleanMask
    mask = numpy.flip(mask, 1)


    header = nrrd.read_header(imagePath)

    nrrd.write(maskPath, mask, header)

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

    seriesFound = False
    for uid in seriesUID:
        seriesIdentifier = uid
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
#co

extractor = radiomics.featureextractor.RadiomicsFeatureExtractor()
convertDicomToNRRD(dirName, imagePath)
extractMask(imagePath, maskPath, pid, len(os.listdir(dirName))-1)

print('Extraction parameters:\n\t', extractor.settings)
print('Enabled filters:\n\t', extractor.enabledImagetypes)
print('Enabled features:\n\t', extractor.enabledFeatures)

result = extractor.execute(imagePath, maskPath)

print("Opening file...")
file = open('featureExtraction.csv', 'w')
writer = writer(file)

print('calculating features...')
for key, value in six.iteritems(result):
    data = [str(key), str(value)]
    writer.writerow(data)
print('Saved features')
file.close()

