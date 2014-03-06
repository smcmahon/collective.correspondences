from Products.Five.browser import BrowserView
from zc.relation.interfaces import ICatalog
from zope import component
from zope.app.intid.interfaces import IIntIds


class ArtworkView(BrowserView):
    """ main artwork view """

    def getRelationsTo(self):
        catalog = component.getUtility(ICatalog)
        intids = component.getUtility(IIntIds)
        relations = sorted(catalog.findRelations({'to_id': intids.getId(self.context)}))
        rez = []
        for r in relations:
            obj = r.from_object
            title = obj.title
            url = obj.aq_parent.absolute_url()
            if 'archive' in url:
                title = 'Archive: %s' % title
            elif 'galleries' in url:
                title = 'Galleries: %s' % title
            rez.append({
                'title': title,
                'url': "%s#c%s" % (url, obj.id),
                })
        return rez
