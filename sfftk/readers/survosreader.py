# -*- coding: utf-8 -*-
'''
``sfftk.readers.survosreader``
==============================

Ad hoc reader for SuRVoS segmentation files
'''
from __future__ import print_function

import numbers

import h5py


class SuRVoSSegmentation(object):
    """A SuRVoS segmentation

    SuRVoS segmentations are based on integer annotations. To the best of my understanding
    no textual information is saved in segmentation.
    """

    def __init__(self, fn, dataset='/data', mask_value=1):
        self._fn = fn
        self._dataset = dataset
        self._mask_value = mask_value
        with h5py.File(fn, u'r') as s:
            self._data = s[self._dataset][()].astype(int)
            self._labels = list(map(int, s[self._dataset].attrs["labels"]))
            pass

    @property
    def data(self):
        """The underlying segmentation data"""
        return self._data

    @property
    def shape(self):
        """The shape of the segmentation volume"""
        return self._data.shape

    def segment_ids(self):
        """Returns a frozenset of segment IDs"""
        return frozenset(self._labels)

    def __getitem__(self, item):
        """Get the segment by segment ID

        The segment will have all segment voxels marked with mask_value (default is 1)
        """
        try:
            assert isinstance(item, numbers.Integral)
        except AssertionError:
            raise ValueError("invalid type for segment_id: {}".format(type(item)))
        try:
            assert item in self.segment_ids()
        except AssertionError:
            raise IndexError("segment_id = {}".format(item))
        return (self._data == item) * self._mask_value


def get_data(fn, *args, **kwargs):
    """Main entry point for reader

    We need to return an object with a handle on the segments:

    - each segment is a 3D volume with only that segments voxel values retained
    - we reference each segment on the segmentation through an index-like interface e.g. s1 = Segmentation[1] returns the segmentation with annotation value of '1'

    .. code-block:: python

        s = SuRVoSSegmentation(fn)
        s.segment_ids() # returns a list of segment IDs
        s[s.segment_ids()[0] # gets the first segment

    """
    return SuRVoSSegmentation(fn, *args, **kwargs)
