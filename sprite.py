import pygame
import random

class Player(pygame.sprite.Sprite):
    """
    Player is not really moving, instead it's the backgound moving. 
    player only moves when the background reach the edge
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        #images of different actions
        # Use simple Surfaces so code can run without external image files
        self.stand = pygame.Surface((50, 80))
        self.stand.fill((255, 0, 0))
        self.move_l = pygame.Surface((50, 80))
        self.move_l.fill((0, 255, 0))
        self.move_r = pygame.Surface((50, 80))
        self.move_r.fill((0, 0, 255))
        self.jump = pygame.Surface((50, 80))
        self.jump.fill((255, 255, 0))
        self.attack_img = pygame.Surface((60, 40))
        self.attack_img.fill((255, 128, 0))
        self.die = pygame.Surface((50, 80))
        self.die.fill((128, 128, 128))


        #starting image is stand
        self.image = self.stand

        # facing: used by Blade to determine spawn direction
        self.facing = 'right'

        #setting rect for collision
        self.rect = self.image.get_rect()

        #displacement
        self.dx = 0
        self.dy = 0

    def move_left(self):
        self.image = self.move_l
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.facing = 'left'

    def move_right(self):
        self.image = self.move_r
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.facing = 'right'

    def move_up(self):
        self.image = self.jump
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)
        

    def death(self):
        self.image = self.die
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)
        

    def attack(self):
        #generate blade
        Blade(owner=self)

    def init_move(self):
        """
        Change the animation back to standing when stop pressing keys
        """
        self.image = self.stand
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)
        

    def update(self, dt=0):
        # accept optional dt so this sprite can be updated by a group with a dt arg
        pass

class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()

        #background, get from the parameter from main
        self.image = image
        self.rect = self.image.get_rect()

        #speed
        self.dx = 0
        self.dy = 0

    def player_move_left(self):
        """
        if player move left, background move right
        """
        self.dx = 5

    def player_move_right(self):
        """
        if player move right, background move left
        """  
        self.dx = -5

    def player_move_up(self):
        pass

    def stop(self):
        self.dx = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy


class Enemy(pygame.sprite.Sprite):
    pass

class Blade(pygame.sprite.Sprite):
    def __init__(self, owner, time=300, offset=(0,0)):
        """Create a short-lived blade that appears outside the player and then disappears.
        The blade does not move after being spawned; it simply exists for `time` ms.
        """
        super().__init__()
        self.owner = owner
        self.offset = offset
        # thin rectangle to look like a blade
        self.image = pygame.Surface((180, 10))
        self.image.fill((255, 128, 0))

        # spawn just outside the player depending on facing
        facing = getattr(owner, 'facing', 'right')
        if facing == 'right':
            x = owner.rect.right + 5 + offset[0]
        else:
            x = owner.rect.left - self.image.get_width() - 5 + offset[0]
        y = owner.rect.centery - (self.image.get_height() // 2) + offset[1]

        self.rect = self.image.get_rect(topleft=(x, y))
        self.blade_hitbox = self.rect.copy()
        self.timer = 0
        self.count_time = time

    def update(self, dt):
        """Advance lifetime; blade does not move after spawning."""
        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, owner, speed=100):
        """Create a bullet that moves in the direction the player is facing.
        """
        super().__init__()
        self.owner = owner
        # simple rectangle to represent bullet
        self.image = pygame.Surface((10, 5))
        self.image.fill((0, 0, 0))

        # spawn just outside the player depending on facing
        facing = getattr(owner, 'facing', 'right')
        if facing == 'right':
            x = owner.rect.right + 5
        else:
            x = owner.rect.left - self.image.get_width() - 5
        y = owner.rect.centery - (self.image.get_height() // 2)

        self.rect = self.image.get_rect(topleft=(x, y))

        # convert requested speed 
        self._pos_x = float(self.rect.x)
        self.vx = (speed * 30) / 1000.0
        if facing != 'right':
            self.vx = -self.vx

        self.timer = 0
        # Bullet lasts for 2 seconds
        self.count_time = 2000

    def update(self, dt):
        """Move the bullet using dt (milliseconds) and expire after count_time."""
        # move with subpixel precision
        self._pos_x += self.vx * dt
        self.rect.x = int(self._pos_x)

        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()


class Weapons(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # placeholder for combined weapon behavior
        pass

class Story(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.active = False
        self.sentences = [
            "Welcome to the game!",
            "Use WASD to move around.",
            "Press E to attack with a blade.",
            "Press Q to shoot a bullet.",
            "Good luck on your adventure!"
        ]
        
    def next_line(self):
        if not self.active:
            return

        self.index += 1
        
        if self.index < len(self.sentences):
            self.surface.fill((0, 0, 0, 160))
            text = self.sentences[self.index]
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.surface.blit(text_surf, (10, 10))

    def start(self):
        self.active = True
        self.index = 0
        self.index = 0

        self.font = pygame.font.SysFont(None, 28)

        self.surface = pygame.Surface((800, 120), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 160))
        self.image = self.surface
        self.rect = self.surface.get_rect(topleft=(560, 900))

    def update(self, dt=0):
        if not self.active:
            self.surface.fill((0, 0, 0, 0))

        #clear the text box
        self.surface.fill((0, 0, 0, 160))

        #render current line of text
        #only render if active and index is valid
        if self.active and self.index < len(self.sentences):
            text = self.sentences[self.index]
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.surface.blit(text_surf, (10, 50))

        elif not self.active or self.index >= len(self.sentences):
            # clear the text box
            self.surface.fill((0, 0, 0, 0))  


class Obstacle(pygame.sprite.Sprite):
    pass