import math

import systems.entities


class AIMixin(object):
    def move_to_target_simple(self: systems.entities.DynamicSprite, target: systems.entities.StaticSprite,
                              colliders: list):
        dx, dy = self.rect.centerx - target.rect.centerx, self.rect.centery - target.rect.centery
        dist = math.hypot(dx, dy)
        dx, dy = -(dx / dist), -(dy / dist)

        self.move(dx * self.speed, dy * self.speed, colliders)
