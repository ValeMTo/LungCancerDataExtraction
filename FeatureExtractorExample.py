
from __future__ import print_function

import radiomics
import six
from radiomics import featureextractor
import logging
from csv import writer

#Using the notebook "Hello Radiomics example"

#Setting up logging

# Regulate verbosity of radiomics during the extraction:
# 30: log messages of level "Warning, errors and critical" --Default
# 20: info too
# 10: debug too
radiomics.setVerbosity(logging.WARNING)

logger = radiomics.logger
logger.setLevel(logging.WARNING) #Levels are the same of above
#There is the possibility to save the log in a file

# Getting data
imagePath, maskPath = radiomics.getTestCase('test_wavelet_64x64x64')

if imagePath is None or maskPath is None:
    raise Exception('Error getting testcase!')

# Instantiate data

extractor = featureextractor.RadiomicsFeatureExtractor()

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
