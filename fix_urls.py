from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID
from transaction import commit
from zope.component import getUtility
from zope.component.hooks import setSite

import re
import plone.app.uuid.utils as uuid_utils

app = app

site = app.Main
pc = site.portal_catalog
target_site = app.colonialart
tpc = target_site.portal_catalog

setSite(site)
redirector = getUtility(IRedirectionStorage)

dexterity_to_fix = (
    ('artwork', 'text'),
    ('gallery', 'body'),
    )
archetypes_to_fix = (
    ('Document', 'getRawText', 'setText'),
    )


def find_scaling(s):
    hpos = s.find('#')
    if hpos > 0:
        anchor = s[hpos:]
        s = s[:hpos]
    else:
        anchor = ''
    split = s.split('/')
    scale = split[-1]
    if 'image_' in scale:
        path = '/'.join(split[:-1])
        scale = '/@@images/image/%s' % scale.replace('image_', '')
    elif 'RSS' in scale:
        path = '/'.join(split[:-1])
        scale = '/RSS'
    else:
        scale = ''
        path = s
    return path, anchor, scale


def resolveUID(mo):
    path, anchor, scale = find_scaling(mo.group(1))
    setSite(site)
    orig_path = uuid_utils.uuidToPhysicalPath(path)
    if orig_path is None:
        # print "NOT resolved:", obj.absolute_url(), mo.group(1)
        return path + scale
    # see if it's there
    try:
        ref_obj = site.restrictedTraverse(str((orig_path)))
    except (AttributeError, KeyError):
        # try redirect
        ref_obj = ref_obj.restrictedTraverse(redirector.get(str(orig_path)))

    setSite(target_site)
    new_path = orig_path.replace('/Main', '/colonialart').replace('/images', '/artworks')
    try:
        new_obj = target_site.restrictedTraverse(str(new_path))
    except (AttributeError, KeyError):
        newer_path = new_path.replace('.jpg', '').replace('.jpeg', '')
        try:
            new_obj = target_site.restrictedTraverse(str(newer_path))
        except (AttributeError, KeyError):
            print "NOT resolved:", obj.absolute_url(), orig_path
            return new_path
    setSite(target_site)
    uid = IUUID(new_obj)
    return "resolveuid/%s%s%s" % (uid, anchor, scale)


def fixRelative(mo):
    # global obj

    hrefsrc = mo.group(1)
    path, anchor, scale = find_scaling(mo.group(2))
    base_obj = obj

    path = path.replace('/images/', '/artworks/')
    path = path.replace('/Main/', '')
    path = path.replace('%20', ' ')

    if 'references' in path or \
       'events' in path or \
       'essays' in path or \
       'artworks' in path or \
       'recent' in path:
        path = path.replace('../', '')
        base_obj = target_site
    try:
        dobj = base_obj.restrictedTraverse(str(path))
    except (AttributeError, KeyError):
        newer_path = path.replace('.jpg', '').replace('.jpeg', '')
        try:
            dobj = base_obj.restrictedTraverse(str(newer_path))
        except (AttributeError, KeyError):
            dobj = None
    if dobj is not None:
        try:
            uid = IUUID(dobj)
        except TypeError:
            import pdb; pdb.set_trace()
        path = "resolveuid/%s%s%s" % (uid, scale, anchor)
        # print "resolved:", obj.absolute_url(), path
    else:
        print "NOT resolved:", obj.absolute_url(), path

    return '%s="%s"' % (hrefsrc, path)


for portal_type, text_attr in dexterity_to_fix:
    setSite(target_site)
    for brain in tpc.search({'portal_type': portal_type}):
        obj = brain.getObject()
        text = getattr(obj, text_attr, None)
        if text is None:
            continue
        raw = getattr(text, 'raw', None)
        if raw is not None:
            text = raw
        if 'resolveuid' in text:
            new_text = re.sub(r'resolveuid/([0-9a-f]+)', resolveUID, text)
            new_text = re.sub(r'(href|src)="(\..+?)"', fixRelative, new_text)
            if text != new_text:
                setattr(obj, text_attr, RichTextValue(new_text, 'text/html', 'text/html'))

for portal_type, getter, setter in archetypes_to_fix:
    setSite(target_site)
    for brain in tpc.search({'portal_type': portal_type}):
        obj = brain.getObject()
        text_getter = getattr(obj, getter)
        try:
            text = text_getter()
        except TypeError:
            # print "Bad type!"
            continue
        if 'resolveuid' in text:
            new_text = re.sub(r'resolveuid/([0-9a-f]+)', resolveUID, text)
            new_text = re.sub(r'(href|src)="(\..+?)"', fixRelative, new_text)
            if text != new_text:
                text_setter = getattr(obj, setter)
                text_setter(new_text)

commit()
