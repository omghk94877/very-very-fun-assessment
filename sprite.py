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

        #setting rect for collision
        self.rect = self.image.get_rect()

        #displacement
        self.dx = 0
        self.dy = 0

    def move_left(self):
        self.image = self.move_l
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_right(self):
        self.image = self.move_r
        # keep same position when swapping image
        self.rect = self.image.get_rect(center=self.rect.center)

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
        

    def update(self):
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
    def __init__(self, owner, time=500, offset=(0,0), size=(40,40)):
        super().__init__()
        self.owner = owner    
        self.offset = offset
        self.blade_hitbox = pygame.Rect(
            owner.rect.x + offset[0],
            owner.rect.y + offset[1],
            size[0],
            size[1]
        )
        self.timer = 0
        self.count_time = time
        self.clock = pygame.time.Clock()


    def update(self,dt):
        """
        dt from mainloop, provide the timer as parameter to this sprite
        """
        #set timer
        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()

        #move with player
        self.blade_hitbox.topleft = (
            self.owner.rect.x + self.offset[0],
            self.owner.rect.y + self.offset[1]
        )


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Weapons(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # placeholder for combined weapon behavior
        pass

class Entities(pygame.sprite.Sprite):
    """
    Include level, health, etc
    """
    pass

class Obstacle(pygame.sprite.Sprite):
    pass