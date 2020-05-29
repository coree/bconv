"""
Format converters.
"""


__author__ = "Lenz Furrer"


import io

from . import txt
from . import tsv
from . import bioc
from . import brat
from . import conll
from . import pubmed
from . import pubanno
from . import pubtator
from . import europepmc
from ._load import wrap_in_collection


# Keep these mappings up to date.
LOADERS = {
    'txt': txt.TXTLoader,
    'txt_json': txt.TXTJSONLoader,
    'bioc_xml': bioc.BioCXMLLoader,
    'bioc_json': bioc.BioCJSONLoader,
    'conll': conll.CoNLLLoader,
    'pubtator': pubtator.PubTatorLoader,
    'pubtator_fbk': pubtator.PubTatorFBKLoader,
    'pxml': pubmed.PXMLLoader,
    'nxml': pubmed.PMCLoader,
}

FETCHERS = {
    'pubmed': pubmed.PXMLFetcher,
    'pmc': pubmed.PMCFetcher,
}

EXPORTERS = {
    'txt': txt.TXTFormatter,
    'tsv': tsv.TSVFormatter,
    'text_tsv': tsv.TextTSVFormatter,
    'bioc_xml': bioc.BioCXMLFormatter,
    'bioc_json': bioc.BioCJSONFormatter,
    'bionlp': brat.BioNLPFormatter,
    'brat': brat.BratFormatter,
    'conll': conll.CoNLLFormatter,
    'pubanno_json': pubanno.PubAnnoJSONFormatter,
    'pubtator': pubtator.PubTatorFormatter,
    'pubtator_fbk': pubtator.PubTatorFBKFormatter,
    'europepmc': europepmc.EuPMCFormatter,
    'europepmc.zip': europepmc.EuPMCZipFormatter,
}


def load(fmt, source, id_=None, mode='native', **options):
    """
    Load a document or collection from a file.

    The mode parameter determines the return type:
        - native: a Document or Collection object, depending
            on the format;
        - collection: a Collection object wrapping all content;
        - lazy: an iterator of Document objects, consumed
            lazily if possible.
    """
    loader = LOADERS[fmt](**options)
    return _load(loader, source, id_, mode)


def _load(loader, source, id_, mode):
    if mode == 'lazy' and hasattr(loader, 'iter_documents'):
        content = loader.iter_documents(source)
    else:
        content = loader.load_one(source, id_)

    if hasattr(loader, 'document'):
        if mode == 'lazy':
            content = iter([content])
        elif mode == 'collection':
            content = wrap_in_collection(content)

    return content


def loads(fmt, source, id_=None, mode='native', **options):
    """
    Load a document or collection from str or bytes.
    """
    wrap = io.StringIO if isinstance(source, str) else io.BytesIO
    return load(fmt, wrap(source), id_, mode, **options)


def fetch(fmt, query, id_=None, mode='native', **options):
    """
    Load a document or collection from a remote service.
    """
    fetcher = FETCHERS[fmt](**options)
    return _load(fetcher, query, id_, mode)


def dump(fmt, content, dest, **options):
    """
    Serialise a document or collection to a file.

    The destination can be a file open for writing or a
    path to a file or to an existing directory.
    """
    exporter = EXPORTERS[fmt](**options)
    if hasattr(dest, 'write'):
        exporter.write(content, dest)
    else:
        exporter.export(content, dest)


def dumps(fmt, content, **options):
    """
    Serialise a document or collection to str or bytes.
    """
    exporter = EXPORTERS[fmt](**options)
    return exporter.dumps(content)
