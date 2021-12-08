

import glob
from subprocess import call
import re

import sys
import os
import getopt

import numpy

import dicom
import nrrd

import logging
import six
import radiomics


class DICOM_to_NRRD:
    def __init__(self):
        self.BACKGROUND = -2048
        self.AIR = -1024
        self.KEY_WORD_FLODER = 'Fleck\w+'
        self.KEY_WORD_FILE = 'Fleck\w+.nrrd'

    def batch_dicom_to_nrrd(self, dicom_root, nrrd_root):
        """Iterativly convert all dicom data in dicom_root to nrrd
        """
        dicom_files_dirs = glob.glob(dicom_root + '/*')
        for dicom_subject in dicom_files_dirs:
            subject = re.search(self.KEY_WORD_FLODER, dicom_subject).group()
            nrrd_subject = nrrd_root + '/' + subject
            self.dicom_to_nrrd(dicom_subject, nrrd_subject)

    def batch_preprocess(self, input_folder, output_folder, padding=20):
        """Pad all images in the input folder
        """
        input_files = glob.glob(input_folder + '/*')
        for input_path in input_files:
            subject_name = re.search(self.KEY_WORD_FILE, input_path).group()
            output_path = output_folder + '/' + subject_name

            data, options = nrrd.read(input_path)
            data, options = self.pad_upper(data, options, padding)
            data, options = self.filter_background_to_air(data, options)

            print ('write ' + output_path)
            nrrd.write(output_path, data, options)  # too slow in Python

    def dicom_to_nrrd(self, dicom_root_dir, nrrd_files_dir):
        """Transfer dicom volumn into nrrd format
        0. Uncompress the dicom image
        1. Load each dicom images in the dicom_files_dir
        2. Save the load image into numpy.array format (rows, columns, depth)
        3. Write the numpy.array out as a nrrd file
        """
        TEMP_FILE = '/Users/chunwei/Downloads/_TEMP'
        SYSTEM_COMMAND = 'gdcmconv -w {0} {1}'

        for i, subject_folder in enumerate(glob.glob(dicom_root_dir + '/*')):
            nrrd_file = nrrd_files_dir + '/'\
                + re.search(self.KEY_WORD_FLODER, subject_folder).group()\
                + '_%02d.nrrd' % (i + 1)
            print ('Processing ' + nrrd_file)

            if not os.path.exists(nrrd_files_dir):
                os.makedirs(nrrd_files_dir)

            data_3d = None

            dicom_files = glob.glob(subject_folder + '/*')
            for j, dicom_file in enumerate(dicom_files):
                # prompt
                ratio = 100 * float(j)/float(len(dicom_files))
                sys.stdout.write('\r%d%%' % ratio)
                sys.stdout.flush()

                # uncompress the dicom image
                command = SYSTEM_COMMAND.format(dicom_file, TEMP_FILE)
                call(command.split(), shell=False)

                # concatenate dicom image layer by layer
                ds = dicom.read_file(TEMP_FILE)
                data = ds.pixel_array
                data_3d = self.concatenate_layers(data_3d, data)  # bottom up

            # get nrrd options
            options = self.load_dicom_options(TEMP_FILE, len(dicom_file))

            # transpose the data
            data_3d = numpy.swapaxes(data_3d, 0, 1)
            data_3d = data_3d[:, :, ::-1]

            # write the stack files in nrrd format
            nrrd.write(nrrd_file, data_3d, options)


    def load_dicom_options(self, file_name, number_of_dicoms):
        ds = dicom.read_file(file_name)

        options = dict()
        options['type'] = 'short'
        options['dimension'] = 3
        options['space'] = 'left-posterior-superior'
        options['space directions'] = [[ds.PixelSpacing[0], 0, 0],
                                       [0, ds.PixelSpacing[1], 0],
                                       [0, 0, 0.25]]
        options['kinds'] = ['domain', 'domain', 'domain']
        # options['encoding'] = 'gzip'
        options['space origin'] = ds.ImagePositionPatient

        return options

    def concatenate_layers(self, data_3d, data):
        try:
            return numpy.dstack((data_3d, data))
        except:
            return data

    # def filter_background_to_air(self, input_file_name, output_file_name):
    def filter_background_to_air(self, data, options):
        """Change value -2048 (background) to -1024 (air)
        """
        numpy.place(data, data <= self.BACKGROUND, self.AIR)
        return (data, options)

    # def pad_upper(self, input_file_name, output_file_name, padding):
    def pad_upper(self, data, options, padding):
        """Pad some layers in upper, so airway segmenter can work later
        """
        # data, options = nrrd.read(input_file_name)
        rows, columns, depths = data.shape

        # numpy.fill
        for i in range(padding):
            padding_layer = [[self.AIR] * columns for j in range(rows)]
            data = self.concatenate_layers(data, padding_layer)

        options['sizes'][2] += padding  # update depths
        return (data, options)


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

dicom_root = ''
nrrd_root = ''

DICOM_to_NRRD().batch_dicom_to_nrrd(dicom_root, nrrd_root)

# Instantiate data

#TODO: parameter file. The following code extracts data by default options
#parameter of first order: pyradiomics -> radiomic feature -> first order statistics && gray level co-occurrence matrix (GMLM) features
# Do i need a filter?
# Try all filters and add the option to use them as requested

extractor = radiomics.featureextractor.RadiomicsFeatureExtractor()

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
