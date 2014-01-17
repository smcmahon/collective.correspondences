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
            rez.append({
                'title': obj.title,
                'url': "%s#c%s" % (obj.aq_parent.absolute_url(), obj.id),
                })
        return rez
