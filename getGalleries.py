from bs4 import BeautifulSoup
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.textfield.value import RichTextValue
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import safe_unicode
from transaction import commit
from z3c.relationfield import RelationValue
from zope import component
from zope.app.intid.interfaces import IIntIds
from zope.component import createObject
from zope.component import getUtility
from zope.component.hooks import setSite

import os.path
import plone.app.uuid.utils as uuid_utils
import re


app = app

site = app.Main
site_outline = site['galleries']
site_archive = app.Main.galleries
new_site = app.colonialart
target = app.colonialart.galleries
artworks = app.colonialart.artworks

setSite(site)
redirector = getUtility(IRedirectionStorage)

setSite(app.colonialart)
normalizer = getUtility(IIDNormalizer)
intids = component.getUtility(IIntIds)

npc = site_archive.portal_catalog


def resolveUID(mo):
    setSite(site)
    new_path = uuid_utils.uuidToPhysicalPath(mo.group(1))
    setSite(new_site)
    new_path = new_path.replace('/Main', '').replace('/images', '/artworks').replace('.jpg', '').replace('.jpeg', '')
    return new_path


def objFromURL(ref_obj, url):
    """ given a URL in old site, find object
    """

    setSite(site)
    if 'resolveuid' in url:
        ref_obj = uuid_utils.uuidToObject(url.replace('resolveuid/', ''))
    else:
        try:
            ref_obj = ref_obj.restrictedTraverse(url)
        except (AttributeError, KeyError):
            if 'http:' not in url:
                # handle relative paths
                base_path = ref_obj.absolute_url().replace('http://nohost', '')
                if not ref_obj.isPrincipiaFolderish:
                    # remove last component of pathname
                    base_path = os.path.dirname(base_path)
                print url,
                url = os.path.normpath(os.path.join(base_path, url))
                print base_path, url
            # try redirect
            ref_obj = ref_obj.restrictedTraverse(redirector.get(url))
    return ref_obj


def addCorrespondence(new_gallery, ref_obj):
    """ get correspondence data from ref_obj,
        add the correspondence to new_gallery
    """

    setSite(new_site)
    id = normalizer.normalize(ref_obj.getId())
    newc = createObject('correspondence')
    newc.title = ref_obj.title
    newc.id = id
    correspondence = []
    for artwork in ref_obj.listFolderContents():
        cid = artwork.getImage().getId().split('.')[0]
        work_obj = artworks.get(cid, None)
        if not work_obj:
            print "Missing:", artwork.getId()
            continue
        correspondence.append(RelationValue(intids.getId(work_obj)))
    newc.correspondence = correspondence
    new_gallery[id] = newc


sections = site_archive.objectIds()
sections = [g for g in sections if ('-es' not in g) and (g != 'galleries')]
for section in sections:
    master_doc = site_archive[section]
    print master_doc,
    source = master_doc.getRawText()
    soup = BeautifulSoup(source)
    last_a = soup.find_all('table')[-1].find_all('a')[-1]
    url = last_a['href']

    setSite(new_site)
    new_gallery = createObject('gallery')
    new_gallery.title = safe_unicode(master_doc.title)
    new_gallery.description = safe_unicode(master_doc.description)
    tables = soup.find_all('table')
    if tables:
        tables[-1].decompose()
    soup.html.unwrap()
    soup.body.unwrap()
    body = soup.prettify()
    body = body.replace('/images', '/artworks')
    body = body.replace('.jpg', '')
    body = body.replace('.jpeg', '')
    # body = re.sub(r'resolveuid/([0-9a-f]+)', resolveUID, body)
    new_gallery.body = RichTextValue(body, 'text/html', 'text/html')
    new_gallery.id = master_doc.id
    target[master_doc.id] = new_gallery
    # get contained object
    new_gallery = target[master_doc.id]
    print new_gallery.title

    ref_obj = objFromURL(master_doc, url)
    while ref_obj is not None:
        addCorrespondence(new_gallery, ref_obj)
        # look for additional correspondences in this chain
        links = BeautifulSoup(ref_obj.getRawMainNavControl()).find_all('a')
        if len(links) >= 2:
            last_a = links[-1]['href']
            ref_obj = objFromURL(ref_obj, last_a)
            cid = ref_obj.getId()
            print cid
            if ref_obj.portal_type != 'ArtworkSet':
                ref_obj = None
        else:
            ref_obj = None

commit()
