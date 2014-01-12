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
                # if item.portal_type == 'gallery':
                if item.portal_type in ('gallery', 'subject_folder'):
                    galleries += 1
                    clist, ccount, scount, sgalleries = getChildren(cnode)
                    # if ccount and scount:
                    #     import pdb; pdb.set_trace()
                    sub_correspondences += ccount + scount
                    if ccount:
                        rez.append((item.Title, cnode['depth'], ccount, item.getURL(), scount, sgalleries))
                    elif scount:
                        rez.append((item.Title, cnode['depth'], scount, None, scount, sgalleries))
                    rez += clist
                elif item.portal_type == 'correspondence':
                    my_correspondences += 1
            return rez, my_correspondences, sub_correspondences, galleries

        context = aq_inner(self.context)

        # queryBuilder = SitemapQueryBuilder(context)
        # query = queryBuilder()

        query = {
            'sort_on': 'getObjPositionInParent',
            'path': {'query': '/colonialart/archive', 'depth': 50},
            'sort_order': 'asc',
            'portal_type': ['subject_folder', 'gallery', 'correspondence']}

        # strategy = getMultiAdapter((context, self), INavtreeStrategy)

        rez = buildFolderTree(context, obj=context,
                              query=query)

        galleries, total, s1, s2 = getChildren(rez)

        return galleries, total
