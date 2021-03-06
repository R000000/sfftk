#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
``sfftk.notes.find``
=======================

Search for terms and display ontologies
"""
from __future__ import division, print_function

import math
import numbers
import random
import sys
import textwrap

import requests
from sfftkrw.core import utils, _str, _xrange
from sfftkrw.core.print_tools import print_date

if sys.version_info[0] > 2:
    from shutil import get_terminal_size

    _get_terminal_size = get_terminal_size
else:
    from backports.shutil_get_terminal_size import get_terminal_size

    _get_terminal_size = get_terminal_size

from styled import Styled

from . import RESOURCE_LIST

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"
__updated__ = '2018-02-14'

# todo: expand OLS options to below

# type
# Restrict a search to an entity type, one of {class,property,individual,ontology}
#
# slim
# Restrict a search to an particular set of slims by name
#
# fieldList
# Specifcy the fields to return, the defaults are {iri,label,short_form,short_form,ontology_name,ontology_prefix,description,type}
#
# queryFields
# Specifcy the fields to query, the defaults are {label, synonym, description, short_form, short_form, annotations, logical_description, iri}
#
# groupField
# Set to true to group results by unique id (IRI)
#
# local
# Set to true to only return terms that are in a defining ontology e.g. Only return matches to gene ontology terms in the gene ontology, and exclude ontologies where those terms are also referenced
#
# childrenOf
# You can restrict a search to children of a given term. Supply a list of IRI for the terms that you want to search under
#
# allChildrenOf
# You can restrict a search to all children of a given term. Supply a list of IRI for the terms that you want to search under (subclassOf/is-a plus any hierarchical/transitive properties like 'part of' or 'develops from')


# todo: Retrieve an ontology GET /api/ontologies/{ontology_id}


JUSTIFY = [u'left', u'right', u'center']


class SearchResource(object):
    """A resource against which to look for accessions or terms"""

    def __init__(self, args, configs):
        self._args = args
        self._configs = configs
        self._response = None
        self._resource = RESOURCE_LIST[args.resource]

    @property
    def search_args(self):
        return self._args

    @property
    def configs(self):
        return self._configs

    @property
    def name(self):
        return self._resource[u'name']

    @property
    def root_url(self):
        return self._resource[u'root_url']

    @property
    def format(self):
        return self._resource[u'format']

    @property
    def result_path(self):
        return self._resource[u'result_path']

    @property
    def result_count(self):
        return self._resource[u'result_count']

    @property
    def response(self):
        return self._response

    def get_url(self):
        """Determine the url to search against"""
        url = None
        # ols
        if self.name == u'OLS':
            if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
                url = self.root_url + u"ontologies?size=1000"
            else:
                url = self.root_url + u"search?q={}&start={}&rows={}&local=true".format(
                    self.search_args.search_term,
                    self.search_args.start - 1,
                    self.search_args.rows,
                )
                if self.search_args.ontology:
                    url += u"&ontology={}".format(self.search_args.ontology)
                if self.search_args.exact:
                    url += u"&exact=on"
                if self.search_args.obsoletes:
                    url += u"&obsoletes=on"
        # go
        elif self.name == u'GO':
            url = self.root_url + u"search?q={}&start={}&rows={}&ontology=go".format(
                self.search_args.search_term,
                self.search_args.start - 1,
                self.search_args.rows,
            )
            if self.search_args.exact:
                url += u"&exact=on"
            if self.search_args.obsoletes:
                url += u"&obsoletes=on"
        # emdb
        elif self.name == u'EMDB':
            url = self.root_url + u"?q={}&start={}&rows={}".format(
                self.search_args.search_term,
                self.search_args.start,
                self.search_args.rows,
            )
        # uniprot
        elif self.name == u"UniProt":
            url = self.root_url + u"?query={search_term}&format=tab&offset={start}&limit={rows}&columns=id,entry_name," \
                                  u"protein_names,organism".format(
                search_term=self.search_args.search_term,
                # search_term2=self.search_args.search_term,
                start=self.search_args.start,
                rows=self.search_args.rows,
            )
        # pdb
        elif self.name == u"PDB":
            url = self.root_url + u"?q={search_term}&wt=json&fl=pdb_id,title,organism_scientific_name&start={start}&" \
                                  u"rows={rows}".format(
                search_term=self.search_args.search_term,
                start=self.search_args.start,
                rows=self.search_args.rows,
            )
        # europepmc
        elif self.name == u"Europe PMC":
            url = self.root_url + u"search?query={search_term}&resultType=lite&cursorMark=*&pageSize={rows}&format=json".format(
                search_term=self.search_args.search_term,
                rows=self.search_args.rows,
            )
        # EMPIAR
        elif self.name == u"EMPIAR":
            url = self.root_url + u"?q={search_term}&wt=json&start={start}&rows={rows}&random={rvalue}".format(
                search_term=self.search_args.search_term,
                start=self.search_args.start,
                rows=self.search_args.rows,
                rvalue=int(random.random() * 100000),
            )
        return url

    def search(self, *args, **kwargs):
        """Perform a search against this resource"""
        url = self.get_url()
        if url is not None:
            # make the search
            R = requests.get(url)
            if R.status_code == 200:
                self._response = R.text
                return SearchResults(self)
            else:
                print_date(u"Error: server responded with {}".format(R.text))
                return None
        else:
            print_date(u'Error: url is None')
            return None

    def _unicode(self):
        return Styled(u"""Search Resource:
                    \rname:\t\t[[ '{name}'|fg-yellow:bold ]]
                    \rroot_url:\t[[ '{root_url}'|fg-yellow:bold ]]
                    \rsearch_url:\t[[ '{search_url}'|fg-yellow:bold ]]
                    \rformat:\t\t[[ '{format}'|fg-yellow:bold ]]
                    \rresult_path:\t[[ '{result_path}'|fg-yellow:bold ]]
                    \rresult_count:\t[[ '{result_count}'|fg-yellow:bold ]]""", search_url=self.get_url(),
                      **self._resource)

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            string = self._unicode()
            return str(string)
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            string = self._unicode()
            return _str(string)


class TableField(object):
    """Class definition for a TableField - single column in a table"""

    def __init__(self, name, key=None, text=None, width=20, pc=None, justify=u'left', _format=None, is_index=False,
                 is_iterable=False, position_in_iterable=0):
        """A single field (column) in a table

        :param str name: the name of the field that will appear in header; can be any object that implements __str__
        :param str key: the key to use to extract the value for the field; if this is not defined then the value of
        name is used instead
        :param str text: a substitute for key; fixed text to appear in this field for all rows
        :param int width: a positive integer for the width of this field
        :param float pc: percentage width of the terminal occupied by this field
        :param str justify: 'left' (default), 'right' or 'center'; how to align text in the field
        :param str _format: a format string with one pair of empty braces to construct a string for each row
        :param bool is_index: if true then this field will be an index (numeric value) for the row
        :param bool is_iterable: if true then the value obtained using key will be from a list and position_in_iterable
        index will be retrieved from the iterable
        :param int position_in_iterable: if is_iterable is true then the value for this field will be retrieved from the
         specified index in the iterable value
        """
        # check mutex nature of key and text
        try:
            assert key is None or text is None
        except AssertionError:
            raise ValueError('key and text are mutually exclusive; only define one or none of them')
        # check valid type for width
        try:
            assert isinstance(width, numbers.Integral)
        except AssertionError:
            raise ValueError('field width must be int or long')
        # check valid value for width
        try:
            assert width > 0
        except AssertionError:
            raise ValueError('field width must be greater than 0')
        # ensure pc is valid type
        try:
            assert isinstance(pc, numbers.Integral) or isinstance(pc, float) or pc is None
        except AssertionError:
            raise ValueError('invalid type for pc (percentage): {}'.format(type(pc)))
        # ensure pc is a valid value
        try:
            if pc is not None:
                assert 0 < pc < 100
            else:
                assert True
        except AssertionError:
            raise ValueError(u'invalid value for pc (percentage): {}'.format(pc))

        # check valid values for justify
        try:
            assert justify in JUSTIFY
        except AssertionError:
            raise ValueError(u"invalid value for kwarg justify: {}; should be {}".format(
                justify,
                ', '.join(JUSTIFY),
            ))
        # check valid value for _format
        try:
            assert _format is None or _format.find("{}") >= 0
        except AssertionError:
            raise ValueError(
                u"invalid value for _format: {}; it should be either None or have one and only one pair of braces".format(
                    _format,
                ))
        # check valid type for position_in_iterable
        try:
            assert isinstance(position_in_iterable, int) or isinstance(position_in_iterable, long)
        except AssertionError:
            raise ValueError(u'field position_in_iterable must be int or long')
        # check valid value for position_in_iterable
        try:
            assert position_in_iterable >= 0
        except AssertionError:
            raise ValueError(u'field position_in_iterable must be greater or equal than 0')
        self._name = str(name)
        if key is None and text is None:
            self._key = name
        else:
            self._key = key
        self._text = text
        self._width = width
        self._pc = pc
        self._format = _format
        self._justify = justify
        self._is_index = is_index
        self._is_iterable = is_iterable
        self._position_in_iterable = position_in_iterable

    def justify(self, text):
        """Justify the given text

        :param str text: the text to justify
        """
        if self._justify == u'left':
            return text.ljust(self._width)
        elif self._justify == u'right':
            return text.rjust(self._width)
        elif self._justify == u'center':
            return text.center(self._width)

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            return self.justify(self._name)
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            return self.justify(self._name)

    @property
    def is_index(self):
        """Is this field an index (numbered) field?"""
        return self._is_index

    @property
    def width(self):
        """The width of the field in characters"""
        return self._width

    @width.setter
    def width(self, width):
        try:
            assert isinstance(width, int) or isinstance(width, long)
        except AssertionError:
            raise ValueError(u'width must be an int or long')
        self._width = width

    @property
    def pc(self):
        """The width of the field in percent; resolves to a character width"""
        return self._pc

    def render(self, row_data, index):
        """Render this field"""
        if self.is_index:
            text = _str(index)
        elif self._key is not None:
            try:
                if self._is_iterable:
                    text = row_data[self._key][self._position_in_iterable]
                else:
                    text = row_data[self._key]
            except KeyError:
                text = u'-'
        elif self._text is not None:
            text = self._text
        # format
        if self._format is not None:
            wrapped_text = textwrap.wrap(self._format.format(text), self._width)
        else:
            wrapped_text = textwrap.wrap(text, self._width)
        if not wrapped_text:  # empty list for empty string
            return [self.justify(u'')]
        else:
            return list(map(self.justify, wrapped_text))


class Table(object):
    """Table superclass"""
    column_separator = u" | "
    row_separator = u"\n"


class TableRow(Table):
    """Class definition for a single row in the table

    Wrapping is automatically handled
    """

    def __init__(self, row_data, fields, index, *args, **kwargs):
        """Initialise a ``TableRow`` object

        :param row_data: the data for the different fields in the row
        :param fields: an iterable of :py:class:`TableField` objects
        :param index: the index for this row; externally resolved henced passed an an init var
        """
        super(TableRow, self).__init__(*args, **kwargs)
        self._row_data = row_data
        self._fields = fields
        self._index = index
        self._rendered = self._render()

    def _render(self):
        rendered = list()
        for field in self._fields:
            rendered.append(field.render(self._row_data, self._index))
        return rendered

    if sys.version_info[0]:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            string = u''
            # get the max number of lines in this row
            no_lines = 0
            for f in self._rendered:
                no_lines = max(len(list(f)), no_lines)
            # build the stack of lines for this row
            for i in _xrange(no_lines):
                row = list()
                for j, F in enumerate(self._fields):
                    try:
                        field = self._rendered[j][i]
                    except IndexError:
                        field = F.justify(u'')
                    row.append(field)
                # don't add an extra row separator to the last line
                if i == no_lines - 1:
                    string += self.column_separator.join(row)
                else:
                    string += self.column_separator.join(row) + self.row_separator
            return string
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            string = u''
            # get the max number of lines in this row
            no_lines = 0
            for f in self._rendered:
                no_lines = max(len(f), no_lines)
            # build the stack of lines for this row
            for i in _xrange(no_lines):
                row = list()
                for j, F in enumerate(self._fields):
                    try:
                        field = self._rendered[j][i]
                    except IndexError:
                        field = F.justify(u'')
                    row.append(field)
                # don't add an extra row separator to the last line
                if i == no_lines - 1:
                    string += self.column_separator.join(row)
                else:
                    string += self.column_separator.join(row) + self.row_separator
            return string


class ResultsTable(Table):
    """Class that formats search results as a table"""

    def __init__(self, search_results, fields, width=u'auto', *args, **kwargs):
        """Initialise a ResultsTable object by specifying results and fields

        :param search_results: a SearchResults object
        :type search_results: SearchResults
        :param list fields: a list of TableField objects
        :param int width: a non-negative integer
        """
        # check the type of search_results
        try:
            assert isinstance(search_results, SearchResults)
        except AssertionError:
            raise ValueError(u'search_results must be a SearchResults object')
        # ensure that we have at least one field
        try:
            assert fields  # nice! an empty list asserts to False
        except AssertionError:
            raise ValueError(u'fields kwarg should not be empty')
        # ensure that the fields kwarg is populated with TableField objects
        try:
            assert all(map(lambda f: isinstance(f, TableField), fields))
        except AssertionError:
            raise ValueError(u'non-TableField object in iterable fields')
        # check valid type for width
        try:
            assert isinstance(width, numbers.Integral) or width == u'auto'
            # assert isinstance(width, int) or isinstance(width, long) or width == 'auto'
        except AssertionError:
            raise ValueError(u"field width must be instance of int or long or the string 'auto'")
        # check valid value for width
        if isinstance(width, _str):
            try:
                assert width == u'auto'
            except AssertionError:
                raise ValueError(u"field width must be greater than 0 or the string 'auto'")
        elif isinstance(width, numbers.Integral):
            try:
                assert width > 0
            except AssertionError:
                raise ValueError(u"field width must be greater than 0 or the string 'auto'")
        # only one index field per table
        try:
            assert len(list(filter(lambda f: f.is_index, fields))) <= 1
        except AssertionError:
            raise ValueError(
                u'there is more than one field with is_index=True set; only one index field per table supported')
        super(ResultsTable, self).__init__(*args, **kwargs)
        self._search_results = search_results
        if width == u'auto':
            terminal_size = _get_terminal_size()  # fallback values
            if terminal_size.columns > 0:
                self._width = terminal_size.columns
            else:
                self._width = 80
        else:
            self._width = width
        self._fields = self._evaluate_widths(fields)
        # ensure width is less than the sum of fields
        total_width = sum([f.width for f in fields])
        try:
            assert total_width < self._width
        except AssertionError:
            print_date(
                u'total field widths greater than table width; '
                u'distortion will occur: table width={}; total field width={}'.format(
                    self._width,
                    total_width,
                ))

    def _evaluate_widths(self, fields):
        """Convert percentage widths into fixed widths

        :param list fields: list of TableField objects
        :return list _fields: list of TableField objects
        """
        _fields = list()
        # we calculate the field's width by taking into account the column separator
        inter_column_distance = len(fields) * len(self.column_separator)
        # subtract the inter-column distance from the screen width
        reduced_width = self._width - inter_column_distance
        for field in fields:
            if field.pc is not None:
                # the field's width is now...
                field.width = int(math.floor(reduced_width * field.pc / 100))
            _fields.append(field)
        return _fields

    @property
    def header(self):
        header = Styled(u"[[ ''|fg-yellow:no-end ]]")
        header += u"=" * self._width + self.row_separator
        header += u"Search term: [[ '{}'|fg-yellow:bold ]]{}{}".format(
            self._search_results.search_args.search_term,
            self.row_separator,
            self.row_separator,
        )
        header += Styled(u"[[ ''|fg-yellow:bold:no-end ]]")
        header += self.column_separator.join(list(map(lambda f: _str(f)[:f.width], self._fields))) + self.row_separator
        header += Styled(u"[[ ''|reset ]][[ ''|fg-yellow:no-end ]]")
        header += u"=" * self._width + self.row_separator
        header += Styled(u"[[ ''|reset ]]")
        return header

    @property
    def body(self):
        index = self._search_results.search_args.start  # index
        if self._search_results.results is not None:
            body = Styled(u"[[ ''|fg-yellow:no-end ]]")
            for row_data in self._search_results.results:
                body += _str(TableRow(row_data, self._fields, index)) + self.row_separator
                body += u"-" * self._width + self.row_separator
                index += 1  # increment index
            body += Styled(u"[[ ''|reset ]]")
        else:
            body = u'\nNo data found at this time. Please try again in a few minutes.'.center(
                self._width) + self.row_separator
            body += self.row_separator
            body += u"-" * self._width + self.row_separator
        return body

    @property
    def footer(self):
        if len(self._search_results):
            footer = u'Showing: {} to {} of {} results found'.format(
                self._search_results.search_args.start,
                min(len(self._search_results),
                    self._search_results.search_args.start + self._search_results.search_args.rows - 1),
                len(self._search_results),
            )
        else:
            footer = u"Showing {} results per page".format(
                self._search_results.search_args.rows,
            )
        return footer

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            string = u""
            string += self.header
            string += self.body
            string += self.footer
            return _str(string)
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            string = u""
            string += self.header
            string += self.body
            string += self.footer
            return _str(string)


class SearchResults(object):
    """SearchResults class"""
    _width = 180  # unreasonable default
    INDEX_WIDTH = 6
    LABEL_WIDTH = 20
    SHORT_FORM_WIDTH = 20
    ONTOLOGY_NAME_WIDTH = 15
    DESCRIPTION_WIDTH = 80
    TYPE_WIDTH = 18

    def __init__(self, resource):
        self._resource = resource  # the resource that was searched
        self._raw_response = resource.response
        self._structured_response = self._structure_response()
        terminal_size = _get_terminal_size()  # fallback values
        if terminal_size.columns > 0:
            self._width = terminal_size.columns
        else:
            self._width = self._width

    @property
    def structured_response(self):
        return self._structured_response

    def _structure_response(self):
        """Structure the raw result according to the format received"""
        if self._resource.format == u'json':
            import json
            try:
                structured_results = json.loads(self._raw_response)
            except ValueError:
                print_date(u"Unable to search at this time. Please try after a few minutes.")
                structured_results = None
            return structured_results
        elif self._resource.format == u'tab':
            try:
                # split rows; split columns; dump first and last rows
                _structured_results = list(map(lambda r: r.split('\t'), self._raw_response.split('\n')))[1:-1]
                # make a list of dicts with the given ids
                structured_results = list(map(lambda r: dict(zip([u'id', u'name', u'proteins', u'organism'], r)),
                                         _structured_results))
            except ValueError:
                structured_results = None
            return structured_results
        else:
            print_date(u"unsupported format: {}".format(self._resource.format))
            return None

    @property
    def search_args(self):
        return self._resource.search_args

    @property
    def results(self):
        if self.structured_response is not None:
            if self._resource.result_path is not None:
                return utils.get_path(self.structured_response, self._resource.result_path)
        return self.structured_response

    if sys.version_info[0]:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            return self.tabulate()
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            return self.tabulate()

    def tabulate(self):
        """Tabulate the search results"""
        table = Styled(u"[[ ''|fg-yellow:no-end ]]")  # u""
        if self._resource.name == u'OLS':
            # only list ontologies as short or long lists
            if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
                if self.search_args.list_ontologies:
                    table += u"\n" + "-" * self._width + u"\n"
                    for ontology in utils.get_path(self.structured_response, [u'_embedded', u'ontologies']):
                        c = ontology[u'config']
                        table += u"\n"
                        ont = [
                            u"Namespace: ".ljust(30) + u"[[ '{}'|bold ]][[ ''|fg-yellow:no-end ]]".format(
                                _str(c[u'namespace'])),
                            u"Pref. prefix: ".ljust(30) + _str(c[u'preferredPrefix']),
                            u"Title: ".ljust(30) + _str(c[u'title']),
                            u"Description: ".ljust(30) + _str(c[u'description']),
                            u"Homepage: ".ljust(30) + _str(c[u'homepage']),
                            u"ID: ".ljust(30) + _str(c[u'id']),
                            u"Version :".ljust(30) + _str(c[u'version']),
                        ]
                        table += u"\n".join(ont)
                        table += u"\n" + "-" * self._width
                elif self.search_args.short_list_ontologies:
                    table += u"List of ontologies\n"
                    table += u"\n" + "-" * self._width + u"\n"
                    for ontology in utils.get_path(self.structured_response, [u'_embedded', u'ontologies']):
                        c = ontology[u'config']
                        ont = [
                            u"[[ '{}'|fg-yellow:bold ]][[ ''|fg-yellow:no-end ]]".format(
                                _str(c[u'namespace']).ljust(10)),
                            u"-",
                            _str(c[u'description'][:200]) if c[u'description'] else u'' + u"...",
                        ]
                        table += u"\t".join(ont) + u"\n"
            # list search results
            else:
                fields = [
                    TableField(u'index', key=u'index', pc=5, is_index=True, justify=u'right'),
                    TableField(u'label', key=u'label', pc=10),
                    TableField(u'resource', key=u'ontology_name', pc=5, justify=u'center'),
                    TableField(u'url', key=u'iri', pc=30),
                    TableField(u'accession', key=u'short_form', pc=10, justify=u'center'),
                    TableField(u'description', key=u'description', pc=40, is_iterable=True),
                ]
                table += _str(ResultsTable(self, fields=fields))
        elif self._resource.name == u'GO':
            fields = [
                TableField(u'index', key=u'index', pc=5, is_index=True, justify=u'right'),
                TableField(u'label', key=u'label', pc=10),
                TableField(u'resource', key=u'ontology_name', pc=5, justify=u'center'),
                TableField(u'url', key=u'iri', pc=30),
                TableField(u'accession', key=u'short_form', pc=10, justify=u'center'),
                TableField(u'description', key=u'description', pc=40, is_iterable=True),
            ]
            table += _str(ResultsTable(self, fields=fields))
        elif self._resource.name == u'EMDB':
            fields = [
                TableField(u'index', key=u'index', pc=5, is_index=True, justify=u'right'),
                TableField(u'label', text=self._resource.search_args.search_term, pc=10, justify=u'center'),
                TableField(u'resource', text=u'EMDB', pc=5, justify=u'center'),
                TableField(u'url', key=u'EntryID', _format=u'https://www.ebi.ac.uk/pdbe/emdb/EMD-{}', pc=30),
                TableField(u'accession', key=u'EntryID', pc=10, _format=u'EMD-{}', justify=u'center'),
                TableField(u'description', key=u'Title', pc=40),
            ]
            table += _str(ResultsTable(self, fields=fields))
        elif self._resource.name == u"UniProt":
            fields = [
                TableField(u'index', pc=5, is_index=True, justify=u'right'),
                TableField(u'label', key=u'name', pc=10),
                TableField(u'resource', text=u'UniProt', pc=5, justify=u'center'),
                TableField(u'url', key=u'id', _format=u'https://www.uniprot.org/uniprot/{}', pc=30),
                TableField(u'accession', key=u'id', pc=10, justify=u'center'),
                TableField(u'description', key=u'proteins', pc=40),
                # TableField('organism', key='organism', width=40),
            ]
            table += _str(ResultsTable(self, fields=fields))
        elif self._resource.name == u"PDB":
            fields = [
                TableField(u'index', pc=5, is_index=True, justify=u'right'),
                TableField(u'label', text=self._resource.search_args.search_term, pc=10),
                TableField(u'resource', text=u'PDB', pc=5, justify=u'center'),
                TableField(u'url', key=u'pdb_id', _format=u'https://www.ebi.ac.uk/pdbe/entry/pdb/{}', pc=30),
                TableField(u'accession', key=u'pdb_id', pc=10, justify=u'center'),
                # TableField('title', key='organism_scientific_name', pc=20, is_iterable=True),
                TableField(u'description', key=u'title', pc=40),
            ]
            table += _str(ResultsTable(self, fields=fields))
        elif self._resource.name == u'Europe PMC':
            fields = [
                TableField(u'index', pc=5, is_index=True, justify=u'right'),
                TableField(u'label (authors)', key=u'authorString', pc=20),
                TableField(u'resource', text=u'Europe PMC', pc=10, justify=u'center'),
                TableField(u'url', key=u'id', _format=u'https://europepmc.org/abstract/MED/{}', pc=30),
                TableField(u'accession', key=u'id', pc=10, justify=u'center'),
                TableField(u'description (title)', key=u'title', pc=25),
                # TableField(u'iri (doi)', key=u'doi', _format=u'https://doi.org/{}', pc=30)
            ]
            table += _str(ResultsTable(self, fields=fields))
        elif self._resource.name == u'EMPIAR':
            fields = [
                TableField(u'index', pc=5, is_index=True, justify=u'right'),
                TableField(u'label', text=self._resource.search_args.search_term, pc=10),
                TableField(u'resource', text=u'EMPIAR', pc=8, justify=u'center'),
                TableField(u'url', key=u'empiarid_abr', _format=u'https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/{}',
                           pc=30),
                TableField(u'accession', key=u'empiarid', pc=10, justify=u'center'),
                TableField(u'description', key=u'title', pc=33),
            ]
            table += _str(ResultsTable(self, fields=fields))
        # close style
        table += Styled(u"[[ ''|reset ]]")
        return _str(table)

    def __len__(self):
        if self.structured_response is not None:
            if self._resource.result_count is not None:
                return utils.get_path(self._structured_response, self._resource.result_count)
        return 0
