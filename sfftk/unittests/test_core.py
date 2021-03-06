# -*- coding: utf-8 -*-
# test_core.py
"""Unit tests for :py:mod:`sfftk.core` package"""
from __future__ import division, print_function

import glob
import os
import random
import shlex
import shutil
import sys
from io import StringIO

import numpy
from random_words import RandomWords, LoremIpsum
from sfftkrw.core import print_tools, utils, _dict_iter_items, _str, _dict
from sfftkrw.unittests import Py23FixTestCase, _random_integer, _random_integers, _random_float, _random_floats, isclose
from stl import Mesh

from . import TEST_DATA_PATH
from .. import BASE_DIR
from ..core.configs import Configs, get_config_file_path, load_configs, \
    get_configs, set_configs, del_configs
from ..core.parser import Parser, parse_args, tool_list, _get_file_extension, _set_subtype_index
from ..core.prep import bin_map, transform_stl_mesh, construct_transformation_matrix
from ..notes import RESOURCE_LIST

rw = RandomWords()
li = LoremIpsum()

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-05-15"


class TestParser(Py23FixTestCase):
    def test_default(self):
        """Test that default operation is OK"""
        args, configs = parse_args("--version", use_shlex=True)
        self.assertEqual(args, os.EX_OK)
        self.assertIsNone(configs)

    def test_use_shlex(self):
        """Test that we can use shlex i.e. treat command as string"""
        args, configs = parse_args("--version", use_shlex=True)
        self.assertEqual(args, os.EX_OK)
        self.assertIsNone(configs)

    def test_fail_use_shlex(self):
        """Test that we raise an error when use_shlex=True but _args not str"""
        args, configs = parse_args("--version", use_shlex=True)
        self.assertEqual(args, os.EX_OK)
        self.assertIsNone(configs)


class TestCoreConfigs(Py23FixTestCase):
    user_configs = os.path.expanduser("~/.sfftk/sff.conf")
    user_configs_hide = os.path.expanduser("~/.sfftk/sff.conf.test")
    dummy_configs = os.path.expanduser("~/sff.conf.test")

    @classmethod
    def setUpClass(cls):
        cls.test_config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'test_sff.conf')
        cls.config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'sff.conf')
        cls.config_values = _dict()
        cls.config_values['__TEMP_FILE'] = './temp-annotated.json'
        cls.config_values['__TEMP_FILE_REF'] = '@'

    @classmethod
    def tearDownClass(cls):
        pass

    def load_values(self):
        """Load config values into test config file"""
        with open(self.config_fn, 'w') as f:
            for n, v in _dict_iter_items(self.config_values):
                f.write('{}={}\n'.format(n, v))

    def clear_values(self):
        """Empty test config file"""
        with open(self.config_fn, 'w') as _:
            pass

    def setUp(self):
        self.load_values()
        self.move_user_configs()

    def tearDown(self):
        self.clear_values()
        self.return_user_configs()

    def move_user_configs(self):
        # when running this test we need to hide ~/.sfftk/sff.conf if it exists
        # we move ~/.sfftk/sff.conf to ~/.sfftk/sff.conf.test
        # then move it back once the test ends
        # if the test does not complete we will have to manually copy it back
        # ~/.sfftk/sff.conf.test to ~/.sfftk/sff.conf
        if os.path.exists(self.user_configs):
            # fixme: use print_date
            self.stderr('found user configs and moving them...')
            shutil.move(
                self.user_configs,
                self.user_configs_hide,
            )

    def return_user_configs(self):
        # we move back ~/.sfftk/sff.conf.test to ~/.sfftk/sff.conf
        if os.path.exists(self.user_configs_hide):
            # fixme: use print_date
            self.stderr('found moved user configs and returning them...')
            shutil.move(
                self.user_configs_hide,
                self.user_configs,
            )
        else:  # it was never there to begin with
            try:
                os.remove(self.user_configs)
            except OSError:
                pass

    def make_dummy_user_configs(self, param='TEST', value='TEST_VALUE'):
        if not os.path.exists(os.path.dirname(self.user_configs)):
            os.mkdir(os.path.dirname(self.user_configs))
        with open(self.user_configs, 'w') as c:
            c.write("{}={}\n".format(param, value))

    def remove_dummy_user_configs(self):
        os.remove(self.user_configs)

    def make_dummy_configs(self, param='TEST_CONFIG', value='TEST_CONFIG_VALUE'):
        with open(self.dummy_configs, 'w') as c:
            c.write("{}={}\n".format(param, value))

    def remove_dummy_configs(self):
        os.remove(self.dummy_configs)

    def test_default_ro(self):
        """Test that on a fresh install we use shipped configs for get"""
        args = Parser.parse_args(shlex.split("config get --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == Configs.shipped_configs)

    def test_user_configs_ro(self):
        """Test that if we have user configs we get them"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config get --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.remove_dummy_user_configs()

    def test_shipped_default(self):
        """Test that we get shipped and nothing else when we ask for them"""
        args = Parser.parse_args(shlex.split("config get --shipped-configs --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, Configs.shipped_configs)

    def test_shipped_user_configs_exist_ro(self):
        """Test that even if user configs exist we can only get shipped configs"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config get --shipped-configs --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, Configs.shipped_configs)
        self.remove_dummy_user_configs()

    def test_config_path_default_ro(self):
        """Test that we can get configs from some path"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config get --config-path {} --all".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_user_configs()

    def test_config_path_over_shipped_ro(self):
        """Test that we use config path even if shipped specified"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(
            shlex.split("config get --config-path {} --shipped-configs --all".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_user_configs()

    def test_default_rw(self):
        """Test that when we try to write configs on a fresh install we get user configs"""
        args = Parser.parse_args(shlex.split("config set A B"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.assertTrue(os.path.exists(self.user_configs))

    def test_user_configs_rw(self):
        """Test that if we have user configs we can set to them"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config set A B"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.remove_dummy_user_configs()

    def test_shipped_default_rw(self):
        """Test that we cannot write to shipped configs"""
        args = Parser.parse_args(shlex.split("config set --shipped-configs A B"))
        config_file_path = get_config_file_path(args)
        self.assertIsNone(config_file_path)

    def test_config_path_default_rw(self):
        """Test that we can get configs from some path"""
        self.make_dummy_configs()
        args = Parser.parse_args(shlex.split("config set --config-path {} A B".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()

    def test_config_path_over_shipped_rw(self):
        """Test that we use config path even if shipped specified"""
        self.make_dummy_configs()
        args = Parser.parse_args(
            shlex.split("config set --config-path {} --shipped-configs A B".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()

    def test_default_other(self):
        """Test that all non-config commands on a fresh install use shipped configs"""
        args = Parser.parse_args(shlex.split("view file.json"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == Configs.shipped_configs)
        self.assertFalse(os.path.exists(self.user_configs))

    def test_user_configs_other(self):
        """Test that if we have user configs we can set to them"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("view file.json"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.remove_dummy_user_configs()

    def test_shipped_default_other(self):
        """Test that we cannot write to shipped configs even if we have user configs"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("view file.json --shipped-configs"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == Configs.shipped_configs)
        self.remove_dummy_user_configs()

    def test_config_path_default_other(self):
        """Test that we can get configs from some path"""
        self.make_dummy_configs()
        args = Parser.parse_args(shlex.split("view --config-path {} file.json".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()

    def test_config_path_over_shipped_other(self):
        """Test that we use config path even if shipped specified"""
        self.make_dummy_configs()
        args = Parser.parse_args(
            shlex.split("view --config-path {} --shipped-configs file.json".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()

    def test_load_shipped(self):
        """Test that we actually load shipped configs"""
        args = Parser.parse_args(shlex.split("view file.json"))
        config_file_path = get_config_file_path(args)
        configs = load_configs(config_file_path)
        # user configs should not exist
        self.assertFalse(os.path.exists(os.path.expanduser("~/.sfftk/sff.conf")))
        self.assertEqual(configs['__TEMP_FILE'], './temp-annotated.json')
        self.assertEqual(configs['__TEMP_FILE_REF'], '@')

    def test_config_path(self):
        """Test that we can read configs from config path"""
        args = Parser.parse_args(shlex.split('view --config-path {} file.sff'.format(self.test_config_fn)))
        config_file_path = get_config_file_path(args)
        configs = load_configs(config_file_path)
        self.assertEqual(configs['HAPPY'], 'DAYS')

    def test_user_config(self):
        """Test that we can read user configs from ~/.sfftk/sff.conf"""
        # no user configs yet
        self.assertFalse(os.path.exists(os.path.expanduser("~/.sfftk/sff.conf")))
        # set a custom value to ensure it's present in user configs
        args = Parser.parse_args(shlex.split('config set --force NAME VALUE'))
        config_file_path = get_config_file_path(args)
        configs = load_configs(config_file_path)
        set_configs(args, configs)
        # now user configs should exist
        self.assertTrue(os.path.exists(os.path.expanduser("~/.sfftk/sff.conf")))
        args, configs = parse_args('view file.sff', use_shlex=True)
        self.assertEqual(configs['NAME'], 'VALUE')

    def test_precedence_config_path(self):
        """Test that config path takes precedence"""
        # set a custom value to ensure it's present in user configs
        args = Parser.parse_args(shlex.split('config set --force NAME VALUE'))
        config_file_path = get_config_file_path(args)
        configs = load_configs(config_file_path)
        set_configs(args, configs)
        args, configs = parse_args(
            'view --config-path {} --shipped-configs file.sff'.format(self.test_config_fn), use_shlex=True)
        self.assertEqual(configs['HAPPY'], 'DAYS')

    def test_precedence_shipped_configs(self):
        """Test that shipped configs, when specified, take precedence over user configs"""
        # set a custom value to ensure it's present in user configs
        args = Parser.parse_args(shlex.split('config set --force NAME VALUE'))
        config_file_path = get_config_file_path(args)
        configs = load_configs(config_file_path)
        set_configs(args, configs)
        args, configs = parse_args('view file.sff --shipped-configs', use_shlex=True)
        self.assertEqual(configs['__TEMP_FILE'], './temp-annotated.json')
        self.assertEqual(configs['__TEMP_FILE_REF'], '@')
        self.assertNotIn('NAME', configs)

    def test_get_configs(self):
        """Test that we can get a config by name"""
        args, configs = parse_args('config get __TEMP_FILE --config-path {}'.format(self.config_fn), use_shlex=True)
        self.assertTrue(get_configs(args, configs) == os.EX_OK)

    def test_get_all_configs(self):
        """Test that we can list all configs"""
        args, configs = parse_args('config get --all --config-path {}'.format(self.config_fn), use_shlex=True)
        self.assertTrue(get_configs(args, configs) == os.EX_OK)
        self.assertTrue(len(configs) > 0)

    def test_get_absent_configs(self):
        """Test that we are notified when a config is not found"""
        args, configs = parse_args('config get alsdjf;laksjflk --config-path {}'.format(self.config_fn), use_shlex=True)
        self.assertTrue(get_configs(args, configs) == 1)

    def test_set_configs(self):
        """Test that we can set configs"""
        args, configs_before = parse_args(
            'config set --force NAME VALUE --config-path {}'.format(self.config_fn), use_shlex=True)
        len_configs_before = len(configs_before)
        self.assertTrue(set_configs(args, configs_before) == 0)
        _, configs_after = parse_args('config get alsdjf;laksjflk --config-path {}'.format(self.config_fn),
                                      use_shlex=True)
        len_configs_after = len(configs_after)
        self.assertTrue(len_configs_before < len_configs_after)

    def test_set_new_configs(self):
        """Test that new configs will by default be written to user configs .i.e. ~/sfftk/sff.conf"""
        args, configs = parse_args('config set --force NAME VALUE', use_shlex=True)
        self.assertTrue(set_configs(args, configs) == os.EX_OK)
        _, configs = parse_args('config get --all', use_shlex=True)
        D = _dict()
        D['NAME'] = 'VALUE'
        self.assertLessEqual(list(_dict_iter_items(D)), list(_dict_iter_items(configs)))

    def test_set_force_configs(self):
        """Test that forcing works"""
        args, configs = parse_args('config set --force NAME VALUE', use_shlex=True)
        self.assertTrue(set_configs(args, configs) == os.EX_OK)
        self.assertTrue(configs['NAME'] == 'VALUE')
        args, configs_after = parse_args('config set --force NAME VALUE1', use_shlex=True)
        self.assertTrue(set_configs(args, configs_after) == os.EX_OK)
        self.assertTrue(configs_after['NAME'] == 'VALUE1')

    def test_del_configs(self):
        """Test that we can delete configs"""
        # first we get current configs
        args, configs = parse_args('config set --force NAME VALUE --config-path {}'.format(self.config_fn),
                                   use_shlex=True)
        # then we set an additional config
        self.assertTrue(set_configs(args, configs) == 0)
        # then we delete the config
        args, configs_before = parse_args(
            'config del --force NAME  --config-path {}'.format(self.config_fn), use_shlex=True)
        len_configs_before = len(configs_before)
        self.assertTrue(del_configs(args, configs_before) == 0)
        args, configs_after = parse_args('config get --all --config-path {}'.format(self.config_fn), use_shlex=True)
        len_configs_after = len(configs_after)
        self.assertTrue(len_configs_before > len_configs_after)

    def test_del_all_configs(self):
        """Test that we can delete all configs"""
        args, configs = parse_args('config del --force --all --config-path {}'.format(self.config_fn), use_shlex=True)
        self.assertTrue(del_configs(args, configs) == 0)
        _, configs = parse_args('config get --all --config-path {}'.format(self.config_fn), use_shlex=True)
        self.assertTrue(len(configs) == 0)

    def test_write_shipped_fails(self):
        """Test that we cannot save to shipped configs"""
        args, configs = parse_args(
            'config set --force NAME VALUE --config-path {}'.format(os.path.join(BASE_DIR, 'sff.conf')), use_shlex=True)
        self.assertTrue(set_configs(args, configs) == 1)


class TestCorePrintUtils(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCorePrintUtils, cls).setUpClass()
        cls._weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def setUp(self):
        super(TestCorePrintUtils, self).setUp()
        self.temp_fn = 'temp_file.txt'
        if sys.version_info[0] > 2:
            self.temp_file = open(self.temp_fn, 'w+', newline='\r\n')
        else:
            self.temp_file = open(self.temp_fn, 'w+')

    def tearDown(self):
        super(TestCorePrintUtils, self).tearDown()
        os.remove(self.temp_fn)

    def test_print_date_default(self):
        """Test default arguments for print_tools.print_date(...)"""
        print_tools.print_date("Test", stream=self.temp_file)
        self.temp_file.flush()  # flush buffers
        self.temp_file.seek(0)  # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertIn(_words[0], self._weekdays)  # the first part is a date
        self.assertEqual(_words[-1][-1], '\n')  #  the last letter is a newline

    def test_print_date_non_basestring(self):
        """Test exception when print_string is not a basestring subclass"""
        with self.assertRaises(ValueError):
            print_tools.print_date(3)

    def test_print_date_no_newline(self):
        """Test that we lack a newline at the end"""
        print_tools.print_date("Test", stream=self.temp_file, newline=False)
        self.temp_file.flush()  # flush buffers
        self.temp_file.seek(0)  # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertNotEqual(_words[-1][-1], '\n')

    def test_print_date_no_date(self):
        """Test that we lack a date at the beginning"""
        print_tools.print_date("Test", stream=self.temp_file, incl_date=False)
        self.temp_file.flush()  # flush buffers
        self.temp_file.seek(0)  # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertNotIn(_words[0], self._weekdays)  # the first part is a date

    def test_print_date_no_newline_no_date(self):
        """Test that we can exclude both newline and the date"""
        print_tools.print_date("Test", stream=self.temp_file, newline=False, incl_date=False)
        self.temp_file.flush()
        self.temp_file.seek(0)
        data = self.temp_file.readline()
        self.assertEqual(data, 'Test')

    def test_printable_ascii_string(self):
        """Test whether we can get a printable substring"""
        s_o = li.get_sentence().encode('utf-8')
        unprintables = list(range(14, 32))
        s_u = b''.join([chr(random.choice(unprintables)).encode('utf-8') for _ in range(100)])
        s = s_o + s_u
        s_p = print_tools.get_printable_ascii_string(s)
        self.assertEqual(s_p, s_o)
        s_pp = print_tools.get_printable_ascii_string(s_u)
        self.assertEqual(s_pp, b'')
        s_b = print_tools.get_printable_ascii_string('')
        self.assertEqual(s_b, b'')

    def test_print_static(self):
        """Test that we can print_static

        * write two sentences
        * only the second one appears because first is overwritten
        """
        s = li.get_sentence()
        print_tools.print_static(s, stream=self.temp_file)
        self.temp_file.flush()
        s1 = li.get_sentence()
        print_tools.print_static(s1, stream=self.temp_file)
        self.temp_file.flush()
        self.temp_file.seek(0)
        _data = self.temp_file.read()
        data = _data[0]
        self.assertEqual(data[0], '\r')
        self.assertTrue(len(_data) > len(s) + len(s1))
        r_split = _data.split('\r')  # split at the carriage reset
        self.assertTrue(len(r_split), 3)  # there should be three items in the list
        self.assertEqual(r_split[1].split('\t')[1], s)  # split the first string and get the actual string (ex. date)
        self.assertEqual(r_split[2].split('\t')[1], s1)  # split the second string and get the actual string (ex. date)

    def test_print_static_no_date(self):
        """Test print static with no date"""
        s = li.get_sentence()
        print_tools.print_static(s, stream=self.temp_file, incl_date=False)
        self.temp_file.flush()
        s1 = li.get_sentence()
        print_tools.print_static(s1, stream=self.temp_file, incl_date=False)
        self.temp_file.seek(0)
        data = self.temp_file.readlines()[0]
        self.assertEqual(data[0], '\r')
        self.assertTrue(len(data) > len(s) + len(s1))
        r_split = data.split('\r')  # split at the carriage reset
        self.assertTrue(len(r_split), 3)  # there should be three items in the list
        self.assertEqual(r_split[1], s)  # split the first string and get the actual string (ex. date)
        self.assertEqual(r_split[2], s1)  # split the second string and get the actual string (ex. date)

    def test_print_static_valueerror(self):
        """Test that we assert print_string type"""
        with self.assertRaises(ValueError):
            print_tools.print_static(1)

    def test_print_static_str(self):
        """Test that we can work with unicode"""
        s = li.get_sentence()
        print_tools.print_static(str(s), stream=self.temp_file)
        self.temp_file.flush()
        self.temp_file.seek(0)
        data = self.temp_file.readlines()[0]
        self.assertEqual(data[0], '\r')
        r_split = data.split('\r')
        self.assertEqual(len(r_split), 2)
        self.assertEqual(r_split[1].split('\t')[1], s)


class TestCoreParserPrepBinmap(Py23FixTestCase):
    def test_default(self):
        """Test default params for prep binmap"""
        args, _ = parse_args('prep binmap file.map', use_shlex=True)
        self.assertEqual(args.prep_subcommand, 'binmap')
        self.assertEqual(args.from_file, 'file.map')
        self.assertEqual(args.mask_value, 1)
        self.assertEqual(args.output, 'file_prep.map')
        self.assertEqual(args.contour_level, 0)
        self.assertFalse(args.negate)
        self.assertEqual(args.bytes_per_voxel, 1)
        self.assertEqual(args.infix, 'prep')
        self.assertFalse(args.verbose)
        args, _ = parse_args('prep binmap -B 2 file.map', use_shlex=True)
        self.assertEqual(args.bytes_per_voxel, 2)
        args, _ = parse_args('prep binmap -B 4 file.map', use_shlex=True)
        self.assertEqual(args.bytes_per_voxel, 4)
        args, _ = parse_args('prep binmap -B 8 file.map', use_shlex=True)
        self.assertEqual(args.bytes_per_voxel, 8)
        args, _ = parse_args('prep binmap -B 16 file.map', use_shlex=True)
        self.assertEqual(args.bytes_per_voxel, 16)

    def test_mask(self):
        """Test setting mask value"""
        mask_value = _random_integer()
        args, _ = parse_args('prep binmap -m {} file.map'.format(mask_value), use_shlex=True)
        self.assertEqual(args.mask_value, mask_value)

    def test_output(self):
        """Test that we can set the output"""
        args, _ = parse_args('prep binmap -o my_file.map file.map', use_shlex=True)
        self.assertEqual(args.output, 'my_file.map')

    def test_contour_level(self):
        """Test that we can set the contour level"""
        contour_level = _random_float()
        args, _ = parse_args('prep binmap -c {} file.map'.format(contour_level), use_shlex=True)
        self.assertEqual(round(args.contour_level, 8), round(contour_level, 8))

    def test_negate(self):
        """Test that we can set negate"""
        args, _ = parse_args('prep binmap --negate file.map', use_shlex=True)
        self.assertTrue(args.negate)

    def test_bytes_per_voxel(self):
        """Test that we can set bytes per voxel"""
        bytes_per_voxel = random.choice([1, 2, 4, 8, 16])
        args, _ = parse_args('prep binmap -B {} file.map'.format(bytes_per_voxel), use_shlex=True)
        self.assertEqual(args.bytes_per_voxel, bytes_per_voxel)

    def test_infix(self):
        """Test setting infix"""
        args, _ = parse_args('prep binmap --infix something file.map', use_shlex=True)
        self.assertEqual(args.infix, 'something')
        self.assertEqual(args.output, 'file_something.map')

    def test_blank_infix(self):
        """Test that a blank infix fails"""
        args, _ = parse_args("prep binmap --infix '' file.map", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)


class TestCoreParserPrepTransform(Py23FixTestCase):
    def test_default(self):
        """Test default param for prep transform"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        args, _ = parse_args('prep transform --lengths {lengths} --indices {indices} file.stl'.format(
            lengths=' '.join(map(str, lengths)),
            indices=' '.join(map(str, indices)),
        ), use_shlex=True)
        self.assertEqual(args.prep_subcommand, 'transform')
        self.assertEqual(args.from_file, 'file.stl')
        self.assertEqual(args.output, 'file_transformed.stl')
        self.assertEqual(args.infix, 'transformed')
        # zip values -> compare using isclose() -> a list of booleans
        l = map(lambda x: isclose(x[0], x[1]), zip(args.lengths, lengths))  # lengths
        i = map(lambda x: isclose(x[0], x[1]), zip(args.indices, indices))  # indices
        # now test that all values in the comparison lists are True using all()
        self.assertTrue(all(l))
        self.assertTrue(all(i))

    def test_origin(self):
        """Test with setting the origin"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            'prep transform --lengths {lengths} --indices {indices} --origin {origin} file.stl'.format(
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            ), use_shlex=True)
        self.assertEqual(args.from_file, 'file.stl')
        # zip values -> compare using isclose() -> a list of booleans
        l = map(lambda x: isclose(x[0], x[1]), zip(args.lengths, lengths))  # lengths
        i = map(lambda x: isclose(x[0], x[1]), zip(args.indices, indices))  # indices
        o = map(lambda x: isclose(x[0], x[1]), zip(args.origin, origin))  # origin
        # now test that all values in the comparison lists are True using all()
        self.assertTrue(all(l))
        self.assertTrue(all(i))
        self.assertTrue(all(o))

    def test_non_stl(self):
        """Test that it fails for non-STL files"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            'prep transform --lengths {lengths} --indices {indices} --origin {origin} file.abc'.format(
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            ), use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_output(self):
        """Test that we can set the output"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(

            'prep transform --lengths {lengths} --indices {indices} --origin {origin} -o my_file.stl file.stl'.format(
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            ), use_shlex=True)
        self.assertEqual(args.output, 'my_file.stl')

    def test_infix(self):
        """Test setting infix"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            'prep transform --lengths {lengths} --indices {indices} --origin {origin} --infix something file.stl'.format(
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            ), use_shlex=True)
        self.assertEqual(args.infix, 'something')
        self.assertEqual(args.output, 'file_something.stl')


class TestCoreParserConvert(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        # fixme: use print_date
        cls.stderr("convert tests...")
        cls.test_data_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod')
        cls.test_data_file_h5 = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.h5')
        cls.test_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')
        cls.test_hff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.hff')
        cls.empty_maps = glob.glob(os.path.join(TEST_DATA_PATH, 'segmentations', 'empty*.map'))
        cls.empty_stls = glob.glob(os.path.join(TEST_DATA_PATH, 'segmentations', 'empty*.stl'))
        cls.empty_segs = glob.glob(os.path.join(TEST_DATA_PATH, 'segmentations', 'empty*.seg'))
        cls.test_seg_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'emd_1014.seg')

    @classmethod
    def tearDownClass(cls):
        # fixme: use print_date
        cls.stderr("")

    def test_default(self):
        """Test convert parser"""
        args, _ = parse_args('convert {}'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertEqual(args.subcommand, 'convert')
        self.assertEqual(args.from_file, self.test_data_file)
        self.assertIsNone(args.config_path)
        # self.assertFalse(args.top_level_only)
        self.assertFalse(args.all_levels)
        self.assertIsNone(args.details)
        self.assertEqual(args.output, os.path.join(os.path.dirname(self.test_data_file), 'test_data.sff'))
        self.assertEqual(args.primary_descriptor, None)
        self.assertFalse(args.verbose)
        self.assertFalse(args.multi_file)
        self.assertEqual(args.subtype_index, -1)

    def test_config_path(self):
        """Test setting of arg config_path"""
        config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'sff.conf')
        args, _ = parse_args('convert --config-path {} {}'.format(config_fn, self.test_data_file), use_shlex=True)
        self.stderr(args)
        self.assertEqual(args.config_path, config_fn)

    def test_details(self):
        """Test convert parser with details"""
        args, _ = parse_args('convert -D "Some details" {}'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertEqual(args.details, 'Some details')

    def test_output_sff(self):
        """Test convert parser to .sff"""
        args, _ = parse_args('convert {} -o file.sff'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertEqual(args.output, 'file.sff')

    def test_output_hff(self):
        """Test convert parser to .hff"""
        args, _ = parse_args('convert {} -o file.hff'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertEqual(args.output, 'file.hff')

    def test_output_json(self):
        """Test convert parser to .json"""
        args, _ = parse_args('convert {} -o file.json'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertEqual(args.output, 'file.json')

    def test_hff_default_output_sff(self):
        """Test that converting an .hff with no args gives .sff"""
        args, _ = parse_args('convert {}'.format(self.test_hff_file), use_shlex=True)
        self.assertEqual(args.output, self.test_sff_file)

    def test_sff_default_output_hff(self):
        """Test that converting a .sff with no args gives .hff"""
        args, _ = parse_args('convert {}'.format(self.test_sff_file), use_shlex=True)
        self.assertEqual(args.output, self.test_hff_file)

    def test_primary_descriptor(self):
        """Test convert parser with primary_descriptor"""
        args, _ = parse_args('convert -R three_d_volume {}'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertEqual(args.primary_descriptor, 'three_d_volume')

    def test_wrong_primary_descriptor_fails(self):
        """Test that we have a check on primary descriptor values"""
        args, _ = parse_args('convert -R something {}'.format(self.test_data_file), use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_verbose(self):
        """Test convert parser with verbose"""
        args, _ = parse_args('convert -v {}'.format(self.test_data_file), use_shlex=True)
        # assertions
        self.assertTrue(args.verbose)

    def test_multifile_map(self):
        """Test that multi-file works for CCP4 masks"""
        cmd = 'convert -v -m {}'.format(' '.join(self.empty_maps))
        args, _ = parse_args(cmd, use_shlex=True)
        # assertions
        self.assertTrue(args.multi_file)
        self.assertCountEqual(args.from_file, self.empty_maps)

    def test_multifile_stl(self):
        """Test that multi-file works for STLs"""
        cmd = 'convert -v -m {}'.format(' '.join(self.empty_stls))
        args, _ = parse_args(cmd, use_shlex=True)
        # assertions
        self.assertTrue(args.multi_file)
        self.assertCountEqual(args.from_file, self.empty_stls)

    def test_multifile_map_fail1(self):
        """Test that excluding -m issues a warning for CCP4"""
        args, _ = parse_args('convert -v {}'.format(' '.join(self.empty_maps)), use_shlex=True)
        # assertions
        self.assertEqual(args, os.EX_USAGE)

    def test_multifile_stl_fail2(self):
        """Test that excluding -m issues a warning for STL"""
        args, _ = parse_args('convert -v {}'.format(' '.join(self.empty_stls)), use_shlex=True)
        # assertions
        self.assertEqual(args, os.EX_USAGE)

    def test_multifile_xxx_fail3(self):
        """Test that other file format fails for multifile e.g. Segger (.seg)"""
        args, _ = parse_args('convert -v {}'.format(' '.join(self.empty_segs)), use_shlex=True)
        # assertions
        self.assertEqual(args, os.EX_USAGE)

    def test_multifile_xxx_fail4(self):
        """Test that other file format fails even with -m e.g. Segger (.seg)"""
        args, _ = parse_args('convert -v -m {}'.format(' '.join(self.empty_segs)), use_shlex=True)
        # assertions
        self.assertEqual(args, os.EX_USAGE)

    def test_all_levels(self):
        """Test that we can set the -a/--all-levels flag for Segger segmentations"""
        args, _ = parse_args('convert -v -a {}'.format(self.test_seg_file), use_shlex=True)
        self.assertTrue(args.all_levels)

    def test_subtype_index_defined(self):
        """Test that users can enter a subtype index"""
        args, _ = parse_args('convert --subtype-index 0 {file}'.format(
            file=self.test_data_file_h5
        ), use_shlex=True)
        self.assertGreaterEqual(args.subtype_index, 0)

    def test_set_subtype_index(self):
        """Test correct functionality of the parser._set_subtype_index function"""
        sys.stdin = StringIO(u'1') # avail for stdin
        # construct the namespace object
        args, _ = parse_args('convert {file}'.format(file=self.test_data_file_h5), use_shlex=True)
        self.assertTrue(args.subtype_index > -1)
        # exceptions
        # invalid file extension e.g. file.mod
        args, _ = parse_args('convert {file}'.format(file=self.test_data_file), use_shlex=True)
        # we need to explicitly invoke _set_subtype_index because it is ignored
        ext = _get_file_extension(args.from_file)
        args = _set_subtype_index(args, ext)
        self.assertEqual(args.subtype_index, -1)
        # invalid entry: type
        sys.stdin = StringIO(u'a')  # avail for stdin
        args, _ = parse_args('convert {file}'.format(file=self.test_data_file_h5), use_shlex=True)
        self.assertEqual(args.subtype_index, -1)
        # invalid entry: range
        sys.stdin = StringIO(u'10')  # avail for stdin
        args, _ = parse_args('convert {file}'.format(file=self.test_data_file_h5), use_shlex=True)
        self.assertEqual(args.subtype_index, -1)
        # fixme: not tested ambiguous mutli-file formats

    def test_get_file_extension(self):
        """Test function to return file extension"""
        self.assertEqual(_get_file_extension('file.abc'), 'abc')
        self.assertEqual(_get_file_extension('file.h5'), 'h5')
        self.assertEqual(_get_file_extension('file.1.2.3.4.something'), 'something')


class TestCoreParserView(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        cls.stderr("view tests...")

    @classmethod
    def tearDownClass(cls):
        cls.stderr("")

    def test_default(self):
        """Test view parser"""
        args, _ = parse_args('view file.sff', use_shlex=True)

        self.assertEqual(args.from_file, 'file.sff')
        self.assertFalse(args.version)
        self.assertIsNone(args.config_path)
        self.assertFalse(args.show_chunks)

    def test_version(self):
        """Test view version"""
        args, _ = parse_args('view --sff-version file.sff', use_shlex=True)

        self.assertTrue(args.sff_version)

    def test_config_path(self):
        """Test setting of arg config_path"""
        config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'sff.conf')
        args, _ = parse_args('view --config-path {} file.sff'.format(config_fn), use_shlex=True)
        self.assertEqual(args.config_path, config_fn)

    def test_show_chunks_mod(self):
        """Test that we can view chunks"""
        args, _ = parse_args('view -C file.mod', use_shlex=True)
        self.assertTrue(args.show_chunks)

    def test_show_chunks_other_fails(self):
        """Test that show chunks only works for .mod files"""
        args, _ = parse_args('view -C file.sff', use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)


class TestCoreParserNotesReadOnly(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        cls.stderr("notes ro tests...")

    @classmethod
    def tearDownClass(cls):
        cls.stderr("")

    # =========================================================================
    # find
    # =========================================================================
    def test_search_default(self):
        """Test default find parameters"""
        cmd = "notes search 'mitochondria' --config-path {}".format(self.config_fn)
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'search')
        self.assertEqual(args.search_term, 'mitochondria')
        self.assertEqual(args.rows, 10)
        self.assertEqual(args.start, 1)
        self.assertIsNone(args.ontology)
        self.assertFalse(args.exact)
        self.assertFalse(args.obsoletes)
        self.assertFalse(args.list_ontologies)
        self.assertFalse(args.short_list_ontologies)
        self.assertEqual(args.config_path, self.config_fn)
        self.assertEqual(args.resource, 'ols')

    def test_search_list_ontologies(self):
        """Test that we can list ontologies in OLS"""
        args, _ = parse_args("notes search -L", use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'search')
        self.assertEqual(args.search_term, '')
        self.assertEqual(args.resource, 'ols')
        self.assertTrue(args.list_ontologies)

    def test_search_short_list_ontologies(self):
        """Test that we can short-list ontologies in OLS"""
        args, _ = parse_args("notes search -l", use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'search')
        self.assertEqual(args.search_term, '')
        self.assertEqual(args.resource, 'ols')
        self.assertTrue(args.short_list_ontologies)

    def test_search_list_ontologies_non_OLS_fail(self):
        """Test failure for list ontologies for non OLS"""
        args, _ = parse_args("notes search -l -R emdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -L -R emdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -O go -R emdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -o -R emdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -x -R emdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -l -R pdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -L -R pdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -O go -R pdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -o -R pdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -x -R pdb", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -l -R uniprot", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -L -R uniprot", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -O go -R uniprot", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -o -R uniprot", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -x -R uniprot", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -l -R europepmc", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -L -R europepmc", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -O go -R europepmc", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -o -R europepmc", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -x -R europepmc", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -l -R empiar", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -L -R empiar", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -O go -R empiar", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -o -R empiar", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        args, _ = parse_args("notes search -x -R empiar", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_search_options(self):
        """Test setting of:
            - number of rows
            - search start
            - ontology
            - exact matches
            - include obsolete entries
            - list of ontologies
            - short list of ontologies
        """
        rows = _random_integer()
        start = _random_integer()
        args, _ = parse_args(
            "notes search --rows {} --start {} -O fma -x -o -L -l 'mitochondria' --config-path {}".format(
                rows, start, self.config_fn
            ), use_shlex=True)
        self.assertEqual(args.rows, rows)
        self.assertEqual(args.start, start)
        self.assertEqual(args.ontology, 'fma')
        self.assertTrue(args.exact)
        self.assertTrue(args.obsoletes)
        self.assertTrue(args.list_ontologies)
        self.assertTrue(args.short_list_ontologies)
        self.assertEqual(args.search_term, "mitochondria")

    def test_search_invalid_start(self):
        """Test that we catch an invalid start"""
        start = -_random_integer()
        args, _ = parse_args("notes search --start {} 'mitochondria' --config-path {}".format(start, self.config_fn),
                             use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_search_invalid_rows(self):
        """Test that we catch an invalid rows"""
        rows = -_random_integer()
        args, _ = parse_args("notes search --rows {} 'mitochondria' --config-path {}".format(rows, self.config_fn),
                             use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_search_resource_options(self):
        """Test various values of -R/--resource"""
        resources = RESOURCE_LIST.keys()
        for R in resources:
            args, _ = parse_args(
                'notes search "term" --resource {} --config-path {}'.format(R, self.config_fn), use_shlex=True)
            self.assertEqual(args.resource, R)

    # =========================================================================
    # view
    # =========================================================================
    def test_list_default(self):
        """Test that we can list notes from an SFF file"""
        args, _ = parse_args('notes list file.sff --config-path {}'.format(self.config_fn), use_shlex=True)
        #  assertion
        self.assertEqual(args.notes_subcommand, 'list')
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertFalse(args.long_format)
        self.assertFalse(args.sort_by_name)
        self.assertFalse(args.reverse)

    def test_list_long(self):
        """Test short list of notes"""
        args, _ = parse_args('notes list -l file.sff --config-path {}'.format(self.config_fn), use_shlex=True)
        # assertions
        self.assertTrue(args.long_format)

    def test_list_shortcut(self):
        """Test that shortcut fails with list"""
        args, _ = parse_args('notes list @ --config-path {}'.format(self.config_fn), use_shlex=True)
        #  assertions
        self.assertEqual(args, os.EX_USAGE)

    def test_list_sort_by_name(self):
        """Test list segments sorted by description"""
        args, _ = parse_args('notes list -D file.sff --config-path {}'.format(self.config_fn), use_shlex=True)
        # assertions
        self.assertTrue(args.sort_by_name)

    def test_list_reverse_sort(self):
        """Test list sort in reverse"""
        args, _ = parse_args('notes list -r file.sff --config-path {}'.format(self.config_fn), use_shlex=True)
        # assertions
        self.assertTrue(args.reverse)

    def test_show_default(self):
        """Test show notes"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args, _ = parse_args(
            'notes show -i {},{} file.sff --config-path {}'.format(segment_id0, segment_id1, self.config_fn),
            use_shlex=True)
        #  assertions
        self.assertEqual(args.notes_subcommand, 'show')
        self.assertCountEqual(args.segment_id, [segment_id0, segment_id1])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertFalse(args.long_format)

    def test_show_short(self):
        """Test short show of notes"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args, _ = parse_args(
            'notes show -l -i {},{} file.sff --config-path {}'.format(segment_id0, segment_id1, self.config_fn),
            use_shlex=True)
        #  assertions
        self.assertTrue(args.long_format)

    def test_show_shortcut(self):
        """Test that shortcut works with show"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args, _ = parse_args(
            'notes show -i {},{} @ --config-path {}'.format(segment_id0, segment_id1, self.config_fn), use_shlex=True)
        #  assertions
        self.assertEqual(args, os.EX_USAGE)


class TestCoreParserTests(Py23FixTestCase):
    def test_tests_default(self):
        """Test that tests can be launched"""
        args, _ = parse_args("tests all", use_shlex=True)
        self.assertEqual(args.subcommand, 'tests')
        self.assertCountEqual(args.tool, ['all'])

    def test_tests_one_tool(self):
        """Test that with any tool we get proper tool"""
        tool = random.choice(tool_list)
        args, _ = parse_args("tests {}".format(tool), use_shlex=True)
        self.assertCountEqual(args.tool, [tool])

    def test_multi_tool(self):
        """Test that we can specify multiple packages (tools) to test"""
        tools = set()
        while len(tools) < 3:
            tools.add(random.choice(tool_list))
        tools = list(tools)
        # normalise
        if 'all' in tools:
            tools = ['all']
        elif 'all_sfftk' in tools:
            tools = ['all_sfftk']
        args, _ = parse_args("tests {}".format(' '.join(tools)), use_shlex=True)
        self.stderr(args.tool, tools)
        self.assertCountEqual(args.tool, tools)

    def test_tool_fail(self):
        """Test that we catch a wrong tool"""
        args, _ = parse_args("tests wrong_tool_spec", use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_tests_no_tool(self):
        """Test that with no tool we simply get usage info"""
        args, _ = parse_args("tests", use_shlex=True)
        self.assertEqual(args, os.EX_OK)

    def test_valid_verbosity(self):
        """Test valid verbosity"""
        args, _ = parse_args("tests all_sfftk -v 0", use_shlex=True)
        self.assertEqual(args.verbosity, 0)
        args, _ = parse_args("tests all_sfftk -v 1", use_shlex=True)
        self.assertEqual(args.verbosity, 1)
        args, _ = parse_args("tests all_sfftk -v 2", use_shlex=True)
        self.assertEqual(args.verbosity, 2)
        args, _ = parse_args("tests all_sfftk -v 3", use_shlex=True)
        self.assertEqual(args.verbosity, 3)

    def test_invalid_verbosity(self):
        """Test that verbosity is in [0,3]"""
        v1 = _random_integer(start=4)
        args, _ = parse_args("tests all_sfftk -v {}".format(v1), use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)
        v2 = -_random_integer(start=0)
        args, _ = parse_args("tests all_sfftk -v {}".format(v2), use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)


class TestCoreParserNotesReadWrite(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        cls.stderr("notes rw tests...")

    @classmethod
    def tearDownClass(cls):
        cls.stderr("")

    def setUp(self):
        Py23FixTestCase.setUp(self)
        _, configs = parse_args('config get --all --config-path {}'.format(self.config_fn), use_shlex=True)
        self.temp_file = configs['__TEMP_FILE']
        if os.path.exists(self.temp_file):
            raise ValueError("Unable to run with temp file {} present. \
Please either run 'save' or 'trash' before running tests.".format(self.temp_file))

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            assert not os.path.exists(self.temp_file)
        Py23FixTestCase.tearDown(self)

    # ===========================================================================
    # notes: add
    # ===========================================================================
    def test_add_to_global(self):
        """Test add global notes"""
        name = ' '.join(rw.random_words(count=3)).title()
        details = li.get_sentences(5)
        software_name = rw.random_word()
        software_version = 'v{}.{}.{}'.format(_random_integer(), _random_integer(), _random_integer())
        software_processing_details = li.get_sentences(4)
        resource1 = rw.random_word()
        url1 = rw.random_word()
        accession1 = rw.random_word()
        resource2 = rw.random_word()
        url2 = rw.random_word()
        accession2 = rw.random_word()
        args, _ = parse_args(
            "notes add -N '{name}' -D '{details}' -S '{software_name}' -T {software_version} "
            "-P '{software_processing_details}' -E {resource1} {url1} {accession1} "
            "-E {resource2} {url2} {accession2} file.sff --config-path {config_path}".format(
                name=name,
                details=details,
                software_name=software_name,
                software_version=software_version,
                software_processing_details=software_processing_details,
                resource1=resource1,
                url1=url1,
                accession1=accession1,
                resource2=resource2,
                url2=url2,
                accession2=accession2,
                config_path=self.config_fn,
            ),
            use_shlex=True
        )
        self.assertEqual(args.notes_subcommand, 'add')
        self.assertEqual(args.name, name)
        self.assertEqual(args.software_name, software_name)
        self.assertEqual(args.software_version, software_version)
        self.assertEqual(args.software_processing_details, software_processing_details)
        self.assertEqual(args.details, details)
        self.assertIsInstance(args.name, _str)
        self.assertIsInstance(args.details, _str)
        self.assertIsInstance(args.software_name, _str)
        self.assertIsInstance(args.software_version, _str)
        self.assertIsInstance(args.software_processing_details, _str)
        for i, tov in enumerate(args.external_ref):
            t, o, v = tov  # resource, url, accession
            self.assertEqual(args.external_ref[i][0], t)
            self.assertEqual(args.external_ref[i][1], o)
            self.assertEqual(args.external_ref[i][2], v)
            self.assertIsInstance(t, _str)
            self.assertIsInstance(o, _str)
            self.assertIsInstance(v, _str)

    def test_add_to_segment(self):
        """Test add segment notes"""
        name = " ".join(rw.random_words(count=3)).title()
        description = li.get_sentences(3)
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        resource1 = rw.random_word()
        url1 = rw.random_word()
        accession1 = rw.random_word()
        resource2 = rw.random_word()
        url2 = rw.random_word()
        accession2 = rw.random_word()
        cmd = "notes add -i {id} -n '{name}' -d '{description}' -I {number_of_instances} " \
              "-E {resource1} {url1} {accession1} -E {resource2} {url2} {accession2} " \
              "file.sff --config-path {config_path}".format(
            id=segment_id, name=name,
            description=description,
            number_of_instances=number_of_instances,
            resource1=resource1,
            url1=url1,
            accession1=accession1,
            resource2=resource2,
            url2=url2,
            accession2=accession2,
            config_path=self.config_fn
        )
        args, _ = parse_args(cmd, use_shlex=True)
        #  assertions
        self.assertEqual(args.notes_subcommand, 'add')
        self.assertCountEqual(args.segment_id, [segment_id])
        self.assertEqual(args.segment_name, name)
        self.assertEqual(args.description, description)
        self.assertEqual(args.number_of_instances, number_of_instances)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)
        # unicode
        self.assertIsInstance(args.segment_name, _str)
        self.assertIsInstance(args.description, _str)
        for i, rua in enumerate(args.external_ref):
            r, u, a = rua  # resource, url, accession
            self.assertEqual(args.external_ref[i][0], r)
            self.assertEqual(args.external_ref[i][1], u)
            self.assertEqual(args.external_ref[i][2], a)
            self.assertIsInstance(r, _str)
            self.assertIsInstance(u, _str)
            self.assertIsInstance(a, _str)

    def test_add_addendum_missing(self):
        """Test assertion fails if addendum is missing"""
        segment_id = _random_integer()
        args, _ = parse_args(
            'notes add -i {} file.sff --config-path {}'.format(segment_id, self.config_fn), use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    # ===========================================================================
    # notes: edit
    # ===========================================================================
    def test_edit_in_global(self):
        """Test edit global notes"""
        name = ' '.join(rw.random_words(count=3)).title()
        details = li.get_sentences(5)
        software_id = _random_integer(start=0)
        software_name = rw.random_word()
        software_version = 'v{}.{}.{}'.format(_random_integer(), _random_integer(), _random_integer())
        software_processing_details = li.get_sentences(4)
        resource1 = rw.random_word()
        url1 = rw.random_word()
        accession1 = rw.random_word()
        resource2 = rw.random_word()
        url2 = rw.random_word()
        accession2 = rw.random_word()
        external_ref_id = _random_integer(start=0)
        cmd = "notes edit -N '{name}' -D '{details}' -s {software_id} -S '{software_name}' -T {software_version} " \
              "-P '{software_processing_details}' file.sff --config-path {config_path} " \
              "-e {external_ref_id} -E {resource1} {url1} {accession1} -E {resource2} {url2} {accession2}".format(
            name=name,
            details=details,
            software_id=software_id,
            software_name=software_name,
            software_version=software_version,
            software_processing_details=software_processing_details,
            external_ref_id=external_ref_id,
            config_path=self.config_fn,
            resource1=resource1,
            url1=url1,
            accession1=accession1,
            resource2=resource2,
            url2=url2,
            accession2=accession2
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.stderr(args)
        self.assertEqual(args.notes_subcommand, 'edit')
        self.assertEqual(args.name, name)
        self.assertEqual(args.details, details)
        self.assertEqual(args.software_id, software_id)
        self.assertEqual(args.software_name, software_name)
        self.assertEqual(args.software_version, software_version)
        self.assertEqual(args.software_processing_details, software_processing_details)
        self.assertIsInstance(args.name, _str)
        self.assertIsInstance(args.details, _str)
        self.assertIsInstance(args.software_name, _str)
        self.assertIsInstance(args.software_version, _str)
        self.assertIsInstance(args.software_processing_details, _str)
        self.assertEqual(args.external_ref_id, external_ref_id)
        for i, tov in enumerate(args.external_ref):
            t, o, v = tov  # resource, url, accession
            self.assertEqual(args.external_ref[i][0], t)
            self.assertEqual(args.external_ref[i][1], o)
            self.assertEqual(args.external_ref[i][2], v)
            self.assertIsInstance(t, _str)
            self.assertIsInstance(o, _str)
            self.assertIsInstance(v, _str)

    def test_edit_in_segment(self):
        """Test edit segment notes"""
        name = " ".join(rw.random_words(count=3)).title()
        description = li.get_sentences(3)
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        external_ref_id = _random_integer(start=0)
        resource1 = rw.random_word()
        url1 = rw.random_word()
        accession1 = rw.random_word()
        resource2 = rw.random_word()
        url2 = rw.random_word()
        accession2 = rw.random_word()
        cmd = "notes edit -i {id} -n '{name}' -d '{description}' -I {number_of_instances} " \
              "-e {external_ref_id} -E {resource1} {url1} {accession1} -E {resource2} {url2} {accession2} " \
              "file.sff --config-path {config_path}".format(
            id=segment_id,
            name=name,
            description=description,
            number_of_instances=number_of_instances,
            external_ref_id=external_ref_id,
            resource1=resource1,
            url1=url1,
            accession1=accession1,
            resource2=resource2,
            url2=url2,
            accession2=accession2,
            config_path=self.config_fn
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'edit')
        self.assertCountEqual(args.segment_id, [segment_id])
        self.assertEqual(args.description, description)
        self.assertEqual(args.number_of_instances, number_of_instances)
        self.assertEqual(args.external_ref_id, external_ref_id)
        self.assertCountEqual(args.external_ref, [[resource1, url1, accession1], [resource2, url2, accession2]])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_edit_failure_on_missing_ids(self):
        """Test handling of missing IDs"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        external_ref_id = _random_integer()
        args, _ = parse_args(
            'notes edit -i {} -d something -I {} -E abc ABC 123 file.sff --config-path {}'.format(
                segment_id, number_of_instances,
                self.config_fn,
            ), use_shlex=True)

        self.assertEqual(args, os.EX_USAGE)

        args, _ = parse_args(
            "notes edit -S new -T 1.3 -P 'we added one piece to another' @ --config-path {}".format(
                self.config_fn,
            ),
            use_shlex=True
        )
        self.assertEqual(args, os.EX_USAGE)

    # ===========================================================================
    # notes: del
    # ===========================================================================
    def test_del_default(self):
        """Test del notes"""
        software_id = _random_integers(count=3, start=0)
        segment_id = _random_integer()
        external_ref_id = _random_integers(count=5, start=0)
        args, _ = parse_args('notes del -s {} -i {} -d -I -e {} file.sff --config-path {}'.format(
            ','.join(map(_str, software_id)),
            segment_id,
            ','.join(map(_str, external_ref_id)),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'del')
        self.assertCountEqual(args.segment_id, [segment_id])
        self.assertTrue(args.description)
        self.assertTrue(args.number_of_instances)
        self.assertEqual(args.software_id, software_id)
        self.assertCountEqual(args.external_ref_id, external_ref_id)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_del_software(self):
        """Test software delete scenarios"""
        ids = _random_integers(count=5, start=0)
        # if -s <id_list> only then delete the whole software entity for all ids
        args, _ = parse_args(
            'notes del -s {} file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.stderr(args)
        self.assertCountEqual(args.software_id, ids)
        self.assertTrue(args.software_name)
        self.assertTrue(args.software_version)
        self.assertTrue(args.software_processing_details)
        # if -s <id_list> -S the delete only the software name for the s/w ids
        args, _ = parse_args(
            'notes del -s {} -S file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.assertCountEqual(args.software_id, ids)
        self.assertTrue(args.software_name)
        self.assertFalse(args.software_version)
        self.assertFalse(args.software_processing_details)
        # if -s <id_list> -T the delete only the software version for the s/w ids
        args, _ = parse_args(
            'notes del -s {} -T file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.assertCountEqual(args.software_id, ids)
        self.assertFalse(args.software_name)
        self.assertTrue(args.software_version)
        self.assertFalse(args.software_processing_details)
        # if -s <id_list> -P the delete only the software processing details for the s/w ids
        args, _ = parse_args(
            'notes del -s {} -P file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.assertCountEqual(args.software_id, ids)
        self.assertFalse(args.software_name)
        self.assertFalse(args.software_version)
        self.assertTrue(args.software_processing_details)
        # if -s <id_list> -S -T the delete only the software name and version for the s/w ids
        args, _ = parse_args(
            'notes del -s {} -S -T file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.assertCountEqual(args.software_id, ids)
        self.assertTrue(args.software_name)
        self.assertTrue(args.software_version)
        self.assertFalse(args.software_processing_details)
        # if -s <id_list> -S -P the delete only the software name and proc. details for the s/w ids
        args, _ = parse_args(
            'notes del -s {} -S -P file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.assertCountEqual(args.software_id, ids)
        self.assertTrue(args.software_name)
        self.assertFalse(args.software_version)
        self.assertTrue(args.software_processing_details)
        # if -s <id_list> -T -P the delete only the software version and proc. details for the s/w ids
        args, _ = parse_args(
            'notes del -s {} -T -P file.sff --config-path {}'.format(','.join(map(_str, ids)), self.config_fn),
            use_shlex=True
        )
        self.assertCountEqual(args.software_id, ids)
        self.assertFalse(args.software_name)
        self.assertTrue(args.software_version)
        self.assertTrue(args.software_processing_details)
        # otherwise all are False
        args, _ = parse_args(
            'notes del file.sff --config-path {}'.format(self.config_fn),
            use_shlex=True
        )
        self.assertIsNone(args.software_id)
        self.assertFalse(args.software_name)
        self.assertFalse(args.software_version)
        self.assertFalse(args.software_processing_details)

    # =========================================================================
    # notes: copy
    # =========================================================================
    def test_copy_default(self):
        """Test that we can run copy"""
        source_id = _random_integer(start=1)
        other_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=source_id, other_id=other_id, config_fn=self.config_fn, )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertCountEqual(args.segment_id, [source_id])
        self.assertCountEqual(args.to_segment, [other_id])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_to_multiple(self):
        """Test that we can copy from one to multiple"""
        source_id = _random_integer(start=1)
        other_id = _random_integers(start=1)
        # make sure that source_id does not exist in other_id
        other_id = list(set(other_id).difference({source_id}))
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=source_id, other_id=','.join(map(str, other_id)), config_fn=self.config_fn, )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertCountEqual(args.segment_id, [source_id])
        self.assertCountEqual(args.to_segment, other_id)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_from_multiple(self):
        """Test that we can copy from multiple to one"""
        source_id = _random_integers(start=1, stop=200)
        other_id = _random_integer(start=201, stop=400)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=','.join(map(str, source_id)), other_id=other_id, config_fn=self.config_fn, )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertCountEqual(args.segment_id, source_id)
        self.assertCountEqual(args.to_segment, [other_id])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_from_multiple_to_multiple(self):
        """Test that we can copy from multiple to multiple"""
        source_id = _random_integers(start=1, stop=100)
        other_id = _random_integers(start=101, stop=200)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=','.join(map(str, source_id)), other_id=','.join(map(str, other_id)), config_fn=self.config_fn, )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertCountEqual(args.segment_id, source_id)
        self.assertCountEqual(args.to_segment, other_id)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_check_unique_ids(self):
        """Test that we don't copy ids between the same segment"""
        source_id = _random_integers(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=','.join(map(str, source_id)), other_id=','.join(map(str, source_id)), config_fn=self.config_fn, )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args, os.EX_USAGE)

    def test_copy_all(self):
        """Test that we can copy to all others"""
        # all other ids should be correctly generated
        source_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-all --config-path {config_fn} file.sff'.format(
            source_id=source_id,
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertTrue(args.to_all)

    def test_copy_to_and_all_exception(self):
        source_id = _random_integer(start=1)
        other_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --to-all --config-path {config_fn} file.sff'.format(
            source_id=source_id,
            other_id=other_id,
            config_fn=self.config_fn,
        )
        with self.assertRaises(SystemExit):
            args, _ = parse_args(cmd, use_shlex=True)

    def test_copy_from_global_notes(self):
        """Test copy from global"""
        other_id = _random_integers(start=1)
        cmd = "notes copy --from-global --to-segment {other_id} --config-path {config_fn} file.sff".format(
            other_id=','.join(map(str, other_id)),
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertTrue(args.from_global)
        self.assertFalse(args.to_global)

    def test_copy_to_global_notes(self):
        """Test copy to global"""
        source_id = _random_integer(start=1)
        cmd = "notes copy --segment-id {source_id} --to-global --config-path {config_fn} file.sff".format(
            source_id=source_id,
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertTrue(args.to_global)
        self.assertFalse(args.from_global)

    # =========================================================================
    # notes: clear
    # =========================================================================
    def test_clear_default(self):
        """Test that we can clear notes for a single segment"""
        source_id = _random_integer(start=1)
        cmd = "notes clear --segment-id {source_id} --config-path {config_fn} file.sff".format(
            source_id=source_id,
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.notes_subcommand, 'clear')
        self.assertEqual(list(args.segment_id), [source_id])
        self.assertFalse(args.from_all_segments)

    def test_clear_multiple(self):
        """Test that we can clear many but not all"""
        source_id = _random_integers(start=1)
        cmd = "notes clear --segment-id {source_id} --config-path {config_fn} file.sff".format(
            source_id=','.join(map(str, source_id)),
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertEqual(list(args.segment_id), source_id)

    def test_clear_all_except_global(self):
        """Test that we can clear all except global"""
        cmd = "notes clear --from-all-segments --config-path {config_fn} file.sff".format(
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertTrue(args.from_all_segments)

    def test_clear_global_only(self):
        """Test that we can clear global only"""
        cmd = "notes clear --from-global --config-path {config_fn} file.sff".format(
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertTrue(args.from_global)

    def test_clear_all(self):
        """Test that we can clear all notes"""
        cmd = "notes clear --all --config-path {config_fn} file.sff".format(
            config_fn=self.config_fn,
        )
        args, _ = parse_args(cmd, use_shlex=True)
        self.assertTrue(args.all)
        self.assertTrue(args.from_global)
        self.assertTrue(args.from_all_segments)

    # =========================================================================
    # notes: save
    # =========================================================================
    def test_save(self):
        """Test save edits"""
        segment_id = _random_integer()
        args, _ = parse_args(
            "notes edit -i {} -d something file.sff --config-path {}".format(segment_id, self.config_fn),
            use_shlex=True)
        self.assertEqual(args.sff_file, 'file.sff')
        #  can only save to an existing file
        save_fn = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')
        args1, _ = parse_args("notes save {} --config-path {}".format(save_fn, self.config_fn), use_shlex=True)
        self.assertEqual(args1.notes_subcommand, 'save')
        self.assertEqual(args1.sff_file, save_fn)
        self.assertEqual(args.config_path, self.config_fn)

    # ===========================================================================
    # notes: trash
    # ===========================================================================
    def test_trash(self):
        """Test trash notes"""
        segment_id = _random_integer()
        args, _ = parse_args(
            "notes edit -i {} -d something file.sff --config-path {}".format(segment_id, self.config_fn),
            use_shlex=True)
        self.assertEqual(args.sff_file, 'file.sff')
        args1, _ = parse_args("notes trash @ --config-path {}".format(self.config_fn), use_shlex=True)
        self.assertEqual(args1.notes_subcommand, 'trash')
        self.assertEqual(args.config_path, self.config_fn)

    # ===========================================================================
    # notes: merge vanilla
    # ===========================================================================
    def test_merge(self):
        """Test merge notes"""
        args, _ = parse_args(
            "notes merge --source file.json file.hff --output file.sff --config-path {}".format(self.config_fn),
            use_shlex=True)
        self.assertEqual(args.source, 'file.json')
        self.assertEqual(args.other, 'file.hff')
        self.assertEqual(args.output, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_merge_output_implied(self):
        """Test with output implied i.e. no --output arg"""
        args, _ = parse_args(
            "notes merge --source file.json file.hff --config-path {}".format(self.config_fn), use_shlex=True)
        self.assertEqual(args.source, 'file.json')
        self.assertEqual(args.other, 'file.hff')
        self.assertEqual(args.output, 'file.hff')
        self.assertEqual(args.config_path, self.config_fn)


class TestCoreUtils(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCoreUtils, cls).setUpClass()
        cls.stderr("utils tests...")

    def test_get_path_one_level(self):
        """Test that we can get an item at a path one level deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': x, 1: y}
        path = ['a']
        self.assertEqual(utils.get_path(D, path), x)
        path = [1]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_two_level(self):
        """Test that we can get an item at a path two levels deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': x,
            1: y,
        }}
        path = ['a', 'b']
        self.assertEqual(utils.get_path(D, path), x)
        path = ['a', 1]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_three_levels(self):
        """Test that we can get an item at a path three levels deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': {
                'c': x,
            },
            1: {
                2: y,
            }
        }}
        path = ['a', 'b', 'c']
        self.assertEqual(utils.get_path(D, path), x)
        path = ['a', 1, 2]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_four_levels(self):
        """Test that we can get an item at a path four levels deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': {
                'c': {
                    'd': x,
                },
                1: {
                    2: y,
                }
            }
        }}
        path = ['a', 'b', 'c', 'd']
        self.assertEqual(utils.get_path(D, path), x)
        path = ['a', 'b', 1, 2]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_keyerror(self):
        """Test that we get a KeyError exception if the path does not exist"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': {
                'c': {
                    'd': x,
                },
                'e': {
                    'f': y,
                }
            }
        }}
        # invalid path returns None
        path = ['a', 'b', 'c', 'f']
        # with self.assertRaises(KeyError):
        val = utils.get_path(D, path)
        self.assertIsNone(val)

    def test_get_path_nondict_type_error(self):
        """Test that we get an exception when D is not a dict"""
        D = ['some rubbish list']
        path = ['a']
        with self.assertRaises(AssertionError):
            utils.get_path(D, path)

    def test_get_path_unhashable_in_path(self):
        """Test that unhashable in path fails"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': x, 'b': y}
        path = [[5]]
        with self.assertRaises(TypeError):
            utils.get_path(D, path)

    def test_rgba_to_hex(self):
        """Test converting colours"""
        hex1 = utils.rgba_to_hex((0, 0, 0, 0))
        self.assertEqual(hex1, '#000000')
        hex2 = utils.rgba_to_hex((0, 0, 0, 0), channels=4)
        self.assertEqual(hex2, '#00000000')
        hex3 = utils.rgba_to_hex((0, 0, 0))
        self.assertEqual(hex3, '#000000')
        hex4 = utils.rgba_to_hex((0, 0, 0), channels=4)
        self.assertEqual(hex4, '#000000ff')
        with self.assertRaises(ValueError):
            utils.rgba_to_hex((2, 2, 2, 0), channels=4)
        with self.assertRaises(ValueError):
            utils.rgba_to_hex((0, 0, 0, 0), channels=5)

    def test_parse_and_split(self):
        """Test the parser utility"""
        cmd = 'notes list file.sff'
        args, configs = parse_args(cmd, use_shlex=True)
        self.assertEqual(args.subcommand, 'notes')
        self.assertEqual(args.notes_subcommand, 'list')
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(configs['__TEMP_FILE'], './temp-annotated.json')
        self.assertEqual(configs['__TEMP_FILE_REF'], '@')


class TestCorePrep(Py23FixTestCase):
    def test_binmap_default(self):
        """Test binarise map"""
        test_map_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map')
        cmd = "prep binmap -v {}".format(test_map_file)
        args, _ = parse_args(cmd, use_shlex=True)
        ex_st = bin_map(args, _)
        self.assertEqual(ex_st, os.EX_OK)
        # clean up
        os.remove(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_prep.map'))

    def test_transform_stl_default(self):
        """Test transform stl"""
        # the original STL file
        test_stl_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.stl')
        # lengths = _random_floats(count=3, multiplier=1000)
        # indices = _random_integers(count=3, start=100, stop=1000)
        # origin = _random_floats(count=3, multiplier=10)
        lengths = (2000, 2000, 2000)
        indices = (1000, 1000, 1000)
        origin = (100, 200, 300)
        args, _ = parse_args(
            "prep transform --lengths {lengths} --indices {indices} --origin {origin} --verbose {file}".format(
                file=test_stl_file,
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            ), use_shlex=True)
        # manual_transform
        lengths = numpy.array(args.lengths, dtype=numpy.float32)
        indices = numpy.array(args.indices, dtype=numpy.int32)
        voxel_size = numpy.divide(lengths, indices)
        origin = numpy.array(args.origin, dtype=numpy.float32)
        transform_manual = numpy.array([
            [voxel_size[0], 0, 0, origin[0]],
            [0, voxel_size[1], 0, origin[1]],
            [0, 0, voxel_size[2], origin[2]],
            [0, 0, 0, 1]
        ], dtype=numpy.float32)
        # transform from function
        transform_f = construct_transformation_matrix(args)
        self.assertTrue(numpy.allclose(transform_manual, transform_f))
        original_mesh = Mesh.from_file(test_stl_file)
        # the upper limit for random ints
        no_verts = original_mesh.v0.shape[0]
        # random vertices
        v0_index = _random_integer(start=0, stop=no_verts)
        v1_index = _random_integer(start=0, stop=no_verts)
        v2_index = _random_integer(start=0, stop=no_verts)
        # transform the mesh
        transformd_mesh = transform_stl_mesh(original_mesh, transform_f)
        # make sure the shapes are identical
        self.assertEqual(original_mesh.v0.shape, transformd_mesh.v0.shape)
        self.assertEqual(original_mesh.v1.shape, transformd_mesh.v1.shape)
        self.assertEqual(original_mesh.v2.shape, transformd_mesh.v2.shape)
        # now we pick some vertices at random and compare them
        transformd_vertex_v0 = numpy.dot(transform_f[0:3, 0:3], original_mesh.v0[v0_index].T).T
        transformd_vertex_v0 += transform_f[0:3, 3].T
        transformd_vertex_v1 = numpy.dot(transform_f[0:3, 0:3], original_mesh.v1[v1_index].T).T
        transformd_vertex_v1 += transform_f[0:3, 3].T
        transformd_vertex_v2 = numpy.dot(transform_f[0:3, 0:3], original_mesh.v2[v2_index].T).T
        transformd_vertex_v2 += transform_f[0:3, 3].T
        self.assertTrue(numpy.allclose(transformd_vertex_v0, transformd_mesh.v0[v0_index]))
        self.assertTrue(numpy.allclose(transformd_vertex_v1, transformd_mesh.v1[v1_index]))
        self.assertTrue(numpy.allclose(transformd_vertex_v2, transformd_mesh.v2[v2_index]))
