import pygame

import pygame.math


class PhysicsMixin(object):
    """
    Simple physics mixin class to be added to any entity that should be affected by physics.
    """

    def __init__(self, *args, **kwargs):
        super(PhysicsMixin, self).__init__(*args, *kwargs)
        self.x_vel = self.y_vel = self.y_vel_i = 0
        self.grav = 10
        self.fall = False
        self.time = None

    def physics_update(self, obstacles):
        """If the player is falling, calculate current y velocity."""
        self.check_falling(obstacles)

        if self.fall:
            time_now = pygame.time.get_ticks()
            if not self.time:
                self.time = time_now
            self.y_vel = self.grav * ((time_now - self.time) / 1000.0) + self.y_vel_i
        else:
            self.time = None
            self.y_vel = self.y_vel_i = 0

    def check_falling(self, obstacles):
        """If player is not contacting the ground, enter fall state."""
        self.rect.move_ip((0, 1))
        collisions = pygame.sprite.spritecollide(self, obstacles, False)
        if self in collisions:
            collisions.remove(self)
        if not pygame.sprite.spritecollideany(self, collisions, pygame.sprite.collide_mask):
            self.fall = True
        self.rect.move_ip((0, -1))
