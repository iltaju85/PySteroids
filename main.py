#############################################
# ASTEROID-style small pygame project v.0.3 #
#   by: Ilkka Jussila                       #
#############################################

# TODO:
# 1. meteor spawn waves
# 2. Highscore (save in a file)

import pygame
import pygame.gfxdraw
from math import pi, cos, sin
from random import randint, uniform, choice


class Ship(pygame.sprite.Sprite):
    """ Player ship class """

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

        self.shoot_sound = pygame.mixer.Sound('audio/laser4.ogg')
        self.nuke_ready_sound = pygame.mixer.Sound('audio/sfx_alarm_loop2.wav')
        self.score_sound = pygame.mixer.Sound('audio/sfx_coin_cluster5.wav')
        self.start_sound = pygame.mixer.Sound('audio/sfx_menu_select4.wav')
        self.score_sound_played = False

        self.nuke_surf = pygame.surface.Surface((50,50))
        self.nuke_rect = self.nuke_surf.get_rect(center=(20, SCREEN_HEIGHT - 20))
        pygame.draw.arc(self.nuke_surf, (127, 255, 0), [0,0,50,50], pi*2/6, pi*2/6*2, 18)
        pygame.draw.arc(self.nuke_surf, (127, 255, 0), [0, 0, 50, 50], pi*2/6*3, pi*2/6*4, 18)
        pygame.draw.arc(self.nuke_surf, (127, 255, 0), [0, 0, 50, 50], pi*2/6*5, pi*2/6*6, 18)
        pygame.draw.circle(self.nuke_surf,(127, 255, 0), (25,25), 3, 0)
        self.nuke_surf.set_colorkey((0,0,0))

        self.nuke_surf_flash = pygame.surface.Surface((50,50))
        pygame.draw.arc(self.nuke_surf_flash, (255, 255, 255), [0,0,50,50], pi*2/6, pi*2/6*2, 18)
        pygame.draw.arc(self.nuke_surf_flash, (255, 255, 255), [0, 0, 50, 50], pi*2/6*3, pi*2/6*4, 18)
        pygame.draw.arc(self.nuke_surf_flash, (255, 255, 255), [0, 0, 50, 50], pi*2/6*5, pi*2/6*6, 18)
        pygame.draw.circle(self.nuke_surf_flash,(255, 255, 255), (25,25), 3, 0)
        self.nuke_surf.set_colorkey((0,0,0))

        self.length = 1
        self.rotation_speed = 250
        self.angle = 0
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 700
        self.force = pygame.math.Vector2(0,0)

        self.offset = pygame.math.Vector2()

        self.started = False
        self.win = False
        self.destroyed = False
        self.destroy_time = 0

        self.can_shoot = True
        self.last_laser_time = 0
        self.time_now = 0
        self.time_ended = 0
        self.score = 0

        self.nuke = False
        self.nuking = True
        self.nuke_detonated_time = 0
        self.icon_flash_time = 0
        self.icon_flashed = False
        self.icon_size = 1
        self.icon_expanding = True

        self.last_kill = 0

        self.last_ufo = 0

    def input(self):
        """ Shoot lasers when space is pressed down """
        if keys[pygame.K_SPACE] and self.can_shoot and not self.destroyed:
            self.shoot_sound.play()
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
            if not self.started or self.destroyed:
                self.spawn_self()

        if keys[pygame.K_LCTRL]:
            if ship.nuke:
                for meteor in meteor_group:
                    Laser(laser_group, (0,0), 0, meteor.rect.center)
                for ufo in ufo_group:
                    Laser(laser_group, (0,0), 0, ufo.rect.center)
                self.nuke = False
                self.nuking = True
                self.nuke_detonated_time = self.time_now

        if self.direction.length() > 0:
            self.direction.scale_to_length(self.length)
        self.pos += self.force * self.speed * dt
        self.offset += self.force * self.speed // 10 * dt

        self.rect.center = round(self.pos.x), round(self.pos.y)

    def spawn_self(self):
        """ Resetting the ship """
        meteor_group.empty()
        laser_group.empty()
        ufo_group.empty()
        self.destroyed = False
        self.started = True
        self.win = False
        self.score = 0
        self.angle = 90
        self.offset.xy = 0,0
        self.direction.xy = 0.000, -0.001
        self.force.xy = 0, -0.1
        self.pos.x = SCREEN_WIDTH // 2
        self.pos.y = SCREEN_HEIGHT // 2 + 100
        self.nuke = False
        self.nuking = False
        self.nuke_detonated_time = self.time_now
        self.icon_flash_time = 0
        self.icon_flashed = False
        self.icon_size = 1
        self.icon_expanding = True
        self.score_sound_played = False
        self.start_sound.play()
        self.last_ufo = self.time_now

    def ufo_timer(self):
        if not self.destroyed:
            if self.time_now - self.last_ufo > 20000:
                Ufo(ufo_group, randint(100,150))
                self.last_ufo = self.time_now

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
        if not ship.destroyed:
            collision = pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask)
            if collision:
                for meteor in collision:
                    explosion = Explosion(pygame.time.get_ticks(), meteor.rect.center)
                    explosion_group.append(explosion)
                explosion = Explosion(pygame.time.get_ticks(), self.rect.center)
                explosion_group.append(explosion)
                meteor_group.empty()
                laser_group.empty()
                for ufo in ufo_group:
                    ufo.sound.stop()
                ufo_group.empty()
                self.destroy_time = self.time_now
                self.destroyed = True

    def ufo_collision(self):
        if not ship.destroyed:
            collisions = pygame.sprite.spritecollide(self, ufo_group, False, pygame.sprite.collide_mask)
            if collisions:
                for ufo in collisions:
                    explosion = Explosion(pygame.time.get_ticks(), ufo.rect.center)
                    explosion_group.append(explosion)
                explosion = Explosion(pygame.time.get_ticks(), self.rect.center)
                explosion_group.append(explosion)
                meteor_group.empty()
                laser_group.empty()
                for ufo in ufo_group:
                    ufo.sound.stop()
                ufo_group.empty()
                self.destroy_time = self.time_now
                self.destroyed = True

    def rotate(self):
        """ Rotate ship graphics """
        rotated_surf = pygame.transform.rotozoom(self.og_surf, self.angle, 1)
        self.image = rotated_surf.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(round(self.pos[0]), round(self.pos[1])))

    def check_nuke(self):
        if not self.destroyed:
            if self.nuking and self.time_now - self.nuke_detonated_time > 350:
                if len(meteor_group) > 0:
                    for meteor in meteor_group:
                        Laser(laser_group, (0, 0), 0, meteor.rect.center)
                    for ufo in ufo_group:
                        Laser(laser_group, (0, 0), 0, ufo.rect.center)
                    self.nuke_detonated_time = self.time_now
                else:
                    laser_group.empty()
                    self.nuking = False

        if not self.nuking and not self.nuke and self.time_now - self.nuke_detonated_time > 40000:
            self.nuke_ready_sound.play()
            self.nuke = True
            self.icon_flashed = False
            self.icon_flash_time = self.time_now

        if self.nuke and not self.icon_flashed:
            if self.time_now - self.icon_flash_time < 1000:
                if self.icon_expanding:
                    self.icon_size += 0.05
                    if self.icon_size > 1.5:
                        self.icon_expanding = False
                else:
                    self.icon_size -= 0.05
                    if self.icon_size < 1:
                        self.icon_expanding = True
            else:
                self.icon_flashed = True

    def draw_nuke_icon(self):
        if self.nuke:
            if not self.icon_flashed:
                scaled_surf = pygame.transform.rotozoom(self.nuke_surf_flash, 0, self.icon_size)
            else:
                scaled_surf = pygame.transform.rotozoom(self.nuke_surf, 0, self.icon_size)
            scaled_surf.set_colorkey((0, 0, 0))
            self.nuke_rect = scaled_surf.get_rect(center=(40, SCREEN_HEIGHT - 40))
            screen.blit(scaled_surf, self.nuke_rect)

    def update(self):
        """ General updates. Will be run every frame """
        self.keyboard_input()
        self.meteor_collision()
        self.ufo_collision()
        self.time_now = pygame.time.get_ticks()
        self.laser_timer()
        self.input()
        self.rotate()
        self.check_borders()
        self.check_nuke()
        self.ufo_timer()


class Laser(pygame.sprite.Sprite):
    """ Laser class """
    def __init__(self, group, direction, angle, pos=None, ufo=False):
        super().__init__(group)
        if ufo:
            laser_surf = pygame.surface.Surface((10, 10))
            pygame.gfxdraw.filled_circle(laser_surf,5,5,5,(255,255,255))
            self.image = laser_surf
        else:
            laser_surf = pygame.surface.Surface((3, 10))
            laser_surf.fill('chartreuse')
            self.image = pygame.transform.rotozoom(laser_surf, angle - 90, 1)
        if not pos:
            self.rect = self.image.get_rect(center=(round(ship.pos[0]), round(ship.pos[1])))
        else:
            self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(direction)
        if ufo:
            self.speed = 400
            self.ufo = True
        else:
            self.speed = 1000
            self.ufo = False

    def meteor_collision(self):
        """ Laser collision with meteors """
        if not ship.destroyed:
            collided = pygame.sprite.spritecollide(self, meteor_group, pygame.sprite.collide_mask)
            if collided:
                for sprite in collided:
                    ship.score += 100
                    ship.last_kill = ship.time_now
                    if sprite.image.get_size()[0] > 115:
                        Meteor(meteor_group, pos=sprite.rect.center, size=(sprite.image.get_size()[0]//2, sprite.image.get_size()[1]//2))
                        Meteor(meteor_group, pos=sprite.rect.center, size=(sprite.image.get_size()[0]//2, sprite.image.get_size()[1]//2))
                    elif sprite.image.get_size()[0] > 80:
                        Meteor(meteor_group, pos=sprite.rect.center, size=(sprite.image.get_size()[0]//2, sprite.image.get_size()[1]//2))
                explosion = Explosion(pygame.time.get_ticks(), self.rect.center)
                explosion_group.append(explosion)
                self.kill()

    def ufo_collision(self):
        if not self.ufo:
            collided = pygame.sprite.spritecollide(self, ufo_group, pygame.sprite.collide_mask)
            if collided:
                for sprite in collided:
                    ship.score += 200
                    ship.last_kill = ship.time_now
                    explosion = Explosion(pygame.time.get_ticks(), self.rect.center)
                    explosion_group.append(explosion)
                    sprite.sound.stop()
                    sprite.kill()
                    self.kill()


    def player_collision(self):
        if self.ufo:
            collided = pygame.sprite.spritecollide(self, ship_group, False, pygame.sprite.collide_mask)
            if collided:
                explosion = Explosion(ship.time_now, self.rect.center)
                explosion_group.append(explosion)
                self.kill()
                laser_group.empty()
                for ufo in ufo_group:
                    ufo.sound.stop()
                ufo_group.empty()
                meteor_group.empty()
                ship.destroy_time = ship.time_now
                ship.destroyed = True

    def recolor(self):
        self.image.fill((0,0,0))
        pygame.gfxdraw.filled_circle(self.image, 5, 5, 4, shimmering_color(ufo_laser=True))

    def update(self):
        """ Laser updates. Will be run every frame """
        if self.ufo:
            self.recolor()
        self.ufo_collision()
        self.meteor_collision()
        self.player_collision()
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
        self.rescaled_image = pygame.transform.scale(surf, rescaled_size)
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
        """ TODO: Spawn waves """
        Meteor(meteor_group)
        # if 20000 > ship.time_now > 15000:
        #     pass
        # if 46000 > ship.time_now > 40000:
        #     Meteor(meteor_group)
        # if 70000 > ship.time_now > 65000:
        #     Meteor(meteor_group)
        # if 105000 > ship.time_now > 100000:
        #     Meteor(meteor_group)
        #     Meteor(meteor_group)

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


class Text:
    """ Text class """
    def __init__(self):
        self.font = pygame.font.SysFont('verdana', 12, False)
        self.expand = True
        self.expand_amount = 0.005
        self.factor = 1
        self.scroll = SCREEN_WIDTH // 2
        self.direction = 3
        self.rotation = -90
        self.y_letter = pygame.transform.rotozoom(ship.image, -90, 1)
        self.y_letter_rect = self.y_letter.get_rect(center=(237,SCREEN_HEIGHT // 2 + 10))
        self.y_letter_pos = self.y_letter_rect.centerx, self.y_letter_rect.centery

    def draw(self):
        """ Draw text """
        draw_stars()

        # animate text
        if self.expand:
            self.factor += self.expand_amount
        else:
            self.factor -= self.expand_amount

        if self.factor >= 1.5:
            self.expand = False
        if self.factor <= 1:
            self.expand = True

        self.scroll += self.direction
        if self.scroll >= SCREEN_WIDTH + 300 or self.scroll <= -300:
            self.direction = -self.direction

        self.rotation += 0.5
        if self.rotation > 360:
            self.rotation = 0

        if not ship.started:

            self.font = pygame.font.SysFont('impact', 20, False)
            text = f'p   STEROIDS'
            text_surf = self.font.render(text, False, 'chartreuse')
            text_surf = pygame.transform.scale_by(text_surf, 5)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surf, text_rect)
            screen.blit(self.y_letter, self.y_letter_rect)

            self.font = pygame.font.SysFont('tahoma', 18, True)
            text = f'press ENTER to play'
            text_surf = self.font.render(text, False, 'white')
            text_surf = pygame.transform.scale_by(text_surf, 1.5 * self.factor)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(text_surf, text_rect)

        elif not ship.destroyed:
            text = f'{ship.score}'
            if ship.time_now - ship.last_kill < 150:
                self.font = pygame.font.SysFont('tahoma', 16, True)
                text_surf = self.font.render(text, False, 'white')
                text_surf = pygame.transform.scale_by(text_surf, 4 * 1.5)
            else:
                self.font = pygame.font.SysFont('courier new', 12, False)
                text_surf = self.font.render(text, False, 'chartreuse')
                text_surf = pygame.transform.scale_by(text_surf, 4)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
            screen.blit(text_surf, text_rect)

        if debug:
            self.font = pygame.font.SysFont('verdana', 16, True)
            text = f'direction: [{ship.direction.x:.2f},{ship.direction.y:.2f}] angle: {ship.angle} force: [{ship.force.x:.2f},{ship.force.y:.2f}]'
            text_surf = self.font.render(text, False, 'white')
            text_surf = pygame.transform.scale_by(text_surf, 2)
            text_rect = text_surf.get_rect(topleft=(0, 0))
            screen.blit(text_surf, text_rect)

        if ship.started and ship.destroyed:
            self.font = pygame.font.SysFont('impact', 20, False, True)
            text = 'Your Score:'
            text_surf = self.font.render(text, False, 'chartreuse')
            text_surf = pygame.transform.scale_by(text_surf, 5)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surf, text_rect)

            if ship.time_now - ship.destroy_time > 1000:
                if not ship.score_sound_played:
                    ship.score_sound.play()
                    ship.score_sound_played = True
                self.font = pygame.font.SysFont('tahoma', 18, True)
                text = f'{ship.score} PTS'
                text_surf = self.font.render(text, False, 'white')
                text_surf = pygame.transform.scale_by(text_surf, self.factor * 3)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
                screen.blit(text_surf, text_rect)

                self.font = pygame.font.SysFont('tahoma', 18, True)
                text = f'press ENTER to try again'
                text_surf = self.font.render(text, False, 'chartreuse')
                text_surf = pygame.transform.scale_by(text_surf, 2)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
                screen.blit(text_surf, text_rect)


class Explosion:
    """ Explosion class """
    def __init__(self, time, pos):
        self.pos = pos
        self.time = time
        self.particles = []
        self.explosion = True
        self.explosion_sound = pygame.mixer.Sound('audio/explosion4.ogg')
        self.explosion_sound.play()

    def update(self):
        self.particles.clear()
        for _ in range(2):
            self.particles.append((randint(-60, 60), randint(-60, 60), randint(20,80)))     # x,y, size
        if pygame.time.get_ticks() - self.time < 200:
            for particle in self.particles:
                pygame.gfxdraw.filled_circle(screen, round(self.pos[0] + particle[0]), round(self.pos[1] + particle[1]),
                                             particle[2], (255, 255, 255))

        else:
            explosion_group.remove(self)
            del self


class Ufo(pygame.sprite.Sprite):
    """ Ufo class """
    def __init__(self, group, speed=None):
        super().__init__(group)
        if speed:
            self.speed = speed
        else:
            self.speed = 100
        self.sound = pygame.mixer.Sound('audio/sfx_vehicle_plainloop.wav')

        # TODO: implement
        self.energy = 2

        self.image = pygame.surface.Surface((100, 50))
        pygame.gfxdraw.filled_circle(self.image,50,25,15, (127, 255, 0))
        pygame.gfxdraw.filled_polygon(self.image, [(0, 37), (25, 25), (75, 25), (100, 37)], (127, 255, 0))
        pygame.gfxdraw.filled_polygon(self.image,[(0,37),(25,50),(37,75),(100,37)],(127, 255, 0))
        self.image.set_colorkey((0,0,0))
        self.mask = pygame.mask.from_surface(self.image)

        spawn_direction = choice(['up','down','left','right'])
        if spawn_direction == 'up':
            random_x_pos = randint(-100, SCREEN_HEIGHT + 100)
            random_y_pos = -100
        if spawn_direction == 'down':
            random_x_pos = randint(-100, SCREEN_HEIGHT + 100)
            random_y_pos = SCREEN_HEIGHT + 100
        if spawn_direction == 'left':
            random_x_pos = -100
            random_y_pos = randint(-100, SCREEN_WIDTH + 100)
        if spawn_direction == 'right':
            random_x_pos = SCREEN_WIDTH + 100
            random_y_pos = randint(-100, SCREEN_WIDTH + 100)
        self.rect = self.image.get_rect(center=(random_x_pos, random_y_pos))
        self.pos = pygame.math.Vector2(self.rect.center)

        self.last_laser_shot = ship.time_now
        self.sound.play(-1)

    def move_towards_player(self):
        self.pos = self.pos.move_towards(ship.pos,self.speed * dt)
        self.rect.center = round(self.pos.x), round(self.pos.y)

    def shoot_laser_at_player(self):
        if ship.time_now - self.last_laser_shot > 1500:
            shooting_direction = pygame.math.Vector2(self.pos)
            shooting_direction.x -= ship.pos[0]
            shooting_direction.y -= ship.pos[1]
            # scale product vector to 1
            if shooting_direction.magnitude():
                shooting_direction.scale_to_length(1)

            shoot_at = pygame.math.Vector2(-shooting_direction)
            Laser(laser_group,shoot_at, 0, self.pos, True)
            self.last_laser_shot = ship.time_now

    def recolor(self):
        pygame.gfxdraw.filled_circle(self.image,50,25,15, shimmering_color(stars=True))
        pygame.gfxdraw.filled_polygon(self.image, [(0, 37), (25, 25), (75, 25), (100, 37)], shimmering_color(stars=True))
        pygame.gfxdraw.filled_polygon(self.image,[(0,37),(25,50),(37,75),(100,37)],shimmering_color(stars=True))

    def update(self):
        self.recolor()
        self.move_towards_player()
        self.shoot_laser_at_player()


def shimmering_color(stars=False, ufo_laser=False):
    """ Generate list of colors that give a shimmering effect to stars """
    if not stars:
        color = choice([(127, 255, 0), (118, 238, 0), (102, 205, 0), (69, 139, 0)])
    else:
        color = choice([(102, 205, 0), (69, 139, 0)])
    if ufo_laser:
        color = choice([(255,255,255), (0,0,0)])
    return color


def draw_stars():
    """ Draw stars function """
    for star in stars:
        # size = randint(1, 3)
        size = 1
        pygame.gfxdraw.filled_circle(screen,round(star[0] - ship.offset.x), round(star[1] - ship.offset.y),size, shimmering_color(stars=True))


# inits and general setup
pygame.init()
clock = pygame.time.Clock()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.mixer_music.load('audio/Pixel River.ogg')
pygame.mixer_music.play(-1,0,5000)

# pixelmode
pixelmode = True

# show debug information?
debug = False

# sprite groups
ship_group = pygame.sprite.GroupSingle()
meteor_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()

explosion_group = []

# initialising sprite groups
ship = Ship(ship_group)
text = Text()

# meteor spawn timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 5000)

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
    if not ship.destroyed:
        ship.score += 1
    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == meteor_timer:  # Meteor spawns
            if ship.started and not ship.destroyed:
                Meteor.spawn()

    # sprite group updates
    ship_group.update()
    meteor_group.update()
    laser_group.update()
    ufo_group.update()

    if debug:
        rect = pygame.surface.Surface(ship.rect.size)
        rect.fill((255, 255, 255))
        screen.blit(rect, ship.rect)
        for sprite in meteor_group:
            rect = pygame.surface.Surface(sprite.rect.size)
            rect.fill((255, 255, 255))
            screen.blit(rect, sprite.rect)

    # nuke effect
    if ship.nuking:
        screen.fill(shimmering_color())

    # sprite group draws
    if ship.started and not ship.destroyed:
        draw_stars()
        laser_group.draw(screen)
        ship_group.draw(screen)
        meteor_group.draw(screen)
        ship.draw_nuke_icon()
        ufo_group.draw(screen)
    text.draw()

    # explosions
    for explosion in explosion_group:
        explosion.update()
        if explosion.explosion:
            screen.fill('white')
            explosion.explosion = False

    # indie mode: make it look pixelated by downscaling and upscaling back up
    if pixelmode:
        pixelated = pygame.transform.scale_by(screen, 0.25)
        pixelated = pygame.transform.scale_by(pixelated, 4)
        screen.blit(pixelated, (0,0))

    # final draw
    pygame.display.update()
