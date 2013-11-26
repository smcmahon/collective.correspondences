from Products.Five.browser import BrowserView

class ArtworkView(BrowserView):

    def __init__(self, context, request):
        """ Initialize context and request as view multi adaption parameters.
        """
        self.context = context
        self.request = request
