class Screen:
    """
    this class will define the base screen
    """
    def __init__(self, app):
        """
        this method will initialize the screen
        it take self and the app as its parameter
        """
        self.app = app

    
    def handle_event(self, event):
        """
        this method will handle the events during the screen
        it take self and the event as its parameter
        """
        pass
    def update(self):
        """
        this method will update the screen
        """
        pass
    def draw(self, surface):
        """
        this method will draw the screen
        it take self and the surface as its parameter
        """
        pass
    def on_enter(self):
        """
        this method will be called when entering the screen
        """
        pass
    def on_exit(self):
        """
        this method will be called when exiting the screen
        """
        pass

