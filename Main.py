
from __future__ import print_function

import radiomics
import six
import logging
from radiomics import featureextractor

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
imagePath, maskPath = radiomics.getTestCase('brain1')

if imagePath is None or maskPath is None:
    raise Exception('Error getting testcase!')

# Instantiate data

#TODO: parameter file. The following code extracts data by default options
#parameter of first order: pyradiomics -> radiomic feature -> first order statistics && gray level co-occurrence matrix (GMLM) features
# Do i need a filter?
# Try all filters and add the option to use them as requested

extractor = featureextractor.RadiomicsFeatureExtractor()

print('Extraction parameters:\n\t', extractor.settings)
print('Enabled filters:\n\t', extractor.enabledImagetypes)
print('Enabled features:\n\t', extractor.enabledFeatures)

result = extractor.execute(imagePath, maskPath)
print('Result type:', type(result))
print('calculated features')
for key, value in six.iteritems(result):
    print('\t', key, ':', value)

#TODO: save the data on a cvs file
#TODO: Visualize features - matrix and graphics
