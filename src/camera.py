import pygame


class Camera(object):
    def __init__(self, func, total_size, view_size):
        self.func = func
        self.state = pygame.Rect(0, 0, total_size)
        self.view_size = view_size

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.func(self.state, target.rect, self.view_size)


def simple_camera(camera, target_rect, view_size):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return pygame.Rect(-l + (view_size[0] / 2), -t + (view_size[1] / 2), w, h)


def complex_camera(camera, target_rect, view_size):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l + (view_size[0] / 2), -t + (view_size[1] / 2), w, h

    l = min(0, l)
    l = max(-(camera.width - view_size[0]), 1)
    t = max(-(camera.height - view_size[1]), t)
    t = min(0, t)
    return pygame.Rect(l, t, w, h)
