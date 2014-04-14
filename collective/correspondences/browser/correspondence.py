from Products.Five.browser import BrowserView

def scaleBoth(c0, c1, max_width, max_height):
    scaling = c0.restrictedTraverse('@@images')
    i0 = scaling.scale(fieldname='image', width=max_width, height=max_height)
    scaling = c1.restrictedTraverse('@@images')
    i1 = scaling.scale(fieldname='image', width=max_width, height=i0.height)
    return [{'img': i0, 'obj': c0}, {'img': i1, 'obj': c1}]


def getScaledCorrespondenceImages(refs, max_height, max_wide=0):
    # make images as large as possible while being same height.

    if len(refs) != 2:
        return []

    if max_wide == 0:
        max_wide = 2 * max_height

    c0 = refs[0].to_object
    s0 = c0.image.getImageSize()
    c1 = refs[1].to_object
    s1 = c1.image.getImageSize()

    # we will never enlarge images to meet max_height
    max_height = min(max_height, min(s0[1], s1[1]))

    # compute dimensions of target images

    # normalize to same max_height
    t0 = [(float(max_height) / float(s0[1])) * s0[0], float(max_height)]
    t1 = [(float(max_height) / float(s1[1])) * s1[0], float(max_height)]

    # make sure not too wide
    factor = (t0[0] + t1[0]) / float(max_wide)
    if factor > 1.0:
        t0[0] = int(t0[0] / factor)
        t0[1] = int(t0[1] / factor)
        t1[0] = int(t1[0] / factor)
        t1[1] = int(t1[1] / factor)

    # and create the images
    scaling = c0.restrictedTraverse('@@images')
    i0 = scaling.scale(fieldname='image', width=t0[0], height=t0[1])
    scaling = c1.restrictedTraverse('@@images')
    i1 = scaling.scale(fieldname='image', width=t1[0], height=t1[1])

    if i0 and i1:
        return [{'img': i0, 'obj': c0}, {'img': i1, 'obj': c1}]
    else:
        return []


class CorrespondenceView(BrowserView):
    """ main view of a correspondence """

    def getSet(self, max_high=400, max_wide=0):
        refs = self.context.correspondence
        if len(refs) != 2:
            return []

        return getScaledCorrespondenceImages(refs, max_high, max_wide)

