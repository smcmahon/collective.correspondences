from Acquisition import aq_inner
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implements


class ArchiveView(BrowserView):
    implements(ISiteMap)

    def siteMap(self):

        def getChildren(node):
            rez = []
            sub_correspondences = 0
            my_correspondences = 0
            galleries = 0
            for cnode in node['children']:
                item = cnode['item']
                if item.portal_type == 'gallery':
                    galleries += 1
                    clist, ccount, scount, sgalleries = getChildren(cnode)
                    sub_correspondences += ccount
                    if sgalleries and ccount:
                        # we're a gallery of galleries and have our own
                        # correspondences.
                        rez.append((item.Title, cnode['depth'], ccount + scount, None, scount, sgalleries))
                        rez.append((item.Title + ': General', cnode['depth'] + 1, ccount, item.getURL(), scount, sgalleries))
                    elif ccount:
                        rez.append((item.Title, cnode['depth'], ccount, item.getURL(), scount, sgalleries))
                    elif scount:
                        rez.append((item.Title, cnode['depth'], scount, None, scount, sgalleries))
                    rez += clist
                elif item.portal_type == 'correspondence':
                    my_correspondences += 1
            return rez, my_correspondences, sub_correspondences + my_correspondences, galleries

        context = aq_inner(self.context)

        # queryBuilder = SitemapQueryBuilder(context)
        # query = queryBuilder()

        query = {
            'sort_on': 'getObjPositionInParent',
            'path': {'query': '/colonialart/archive', 'depth': 50},
            'sort_order': 'asc',
            'portal_type': ['gallery', 'correspondence']}

        # strategy = getMultiAdapter((context, self), INavtreeStrategy)

        rez = buildFolderTree(context, obj=context,
                              query=query)

        galleries, total, s1, s2 = getChildren(rez)

        return galleries, total
