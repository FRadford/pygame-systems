import sys

import pygame

import examples.simple.extend.entities as extend
import systems


# TODO: camera shake when player shoots
# TODO: solve movement and then firing issue


def main():
    pygame.init()
    size = width, height = 800, 640
    white = (255, 255, 255)
    screen = pygame.display.set_mode(size)

    colliders = pygame.sprite.Group()
    non_colliders = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    player = extend.Player(width / 2, height / 2,
                           {"base": "examples/simple/assets/player.png",
                            "hurt": "examples/simple/assets/player-hurt.png"})
    main_cam = systems.camera.Camera(systems.camera.simple_camera, (width, height))
    clock = pygame.time.Clock()

    level = [
        "###############################",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "###############################"
    ]

    x, y = 0, 0
    for row in level:
        for col in row:
            if col == ".":
                extend.Floor(x, y).add(non_colliders, all_sprites)
            elif col == "#":
                extend.Wall(x, y).add(colliders, all_sprites)
            x += 32
        y += 32
        x = 0

    player.add(colliders, all_sprites)
    follower = extend.Follower(100, 100, {"base": "examples/simple/assets/enemy.png",
                                          "hurt": "examples/simple/assets/enemy-hurt.png"},
                               player)
    follower.add(colliders, all_sprites)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        keys = pygame.key.get_pressed()
        player.rotate_to_mouse((width / 2, height / 2))
        screen.fill(white)
        if keys[pygame.K_w]:
            player.move(0, -player.speed, colliders)
        if keys[pygame.K_s]:
            player.move(0, player.speed, colliders)
        if keys[pygame.K_a]:
            player.move(-player.speed, 0, colliders)
        if keys[pygame.K_d]:
            player.move(player.speed, 0, colliders)

        if pygame.mouse.get_pressed()[0]:
            shake = player.attack()

        main_cam.update(player)

        for sprite in all_sprites:
            if sprite.health > 0:
                try:
                    for bullet in sprite.bullets:
                        screen.blit(bullet.image, main_cam.apply(bullet))
                except AttributeError:
                    pass
                finally:
                    screen.blit(sprite.image, main_cam.apply(sprite))

        all_sprites.update(colliders, screen, main_cam)

        pygame.display.flip()


if __name__ == "__main__":
    main()
