from Products.Five.browser import BrowserView

def scaleBoth(c0, c1, max_width, max_height):
    scaling = c0.restrictedTraverse('@@images')
    i0 = scaling.scale(fieldname='image', width=max_width, height=max_height) 
    scaling = c1.restrictedTraverse('@@images')
    i1 = scaling.scale(fieldname='image', width=max_width, height=i0.height) 
    return [{'img': i0, 'obj': c0}, {'img': i1, 'obj': c1}]


def getScaledCorrespondenceImages(refs, max_dim):
    # we have 2 * max_dim width and max_dim height available;
    # make images as large as possible while being same height.

    c0 = refs[0].to_object
    s0 = c0.image.getImageSize()
    c1 = refs[1].to_object
    s1 = c1.image.getImageSize()

    both_width = s0[0] + s1[0]
    if both_width > max_dim * 2:
        factor = max_dim * 2.0 / both_width
    else:
        factor = 1.0

    if s0[0] >= s1[0]:
        return scaleBoth(c0, c1, int(factor * s0[0]), max_dim)
    else:
        rez = scaleBoth(c1, c0, int(factor * s1[0]), max_dim)
        return [rez[1], rez[0]]


class CorrespondenceView(BrowserView):
    """ main view of a correspondence """

    def getSet(self, max_dim=400):
        if max_dim == 400:
            import pdb; pdb.set_trace()

        refs = self.context.correspondence
        if len(refs) != 2:
            return []

        return getScaledCorrespondenceImages(refs, max_dim)

