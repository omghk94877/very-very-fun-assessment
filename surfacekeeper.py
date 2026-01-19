import pygame
import make_save
import os
from json_loader import load_json
import game_state
import random
 
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
    def update(self, dt):
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
                self.onclick()
                if callable(self.onclick):
                    self.onclick()



class LogoScreen(ScreenManager):
    def __init__(self, app):
        super().__init__(app)
        # Randomly choose Logo_1 or Logo_2
        logo_choice =[r'src\Images\Logo_1.png', 
                      r'src\Images\Logo_2.png']
        
        logo = random.choice(logo_choice)
        
        self.image = pygame.image.load(logo).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.app.size)
        
        # Initialize timer and fade parameters
        self.timer = 0
        self.display_duration = 3000  # 3 seconds
        self.fade_duration = 1000  # 1 second
        self.fading = False

    def update(self, dt):
        self.timer += dt
        if not self.fading and self.timer >= self.display_duration:
            self.fading = True
            self.timer = 0
        if self.fading:
            self.alpha = max(0, 255 - int(255 * (self.timer / self.fade_duration)))
            self.image.set_alpha(self.alpha)
            if self.alpha <= 0:
                self.app.change_screen(MainMenu(self.app))

    def draw(self, surface):
        surface.blit(self.image, (0, 0))


class MainMenu(ScreenManager):
    def __init__(self, app):
        super().__init__(app)
        w, h = app.size
        btn_w, btn_h = 200, 50
        cx = w // 2 - btn_w // 2
        top = h // 2 - 100
        self.title_font = pygame.font.SysFont(None, 56)
        self.font = pygame.font.SysFont(None, 28)

        # Try to load background image, use solid color if not available
        try:
            self.image = pygame.image.load("src/Images/intro/menu.png")
            self.image = pygame.transform.scale(self.image, (2000, 600))
            self.image = self.image.convert()
        except:
            self.image = None

        # Position image at top-left of screen
        if self.image:
            self.scroll_offset = 0
            self.scroll_speed = 1
        
        # 5 buttons: play, intro, load save, visual novel, quit
        self.buttons = [
            Button((cx, top + 1*(btn_h+14), btn_w, btn_h), "Play", self.play_game, self.font),
            Button((cx, top + 2*(btn_h+14), btn_w, btn_h), "Introduction", self.show_intro, self.font),
            Button((cx, top + 3*(btn_h+14), btn_w, btn_h), "Load Save", self.load_save, self.font),
            Button((cx, top + 5*(btn_h+14), btn_w, btn_h), "Quit", self.quit_game, self.font),
        ]

    def update(self, dt):
        '''Called automatically during Refresh to update sprite's position.'''
        if self.image:
            # Move scroll offset
            self.scroll_offset -= self.scroll_speed
            # Wrap around when we've scrolled past the image width
            if self.scroll_offset <= -self.image.get_width():
                self.scroll_offset += self.image.get_width()

    def handle_event(self, event):
        """
        this method will handle the events during the main menu screen
        it take self and the event as its parameter
        """
        # execute the function if one of the button is clicked
        for b in self.buttons:
            b.handle_event(event)
    
    def draw(self, surface):
        """
        this method will draw the main menu screen
        it take self and the surface as its parameter
        """
        # fill background color
        surface.fill((18, 20, 28))
        
        # draw scrolling background image if available
        if self.image:
            img_width = self.image.get_width()
            screen_width = self.app.size[0]
            # Calculate starting x position
            x = self.scroll_offset % img_width
            if x > 0:
                x -= img_width
            # Draw copies until screen is covered
            while x < screen_width:
                surface.blit(self.image, (x, 0))
                x += img_width
        
        title = self.title_font.render("Monster Mash", True, (255, 220, 60))
        surface.blit(title, title.get_rect(center=(self.app.size[0]//2, 50)))

        for b in self.buttons:
            b.draw(surface)

    def play_game(self):
        # Start name input
        self.app.change_screen(NameInput(self.app))

    def show_intro(self):
        self.app.change_screen(ShowIntro(self.app))

    def load_save(self):
        self.app.change_screen(MakeSave(self.app))

    
    def quit_game(self):
        self.app.quit()

class ShowIntro(ScreenManager):
    def __init__(self, app):
        super().__init__(app)

        self.font = pygame.font.SysFont(None, 24)
        self.intro_index = 0

        paths = [
            "src/Images/intro/intro-1.png",
            "src/Images/intro/intro-2.png",
            "src/Images/intro/intro-3.png",
            "src/Images/intro/intro-4.png",
            "src/Images/intro/intro-5.png",
            "src/Images/intro/intro-6.png",
            "src/Images/intro/intro-7.png",
        ]

        self.intro_images = []
        for p in paths:
            try:
                img = pygame.image.load(p)
                img = pygame.transform.scale(img, (800, 450))
                img = img.convert()
                self.intro_images.append(img)
            except:
                # Skip images that don't exist
                pass

        self.total = len(self.intro_images)
        if self.total == 0:
            # Create a placeholder surface if no images loaded
            placeholder = pygame.Surface((800, 450))
            placeholder.fill((50, 50, 50))
            self.intro_images.append(placeholder)
            self.total = 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.app.change_screen(MainMenu(self.app))

            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.intro_index -= 1

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.intro_index += 1

            self.intro_index = max(0, min(self.intro_index, self.total - 1))

    def draw(self, surface):
        surface.fill((12, 12, 40))

        # draw the image in center
        img = self.intro_images[self.intro_index]
        rect = img.get_rect(center=surface.get_rect().center)
        surface.blit(img, rect)


class VisualNovel(ScreenManager):
    def __init__(self, app, story_part="intro", previous_screen=None):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 24)
        self.name_font = pygame.font.SysFont(None, 28)
        self.story_part = story_part
        self.previous_screen = previous_screen
        self.story_file = f"stories/{story_part}.json"
        self.story_data = load_json(self.story_file) or []
        self.current_index = 0
        self.background = None
        self.load_current_background()
        pygame.mixer.init()  # Ensure mixer is initialized

    def load_current_background(self):
        if self.story_data and self.current_index < len(self.story_data):
            bg_path = os.path.join("src", "Images", self.story_data[self.current_index].get("background", ""))
            try:
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, self.app.size)
            except:
                self.background = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.advance_story()
            elif event.key == pygame.K_ESCAPE:
                self.app.change_screen(MainMenu(self.app))

    def advance_story(self):
        if self.current_index < len(self.story_data) - 1:
            # Play sound effect
            sound_path = os.path.join("src", "Sounds", self.story_data[self.current_index].get("sound", ""))
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.play()
            except:
                pass  # No sound or error
            self.current_index += 1
            self.load_current_background()
        else:
            # End of story, go to next
            self.on_story_end()

    def on_story_end(self):
        if self.story_part == "intro":
            self.app.start_game_real(1)
        elif self.story_part == "boss_defeat":
            # After boss defeat story, start level 1 again — since
            # `game_state.level1_completed` is already set, the boss won't respawn.
            self.app.start_game_real(1)
        elif self.story_part == "level1_end":
            if self.previous_screen:
                self.app.change_screen(self.previous_screen)
            else:
                self.app.start_game_real(1)
        elif self.story_part == "portal":
            # After the portal visual novel, ask for hard mode choice
            self.app.change_screen(HardModeChoiceScreen(self.app))
        else:
            self.app.change_screen(MainMenu(self.app))

    def draw(self, surface):
        surface.fill((0, 0, 0))  # Black background if no image
        if self.background:
            surface.blit(self.background, (0, 0))

        if self.story_data and self.current_index < len(self.story_data):
            data = self.story_data[self.current_index]
            name = data.get("name", "").replace("USER_NAME", self.app.game_state.player_name)
            line = data.get("line", "").replace("USER_NAME", self.app.game_state.player_name)

            # Draw name
            name_text = self.name_font.render(name, True, (255, 255, 255))
            surface.blit(name_text, (50, self.app.size[1] - 170))

            # Draw line with wrapping to avoid overflow
            wrap_rect = pygame.Rect(50, self.app.size[1] - 140, self.app.size[0] - 100, 120)
            self._render_text_block(surface, line, self.font, (255, 255, 255), wrap_rect)

            # Instruction
            instr = self.font.render("Press SPACE or ENTER to continue, ESC to menu", True, (200, 200, 200))
            surface.blit(instr, (50, self.app.size[1] - 30))

    def _render_text_block(self, surface, text, font, color, rect, line_spacing=4):
        """Render `text` inside `rect` with word-wrapping using `font`.

        - `rect` is a pygame.Rect defining position and max width/height.
        - Lines that don't fit vertically will be truncated.
        """
        words = text.split(' ')
        space_width, space_height = font.size(' ')
        x, y = rect.topleft
        max_x = rect.right
        line = ''
        for word in words:
            test_line = word if not line else f"{line} {word}"
            test_width, _ = font.size(test_line)
            if x + test_width <= max_x:
                line = test_line
            else:
                # draw current line
                if line:
                    rendered = font.render(line, True, color)
                    surface.blit(rendered, (x, y))
                    y += rendered.get_height() + line_spacing
                    if y > rect.bottom:
                        return
                line = word

        # draw last line
        if line and y <= rect.bottom:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y))


class IntroScreen(VisualNovel):
    def __init__(self, app, level, game_state):
        super().__init__(app, "intro", previous_screen=None)
        self.level = level
        self.timer = 0  # Auto-advance timer
    
    def update(self, dt):
        super().update(dt)
        self.timer += dt
        if self.timer > 3000:  # Auto-advance after 3 seconds
            self.advance_story()
    
    def on_story_end(self):
        self.app.start_game_real(self.level)


class MakeSave(ScreenManager, make_save.SaveSystem):
    def __init__(self, app):
        ScreenManager.__init__(self, app)
        make_save.SaveSystem.__init__(self)
        self.font = pygame.font.SysFont(None, 24)
        self.save_list = []
        self.selected_index = 0
        self.load_save_files()
    
    def load_save_files(self):
        """Load available save files from the save directory"""
        import os
        save_dir = "saves"
        if os.path.exists(save_dir):
            self.save_list = [f for f in os.listdir(save_dir) if f.endswith('.json')]
        if not self.save_list:
            self.save_list = ["No saves available"]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_screen(MainMenu(self.app))
            elif event.key == pygame.K_UP and len(self.save_list) > 1:
                self.selected_index = (self.selected_index - 1) % len(self.save_list)
            elif event.key == pygame.K_DOWN and len(self.save_list) > 1:
                self.selected_index = (self.selected_index + 1) % len(self.save_list)
            elif event.key == pygame.K_RETURN and self.save_list[0] != "No saves available":
                # Load the selected save
                try:
                    player_name = self.save_list[self.selected_index].replace('_save.json', '')
                    if self.app.game_state.load(player_name):
                        self.app.start_game(1)
                except:
                    pass

    def draw(self, surface):
        surface.fill((18, 20, 28))
        title = self.font.render("Load Save", True, (255, 220, 60))
        surface.blit(title, title.get_rect(center=(self.app.size[0]//2, 50)))
        
        y_offset = 150
        for i, save in enumerate(self.save_list):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            display_name = save.replace('_save.json', '') if save.endswith('_save.json') else save
            text = self.font.render(f"{'> ' if i == self.selected_index else '  '}{display_name}", True, color)
            surface.blit(text, (100, y_offset + i * 40))
        
        instruction = self.font.render("UP/DOWN to select, ENTER to load, ESC to return", True, (200, 200, 200))
        surface.blit(instruction, (100, self.app.size[1] - 50))


class NameInput(ScreenManager):
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 36)
        self.input_font = pygame.font.SysFont(None, 48)
        self.prompt = "Enter your name:"
        self.name = ""
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.name.strip():
                self.app.game_state.new_game(self.name.strip())
                self.app.change_screen(VisualNovel(self.app, "intro"))
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.app.change_screen(MainMenu(self.app))
            else:
                if len(self.name) < 20 and event.unicode.isprintable():
                    self.name += event.unicode

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface):
        surface.fill((18, 20, 28))
        prompt_text = self.font.render(self.prompt, True, (255, 220, 60))
        surface.blit(prompt_text, prompt_text.get_rect(center=(self.app.size[0]//2, self.app.size[1]//2 - 50)))
        
        name_text = self.input_font.render(self.name + ("|" if self.cursor_visible else ""), True, (255, 255, 255))
        surface.blit(name_text, name_text.get_rect(center=(self.app.size[0]//2, self.app.size[1]//2 + 20)))
        
        instr = self.font.render("Press ENTER to confirm, ESC to cancel", True, (200, 200, 200))
        surface.blit(instr, instr.get_rect(center=(self.app.size[0]//2, self.app.size[1] - 50)))


class MakeWhiteScreem(ScreenManager):
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, surface):
        surface.fill((255, 255, 255))


class UnderDevelopmentScreen(ScreenManager):
    """Simple screen that shows an 'under development' message and a button back to main menu."""
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 36)
        self.small = pygame.font.SysFont(None, 24)
        w, h = app.size
        btn_w, btn_h = 240, 48
        cx = w // 2 - btn_w // 2
        cy = h // 2 + 40
        self.back_button = Button((cx, cy, btn_w, btn_h), "Back to Main Menu", self.back_to_menu, self.small)

    def back_to_menu(self):
        self.app.change_screen(MainMenu(self.app))

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def draw(self, surface):
        surface.fill((18, 20, 28))
        title = self.font.render("Under development, please wait", True, (255, 220, 60))
        surface.blit(title, title.get_rect(center=(self.app.size[0]//2, self.app.size[1]//2 - 20)))
        self.back_button.draw(surface)


class TheEndScreen(ScreenManager):
    """Screen that shows the 'the_end' image and waits for key press to go to main menu."""
    def __init__(self, app):
        super().__init__(app)
        self.image_path = r"src\Images\story\the_end.gif"
        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, self.app.size)
        except:
            self.image = None
        self.font = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.app.change_screen(MainMenu(self.app))

    def draw(self, surface):
        surface.fill((0, 0, 0))  # Black background
        if self.image:
            surface.blit(self.image, (0, 0))
        else:
            # Fallback if image fails to load
            text = self.font.render("The End", True, (255, 255, 255))
            surface.blit(text, text.get_rect(center=(self.app.size[0]//2, self.app.size[1]//2)))

        # Instruction
        instr = self.font.render("Press SPACE or ENTER to continue", True, (200, 200, 200))
        surface.blit(instr, (50, self.app.size[1] - 30))


class HardModeChoiceScreen(ScreenManager):
    """Screen that asks the player if they want to enable hard mode."""
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 36)
        self.small = pygame.font.SysFont(None, 24)
        w, h = app.size
        btn_w, btn_h = 200, 48
        cx = w // 2 - btn_w // 2
        cy = h // 2 + 40
        self.yes_button = Button((cx - 120, cy, btn_w, btn_h), "Yes, Hard Mode", self.enable_hard_mode, self.small)
        self.no_button = Button((cx + 120, cy, btn_w, btn_h), "No, Normal", self.disable_hard_mode, self.small)

    def enable_hard_mode(self):
        if self.app.game_state:
            self.app.game_state.hard_mode = True
            self.app.game_state.save()
        self.app.start_game_real(1)

    def disable_hard_mode(self):
        if self.app.game_state:
            self.app.game_state.hard_mode = False
            self.app.game_state.save()
        self.app.change_screen(TheEndScreen(self.app))

    def handle_event(self, event):
        self.yes_button.handle_event(event)
        self.no_button.handle_event(event)

    def draw(self, surface):
        surface.fill((18, 20, 28))
        title = self.font.render("Congratulations on completing the game!", True, (255, 220, 60))
        surface.blit(title, title.get_rect(center=(self.app.size[0]//2, self.app.size[1]//2 - 60)))
        subtitle = self.font.render("Enable Hard Mode? (Enemies take 2x hits)", True, (255, 220, 60))
        surface.blit(subtitle, subtitle.get_rect(center=(self.app.size[0]//2, self.app.size[1]//2 - 20)))
        self.yes_button.draw(surface)
        self.no_button.draw(surface)


class DeathCount(ScreenManager):
    def __init__(self):
        self.death_count = 0 

    def add_death_count(self):
        self.death_count += 1

    def death_count_keeper(self):
        self.in_game = False
        while self.in_game == True:
            pass


class App:
    """Main application class that manages screen transitions and the game loop"""
    def __init__(self, size=(1000, 600)):
        pygame.init()
        self.size = size
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Monster Smash")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = None
        self.game_instance = None
        self.game_state = game_state.GameState()
        
        # Start with logo screen
        self.change_screen(LogoScreen(self))
        
    def change_screen(self, new_screen):
        """Change to a new screen"""
        if self.current_screen and hasattr(self.current_screen, "on_exit"):
            self.current_screen.on_exit()
        
        self.current_screen = new_screen
        if hasattr(self.current_screen, "on_enter"):
            self.current_screen.on_enter()
    
    def start_game(self, level=1):
        """Start the intro screen before the actual game"""
        self.current_screen = IntroScreen(self, level, self.game_state)
    
    def start_game_real(self, level=1):
        """Start the actual game"""
        # Import here to avoid circular imports
        import main
        # Instantiate `Main` with `app` as first argument and run its own loop.
        # `Main.loop()` is a blocking loop that runs the gameplay; call it so
        # the game actually starts when requested (level 1, etc.).
        self.game_instance = main.Main(self, level=level, game_state=self.game_state)
        # Run the game's loop (blocks until game ends)
        self.game_instance.loop()
        # After the game's loop finishes, check if the game requested a follow-up action
        action = getattr(self.game_instance, 'next_action', None)
        if action and action[0] == 'visual_novel':
            # action format: ('visual_novel', story_name)
            _, story_name = action
            self.change_screen(VisualNovel(self, story_name))
        else:
            # Default: return to main menu
            self.change_screen(MainMenu(self))
    
    def quit(self):
        """Quit the application"""
        self.running = False
    
    def run(self):
        """Main application loop"""
        while self.running:
            dt = self.clock.tick(30)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.current_screen:
                    self.current_screen.handle_event(event)
            
            if self.current_screen:
                self.current_screen.update(dt)
                self.screen.fill((0, 0, 0))
                self.current_screen.draw(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()
