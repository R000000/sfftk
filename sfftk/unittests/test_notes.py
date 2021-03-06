#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for :py:mod:`sfftk.core.notes` package"""

from __future__ import division, print_function

import json
import os

import requests
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
import shutil
import unittest
from random_words import RandomWords, LoremIpsum
from sfftkrw.core import _urlencode, _xrange, _str, utils
from sfftkrw.unittests import Py23FixTestCase, _random_integer, _random_integers

from . import TEST_DATA_PATH
from .. import BASE_DIR
from ..core.parser import parse_args
from ..notes import find, modify, view, RESOURCE_LIST
from ..sff import _handle_notes_modify, handle_notes_trash

rw = RandomWords()
li = LoremIpsum()

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-05-15"


# :TODO: rewrite to use sfftk.notes.modify.SimpleNote


class TestNotesModifyExternalReference(Py23FixTestCase):
    def test_ols(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        resource = u'ncit'
        url = u'http://purl.obolibrary.org/obo/NCIT_C62195'
        accession = u'NCIT_C62195'
        # likely to change
        label = u'Wild Type'
        description = u'The naturally-occurring, normal, non-mutated version of a gene or genome.'
        urlenc = _urlencode({u'iri': url.encode(u'idna')})
        urlenc2 = _urlencode({u'iri': urlenc.split(u'=')[1]})
        urlenc3 = urlenc2.split(u'=')[1]
        ext_ref = modify.ExternalReference(
            resource=resource,
            url=url,
            accession=accession,
        )
        self.assertEqual(ext_ref.resource, resource)
        self.assertEqual(ext_ref.url, url)
        self.assertEqual(ext_ref.accession, accession)
        self.assertEqual(ext_ref.label, label)
        self.assertEqual(ext_ref.description,
                         description)
        self.assertCountEqual(ext_ref._get_text(), [label, description])
        self.assertEqual(ext_ref.iri, urlenc3)

    def test_emdb(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        resource = u'EMDB'
        url = u'https://www.ebi.ac.uk/pdbe/emdb/EMD-8654'
        accession = u'EMD-8654'
        # likely to change
        label = u'EMD-8654'
        description = u'Zika virus-infected Vero E6 cell at 48 hpi: dual-axis tilt series tomogram from 3 serial sections'
        ext_ref = modify.ExternalReference(
            resource=resource,
            url=url,
            accession=accession,
        )
        self.assertEqual(ext_ref.resource, resource)
        self.assertEqual(ext_ref.url, url)
        self.assertEqual(ext_ref.accession, accession)
        self.assertEqual(ext_ref.label, label)
        self.assertEqual(ext_ref.description,
                         description)
        self.assertCountEqual(ext_ref._get_text(), [label, description])

    def test_pdb(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        resource = u'PDB'
        url = u'https://www.ebi.ac.uk/pdbe/entry/pdb/4gzw'
        accession = u'4gzw'
        # likely to change
        label = u'N2 neuraminidase D151G mutant of A/Tanzania/205/2010 H3N2 in complex with avian sialic acid receptor'
        description = u'H3N2 subtype'
        ext_ref = modify.ExternalReference(
            resource=resource,
            url=url,
            accession=accession,
        )
        self.assertEqual(ext_ref.resource, resource)
        self.assertEqual(ext_ref.url, url)
        self.assertEqual(ext_ref.accession, accession)
        self.assertEqual(ext_ref.label, label)
        self.assertEqual(ext_ref.description,
                         description)
        self.assertCountEqual(ext_ref._get_text(), [label, description])

    def test_uniprot(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        resource = u'UniProt'
        url = u'https://www.uniprot.org/uniprot/A0A1Q8WSX6'
        accession = u'A0A1Q8WSX6'
        # likely to change
        label = u'A0A1Q8WSX6_9ACTO'
        description = u'Type I-E CRISPR-associated protein Cas5/CasD (Organism: Actinomyces oris)'
        ext_ref = modify.ExternalReference(
            resource=resource,
            url=url,
            accession=accession,
        )
        self.assertEqual(ext_ref.resource, resource)
        self.assertEqual(ext_ref.url, url)
        self.assertEqual(ext_ref.accession, accession)
        self.assertEqual(ext_ref.label, label)
        self.assertEqual(ext_ref.description,
                         description)
        self.assertCountEqual(ext_ref._get_text(), [label, description])

    def test_europepmc(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        resource = u'Europe PMC'
        url = u'http://europepmc.org/abstract/MED/30932919'
        accession = u'30932919'
        label = u'Perugi G, De Rossi P, Fagiolini A, Girardi P, Maina G, Sani G, Serretti A.'
        description = u'Personalized and precision medicine as informants for treatment management of bipolar disorder.'
        ext_ref = modify.ExternalReference(
            resource=resource,
            url=url,
            accession=accession,
        )
        self.assertEqual(ext_ref.resource, resource)
        self.assertEqual(ext_ref.url, url)
        self.assertEqual(ext_ref.accession, accession)
        self.assertEqual(ext_ref.label, label)
        self.assertEqual(ext_ref.description,
                         description)
        self.assertCountEqual(ext_ref._get_text(), [label, description])

    def test_empiar(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        resource = u'EMPIAR'
        url = u'https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/10087/'
        accession = u'EMPIAR-10087'
        label = u'Soft X-ray tomography of Plasmodium falciparum infected human erythrocytes stalled in egress by the ' \
                u'inhibitors Compound 2 and E64'
        description = u'SXT'
        ext_ref = modify.ExternalReference(
            resource=resource,
            url=url,
            accession=accession,
        )
        self.assertEqual(ext_ref.resource, resource)
        self.assertEqual(ext_ref.url, url)
        self.assertEqual(ext_ref.accession, accession)
        self.assertEqual(ext_ref.label, label)
        self.assertEqual(ext_ref.description,
                         description)
        self.assertCountEqual(ext_ref._get_text(), [label, description])


class TestNotesFindSearchResource(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestNotesFindSearchResource, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_unknown_resource(self):
        """Test exception raised formed unknown resource"""
        with self.assertRaises(SystemExit):
            args, config = parse_args(
                'notes search --resource xxx "something" --config-path {}'.format(self.config_fn),
                use_shlex=True
            )

    def test_configs_attribute(self):
        """Test the value of the configs attribute"""
        args, configs = parse_args(
            'notes search --resource ols "mitochondria" --config-path {}'.format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.configs, configs)

    def test_result_path(self):
        """Test result path attr"""
        args, configs = parse_args("notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn),
                                   use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.result_path, RESOURCE_LIST['ols']['result_path'])

    def test_result_count(self):
        """Test result_count attr"""
        args, configs = parse_args(
            "notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.result_count, RESOURCE_LIST['ols']['result_count'])

    def test_format(self):
        """Test format attr"""
        args, configs = parse_args("notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn),
                                   use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.format, RESOURCE_LIST['ols']['format'])

    def test_response(self):
        """Test response attr"""
        args, configs = parse_args(
            "notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertIsNone(resource.response)
        resource.search()
        url = resource.get_url()
        R = requests.get(url)
        if resource.response is not None:
            resource_results = utils.get_path(json.loads(resource.response), resource.result_path)
        else:
            resource_results = None
        test_results = utils.get_path(json.loads(R.text), resource.result_path)
        if resource_results is not None and test_results is not None:
            self.assertCountEqual(resource_results, test_results)
        else:
            self.stderr(u"Warning: unable to run test on response due to API issue to {url}".format(url=url))

    def test_get_url_ols_list_ontologies(self):
        """Test url correctness for OLS"""
        resource_name = 'ols'
        args, configs = parse_args("notes search -R {resource_name} 'mitochondria' -L --config-path {config_fn}".format(
            resource_name=resource_name,
            config_fn=self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}ontologies?size=1000".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_ols(self):
        """Test url correctness for OLS"""
        resource_name = 'ols'
        args, configs = parse_args(
            "notes search -R {resource_name} 'mitochondria' -O go -x -o --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}search?q={search_term}&start={start}&rows={rows}&local=true&ontology={ontology}&exact=on&obsoletes=on".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start - 1,
            rows=args.rows,
            ontology=args.ontology,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_emdb(self):
        """Test url correctness for EMDB"""
        resource_name = 'emdb'
        args, configs = parse_args("notes search -R {resource_name} 'mitochondria' --config-path {config_fn}".format(
            resource_name=resource_name,
            config_fn=self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}?q={search_term}&start={start}&rows={rows}".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_uniprot(self):
        """Test url correctness for UniProt"""
        resource_name = 'uniprot'
        args, configs = parse_args(
            "notes search -R {resource_name} 'mitochondria' --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}?query={search_term}&format=tab&offset={start}&limit={rows}&columns=id,entry_name,protein_names,organism".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_pdb(self):
        """Test url correctness for PDB"""
        resource_name = 'pdb'
        args, configs = parse_args("notes search -R {resource_name} 'mitochondria' --config-path {config_fn}".format(
            resource_name=resource_name,
            config_fn=self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}?q={search_term}&wt=json&fl=pdb_id,title,organism_scientific_name&start={start}&rows={rows}".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_europepmc(self):
        """Test url correctness for Europe PMC"""
        resource_name = 'europepmc'
        args, configs = parse_args(
            "notes search -R {resource_name} 'picked' --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ), use_shlex=True
        )
        resource = find.SearchResource(args, configs)
        url = "{root_url}search?query={search_term}&resultType=lite&cursorMark=*&pageSize={rows}&format=json".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_empiar(self):
        """Test url correctness for EMPIAR"""
        resource_name = 'empiar'
        args, configs = parse_args(
            "notes search -R {resource_name} 'picked' --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ),
            use_shlex=True,
        )
        resource = find.SearchResource(args, configs)
        url = "{root_url}?q={search_term}&wt=json&start={start}&rows={rows}".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows
        )
        # the url has an additional random (unpredictable) value that will break the comparison
        # let's remove it before the equality assertion
        resource_url = '&'.join(resource.get_url().split('&')[:-1])
        self.assertEqual(resource_url, url)


class TestNotesFindTableField(Py23FixTestCase):
    def test_init_name(self):
        """Test instantiation of TableField object"""
        with self.assertRaisesRegex(ValueError,
                                    "key and text are mutually exclusive; only define one or none of them"):
            find.TableField('my-field', key='k', text='t')

    def test_init_width_type(self):
        """Test check on width type"""
        with self.assertRaisesRegex(ValueError, "field width must be int or long"):
            find.TableField('my-field', width=1.3)

    def test_init_width_value(self):
        """Test check on width value"""
        with self.assertRaisesRegex(ValueError, "field width must be greater than 0"):
            find.TableField('my-field', width=0)

    def test_init_pc_type(self):
        """Test pc type"""
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc='1.3')
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=u'1.3')
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=list())
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=dict())
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=tuple())

    def test_init_pc_value(self):
        """Test pc value"""
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=-1)
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=100)
        self.assertIsInstance(find.TableField('my-field', pc=50), find.TableField)

    def test_init_justify(self):
        """Test value for justify"""
        self.assertIsInstance(find.TableField('my-field', text='t', justify='left'), find.TableField)
        self.assertIsInstance(find.TableField('my-field', text='t', justify='right'), find.TableField)
        self.assertIsInstance(find.TableField('my-field', text='t', justify='center'), find.TableField)


class TestNotes_view(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestNotes_view, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def setUp(self):
        super(TestNotes_view, self).setUp()
        self.segment_id = 15559
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')

    def test_list_default(self):
        """Test that we can view the list of segmentations with annotations"""
        args, configs = parse_args("notes list {} --config-path {}".format(
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.list_notes(args, configs)
        # assertions
        self.assertEqual(status, os.EX_OK)

    def test_long_list(self):
        """Test that we can long list (-l) the list of segmentations with annotations"""
        args, configs = parse_args("notes list -l {} --config-path {}".format(
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.list_notes(args, configs)
        # assertions
        self.assertEqual(status, os.EX_OK)

    def test_list_ids(self):
        """Test that we can list ids only and that they are usable"""
        args, configs = parse_args("notes list -I {file} --config-path {config}".format(
            file=self.sff_file,
            config=self.config_fn
        ), use_shlex=True)
        view.list_notes(args, configs)
        seg = schema.SFFSegmentation.from_file(self.sff_file)
        for segment_id in seg.segment_list.get_ids():
            args, configs = parse_args("notes show -i {segment_id} {file} --config-path {config}".format(
                segment_id=segment_id,
                file=self.sff_file,
                config=self.config_fn
            ), use_shlex=True)
            status = view.show_notes(args, configs)
            self.assertEqual(status, os.EX_OK)



    def test_show_default(self):
        """Test that we can show annotations in a single segment"""
        args, configs = parse_args("notes show -i {} {} --config-path {}".format(
            self.segment_id,
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.show_notes(args, configs)
        self.assertEqual(status, os.EX_OK)

    def test_long_show(self):
        """Test that we can show in long format annotations in a single segment"""
        args, configs = parse_args("notes show -l -i {} {} --config-path {}".format(
            self.segment_id,
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.show_notes(args, configs)
        self.assertEqual(status, os.EX_OK)


class TestNotes_modify(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestNotes_modify, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        cls.sff_file = None
        cls.output = None
        cls.annotated_sff_file = None

    # test filetypeA to filetypeB
    def setUp(self):
        super(TestNotes_modify, self).setUp()
        # remove any temporary files
        args, configs = parse_args("notes trash @ --config-path {config}".format(
            config=self.config_fn), use_shlex=True
        )
        handle_notes_trash(args, configs)
        self.segment_id = 15559

    def tearDown(self):
        super(TestNotes_modify, self).tearDown()
        # remove any temporary files
        args, configs = parse_args("notes trash @ --config-path {config}".format(
            config=self.config_fn), use_shlex=True
        )
        handle_notes_trash(args, configs)

    def _test_add_global(self):
        """Test addding of global notes"""
        name = ' '.join(rw.random_words())
        details = li.get_sentences(sentences=3)
        software_name = rw.random_word()
        software_version = rw.random_word()
        software_processing_details = li.get_sentences(sentences=2)
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        # self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        cmd = "notes add -N '{name}' -D '{details}' -S {software_name} -T {software_version} " \
              "-P '{software_processing_details}' -E {extref1} -E {extref2} {sff_file} " \
              "--verbose --config-path {config}".format(
            name=name,
            details=details,
            software_name=software_name,
            software_version=software_version,
            software_processing_details=software_processing_details,
            extref1=' '.join(extref1),
            extref2=' '.join(extref2),
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        # pass modified args to modify
        status = modify.add_note(args, configs)
        seg = schema.SFFSegmentation.from_file(args.sff_file)
        self.assertEqual(status, os.EX_OK)
        self.assertEqual(seg.name, name)
        self.assertEqual(seg.details, details)
        self.assertTrue(len(seg.software_list) > 0)
        self.assertEqual(seg.software_list[1].name, software_name)
        self.assertEqual(seg.software_list[1].version, software_version)
        self.assertEqual(seg.software_list[1].processing_details, software_processing_details)
        self.assertEqual(len(seg.global_external_references), 3)
        self.assertEqual(seg.global_external_references[1].resource, extref1[0])
        self.assertEqual(seg.global_external_references[1].url, extref1[1])
        self.assertEqual(seg.global_external_references[1].accession, extref1[2])
        self.assertEqual(seg.global_external_references[2].resource, extref2[0])
        self.assertEqual(seg.global_external_references[2].url, extref2[1])
        self.assertEqual(seg.global_external_references[2].accession, extref2[2])

    def _test_add(self):
        """Test adding segment notes"""
        segment_name = ' '.join(rw.random_words())
        desc = li.get_sentences(sentences=1)
        num = _random_integer()
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        # self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        cmd = "notes add -i {segment_id} -n '{name}' -d '{description}' -E {extref1} -E {extref2} -I {num} " \
              "{sff_file} --config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name,
            description=desc,
            extref1=" ".join(extref1),
            extref2=" ".join(extref2),
            num=num,
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        # first we get the raw args
        _args, configs = parse_args(cmd, use_shlex=True)
        # we intercept them for 'modify' actions
        args = _handle_notes_modify(_args, configs)
        # we pass modified args for 'temp-annotated.json'
        status = modify.add_note(args, configs)
        seg = schema.SFFSegmentation.from_file(args.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status, os.EX_OK)
        self.assertEqual(segment.biological_annotation.description, desc)
        self.assertEqual(segment.biological_annotation.number_of_instances, num)
        self.assertEqual(segment.biological_annotation.external_references[0].resource, extref1[0])
        self.assertEqual(segment.biological_annotation.external_references[0].url, extref1[1])
        self.assertEqual(segment.biological_annotation.external_references[0].accession, extref1[2])
        self.assertEqual(segment.biological_annotation.external_references[1].resource, extref2[0])
        self.assertEqual(segment.biological_annotation.external_references[1].url, extref2[1])
        self.assertEqual(segment.biological_annotation.external_references[1].accession, extref2[2])

    def _test_edit_global(self):
        """Test that we can edit a note"""
        # self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        name = ' '.join(rw.random_words())
        details = li.get_sentences(sentences=3)
        software_name = rw.random_word()
        software_version = rw.random_word()
        software_processing_details = li.get_sentences(sentences=2)
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        # add
        cmd = "notes add -N '{name}' -D '{details}' -S {software_name} -T {software_version} " \
              "-P '{software_processing_details}' -E {extref1} -E {extref2} {sff_file} " \
              "--verbose --config-path {config}".format(
            name=name,
            details=details,
            software_name=software_name,
            software_version=software_version,
            software_processing_details=software_processing_details,
            extref1=' '.join(extref1),
            extref2=' '.join(extref2),
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        modify.add_note(args, configs)
        _seg = schema.SFFSegmentation.from_file(args.sff_file)
        name1 = name[::-1]
        details1 = details[::-1]
        software_name1 = software_name[::-1]
        software_version1 = software_version[::-1]
        software_processing_details1 = software_processing_details[::-1]
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        cmd1 = "notes edit -N '{name}' -D '{details}' -s 1 -S {software_name} -T {software_version} " \
               "-P '{software_processing_details}' -e 1 -E {extref1} -E {extref2} @ " \
               "--verbose --config-path {config}".format(
            name=name1,
            details=details1,
            software_name=software_name1,
            software_version=software_version1,
            software_processing_details=software_processing_details1,
            extref1=' '.join(extref1),
            extref2=' '.join(extref2),
            config=self.config_fn,
        )
        _args1, configs = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs)
        # edit
        status1 = modify.edit_note(args1, configs)
        # we have to compare against the temp-annotated.json file!!!
        seg = schema.SFFSegmentation.from_file(args1.sff_file)
        self.assertEqual(status1, os.EX_OK)
        self.assertEqual(seg.name, name1)
        self.assertEqual(seg.details, details1)
        self.assertTrue(len(seg.software_list), len(_seg.software_list))
        self.assertEqual(seg.software_list[1].name, software_name1)
        self.assertEqual(seg.software_list[1].version, software_version1)
        self.assertEqual(seg.software_list[1].processing_details, software_processing_details1)
        self.assertEqual(seg.global_external_references[1].resource, extref1[0])
        self.assertEqual(seg.global_external_references[1].url, extref1[1])
        self.assertEqual(seg.global_external_references[1].accession, extref1[2])
        self.assertEqual(seg.global_external_references[2].resource, extref2[0])
        self.assertEqual(seg.global_external_references[2].url, extref2[1])
        self.assertEqual(seg.global_external_references[2].accession, extref2[2])

    def _test_edit(self):
        """Test that we can edit a note"""
        # self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        segment_name = ' '.join(rw.random_words())
        desc = li.get_sentences(sentences=1)
        num = _random_integer()
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        # add
        cmd = "notes add -i {segment_id} -n '{name}' -d '{description}' -E {extref1} -E {extref2} -I {num} " \
              "{sff_file} --config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name,
            description=desc,
            extref1=" ".join(extref1),
            extref2=" ".join(extref2),
            num=num,
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        modify.add_note(args, configs)
        segment_name1 = segment_name[::-1]
        desc1 = desc[::-1]
        num1 = _random_integer()
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        cmd1 = "notes edit -i {segment_id} -n '{name}' -d '{description}' " \
               "-e 1 -E {extref1} -E {extref2} -I {num} " \
               "@ --config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name1,
            description=desc1,
            extref1=" ".join(extref1),
            extref2=" ".join(extref2),
            num=num1,
            config=self.config_fn,
        )
        _args1, configs = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs)
        # edit
        status1 = modify.edit_note(args1, configs)
        # # we have to compare against the temp-annotated.json file!!!
        seg = schema.SFFSegmentation.from_file(args1.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status1, os.EX_OK)
        self.assertEqual(segment.biological_annotation.name, segment_name1)
        self.assertEqual(segment.biological_annotation.description, desc1)
        self.assertEqual(segment.biological_annotation.number_of_instances, num1)
        self.assertEqual(segment.biological_annotation.external_references[1].resource, extref1[0])
        self.assertEqual(segment.biological_annotation.external_references[1].url, extref1[1])
        self.assertEqual(segment.biological_annotation.external_references[1].accession, extref1[2])
        self.assertEqual(segment.biological_annotation.external_references[2].resource, extref2[0])
        self.assertEqual(segment.biological_annotation.external_references[2].url, extref2[1])
        self.assertEqual(segment.biological_annotation.external_references[2].accession, extref2[2])

    def _test_del_global(self):
        # self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        name = ' '.join(rw.random_words())
        details = li.get_sentences(sentences=3)
        software_name = rw.random_word()
        software_version = rw.random_word()
        software_processing_details = li.get_sentences(sentences=2)
        extref1 = rw.random_words(count=3)
        extref2 = rw.random_words(count=3)
        # add
        cmd = "notes add -N '{name}' -D '{details}' -S {software_name} -T {software_version} " \
              "-P '{software_processing_details}' -E {extref1} -E {extref2} {sff_file} " \
              "--verbose --config-path {config}".format(
            name=name,
            details=details,
            software_name=software_name,
            software_version=software_version,
            software_processing_details=software_processing_details,
            extref1=' '.join(extref1),
            extref2=' '.join(extref2),
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        modify.add_note(args, configs)
        cmd1 = "notes del -D -s 1 -e 0,1 @ --verbose --config-path {config}".format(
            config=self.config_fn,
        )
        _args1, configs = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs)
        status1 = modify.del_note(args1, configs)
        self.assertEqual(status1, os.EX_OK)
        seg = schema.SFFSegmentation.from_file(args1.sff_file)
        self.assertIsNone(seg.details)
        self.assertEqual(len(seg.software_list), 1)
        self.assertEqual(len(seg.global_external_references), 1)

    def _test_del(self):
        # add
        # self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        name = ' '.join(rw.random_words(count=3))
        descr = li.get_sentences(sentences=2)
        num = _random_integer()
        extref1 = ' '.join(rw.random_words(count=3))
        extref2 = ' '.join(rw.random_words(count=3))
        cmd = "notes add -i {segment_id} -n '{name}' -d '{descr}' -I {num} -E {extref1} -E {extref2} " \
              "{file} --config-path {config}".format(
            segment_id=self.segment_id,
            name=name,
            descr=descr,
            num=num,
            extref1=extref1,
            extref2=extref2,
            file=self.sff_file,
            config=self.config_fn
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        status = modify.add_note(args, configs)
        # delete
        cmd1 = "notes del -i {segment_id} -n -d -I -e 0,1 @ --config-path {config}".format(
            segment_id=self.segment_id,
            config=self.config_fn
        )
        _args1, configs1 = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs1)
        status1 = modify.del_note(args1, configs1)
        seg = schema.SFFSegmentation.from_file(args1.sff_file)
        segment = seg.segment_list.get_by_id(self.segment_id)
        self.assertEqual(status1, os.EX_OK)
        self.assertIsNone(segment.biological_annotation.name)
        self.assertIsNone(segment.biological_annotation.description)
        self.assertEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertEqual(len(segment.biological_annotation.external_references), 0)

    def _test_merge(self):
        """Test that we can merge notes"""
        segment_name = ' '.join(rw.random_words(count=3))
        desc = li.get_sentences(sentences=2)
        num = _random_integer()
        extref = rw.random_words(count=3)
        # add
        cmd = "notes add -i {segment_id} -n '{segment_name}' -d '{desc}' -E {extref} -I {num} {sff_file} --config-path {config}".format(
            segment_id=self.segment_id,
            segment_name=segment_name,
            desc=desc,
            extref=' '.join(extref),
            num=num,
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        args, configs = parse_args(cmd, use_shlex=True)
        status = modify.add_note(args, configs)
        self.assertEqual(status, os.EX_OK)
        # merge
        cmd1 = 'notes merge --source {source} {other} --output {output} --config-path {config_fn}'.format(
            source=self.sff_file,
            other=self.other,
            output=self.output,
            config_fn=self.config_fn,
        )
        args1, configs1 = parse_args(cmd1, use_shlex=True)
        status1 = modify.merge(args1, configs1)
        self.assertEqual(status1, os.EX_OK)
        source_seg = schema.SFFSegmentation.from_file(self.sff_file)
        output_seg = schema.SFFSegmentation.from_file(self.output)
        source_segment = source_seg.segments.get_by_id(self.segment_id)
        output_segment = output_seg.segments.get_by_id(self.segment_id)
        self.assertEqual(source_segment.biological_annotation.name, segment_name)
        self.assertEqual(source_segment.biological_annotation.description, desc)
        self.assertEqual(source_segment.biological_annotation.description,
                         output_segment.biological_annotation.description)
        self.assertEqual(source_segment.biological_annotation.number_of_instances, num)
        self.assertEqual(source_segment.biological_annotation.number_of_instances,
                         output_segment.biological_annotation.number_of_instances)
        self.assertEqual(source_segment.biological_annotation.external_references[0].resource, extref[0])
        self.assertEqual(source_segment.biological_annotation.external_references[0].url, extref[1])
        self.assertEqual(source_segment.biological_annotation.external_references[0].accession, extref[2])
        self.assertEqual(source_segment.biological_annotation.external_references[0].resource,
                         output_segment.biological_annotation.external_references[0].resource)

    def _test_clear(self):
        """Test that we can clear notes"""
        segment_name = ' '.join(rw.random_words(count=3))
        desc = li.get_sentences(sentences=2)
        num = _random_integer()
        extref = rw.random_words(count=3)
        # add
        cmd = "notes add -i {segment_id} -n '{name}' -d '{desc}' -E {extref} -I {num} {sff_file} " \
              "--config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name,
            desc=desc,
            extref=" ".join(extref),
            num=num,
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        status = modify.add_note(args, configs)
        self.assertEqual(status, os.EX_OK)
        # clear
        cmd1 = 'notes clear --all @ --config-path {config_fn}'.format(
            config_fn=self.config_fn,
        )
        _args1, configs1 = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs1)
        status1 = modify.clear_notes(args1, configs1)
        self.assertEqual(status1, os.EX_OK)
        seg = schema.SFFSegmentation.from_file(args1.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(len(segment.biological_annotation.external_references), 0)

    def _test_copy(self):
        """Test that we can copy notes"""
        # we have an annotated EMDB-SFF file
        # make a copy of the file for the test
        annotated_sff_file = os.path.join(os.path.dirname(self.annotated_sff_file),
                                          'temp_' + os.path.basename(self.annotated_sff_file))
        shutil.copy2(self.annotated_sff_file, annotated_sff_file)
        # use the file copy
        # before copy
        seg = schema.SFFSegmentation.from_file(annotated_sff_file)
        source_segment = seg.segments.get_by_id(15559)
        # copy
        cmd = "notes copy -i 15559 -t 15578 {ann_sff_file} --config-path {config}".format(
            ann_sff_file=annotated_sff_file,
            config=self.config_fn
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        status1 = modify.copy_notes(args, configs)
        # save
        cmd1 = "notes save {sff_file} --config-path {config}".format(
            sff_file=annotated_sff_file,
            config=self.config_fn,
        )
        args, configs = parse_args(cmd1, use_shlex=True)
        status3 = modify.save(args, configs)
        # debug
        cmd2 = "notes list {sff_file} --config-path {config}".format(
            sff_file=annotated_sff_file,
            config=self.config_fn
        )
        _args1, config = parse_args(cmd2, use_shlex=True)
        args1 = _handle_notes_modify(_args1, config)
        view.list_notes(args1, config)
        self.assertEqual(status1, os.EX_OK)

        copied_seg = schema.SFFSegmentation.from_file(annotated_sff_file)
        copied_segment = copied_seg.segments.get_by_id(15578)
        self.assertEqual(len(source_segment.biological_annotation.external_references),
                         len(copied_segment.biological_annotation.external_references))
        self.assertEqual(source_segment.biological_annotation.external_references[0].resource,
                         copied_segment.biological_annotation.external_references[0].resource)
        self.assertEqual(source_segment.biological_annotation.external_references[0].url,
                         copied_segment.biological_annotation.external_references[0].url)
        self.assertEqual(source_segment.biological_annotation.external_references[0].accession,
                         copied_segment.biological_annotation.external_references[0].accession)
        # # get rid of the copy
        os.remove(annotated_sff_file)


class TestNotes_modify_sff(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_sff, self).setUp()
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff')
        self.other = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'other_emd_1014.sff')
        self.output = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'output_emd_1181.sff')
        self.annotated_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'annotated_emd_1014.sff')

    def tearDown(self):
        super(TestNotes_modify_sff, self).tearDown()
        seg = schema.SFFSegmentation.from_file(self.sff_file)
        # remove all annotations
        for segment in seg.segments:
            segment.biological_annotation = schema.SFFBiologicalAnnotation()
        seg.export(self.sff_file)

    def test_add_global(self):
        super(TestNotes_modify_sff, self)._test_add_global()

    def test_add(self):
        super(TestNotes_modify_sff, self)._test_add()

    def test_edit_global(self):
        super(TestNotes_modify_sff, self)._test_edit_global()

    def test_edit(self):
        super(TestNotes_modify_sff, self)._test_edit()

    def test_del_global(self):
        super(TestNotes_modify_sff, self)._test_del_global()

    def test_del(self):
        super(TestNotes_modify_sff, self)._test_del()

    def test_merge(self):
        super(TestNotes_modify_sff, self)._test_merge()

    def test_clear(self):
        super(TestNotes_modify_sff, self)._test_clear()

    def test_copy(self):
        super(TestNotes_modify_sff, self)._test_copy()


class TestNotes_modify_hff(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_hff, self).setUp()
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.hff')
        self.other = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'other_emd_1014.hff')
        self.output = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'output_emd_1014.hff')
        self.annotated_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'annotated_emd_1014.hff')

    def tearDown(self):
        super(TestNotes_modify_hff, self).tearDown()
        seg = schema.SFFSegmentation.from_file(self.sff_file)
        # remove all annotations
        for segment in seg.segments:
            segment.biological_annotation = schema.SFFBiologicalAnnotation()
        seg.export(self.sff_file)

    def test_add_global(self):
        super(TestNotes_modify_hff, self)._test_add_global()

    def test_add(self):
        super(TestNotes_modify_hff, self)._test_add()

    def test_edit_global(self):
        super(TestNotes_modify_hff, self)._test_edit_global()

    def test_edit(self):
        super(TestNotes_modify_hff, self)._test_edit()

    def _test_del_global(self):
        super(TestNotes_modify_hff, self)._test_del_global()

    def test_del(self):
        super(TestNotes_modify_hff, self)._test_del()

    def test_clear(self):
        super(TestNotes_modify_hff, self)._test_clear()

    def test_copy(self):
        super(TestNotes_modify_hff, self)._test_copy()


class TestNotes_modify_json(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_json, self).setUp()
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.json')
        self.other = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'other_emd_1014.json')
        self.output = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'output_emd_1181.json')
        self.annotated_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'annotated_emd_1014.json')

    def tearDown(self):
        super(TestNotes_modify_json, self).tearDown()
        seg = schema.SFFSegmentation.from_file(self.sff_file)
        # remove all annotations
        for segment in seg.segments:
            segment.biological_annotation = schema.SFFBiologicalAnnotation()
        seg.export(self.sff_file)

    def test_add_global(self):
        super(TestNotes_modify_json, self)._test_add_global()

    def test_add(self):
        super(TestNotes_modify_json, self)._test_add()

    def test_edit_global(self):
        super(TestNotes_modify_json, self)._test_edit_global()

    def test_edit(self):
        super(TestNotes_modify_json, self)._test_edit()

    def test_del_global(self):
        super(TestNotes_modify_json, self)._test_del_global()

    def test_del(self):
        super(TestNotes_modify_json, self)._test_del()

    def test_merge(self):
        super(TestNotes_modify_json, self)._test_merge()

    def test_clear(self):
        super(TestNotes_modify_json, self)._test_clear()

    def test_copy(self):
        super(TestNotes_modify_json, self)._test_copy()


class TestNotesClasses(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestNotesClasses, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_SimpleNote(self):
        """Test SimpleNote class"""
        name = li.get_sentence()
        description = li.get_sentences(5)
        num = _random_integer(1)
        num_ext_refs = _random_integer(2)
        ext_refs = [rw.random_words(count=3) for _ in _xrange(3)]
        sn = modify.SimpleNote(
            name=name,
            description=description,
            number_of_instances=num,
            external_reference_id=num_ext_refs,
            external_references=ext_refs,
        )
        self.assertEqual(sn.name, name)
        self.assertEqual(sn.description, description)
        self.assertEqual(sn.number_of_instances, num)
        for idx, ext_ref in enumerate(sn.external_references):
            self.assertCountEqual(
                [ext_ref.resource, ext_ref.url, ext_ref.accession],
                ext_refs[idx],
            )
            self.assertIsInstance(ext_ref, modify.ExternalReference)
        # direct assigment of external references
        eRefs = [rw.random_words(count=3) for _ in _xrange(3)]
        sn.external_references = eRefs
        for idx, ext_ref in enumerate(sn.external_references):
            self.assertCountEqual(
                [ext_ref.resource, ext_ref.url, ext_ref.accession],
                eRefs[idx],
            )
            self.assertIsInstance(ext_ref, modify.ExternalReference)

    def test_GlobalArgsNote(self):
        """Test GlobalArgsNote (construct global notes from command-line arguments)"""
        name = li.get_sentence()
        details = li.get_sentences(sentences=10)
        sw_name = rw.random_word()
        sw_version = rw.random_word()
        sw_proc = li.get_sentences(sentences=5)
        ext_refs = [rw.random_words(count=3) for _ in _xrange(3)]
        cmd = "notes add -N '{name}' -D '{details}' -S '{sw_name}' -T '{sw_version}' -P '{sw_proc}' file.sff " \
              "--config-path {config}".format(
            name=name,
            details=details,
            sw_name=sw_name,
            sw_version=sw_version,
            sw_proc=sw_proc,
            config=self.config_fn,
        )
        for e in ext_refs:
            cmd += ' -E {} '.format(' '.join(e))
        args, configs = parse_args(cmd, use_shlex=True)
        gan = modify.GlobalArgsNote(args, configs)
        self.assertEqual(gan.name, name)
        self.assertEqual(gan.details, details)
        self.assertEqual(gan.software_name, sw_name)
        self.assertEqual(gan.software_version, sw_version)
        self.assertEqual(gan.software_processing_details, sw_proc)
        for idx, ext_ref in enumerate(gan.external_references):
            self.assertCountEqual(
                [ext_ref.resource, ext_ref.url, ext_ref.accession],
                ext_refs[idx],
            )
            self.assertIsInstance(ext_ref, modify.ExternalReference)
        # add to segmentation
        seg_in = schema.SFFSegmentation()
        seg_out = gan.add_to_segmentation(seg_in)
        self.assertEqual(seg_out.name, name)
        self.assertEqual(seg_out.details, details)
        for idx, ext_ref in enumerate(seg_out.global_external_references):
            self.assertCountEqual(
                [ext_ref.resource, ext_ref.url, ext_ref.accession],
                ext_refs[idx]
            )
            self.assertIsInstance(ext_ref, schema.SFFExternalReference)
        software = seg_out.software_list[0]
        self.assertEqual(software.name, sw_name)
        self.assertEqual(software.version, sw_version)
        self.assertEqual(software.processing_details, sw_proc)
        self.assertEqual(seg_out.details, details)
        # edit in segmentation
        name = li.get_sentence()
        sw_name = rw.random_word()
        sw_version = rw.random_word()
        sw_proc = li.get_sentences(sentences=5)
        details = li.get_sentences(sentences=10)
        ext_refs = rw.random_words(count=3)
        ext_refs1 = rw.random_words(count=3)
        ext_refs2 = rw.random_words(count=3)
        cmd_edit = "notes edit -N '{name}' -s 0 -S '{sw_name}' -T '{sw_version}' -P '{sw_proc}' -D '{details}' -e 2 " \
                   "-E {extRefs} -E {extRefs1} -E {extRefs2} file.sff --config-path {config}".format(
            name=name,
            sw_name=sw_name,
            sw_version=sw_version,
            sw_proc=sw_proc,
            details=details,
            extRefs=' '.join(ext_refs),
            extRefs1=' '.join(ext_refs1),
            extRefs2=' '.join(ext_refs2),
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_edit, use_shlex=True)
        gan_edit = modify.GlobalArgsNote(args, configs)
        seg_out_edit = gan_edit.edit_in_segmentation(seg_out)
        # we have edited the last extref
        self.assertEqual(seg_out_edit.name, name)
        software = seg_out_edit.software_list[0]
        self.assertEqual(software.name, sw_name)
        self.assertEqual(software.version, sw_version)
        self.assertEqual(software.processing_details, sw_proc)
        self.assertEqual(seg_out_edit.details, details)
        self.assertEqual(
            [
                seg_out_edit.global_external_references[2].resource,
                seg_out_edit.global_external_references[2].url,
                seg_out_edit.global_external_references[2].accession
            ],
            ext_refs,
        )
        self.assertEqual(
            [
                seg_out_edit.global_external_references[3].resource,
                seg_out_edit.global_external_references[3].url,
                seg_out_edit.global_external_references[3].accession
            ],
            ext_refs1
        )
        self.assertEqual(
            [
                seg_out_edit.global_external_references[4].resource,
                seg_out_edit.global_external_references[4].url,
                seg_out_edit.global_external_references[4].accession
            ],
            ext_refs2
        )
        # delete from segmentation
        cmd_del = "notes del -s 0 -D -e 0,1,2,3,4,5 file.sff --config-path {config}".format(
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_del, use_shlex=True)
        gan_del = modify.GlobalArgsNote(args, configs)
        seg_out_del = gan_del.del_from_segmentation(seg_out_edit)
        self.assertEqual(len(seg_out_del.software_list), 0)
        self.assertIsNone(seg_out_del.details)
        self.assertEqual(len(seg_out_del.global_external_references), 0)

    def test_ArgsNote(self):
        """Test ArgsNote (construct local notes from command-line arguments)"""
        segment_id = _random_integers(count=1, start=1)
        name = li.get_sentence()
        description = li.get_sentences(sentences=4)
        num = _random_integer(start=1)
        ext_refs = [rw.random_words(count=3) for _ in _xrange(3)]
        cmd_add = "notes add -i {segment_id} -n '{name}' -d '{description}' -I {num} file.sff " \
                  "--config-path {config}".format(
            segment_id=','.join(map(_str, segment_id)),
            name=name,
            description=description,
            num=num,
            config=self.config_fn,
        )
        for e in ext_refs:
            cmd_add += ' -E {} '.format(' '.join(e))
        args, configs = parse_args(cmd_add, use_shlex=True)
        # add notes
        an_add = modify.ArgsNote(args, configs)
        segment = schema.SFFSegment()
        segment_add = an_add.add_to_segment(segment)
        self.assertEqual(segment_add.biological_annotation.name, name)
        self.assertEqual(segment_add.biological_annotation.description, description)
        self.assertEqual(segment_add.biological_annotation.number_of_instances, num)
        for idx, ext_ref in enumerate(an_add.external_references):
            self.assertCountEqual(
                [ext_ref.resource, ext_ref.url, ext_ref.accession],
                ext_refs[idx],
            )
            self.assertIsInstance(ext_ref, modify.ExternalReference)
        # edit notes
        name = li.get_sentence()
        desc = li.get_sentences(sentences=10)
        num = _random_integer(start=1)
        ext_refs = rw.random_words(count=3)
        extRefs1 = rw.random_words(count=3)
        extRefs2 = rw.random_words(count=3)
        cmd_edit = "notes edit -i {segment_id} -n '{name}' -d '{desc}' -I {num} " \
                   "-e 4 -E {extRefs} -E {extRefs1} -E {extRefs2} " \
                   "file.sff --config-path {config}".format(
            segment_id=','.join(map(_str, segment_id)),
            name=name,
            desc=desc,
            num=num,
            extRefs=' '.join(ext_refs),
            extRefs1=' '.join(extRefs1),
            extRefs2=' '.join(extRefs2),
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_edit, use_shlex=True)
        an_edit = modify.ArgsNote(args, configs)
        segment_edit = an_edit.edit_in_segment(segment_add)
        self.assertEqual(segment_edit.biological_annotation.name, name)
        self.assertEqual(segment_edit.biological_annotation.description, desc)
        self.assertEqual(segment_edit.biological_annotation.number_of_instances, num)
        self.assertEqual(
            [
                segment_edit.biological_annotation.external_references[-3].resource,
                segment_edit.biological_annotation.external_references[-3].url,
                segment_edit.biological_annotation.external_references[-3].accession
            ],
            ext_refs
        )
        self.assertEqual(
            [
                segment_edit.biological_annotation.external_references[-2].resource,
                segment_edit.biological_annotation.external_references[-2].url,
                segment_edit.biological_annotation.external_references[-2].accession
            ],
            extRefs1
        )
        self.assertEqual(
            [
                segment_edit.biological_annotation.external_references[-1].resource,
                segment_edit.biological_annotation.external_references[-1].url,
                segment_edit.biological_annotation.external_references[-1].accession
            ],
            extRefs2
        )
        # del notes
        cmd_del = "notes del -i {segment_id} -n -d -I -e 0,1,2,3,4,5 " \
                  "file.sff --config-path {config}".format(
            segment_id=','.join(map(_str, segment_id)),
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_del, use_shlex=True)
        an_del = modify.ArgsNote(args, configs)
        segment_del = an_del.del_from_segment(segment_edit)
        self.assertIsNone(segment_del.biological_annotation.name)
        self.assertIsNone(segment_del.biological_annotation.description)
        self.assertEqual(segment_del.biological_annotation.number_of_instances, 1)
        self.assertEqual(len(segment_del.biological_annotation.external_references), 0)


class TestNotes_find(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestNotes_find, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_search_default(self):
        """Test default search parameters"""
        args, configs = parse_args("notes search 'mitochondria' --config-path {}".format(self.config_fn),
                                   use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        if results is not None:
            self.assertGreater(len(results), 0)
        else:
            self.stderr(
                u"Warning: unable to run test on response due to API issue to {url}".format(url=resource.get_url()))

    def test_search_no_results(self):
        """Test search that returns no results"""
        # I'm not sure when some biological entity with such a name will be discovered!
        args, configs = parse_args(
            "notes search 'nothing' --exact --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        if results is not None:
            self.assertEqual(len(results), 0)
        else:
            self.stderr(
                u"Warning: unable to run test on response due to API issue to {url}".format(url=resource.get_url()))

    def test_search_exact_result(self):
        """Test that we get an exact result

        NOTE: this test is likely to break as the ontologies get updated
        """
        # this usually returns a single result
        args, configs = parse_args(
            "notes search 'DNA replication licensing factor MCM6' --exact --config-path {}".format(self.config_fn),
            use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        self.assertTrue(len(results) >= 2)  # funny!

    def test_search_ontology(self):
        """Test that we can search an ontology"""
        #  this search should bring at least one result
        args, configs = parse_args(
            "notes search 'mitochondria' --exact -O omit --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        if results is not None:
            self.assertGreaterEqual(len(results), 1)
        else:
            self.stderr(
                u"Warning: unable to run test on response due to API issue to {url}".format(url=resource.get_url()))

    def test_search_from_start(self):
        """Test that we can search from the starting index"""
        # this search usually has close to 1000 results
        random_start = _random_integer(1, 970)
        args, configs = parse_args("notes search 'mitochondria' --start {} --config-path {}".format(
            random_start,
            self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        if results is not None:
            self.assertGreaterEqual(results.structured_response['response']['start'], random_start - 1)
        else:
            self.stderr(
                u"Warning: unable to run test on response due to API issue to {url}".format(url=resource.get_url()))

    def test_search_result_rows(self):
        """Test that we get as many result rows as specified"""
        # this search usually has close to 1000 results; 100 is a reasonable start
        random_rows = _random_integer(10, 100)
        args, configs = parse_args("notes search 'mitochondria' --rows {} --config-path {}".format(
            random_rows,
            self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        if results is not None:
            self.assertGreaterEqual(len(results), random_rows)
        else:
            self.stderr(
                u"Warning: unable to run test on response due to API issue to {url}".format(url=resource.get_url()))


if __name__ == "__main__":
    unittest.main()
