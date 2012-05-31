# -*- coding: utf-8 -*-
import logging

from zope.interface import implements

try:
    from zope.schema.interfaces import IVocabularyFactory
except ImportError:
    from zope.app.schema.vocabulary import IVocabularyFactory

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces._content import IFolderish

from plone.app.vocabularies.catalog import SearchableTextSource
from plone.app.vocabularies.catalog import QuerySearchableTextSourceView

from plone.app.vocabularies.terms import BrowsableTerm

from sc.contentrules.groupbydate.config import RELPATHVOC, STRUCTURES

from sc.contentrules.groupbydate import MessageFactory as _

logger = logging.getLogger('sc.contentrules.groupbydate')


class HierarchiesVocabulary(object):
    """Vocabulary factory listing available hierarchies
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []

        for key, title  in STRUCTURES:
            terms.append(
                SimpleTerm(
                    key,
                    title=title)
                )

        return SimpleVocabulary(terms)

HierarchiesVocabularyFactory = HierarchiesVocabulary()


class RelPathSearchableTextSource(SearchableTextSource):
    """ A special case of a SearchableTextSource where we always support
        relative paths
    """
    def __contains__(self, value):
        """Return whether the value is available in this source
        """
        if not (value[0] == '.'):
            result = super(RelPathSearchableTextSource,
                           self).__contains__(value)
        else:
            result = True
        return result

    def search(self, query_string):
        """ Add relative paths to vocabulary
        """
        results = super(RelPathSearchableTextSource,
                        self).search(query_string)
        relPaths = RELPATHVOC.keys()
        results = relPaths + list(results)
        return (r for r in results)


class RelPathQSTSourceView(QuerySearchableTextSourceView):
    """ A special case of a QuerySearchableTextSourceView where we
        always support relative paths
    """
    def getTerm(self, value):
        if not (value[0] == '.'):
            return super(RelPathQSTSourceView, self).getTerm(value)
        terms = RELPATHVOC
        token = value
        title = terms.get(value, value)
        browse_token = parent_token = None
        return BrowsableTerm(value, token=token, title=title,
                             description=value,
                             browse_token=browse_token,
                             parent_token=parent_token)


class ContainerSearcher(object):
    """
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        portal_url = getToolByName(context, 'portal_url')
        site = portal_url.getPortalObject()
        new_list = []
        pt = getToolByName(site, 'portal_types')
        types = pt.listTypeInfo()
        for site_type in types:
            if 'item' in site.keys():
                del site['item']

            try:
                item = site_type._constructInstance(site, 'item')
            except (TypeError, ValueError):
                item = None
                logger.info('There is a problem to see if %s is Folderish' %
                            site_type)
                pass

            if item:
                if IFolderish.providedBy(item):
                    new_list.append(SimpleTerm(site_type.getId(),
                                    site_type.getId()))
                del site['item']
        return SimpleVocabulary(new_list)

ContainerSearcherFactory = ContainerSearcher()
