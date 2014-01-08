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
            i0, i1 = getScaledCorrespondenceImages(obj.correspondence,
                                                   max_dim=128)
#            ctags = []
#            for artwork_ref in obj.correspondence:
#                aobj = artwork_ref.to_object
#                scales = getMultiAdapter(
#                    (aobj, self.request),
#                    name=u'images'
#                )
#                ctags.append(scales.tag('image', scale='thumb'))
#            item['image_tags'] = ctags
            item['image_tags'] = [i0['img'].tag(), i1['img'].tag()]
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

