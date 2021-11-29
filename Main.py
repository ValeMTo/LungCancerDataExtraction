
from __future__ import print_function

import radiomics
import six
from radiomics import featureextractor


# Getting data
imagePath, maskPath = radiomics.getTestCase('brain1')

if imagePath is None or maskPath is None:
    raise Exception('Error getting testcase!')

# Instantiate data

#TODO: parameter file. The following code extracts data by default options
extractor = featureextractor.RadiomicsFeatureExtractor()

print('Extraction parameters:\n\t', extractor.settings)
print('Enabled filters:\n\t', extractor.enabledImagetypes)
print('Enabled features:\n\t', extractor.enabledFeatures)

result = extractor.execute(imagePath, maskPath)
print('Result type:', type(result))
print('calculated features')
for key, value in six.iteritems(result):
    print('\t', key, ':', value)
