from google.appengine.ext import ndb
# from app import Time
# from app import Author
# class Tag(ndb.Model):
# 	name = ndb.StringProperty()

class Resource(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    # creator = ndb.StructuredProperty(Author)
    # name = ndb.StringProperty(indexed=False)
    # date = ndb.DateTimeProperty(auto_now_add=True)
    # tags = ndb.StructuredProperty(Tag, repeated=True)
    # availability = ndb.StructuredProperty(Time, repeated=True)

    # def __repr__(self):
    # 	return "[Resource] %s" %name


