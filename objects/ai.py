import math

from objects.entities import DynamicSprite, StaticSprite


class AIMixin(object):
    """
    Basic AI mixin class that implements (or will implement) a variety of ai behaviours.
    """

    def move_to_target_simple(self: DynamicSprite, target: StaticSprite,
                              colliders):
        """Moves the entity one step closer to the targeted object, ignoring obstacles."""
        dx, dy = self.rect.centerx - target.rect.centerx, self.rect.centery - target.rect.centery
        dist = math.hypot(dx, dy)
        dx, dy = -(dx / dist), -(dy / dist)

        self.move(dx * self.speed, dy * self.speed, colliders)
