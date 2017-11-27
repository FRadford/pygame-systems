import math
from random import gauss, randint

import pygame


# decorator function to check collisions on sprites
def basic_movement(func):
    def wrapper(self, dx, dy, colliders):
        self.rect.x += dx  # add change in x to x position
        self.rect.y += dy  # add change in y to y position

        func(self, dx, dy, colliders)  # call wrapped function

        for other in colliders:
            if self is other:
                pass
            elif self.check_collision(other):  # check if collision is happening
                # Check each axis and correct positioning on that axis, effectively blocking objects from moving into
                # or passing through one another
                if dx > 0:
                    self.rect.right = other.rect.left  # if colliding with the left side of an object move out
                elif dx < 0:
                    self.rect.left = other.rect.right  # if colliding with the right side of an object move out
                if dy > 0:
                    self.rect.bottom = other.rect.top  # if colliding with the top side of an object move out
                elif dy < 0:
                    self.rect.top = other.rect.bottom  # if colliding with the bottom side of an object move out

    return wrapper


def gaussian(mu, inverse_scale):
    # return a random integer from a gaussian distribution with mean mu and standard deviation mu / inverse_scale
    return int(gauss(mu, round(mu / inverse_scale)))


def clamp(n, minimum, maximum):
    # clamp any number n between minimum and maximum values
    return max(minimum, min(n, maximum))


def load_sprites(sprite_paths, scale):
    for name, path in sprite_paths.items():
        sprite_paths[name] = pygame.image.load(path).convert_alpha()
        sprite_paths[name] = pygame.transform.scale(sprite_paths[name],
                                                    [int(x * scale) for x in sprite_paths[name].get_size()])
    return sprite_paths


class StaticSprite(pygame.sprite.Sprite):
    """
    Basic sprite class for static objects

    Adds automatic image loading from files
    """

    def __init__(self, x, y, sprite_paths=None, scale=1.0):
        super(StaticSprite, self).__init__()

        if sprite_paths:
            self.sprites = load_sprites(sprite_paths, scale)
            self.sprites["no_rotation"] = self.sprites["base"]
            self.image = self.sprites["base"]
            self.rect = pygame.Rect((x, y), self.image.get_size())
        else:
            self.rect = pygame.Rect((x, y), (8, 8))


class DynamicSprite(StaticSprite):
    """
    Basic sprite class meant to move

    Adds movement with collision checking and rotation
    """

    def __init__(self, x, y, sprite_paths=None, scale=1.0, angle=0.0):
        super(DynamicSprite, self).__init__(x, y, sprite_paths, scale)

        self.angle = angle
        self.speed = 1
        self.x_speed_buffer = 0
        self.y_speed_buffer = 0

    def check_collision(self, other):
        return self.rect.colliderect(other.rect)

    def rotate(self, angle):
        orig_rect = self.rect

        rot_image = pygame.transform.rotate(self.sprites["no_rotation"], angle)

        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center

        self.image = rot_image.subsurface(rot_rect).copy()
        self.angle = angle

    @basic_movement
    def move_single_axis(self, dx, dy, colliders):
        pass

    def move(self, dx, dy, colliders):
        if dx != 0:
            self.x_speed_buffer += dx
            if abs(self.x_speed_buffer) >= 1:
                speed_int = int(self.x_speed_buffer)

                self.move_single_axis(speed_int, 0, colliders)
                self.x_speed_buffer -= speed_int
        if dy != 0:
            self.y_speed_buffer += dy
            if abs(self.y_speed_buffer) >= 1:
                speed_int = int(self.y_speed_buffer)

                self.move_single_axis(0, speed_int, colliders)
                self.y_speed_buffer -= speed_int


class LivingSprite(DynamicSprite):
    """
    Basic sprite class meant for living objects

    Adds health, damage, particles, and death
    """

    def __init__(self, x, y, sprite_paths=None, scale=1.0, angle=0.0):
        super(LivingSprite, self).__init__(x, y, sprite_paths, scale, angle)

        self.health = 1
        self.hurt_bool = False
        self.blood = 50
        self.hurt_blood = round(self.blood / 4)
        self.base_hurt_time = 20
        self.hurt_time = self.base_hurt_time

        self.particles = pygame.sprite.Group()

    def damage(self, value):
        self.health -= value
        num_particles = gaussian(self.hurt_blood, 4)
        self.hurt_bool = True

        try:
            self.sprites["no_rotation"] = self.sprites["hurt"]
            self.rotate(self.angle)
        except KeyError:
            pass

        if self.health <= 0:
            self.remove(self.groups()[0])
            num_particles = gaussian(self.blood, 4)
        self.particles.add(*[Particle(self.rect.x, self.rect.y, (200, 25, 25), 50) for _ in range(num_particles)])

    def update(self, colliders, surface, cam):
        self.particles.update(colliders, surface, cam)
        if self.hurt_bool and self.hurt_time > 0:
            self.hurt_time -= 1
        elif self.hurt_bool:
            self.sprites["no_rotation"] = self.sprites["base"]
            self.rotate(self.angle)
            self.hurt_bool = False
            self.hurt_time = self.base_hurt_time

        if self.health <= 0 and len(self.particles) == 0:
            self.kill()


class Particle(DynamicSprite):
    """
    Basic particle class with automatic random motion, built in timer with random distribution, and colour variation
    """
    def __init__(self, x, y, rgb, duration):
        super(Particle, self).__init__(x, y)

        self.rgb = (clamp(gaussian(rgb[0], 4), 0, 255),
                    clamp(gaussian(rgb[1], 4), 0, 255),
                    clamp(gaussian(rgb[2], 4), 0, 255))
        self.duration = gaussian(duration, 4)
        self.move_gen = self.move_random(10)

    @staticmethod
    def move_random(mag):
        for _ in range(randint(-mag, mag)):
            x = randint(-mag, mag)
            y = randint(-mag, mag)
            yield (x, y)

    def update(self, colliders, surface, cam):
        if self.duration > 0:
            try:
                self.move(*next(self.move_gen), colliders)
            except StopIteration:
                pass
            finally:
                pygame.draw.rect(surface, self.rgb, cam.apply(self))
            self.duration -= 1
        else:
            self.kill()


class Player(LivingSprite):
    """
    Basic player class

    Should be extended to suit the particular genre of game
    """
    def __init__(self, x, y, sprites):
        super(Player, self).__init__(x, y, sprites)

    @staticmethod
    def shake_screen():
        s = -1
        for _ in range(0, 3):
            for x in range(0, 2):
                yield (x * s, x * s)
            for x in range(2, 0):
                yield (x * s, x * s)
            s *= -1

    def rotate_to_mouse(self, center):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        move_vector = (center[0] - mouse_x, center[1] - mouse_y)

        try:
            theta = -math.degrees(math.atan2(move_vector[1], move_vector[0])) + 90
        except ZeroDivisionError:
            theta = 0

        self.rotate(theta)


class Enemy(LivingSprite):
    """
    Placeholder enemy class

    Should be extended to suit the particular genre of game
    """
    def __init__(self, x, y, sprites):
        super(Enemy, self).__init__(x, y, sprites)
