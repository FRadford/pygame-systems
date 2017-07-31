import pygame
import math
from random import gauss, randint


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_paths=None, scale=1.0, angle=0.0):
        super(Entity, self).__init__()

        self.angle = angle
        self.x_speed_buffer = 0
        self.y_speed_buffer = 0

        self.sprites = self.load_sprites(sprite_paths, scale)

        self.health = 0
        self.hurt_bool = False
        self.blood = 50
        self.hurt_blood = round(self.blood / 4)
        self.base_hurt_time = 20
        self.hurt_time = self.base_hurt_time

        if sprite_paths:
            self.sprites["no_rotation"] = self.sprites["base"]
            self.sprites["current"] = self.sprites["base"]
            self.rect = pygame.Rect((x, y), self.sprites["base"].get_size())
        else:
            self.rect = pygame.Rect((x, y), (8, 8))

    @staticmethod
    def gaussian(base, scale):
        return gauss(base, round(base / scale))

    @staticmethod
    def load_sprites(sprite_paths, scale):
        for name, path in sprite_paths.items:
            sprite_paths[name] = pygame.image.load(path).convert_alpha()
            sprite_paths[name] = pygame.transform.scale(sprite_paths[name],
                                                        [int(x * scale) for x in sprite_paths[name].get_size()])
        return sprite_paths

    def check_collision(self, other):
        return self.rect.colliderect(other.rect)

    def rotate(self, angle):
        orig_rect = self.rect

        rot_image = pygame.transform.rotate(self.sprites["no_rotation"], angle)

        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center

        self.sprites["current"] = rot_image.subsurface(rot_rect).copy()
        self.angle = angle

    def move_single_axis(self, dx, dy, sprites):
        self.rect.x += dx
        self.rect.y += dy

        for other in sprites:
            if self == other:
                pass
            elif self.check_collision(other):
                if dx > 0:
                    self.rect.right = other.rect.left
                elif dx < 0:
                    self.rect.left = other.rect.right
                if dy > 0:
                    self.rect.bottom = other.rect.top
                elif dy < 0:
                    self.rect.top = other.rect.bottom

    def move(self, dx, dy, sprites):
        if dx != 0:
            self.x_speed_buffer += dx
            if abs(self.x_speed_buffer) >= 1:
                speed_int = int(self.x_speed_buffer)

                self.move_single_axis(speed_int, 0, sprites)
                self.x_speed_buffer -= speed_int
        if dy != 0:
            self.y_speed_buffer += dy
            if abs(self.y_speed_buffer) >= 1:
                speed_int = int(self.y_speed_buffer)

                self.move_single_axis(0, speed_int, sprites)
                self.y_speed_buffer -= speed_int

    def damage(self, value):
        self.health -= value
        num_particles = self.gaussian(self.hurt_blood, 2)
        self.hurt_bool = True

        self.sprites["no_rotation"] = self.sprites["hurt"]
        self.rotate(self.angle)

        if self.health > 0:
            for _ in range(num_particles):
                yield Particle(self.rect.x, self.rect.y, (200, 25, 25), 20)
        else:
            self.kill()
            num_particles = self.gaussian(self.blood, 2)
            for _ in range(num_particles):
                yield Particle(self.rect.x, self.rect.y, (200, 25, 25), 20)

    def update(self):
        if self.hurt_bool and self.hurt_time > 0:
            self.hurt_time -= 1
        elif self.hurt_bool:
            self.sprites["no_rotation"] = self.sprites["base"]
            self.rotate(self.angle)
            self.hurt_bool = False
            self.hurt_time = self.base_hurt_time


class Particle(Entity):
    def __init__(self, x, y, rgb, duration):
        self.rgb = (self.gaussian(rgb[0], 4), self.gaussian(rgb[1], 4), self.gaussian(rgb[2], 4))
        self.duration = self.gaussian(duration, 2)
        self.move_gen = self.move_random(10)

        Entity.__init__(self, x, y)

    @staticmethod
    def move_random(mag):
        for x in range(randint(-mag, mag)):
            y = randint(-mag, mag)
            yield(x, y)

    def update(self):
        if self.duration > 0:
            self.duration -= 1
        else:
            self.kill()


class Player(Entity):
    def __init__(self, x, y, sprites):
        Entity.__init__(self, x, y, sprites)

    @staticmethod
    def shake_screen():
        s = -1
        for _ in range(0, 3):
            for x in range(0, 2):
                yield (x * s, x * s)
            for x in range(2, 0):
                yield (x * s, x * s)
            s *= -1

    def rotate_to_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        move_vector = (self.rect.centerx - mouse_x, self.rect.centery - mouse_y)

        try:
            theta = -math.degrees(math.atan2(move_vector[1], move_vector[0])) + 90
        except ZeroDivisionError:
            theta = 0

        self.rotate(theta)
