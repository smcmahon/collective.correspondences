from bs4 import BeautifulSoup
from plone.app.textfield.value import RichTextValue
from plone.namedfile import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from transaction import commit
from zope.component import createObject
from zope.component.hooks import setSite

"""
artist  4584
correspondance credit   3
correspondence credit   1713
correspondence source   1
credit  1
date    4455
image   93
item    4454
literature  174
literture   1
location    2225
medium  4577
note    71
photo   1
photo credit    2
photo source    4539
photosource 1
title   4582
"""

app = app

ids = {
    'artist': 'artist',
    'date': 'date',
    'location': 'location',
    'medium': 'medium',
    'photo': ' photo_credit',
    'photo credit': 'photo_credit',
    'photo source': 'photo_credit',
    'photosource': 'photo_credit',
}

# if an image exceeds these dimensions, it will be checked
max_size = (768, 768)
# if we'd save this much, we'll rescale
margin = 50000


def scaleImage(imageField, imageItem):
    value = imageField.getRaw(imageItem)
    if value.width > max_size[0] or value.height > max_size[1]:
        factor = min(float(max_size[0]) / float(value.width),
                     float(max_size[1]) / float(value.height))
        w = int(factor * value.width)
        h = int(factor * value.height)
        fvalue, format = imageField.scale(value.data, w, h)
        return fvalue.read()
    else:
        return value.data


site = app.Main
pc = site.portal_catalog

target_site = app.colonialart
setSite(target_site)
target_folder = target_site.artworks

done = set()

artworks = pc(portal_type='Artwork')
for brain in artworks:
    aw = brain.getObject()
    awImageItem = aw.getImage()
    if not awImageItem:
        continue
    id = awImageItem.getId().split('.')[0]
    if id in done:
        continue
    done.add(id)
    newart = createObject('artwork')
    newart.title = id
    newart.description = safe_unicode(brain.Title)
    newart.id = id
    source = aw.getRawDescription()
    soup = BeautifulSoup(source)
    for row in soup.find_all('tr'):
        els = row.get_text().split('\n')
        els = [s.replace(u'\xa0', ' ').strip() for s in els]
        els = [s for s in els if s]
        if len(els) > 1:
            key = els[0].lower()
            value = safe_unicode(els[1])
            if key in ids:
                setattr(newart, ids[key], value)
            elif key == 'note' and value:
                newart.text = RichTextValue(value, 'text/html', 'text/html')
                print "Note",
    awImageField = awImageItem.Schema().get('image')
    image = NamedBlobImage()
    image.data = scaleImage(awImageField, awImageItem)
    image.contentType = awImageItem.content_type
    filename = awImageItem.getFilename()
    if filename:
        image.filename = filename.decode('ASCII')
    else:
        filename = id
    newart.image = image
    target_folder[id] = newart
    print id
commit()

