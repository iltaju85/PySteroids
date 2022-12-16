#############################################
# ASTEROID-style small pygame project v.0.2 #
#   by: Ilkka Jussila                       #
#############################################

# TODO:
# 1. start ship pointing up
# 2. nuke
# 3. flash screen when explosion occurs - fix draw order

import pygame
import pygame.gfxdraw
from random import randint, uniform, choice


class Ship(pygame.sprite.Sprite):
    """ Player ship class. Containts a lot of extra game logic """

    def __init__(self, group):
        super().__init__(group)
        ship = pygame.surface.Surface((50, 50))
        pygame.gfxdraw.filled_polygon(ship, ((25, 3), (47, 47), (25, 40), (3, 47)), (127, 255, 0))
        ship = pygame.transform.rotozoom(ship, -90, 1)
        self.image = ship.convert_alpha()
        self.og_surf = self.image
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.image)

        self.length = 1
        self.rotation_speed = 250
        self.angle = 0
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 500
        self.force = pygame.math.Vector2(self.direction)

        self.offset = pygame.math.Vector2()

        self.started = False
        self.win = False
        self.destroyed = False

        self.can_shoot = True
        self.last_laser_time = 0
        self.time_now = 0
        self.time_ended = 0
        self.score = 0

    def input(self):
        """ Shoot lasers when space is pressed down """
        if keys[pygame.K_SPACE] and self.can_shoot:
            self.can_shoot = False
            self.last_laser_time = self.time_now
            Laser(laser_group, self.direction, self.angle)

    def keyboard_input(self):
        """ Keyboard inputs """
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed * dt
            self.direction = self.direction.rotate(-self.rotation_speed * dt)

        elif keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed * dt
            self.direction = self.direction.rotate(self.rotation_speed * dt)

        if keys[pygame.K_UP]:
            if self.force.length() < 1:
                self.force += self.direction * dt
            else:
                self.force.scale_to_length(0.99)

        if keys[pygame.K_DOWN]:
            if self.force.length() < 1:
                self.force += -(self.direction * dt)
            else:
                self.force.scale_to_length(0.99)

        if keys[pygame.K_RETURN]:
            if not self.started:
                self.spawn_self()
        if self.direction.length() > 0:
            self.direction.scale_to_length(self.length)
        self.pos += self.force * self.speed * dt
        self.offset += self.force * self.speed // 10 * dt

        self.rect.center = round(self.pos.x), round(self.pos.y)

    def spawn_self(self):
        """ Resetting the ship """
        self.destroyed = False
        self.started = True
        self.win = False
        self.score = 0
        self.angle = 0
        self.offset.xy = 0,0
        self.direction.xy = 0.001, 0
        self.force.xy = 0, 0
        self.pos.x = SCREEN_WIDTH // 2
        self.pos.y = SCREEN_HEIGHT // 2

    def check_borders(self):
        """ Crossing the screen boundaries """
        if ship.rect.top > SCREEN_HEIGHT:
            self.pos.y = 0
        if ship.rect.bottom < 0:
            self.pos.y = SCREEN_HEIGHT - 1
        if ship.rect.right < 0:
            self.pos.x = SCREEN_WIDTH - 1
        if ship.rect.left > SCREEN_WIDTH:
            self.pos.x = 0

    def laser_timer(self):
        """ Laser shooting speed limiter """
        if self.time_now - self.last_laser_time > 250:
            self.can_shoot = True

    def meteor_collision(self):
        """ When ship collides with meteors """
        collision = pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask)
        if collision:
            for col in collision:
                explosion = Explosion(pygame.time.get_ticks(), col.rect.center)
                explosion_group.append(explosion)
            explosion = Explosion(pygame.time.get_ticks(), self.rect.center)
            explosion_group.append(explosion)
            self.started = False
            self.destroyed = True

    def rotate(self):
        """ Rotate ship graphics """
        rotated_surf = pygame.transform.rotozoom(self.og_surf, self.angle, 1)
        self.image = rotated_surf.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(round(self.pos[0]), round(self.pos[1])))

    def update(self):
        """ General updates. Will be run every frame """
        self.keyboard_input()
        self.meteor_collision()
        self.time_now = pygame.time.get_ticks()
        self.laser_timer()
        self.input()
        self.rotate()
        self.check_borders()


class Laser(pygame.sprite.Sprite):
    """ Laser class """
    def __init__(self, group, direction, angle):
        super().__init__(group)
        laser_surf = pygame.surface.Surface((3, 40))
        laser_surf.fill('chartreuse')
        self.image = pygame.transform.rotozoom(laser_surf, angle - 90, 1)
        self.rect = self.image.get_rect(center=(round(ship.pos[0]), round(ship.pos[1])))
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(direction)
        self.speed = 1000

    def meteor_collision(self):
        """ Laser collision with meteors """
        collided = pygame.sprite.spritecollide(self, meteor_group, pygame.sprite.collide_mask)
        if collided:
            for sprite in collided:
                if sprite.image.get_size()[0] > 115:
                    Meteor(meteor_group, pos=sprite.rect.center, size=(sprite.image.get_size()[0]//2, sprite.image.get_size()[1]//2))
                    Meteor(meteor_group, pos=sprite.rect.center, size=(sprite.image.get_size()[0]//2, sprite.image.get_size()[1]//2))
                elif sprite.image.get_size()[0] > 80:
                    Meteor(meteor_group, pos=sprite.rect.center, size=(sprite.image.get_size()[0]//2, sprite.image.get_size()[1]//2))
            ship.score += self.image.get_width()
            explosion = Explosion(pygame.time.get_ticks(), self.rect.center)
            explosion_group.append(explosion)
            self.kill()

    def update(self):
        """ Laser updates. Will be run every frame """
        self.meteor_collision()
        self.pos += self.direction * self.speed * dt
        self.rect.center = round(self.pos.x), round(self.pos.y)
        if self.rect.bottom < 0:
            self.kill()
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        if self.rect.left > SCREEN_WIDTH:
            self.kill()
        if self.rect.right < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    """ Meteor class """
    def __init__(self, group, pos=None, size=None):
        super().__init__(group)
        self.wave = 1

        # give meteor random size when initialized
        surf = pygame.surface.Surface((50, 50))

        # randomly generated polygon graphics representing the Meteor. very janky but concept is the key here
        pygame.gfxdraw.filled_polygon(surf,
                                      ((randint(3, 8), randint(9,13)),
                                       (randint(7, 15), randint(2, 7)),
                                       (randint(30, 45), randint(10, 16)),
                                       (randint(42, 49), randint(23, 27)),
                                       (randint(39, 46), randint(38,47)),
                                       (randint(22,28), randint(43, 48)),
                                       (randint(12, 17), randint(40, 49)),
                                       (randint(2, 5), randint(40,42))),
                                      (127, 255, 0))
        # Meteor's size is either passed on as an argument when one of the meteors is 'split' or randomly generated:
        if not size:
            factor = uniform(1, 2.5)  # random size as a float
            rescaled_size = factor * surf.get_size()[0], factor * surf.get_size()[1]
        else:
            factor = uniform(0.9, 1.2)
            rescaled_size = factor * size[0], factor * size[0]
        self.rescaled_image = pygame.transform.scale(surf, (rescaled_size))
        self.image = self.rescaled_image.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)

        # Meteor's position is either passed on as an argument when one of the meteors is 'split' or randomly generated:
        if not pos:
            random_x_pos = randint(-100, SCREEN_WIDTH + 100)
            random_y_pos = randint(-300, -100)
            self.rect = self.image.get_rect(center=(random_x_pos, random_y_pos))
            self.pos = pygame.math.Vector2(self.rect.center)
        else:
            self.rect = self.image.get_rect(center=pos)
            self.pos = pygame.math.Vector2(self.rect.center)

        # random directions
        random_x_direction = uniform(-1.0, 1.0)
        random_y_direction = uniform(-1.0, 1.0)
        self.direction = pygame.math.Vector2(random_x_direction, random_y_direction)
        self.speed = 300

        # rotation
        self.rotation = 0
        self.rotation_speed = randint(-50, 50)  # random rotation speed

    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pygame.transform.rotate(self.rescaled_image, self.rotation)
        self.image = rotated_surf.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(round(self.pos[0]), round(self.pos[1])))

    @staticmethod
    def spawn():
        """ Spawn waves make gameplay a little more interesting. Not implemented properly. Just a concept"""
        ship.win = False
        Meteor(meteor_group)
        if 20000 > ship.time_now > 15000:
            pass
        if 46000 > ship.time_now > 40000:
            Meteor(meteor_group)
        if 70000 > ship.time_now > 65000:
            Meteor(meteor_group)
        if 105000 > ship.time_now > 100000:
            Meteor(meteor_group)
            Meteor(meteor_group)
        # if ship.time_now > 109000:
        #     ship.win = True

    def update(self):
        self.rotate()
        self.pos += self.speed * self.direction * dt
        self.rect.topleft = round(self.pos.x), round(self.pos.y)

        # collisions with screen borders
        if self.rect.top > SCREEN_HEIGHT:
            self.pos.y = 0 - self.rect.height + 1
        if self.rect.bottom < 0:
            self.pos.y = SCREEN_HEIGHT
        if self.rect.right < 0:
            self.pos.x = SCREEN_WIDTH - 1
        if self.rect.left > SCREEN_WIDTH:
            self.pos.x = 0 - self.rect.width


class Score:
    def __init__(self):
        self.font = pygame.font.SysFont('verdana', 50, True)

    def draw(self):
        if not ship.started:
            text = f'PYSTEROIDS'
            text_surf = self.font.render(text, False, 'chartreuse')
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
            screen.blit(text_surf, text_rect)
            text = f'press ENTER to play...'
            text_surf = self.font.render(text, True, 'chartreuse')
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surf, text_rect)
            meteor_group.empty()
        if debug:
            text = f'time: {ship.time_now} ships: {len(ship_group)} meteors: {len(meteor_group)} lasers: {len(laser_group)}'
            text_surf = self.font.render(text, True, 'chartreuse')
            text_rect = text_surf.get_rect(topleft=(0, 0))
            screen.blit(text_surf, text_rect)
        if not ship.win and ship.started and ship.destroyed:
            text = f'GAME OVER!'
            text_surf = self.font.render(text, True, 'chartreuse')
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surf, text_rect)
            meteor_group.empty()

        elif ship.win:
            text = f'YOU WIN! YOUR SCORE {ship.score}'
            text_surf = self.font.render(text, True, 'chartreuse')
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surf, text_rect)


class Explosion:
    def __init__(self, time, pos):
        self.pos = pos
        self.time = time
        self.particles = []
        screen.fill(shimmering_color())

    def update(self):
        self.particles.clear()
        for _ in range(2):
            self.particles.append((randint(-60, 60), randint(-60, 60), randint(20,80))) # x,y, size
        if pygame.time.get_ticks() - self.time < 200:
            for particle in self.particles:
                # rect = pygame.rect.Rect((self.pos[0] + particle[0], self.pos[1] + particle[1]), (80, 80))
                # pygame.draw.ellipse(screen, shimmering_color(), rect)

                pygame.gfxdraw.filled_circle(screen, round(self.pos[0] + particle[0]), round(self.pos[1] + particle[1]),
                                             particle[2], shimmering_color())


        else:
            explosion_group.remove(self)
            del self


def shimmering_color(stars=False):
    if not stars:
        color = choice([(127, 255, 0), (118, 238, 0), (102, 205, 0), (69, 139, 0)])
    else:
        color = choice([(102, 205, 0), (69, 139, 0)])
    return color


def draw_stars():
    for star in stars:
        # size = randint(1, 3)
        size = 1
        pygame.gfxdraw.filled_circle(screen,round(star[0] - ship.offset.x), round(star[1] - ship.offset.y),size, shimmering_color(stars=True))


# inits and general setup
pygame.init()
clock = pygame.time.Clock()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# show debug information?
debug = False

# sprite groups
ship_group = pygame.sprite.GroupSingle()
meteor_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()

explosion_group = []

# initialising sprite groups
ship = Ship(ship_group)
score = Score()

# meteor spawn timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 3000)

# generate random stars for background
stars = []
for _ in range(1400):
    x = randint(-2000, 2000)
    y = randint(-2000, 2000)
    stars.append((x, y))

while True:
    # delta time and other stuff
    keys = pygame.key.get_pressed()
    screen.fill((0, 0, 0))
    pygame.display.set_caption(f'PySteroids')
    dt = clock.tick(60) / 1000
    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == meteor_timer:  # Meteor spawns
            if not ship.win and ship.started:
                Meteor.spawn()
            else:
                meteor_group.empty()
    # sprite group updates
    ship_group.update()
    meteor_group.update()
    laser_group.update()

    if debug:
        rect = pygame.surface.Surface(ship.rect.size)
        rect.fill((255, 255, 255))
        screen.blit(rect, ship.rect)
        for sprite in meteor_group:
            rect = pygame.surface.Surface(sprite.rect.size)
            rect.fill((255, 255, 255))
            screen.blit(rect, sprite.rect)

    # sprite group draws
    if ship.started and not ship.win:
        draw_stars()
        laser_group.draw(screen)
        ship_group.draw(screen)
        meteor_group.draw(screen)
    score.draw()

    # explosions
    for explosion in explosion_group:
        explosion.update()

    # final draw
    pygame.display.update()
