from Acquisition import aq_inner
from plone.app.layout.navigation.navtree import buildFolderTree
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.Five import BrowserView
from zope.interface import implements


class ArchiveView(BrowserView):
    implements(ISiteMap)

    def siteMap(self):

        context = aq_inner(self.context)

        query = {
            'sort_on': 'getObjPositionInParent',
            'path': {'query': '/'.join(context.getPhysicalPath()), 'depth': 50},
            'sort_order': 'asc',
            'portal_type': ['subject_folder', 'gallery', 'correspondence']}

        # The building of the tree is the hot spot of this routine.
        # Caching this might be a good optimization, but we'd be caching
        # all the subject folders as separate cache items.
        rez = buildFolderTree(context, obj=context, query=query)

        # This flattening is more simple expressed via recursion, but it's hard to avoid
        # memory leaks.

        # nstack is a stack of nodes; we add to the stack as we descend the tree.
        nstack = [{'parent': rez, 'sub_galleries': 0, 'sub_correspondences': 0, 'my_correspondences': 0}, ]
        # flat_rez is a list of our nodes, build as we flatten the tree
        flat_rez = []
        while nstack:
            stack_top = nstack[-1]
            children = stack_top['parent']['children']
            pushed = False
            while children:
                child = children.pop(0)
                item = child['item']
                if item.portal_type in ('gallery', 'subject_folder'):
                    # push it onto the stack
                    nstack.append({
                        'parent': child,
                        'sub_galleries': 0,
                        'sub_correspondences': 0,
                        'my_correspondences': 0
                    })
                    # and add it to the flattened list
                    flat_rez.append(nstack[-1])
                    pushed = True
                    # we will return to process the rest of the children
                    # when we pop the just-pushed node.
                    break
                elif item.portal_type == 'correspondence':
                    stack_top['my_correspondences'] += 1
            if pushed:
                continue
            # children of this node exhausted.
            # add last node's correspondence count sub correspondence
            # counts up the stack.
            my_correspondences = stack_top['my_correspondences']
            for item in nstack[:-1]:
                item['sub_correspondences'] += my_correspondences
            # pop the stack
            del nstack[-1]

        # galleries will be a simplified version of flat_rez,
        # meant to be used in the template.
        galleries = []
        for stack_item in flat_rez:
            my_correspondences = stack_item['my_correspondences']
            sub_correspondences = stack_item['sub_correspondences']
            node = stack_item['parent']
            item = node['item']
            if sub_correspondences:
                galleries.append((
                    item.Title,
                    node['depth'],
                    sub_correspondences,
                    None,
                ))
            else:
                galleries.append((
                    item.Title,
                    node['depth'],
                    my_correspondences,
                    item.getURL(),
                ))

        return galleries, 0
