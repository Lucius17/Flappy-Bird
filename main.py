import pipes
import re
import pygame
import sys
import random
import math
import numpy as np

pygame.init()
screen = pygame.display.set_mode((450, 800))

background = pygame.image.load("bg.png")
background = pygame.transform.scale(background, (450, 800))
img_pipe = pygame.image.load("pipe.png")
img_pipe = pygame.transform.scale(img_pipe, (100, 800))
clock = pygame.time.Clock()
pipe_speed = 5
pipe_gap = 200
pipe_list = []
img_bird = pygame.image.load("bird.png")
img_bird = pygame.transform.scale(img_bird, (64, 48))

q_values = np.zeros((800, 800, 2))


epsilon = 0.9
discount_factor = 0.9
learning_rate = 0.9


class Bird:
    def __init__(self):
        self.x = 100
        self.y = 400
        self.fly = False
        self.vel_y = 10
        self.dead = False
        self.hit_box = pygame.Rect(self.x, self.y, 64, 64)
        lenght_up = 0
        lenght_down = 0

    def move(self):
        # gravity
        self.vel_y += 0.5
        if self.vel_y > 5:
            self.vel_y = 5
        if self.y < 800:
            self.y += int(self.vel_y)
        if self.fly and not self.dead:
            self.vel_y = -10
            self.fly = False
        self.hit_box = pygame.Rect(self.x, self.y, 64, 64)
        if len(pipe_list) > 0:
            if self.hit_box.colliderect(pipe_list[0].hit_box_down) or self.hit_box.colliderect(pipe_list[0].hit_box_up):
                self.dead = True

    def draw(self):
        screen.blit(img_bird, (self.x, self.y))
        if len(pipe_list) > 0:
            pygame.draw.line(screen, (255, 0, 0), (self.x + 32,
                                                   self.y + 32), (pipe_list[0].x+100, pipe_list[0].y - pipe_gap), 3)
            pygame.draw.line(screen, (255, 0, 0), (self.x + 32,
                                                   self.y + 32), (pipe_list[0].x+100, pipe_list[0].y), 3)
            dist_up = math.dist((self.x + 32, self.y + 32),
                                (pipe_list[0].x+100, pipe_list[0].y - pipe_gap))
            dist_down = math.dist((self.x + 32, self.y + 32),
                                  (pipe_list[0].x+100, pipe_list[0].y))
            print(([dist_up, dist_down]))


bird = Bird()


class Pipe:
    def __init__(self):
        self.x = 450
        self.y = random.randint(300, 600)
        self.hit_box_down = pygame.Rect(
            self.x, self.y, img_pipe.get_width(), img_pipe.get_height())
        self.hit_box_up = pygame.Rect(
            self.x, self.y - pipe_gap - img_pipe.get_height(), img_pipe.get_width(), img_pipe.get_height())

    def draw(self):
        screen.blit(img_pipe, (self.x, self.y))
        screen.blit(pygame.transform.flip(
            img_pipe, False, True), (self.x, self.y - pipe_gap - img_pipe.get_height()))

        pygame.draw.rect(screen, (250, 0, 0), self.hit_box_down, 2)
        pygame.draw.rect(screen, (250, 0, 0), self.hit_box_up, 2)

    def move(self):
        self.x -= pipe_speed
        self.hit_box_down.move_ip(-pipe_speed, 0)
        self.hit_box_up.move_ip(-pipe_speed, 0)


while True:
    screen.blit(background, (0, 0))

    if len(pipe_list) < 1:
        pipe_list.append(Pipe())
    for pipe in pipe_list:
        pipe.draw()
        pipe.move()
        if pipe.x < -100:
            pipe_list.remove(pipe)
        # bird.dead = True

    for event in pygame.event.get():  # event handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.fly = True
            if event.key == pygame.K_s:
                pass
                # zapis
        if event.type == pygame.QUIT:
            sys.exit()

    bird.move()
    bird.draw()

    print(bird.dead)
    # print(bird.x, bird.y)

    pygame.display.update()
    clock.tick(60)
