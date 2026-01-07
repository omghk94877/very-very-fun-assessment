import pygame

class ScreenManager:
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


class Button:
    """
    This class defines a clickable button with hover effect.
    """

    def __init__(self, rect, text, onclick, font, bg=(80,80,80), hover_bg=(110,110,110), text_color=(255,255,255)):
        """
        this method will initialize the button
        it take self, rect, text, onclick, font, bg, hover_bg, text_color as its parameter
        """
        # initialize everything in the introduction screen
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick
        self.font = font
        self.bg = bg
        self.hover_bg = hover_bg
        self.text_color = text_color

    def update_text(self, new_text):
        """
        this method will update the button text
        it take self and the new_text as its parameter
        """
        self.text = new_text

    def draw(self, surface):
        """
        this method will draw the button on the screen
        it take self and the surface as its parameter
        """
        #play hover efffect if mouse on button
        mouse = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse)
        color = self.hover_bg 
        if is_hover :
            color = self.hover_bg
        else:
            color = self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=6)

        #setting texts and set text's collision box for clicking
        txt = self.font.render(self.text, True, self.text_color)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        """
        this method will handle the events during the button
        it take self and the event as its parameter
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.onclick):
                    self.onclick()



class MainMenu():
    def __init__(self, app):

        super().__init__(self, app)
        w, h = app.size
        btn_w, btn_h = 1920, 1080
        cx = w // 2 - btn_w // 2
        top = h // 2 - 40
        self.title_font = pygame.font.SysFont(None, 56)
        self.font = pygame.font.SysFont(None, 28)
        
        #4 buttons, play, intro, setting or quit
        self.buttons = [
            self.paddle_btn,
            Button((cx, top + 1*(btn_h+14), btn_w, btn_h), "Play", self.start_game, self.font),
            Button((cx, top + 2*(btn_h+14), btn_w, btn_h), "Introduction", self.show_intro, self.font),
            Button((cx, top + 3*(btn_h+14), btn_w, btn_h), "Setting", self.setting, self.font),
            Button((cx, top + 4*(btn_h+14), btn_w, btn_h), "Quit", self.quit_game, self.font),
        ]
    def  play_game(self):
        pass