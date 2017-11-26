import pygame


class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print("Could not load spritesheet:", filename)
            raise SystemExit(e)

    def image_at(self, selector):
        rect = pygame.Rect(selector)
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        return image

    def images_at(self, selectors):
        return [self.image_at(selector) for selector in selectors]

    def load_strip(self, selector, image_count):
        return self.images_at([(selector[0] + selector[2] * x, selector[1], selector[2], selector[3])
                               for x in range(image_count)])


class SpriteSheetAnimator(object):
    def __init__(self, filename, rect, count, loop=False, frames=1):
        self.filename = filename
        self.ss = SpriteSheet(self.filename)

        self.images = self.ss.load_strip(rect, count)
        self.loop = loop

        self.max_frames = frames
        self.cur_frame = self.max_frames

        self.i = 0

    def iter(self):
        self.i = 0
        self.cur_frame = self.max_frames
        return self

    def next(self):
        if self.i >= len(self.images):
            if not self.loop:
                raise StopIteration
            else:
                self.i = 0

        image = self.images[self.i]
        self.cur_frame -= 1

        if self.cur_frame == 0:
            self.i += 1
            self.cur_frame = self.max_frames
        return image

    def __add__(self, other):
        self.images.extend(other.images)
        return self

