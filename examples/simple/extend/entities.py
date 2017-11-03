import itertools
import math

import pygame

import systems.entities


class Player(systems.entities.Player):
    def __init__(self, x, y, sprites):
        systems.entities.Player.__init__(self, x, y, sprites)
        self.attack_type = self.shoot
        self.attack_strength = 5
        self.cool_down = 10

        self.bullets = pygame.sprite.Group()

        self.max_health = 100
        self.health = self.max_health
        self.base_hurt_time = 50

    def attack(self):
        if self.cool_down <= 0:
            self.cool_down = 10
            return self.attack_type(self.angle)
        else:
            return itertools.repeat(0, 0)

    def update(self, colliders, surface, cam):
        systems.entities.Player.update(self, colliders, surface, cam)
        for bullet in self.bullets:
            bullet.move(bullet.dx, bullet.dy, colliders)
        if self.cool_down >= 0:
            self.cool_down -= 1

    def shoot(self, angle):
        self.bullets.add(Bullet(self.rect.centerx, self.rect.centery, angle, self.speed + 1, self.attack_strength))
        return self.shake_screen()


class Bullet(systems.entities.Entity):
    def __init__(self, x, y, angle, speed, strength):
        systems.entities.Entity.__init__(self, x, y, {"base": "examples/simple/assets/bullet.png"}, scale=0.5)
        self.speed = speed
        self.strength = strength
        self.dx, self.dy = self.parse_directions(math.radians(-angle - 90), speed)

    @staticmethod
    def parse_directions(angle, speed):
        return [speed * math.cos(angle), speed * math.sin(angle)]

    def move_single_axis(self, dx, dy, colliders):
        self.rect.x += dx
        self.rect.y += dy

        for other in colliders:
            if len(self.groups()) > 0:
                if self is other:
                    pass
                elif self.check_collision(other):
                    if not isinstance(other, Player):
                        self.kill()
                        other.damage(self.strength)


class Follower(systems.entities.Enemy):
    def __init__(self, x, y, sprites, target):
        systems.entities.Enemy.__init__(self, x, y, sprites)
        self.speed = 0.75
        self.attack_strength = 1
        self.target = target
        self.health = 10

    def update(self, colliders, surface, cam):
        systems.entities.Enemy.update(self, colliders, surface, cam)
        self.move_towards(self.target, colliders)

    def move_towards(self, target, colliders):
        dx, dy = self.rect.centerx - target.rect.centerx, self.rect.centery - target.rect.centery
        dist = math.hypot(dx, dy)
        dx, dy = -(dx / dist), -(dy / dist)

        self.move(dx * self.speed, dy * self.speed, colliders)

    @systems.entities.basic_movement
    def move_single_axis(self, dx, dy, colliders):
        for other in colliders:
            if self is other:
                pass
            elif self.check_collision(other):
                if other is self.target:
                    self.target.damage(self.attack_strength)


class Floor(systems.entities.Entity):
    def __init__(self, x, y):
        systems.entities.Entity.__init__(self, x, y, {"base": "examples/simple/assets/floor.png"})


class Wall(systems.entities.Entity):
    def __init__(self, x, y):
        systems.entities.Entity.__init__(self, x, y, {"base": "examples/simple/assets/wall.png"}, scale=2)

    def damage(self, value):
        pass
