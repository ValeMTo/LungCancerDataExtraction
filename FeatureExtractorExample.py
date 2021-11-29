
from __future__ import print_function

import radiomics
import six
from radiomics import featureextractor

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
imagePath, maskPath = radiomics.getTestCase('brain1')

if imagePath is None or maskPath is None:
    raise Exception('Error getting testcase!')

# Instantiate data

#TODO: parameter file. The following code extracts data by default options
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
