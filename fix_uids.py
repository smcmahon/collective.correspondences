from plone.app.dexterity.upgrades.to2001 import add_missing_uuids
from transaction import commit


add_missing_uuids(app.colonialart)
commit()

print "UID's applied"