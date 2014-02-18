from transaction import commit

site = app.Main
target_site = app.colonialart
target_folder = target_site.artworks

existing_images = {}
for id in site.images.objectIds():
    existing_images[id.replace('.jpg', '').replace('.jpeg', '')] = id

for id in target_site.artworks.objectIds():
    if id in existing_images:
        del existing_images[id]

print "Copying %d objects" % len(existing_images)
for key in existing_images.keys():
    id = existing_images[key]
    print id, key
    cb = site.images.manage_copyObjects(id)
    target_folder.manage_pasteObjects(cb)
    target_folder.manage_renameObjects([id], [key])

commit()