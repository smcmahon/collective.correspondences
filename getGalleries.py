from bs4 import BeautifulSoup
from plone.i18n.normalizer.interfaces import IIDNormalizer
from transaction import commit
from z3c.relationfield import RelationValue
from zope import component
from zope.app.intid.interfaces import IIntIds
from zope.component import createObject
from zope.component import getUtility
from zope.component.hooks import setSite

app = app

site = app.Main
site_outline = site['site-outline']
site_archive = app.Main.archive
target = app.colonialart.archive
artworks = app.colonialart.artworks

setSite(app.colonialart)
normalizer = getUtility(IIDNormalizer)
intids = component.getUtility(IIntIds)


def getArtworkMetadata(aw):
    """ get the metadata for an old artwork from the html getRawDescription
    """

    metadata = {}
    source = aw.getRawDescription()
    soup = BeautifulSoup(source)
    for row in soup.find_all('tr'):
        els = row.get_text().split('\n')
        els = [s.replace(u'\xa0', '').strip() for s in els]
        els = [s for s in els if s]
        if len(els) > 1:
            key = els[0].lower()
            value = els[1]
            metadata[key] = value
    return metadata


def getSections(context):
    """ extract sections from structured body text.
        returns [{'depth':depth, 'title':title, 'currentSection':refs} ...]
    """

    sections = []

    s = context.getText() \
            .replace('<p>', '') \
            .replace('</p>', '') \
            .replace('<strong>', '') \
            .replace('</strong>', '') \
            .replace('<em>', '') \
            .replace('</em>', '') \
            .replace('<br />', '') \
            .replace('\r', '') \
            .replace('&nbsp;', ' ')

    for line in s.split('\n'):
        line = line.strip()
        if not line:
            continue

        parts = [a.strip() for a in line.split(':')]
        if len(parts):
            tsplit = [a.strip() for a in parts[0].split('"')[:2]]
            if (len(tsplit) == 2):
                depth = tsplit[0].strip('[]')
                title = tsplit[1].strip('')
                if len(parts) > 1:
                    refs = [a.strip().split('+') for a in parts[1].split(',')]
                else:
                    refs = []
                sections.append({'depth': int(depth), 'title': title, 'currentSection': refs})

    return sections

sections = getSections(site_outline)

folder_stack = [target]
last_depth = 0
last_folder = target
for section_position in range(0, len(sections)):
    gallery = sections[section_position]
    depth = gallery['depth']
    title = gallery['title']
    if depth > last_depth:
        folder_stack.append(last_folder)
        last_depth = depth
    while depth < last_depth:
        folder_stack.pop()
        last_depth -= 1
    context = folder_stack[-1]
    id = normalizer.normalize(title)
    # Do we have child galleries? If so, we need to create a subject folder.
    if section_position + 1 < len(sections) and sections[section_position +
                                                         1]['depth'] > depth:
        context.invokeFactory('subject_folder', id, title=title)
        context = context[id]
        title += ': General'
        last_folder = context
        print id, last_folder.absolute_url()
    # do we have correspondences of our own?
    # if not gallery['currentSection']:
    #     commit()
    #     continue
    context.invokeFactory('gallery', id, title=title)
    current_subject = context[id]
    print id, current_subject.absolute_url(),
    for correspondence in gallery['currentSection']:
        for citem in correspondence:
            if not citem:
                continue
            id = normalizer.normalize(citem)
            oldc = site_archive[id]
            newc = createObject('correspondence')
            newc.title = citem
            newc.id = id
            correspondence = []
            for artwork in oldc.listFolderContents():
                cid = artwork.getImage().getId().split('.')[0]
                work_obj = artworks.get(cid, None)
                if not work_obj:
                    print "Missing:", artwork.getId()
                    continue
                correspondence.append(RelationValue(intids.getId(work_obj)))
                # # Look for a correspondence credit
                # metadata = getArtworkMetadata(artwork)
                # for s in ('correspondance credit', 'correspondence credit', 'correspondence source'):
                #     if s in metadata:
                #         newc.credit = metadata[s]
            newc.correspondence = correspondence
            current_subject[id] = newc
            print id,
    print
    commit()
