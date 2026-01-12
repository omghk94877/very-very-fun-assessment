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

    def change_screen(self, new_screen):
        """
        this method take self and the new_screen (str name) as it parameter
        it will check which name it is and call the funtion
        """
        #if the name is on_exit it will call method on_exit
        if hasattr(self.current_screen, "on_exit"):
            self.current_screen.on_exit()

        #If the name is on_enter, it will call metod on_enter
        self.current_screen = new_screen
        if hasattr(self.current_screen, "on_enter"):
            self.current_screen.on_enter()
    
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
            Button((cx, top + 1*(btn_h+14), btn_w, btn_h), "Play", self.play_game, self.font),
            Button((cx, top + 2*(btn_h+14), btn_w, btn_h), "Introduction", self.show_intro, self.font),
            Button((cx, top + 3*(btn_h+14), btn_w, btn_h), "load Save", self.load_save, self.font),
            Button((cx, top + 4*(btn_h+14), btn_w, btn_h), "Quit", self.quit_game, self.font),
        ]
    def handle_event(self, event):
        """
        this method will handle the events during the main menu screen
        it take self and the event as its parameter
        """

        #exccute the function if one of the button is clicked
        for b in self.buttons:
            b.handle_event(event)
    
    def draw(self, surface):
        """
        this method will draw the main menu screen
        it take self and the surface as its parameter
        """

        #fill colour for the 
        surface.fill((18, 20, 28))
        title = self.title_font.render("Monster  Smash", True, (255, 220, 60))
        surface.blit(title, title.get_rect(center=(self.app.size[0]//2, 100)))

        for b in self.buttons:
            b.draw(surface)

    def  play_game(self):
        self.app.change_screen(MainMenu(self.app))

    def show_intro(self):
        self.app.change_screen(ShowIntro(self.app))

    def load_save(self):
        self.app.change_screen(MainMenu(self.app))
    
    def quit_game(self):
        self.app.quit()

class ShowIntro(ScreenManager):
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 24)
        self.intro_index = 0

    def handle_event(self, event):
        """
        this method will handle the events during the introduction screen
        it take self and the event as its parameter
        """
        #if user click ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen(MainMenu(self.app))

        if event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.intro_index != 0 :
            pass
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.intro_index != 5:
            pass
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.intro_index == 0 :
            pass
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.intro_index == 5 :
            pass


    def draw(self, surface):
        """
        this method will draw the introduction screen
        it take self and the surface as its parameter
        """
        surface.fill((12, 12, 40))
        for i, line in enumerate(self.lines):
            txt = self.font.render(line, True, (230,230,230))
            surface.blit(txt, (40, 40 + i*28))

class MakeSave(ScreenManager):
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 24)
    
    def load_save(self):
        pass

    def make_save(self):
        pass

class MakeWhiteScreem(ScreenManager):
    def __init__(self):
        pass

class DeathCount(ScreenManager):
    def __init__(self):
        self.death_count = 0 

    def add_death_count(self):
        self.death_count += 1

    def death_count_keeper(self):
        self.in_game = False
        while self.in_game == True:
            pass