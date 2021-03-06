# -*- coding: utf-8 -*-
# test_formats.py
"""
sfftk.formats modules unit tests
"""
from __future__ import division

import numbers
import os
import sys
from io import StringIO

import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.unittests import Py23FixTestCase

from . import TEST_DATA_PATH
# from .. import schema
from ..core.parser import parse_args
from ..formats import am, seg, map, mod, stl, surf, survos

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-03-28"
__updated__ = '2018-02-14'


class TestFormats(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestFormats, cls).setUpClass()
        # path to test files
        cls.segmentations_path = os.path.join(TEST_DATA_PATH, 'segmentations')
        # schema version
        cls.schema_version = schema.SFFSegmentation().version

    def read_am(self):
        """Read .am files"""
        if not hasattr(self, 'am_file'):
            self.am_file = os.path.join(self.segmentations_path, 'test_data.am')
            self.am_segmentation = am.AmiraMeshSegmentation(self.am_file)

    def read_seg(self):
        """Read .seg files"""
        if not hasattr(self, 'seg_file'):
            self.seg_file = os.path.join(self.segmentations_path, 'test_data.seg')
            self.seg_segmentation = seg.SeggerSegmentation(self.seg_file)

    def read_map(self):
        """Read .seg files"""
        if not hasattr(self, 'map_file'):
            self.map_file = os.path.join(self.segmentations_path, 'test_data.map')
            self.map_segmentation = map.MapSegmentation([self.map_file])

    def read_map_multi(self):
        """Read .map multi files"""
        if not hasattr(self, 'map_multi0_file'):
            self.map_multi0_file = os.path.join(self.segmentations_path, 'test_data_multi0.map')
            self.map_multi1_file = os.path.join(self.segmentations_path, 'test_data_multi1.map')
            self.map_multi2_file = os.path.join(self.segmentations_path, 'test_data_multi2.map')
            self.map_multi_segmentation = map.MapSegmentation(
                [self.map_multi0_file, self.map_multi1_file, self.map_multi2_file]
            )

    def read_mod(self):
        """Read .mod files"""
        if not hasattr(self, 'mod_file'):
            self.mod_file = os.path.join(self.segmentations_path, 'test_data.mod')
            # self.mod_file = '/Users/pkorir/data/for_debugging/mod/input_file.mod' # -25 multiple
            # self.mod_file = '/Users/pkorir/data/segmentations/mod/test10.mod' # -23
            self.mod_segmentation = mod.IMODSegmentation(self.mod_file)

    def read_stl(self):
        """Read .stl files"""
        if not hasattr(self, 'stl_file'):
            self.stl_file = os.path.join(self.segmentations_path, 'test_data.stl')
            self.stl_segmentation = stl.STLSegmentation([self.stl_file])

    def read_stl_multi(self):
        """Read .stl multi files"""
        if not hasattr(self, 'stl_multi0_file'):
            self.stl_multi0_file = os.path.join(self.segmentations_path, 'test_data_multi0.stl')
            self.stl_multi1_file = os.path.join(self.segmentations_path, 'test_data_multi1.stl')
            self.stl_multi2_file = os.path.join(self.segmentations_path, 'test_data_multi2.stl')
            self.stl_multi_segmentation = stl.STLSegmentation(
                [self.stl_multi0_file, self.stl_multi1_file, self.stl_multi2_file]
            )

    def read_surf(self):
        """Read .surf files"""
        if not hasattr(self, 'surf_file'):
            self.surf_file = os.path.join(self.segmentations_path, 'test_data.surf')
            self.surf_segmentation = surf.AmiraHyperSurfaceSegmentation(self.surf_file)

    def read_survos(self):
        """Read SuRVoS .h5 files"""
        if not hasattr(self, 'survos_file'):
            self.survos_file = os.path.join(self.segmentations_path, 'test_data.h5')
            self.survos_segmentation = survos.SuRVoSSegmentation(self.survos_file)

    # read
    def test_am_read(self):
        """Read an AmiraMesh (.am) segmentation"""
        self.read_am()
        # assertions
        self.assertIsInstance(self.am_segmentation.header, am.AmiraMeshHeader)
        self.assertIsInstance(self.am_segmentation.segments, list)
        # self.assertIsInstance(self.am_segmentation.segments[0], am.AmiraMeshSegment)

    def test_seg_read(self):
        """Read a Segger (.seg) segmentation"""
        self.read_seg()
        # assertions
        self.assertIsInstance(self.seg_segmentation.header, seg.SeggerHeader)
        self.assertIsInstance(self.seg_segmentation.segments, list)
        self.assertIsInstance(self.seg_segmentation.segments[0], seg.SeggerSegment)

    def test_map_read(self):
        """Read an EMDB Map mask (.map) segmentation"""
        self.read_map()
        # assertions
        self.assertIsInstance(self.map_segmentation.header, map.MapHeader)
        self.assertIsInstance(self.map_segmentation.segments, list)
        self.assertIsInstance(self.map_segmentation.segments[0], map.MapSegment)

    def test_mod_read(self):
        """Read an IMOD (.mod) segmentation"""
        self.read_mod()
        # assertions
        self.assertIsInstance(self.mod_segmentation.header, mod.IMODHeader)
        self.assertIsInstance(self.mod_segmentation.segments, list)
        self.assertIsInstance(self.mod_segmentation.segments[0], mod.IMODSegment)

    def test_stl_read(self):
        """Read a Stereo Lithography (.stl) segmentation"""
        self.read_stl()
        # assertions
        self.assertIsInstance(self.stl_segmentation.header, stl.STLHeader)
        self.assertIsInstance(self.stl_segmentation.segments, list)
        self.assertIsInstance(self.stl_segmentation.segments[0], stl.STLSegment)

    def test_surf_read(self):
        """Read a HyperSurface (.surf) segmentation"""
        self.read_surf()
        # assertions
        self.assertIsInstance(self.surf_segmentation.header, surf.AmiraHyperSurfaceHeader)
        self.assertIsInstance(self.surf_segmentation.segments, list)
        self.assertIsInstance(self.surf_segmentation.segments[0], surf.AmiraHyperSurfaceSegment)

    def test_survos_read(self):
        """Read a SuRVoS (.h5) segmentation"""
        self.read_survos()
        segmentation = self.survos_segmentation
        self.assertIsInstance(segmentation, survos.SuRVoSSegmentation)
        self.assertIsInstance(segmentation.segments, list)
        self.assertIsInstance(segmentation.segments[0], survos.SuRVoSSegment)
        self.assertIsInstance(segmentation.segments[0].segment_id, int)

    # convert
    def test_am_convert(self):
        """Convert a segmentation from an AmiraMesh file to an SFFSegmentation object"""
        self.read_am()
        args, configs = parse_args('convert {}'.format(self.am_file), use_shlex=True)
        seg = self.am_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'AmiraMesh Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Amira')
        self.assertEqual(seg.software_list[0].version, self.am_segmentation.header.version)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        if seg.lattice_list[0].data != '':  # MemoryError will set .data to an emtpy string
            self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_seg_convert(self):
        """Convert a segmentation from a Segger file to an SFFSegmentation object"""
        self.read_seg()
        args, configs = parse_args('convert {}'.format(self.seg_file), use_shlex=True)
        seg = self.seg_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'Segger Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'segger')
        self.assertEqual(seg.software_list[0].version, self.seg_segmentation.header.version)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_map_convert(self):
        """Convert a segmentation from an EMDB Map mask file to an SFFSegmentation object"""
        self.read_map()
        args, configs = parse_args('convert {}'.format(self.map_file), use_shlex=True)
        seg = self.map_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Undefined')
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_map_multi_convert(self):
        """Convert several EMDB Map mask files to a single SFFSegmentation object"""
        self.read_map_multi()
        args, configs = parse_args(
            'convert -m {}'.format(' '.join([self.map_multi0_file, self.map_multi1_file, self.map_multi2_file])),
            use_shlex=True)
        seg = self.map_multi_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Undefined')
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual(len(seg.segment_list), 3)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_mod_convert(self):
        """Convert a segmentation from an IMOD file to an SFFSegmentation object"""
        self.read_mod()
        args, configs = parse_args('convert {}'.format(self.mod_file), use_shlex=True)
        seg = self.mod_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'IMOD-NewModel')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'IMOD')
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transforms[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_stl_convert(self):
        """Convert a segmentation from an Stereo Lithography file to an SFFSegmentation object"""
        self.read_stl()
        args, configs = parse_args('convert {}'.format(self.stl_file), use_shlex=True)
        seg = self.stl_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'STL Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Unknown')
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transform_list[0].id, 0)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_stl_multi_convert(self):
        """Convert several STL files into a single SFFSegmentation object"""
        self.read_stl_multi()
        args, configs = parse_args(
            'convert -m {}'.format(' '.join([self.stl_multi0_file, self.stl_multi1_file, self.stl_multi2_file])),
            use_shlex=True)
        seg = self.stl_multi_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'STL Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Unknown')
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual(len(seg.segments), 3)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_surf_convert(self):
        """Convert a segmentation from a HyperSurface file to an SFFSegmentation object"""
        self.read_surf()
        args, configs = parse_args('convert {}'.format(self.surf_file), use_shlex=True)
        seg = self.surf_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'Amira HyperSurface Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Amira')
        self.assertEqual(seg.software_list[0].version, self.surf_segmentation.header.version)
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transform_list[0].id, 0)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_survos_convert(self):
        """Convert a segmentation from SuRVoS to SFFSegmentation object"""
        self.read_survos()
        sys.stdin = StringIO(u'0')
        args, configs = parse_args('convert {}'.format(self.survos_file), use_shlex=True)
        seg = self.survos_segmentation.convert(args, configs)
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, "SuRVoS Segmentation")
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, "SuRVoS")
        self.assertEqual(seg.software_list[0].version, "1.0")
        self.assertEqual(seg.primary_descriptor, "three_d_volume")
        self.assertTrue(len(seg.segment_list) > 0)
        segment = seg.segment_list.get_by_id(1)
        self.assertEqual(segment.biological_annotation.name, "SuRVoS Segment #1")
        self.assertTrue(0 <= segment.colour.red <= 1)
        self.assertTrue(0 <= segment.colour.green <= 1)
        self.assertTrue(0 <= segment.colour.blue <= 1)
        self.assertTrue(0 <= segment.colour.alpha <= 1)
        lattice = seg.lattice_list.get_by_id(0)
        self.assertEqual(lattice.mode, 'int8')
        self.assertEqual(lattice.endianness, 'little')
        self.assertIsInstance(lattice.size, schema.SFFVolumeStructure)
        self.assertIsInstance(lattice.start, schema.SFFVolumeIndex)
        self.assertTrue(lattice.size.cols > 0)
        self.assertTrue(lattice.size.rows > 0)
        self.assertTrue(lattice.size.sections > 0)
        self.assertIsInstance(lattice.start.cols, numbers.Integral)
        self.assertIsInstance(lattice.start.rows, numbers.Integral)
        self.assertIsInstance(lattice.start.sections, numbers.Integral)
