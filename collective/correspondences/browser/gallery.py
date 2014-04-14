from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from correspondence import getScaledCorrespondenceImages


BLOCK_SIZE = 3


class GalleryView(BrowserView):
    """ main gallery view """

    def getCorrespondences(self):
        context = self.context
        pc = getToolByName(context, 'portal_catalog')
        cur_path = '/'.join(context.getPhysicalPath())
        path = {}
        contentFilter = {}
        contentFilter['sort_on'] = 'getObjPositionInParent'
        path['query'] = cur_path
        path['depth'] = 1
        contentFilter['path'] = path
        contentFilter['portal_type'] = 'correspondence'
        brains = pc.queryCatalog(contentFilter)
        rez = []
        for brain in brains:
            item = {}
            obj = brain.getObject()
            item['title'] = obj.title
            item['url'] = obj.absolute_url()
            item['description'] = obj.description
            item['id'] = obj.getId()
            items = getScaledCorrespondenceImages(obj.correspondence,
                                                  max_height=128)
            if len(items) == 2:
                item['image_tags'] = [items[0]['img'].tag(), items[1]['img'].tag()]
                rez.append(item)

        # Break into groups for scrollable
        grouped = []
        while rez:
            group = []
            for i in range(0, BLOCK_SIZE):
                if rez:
                    group.append(rez.pop(0))
            if group:
                grouped.append(group)        
        return grouped

