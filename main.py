import pygame
import sys
import random

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


class Pipe:
    def __init__(self):
        self.x = 450
        self.y = random.randint(150, 700)

    def draw(self):
        screen.blit(img_pipe, (self.x, self.y))
        screen.blit(pygame.transform.flip(
            img_pipe, False, True), (self.x, self.y - pipe_gap - img_pipe.get_height()))

    def move(self):
        self.x -= pipe_speed


while True:
    screen.blit(background, (0, 0))
    if len(pipe_list) < 1:
        pipe_list.append(Pipe())
    for pipe in pipe_list:
        pipe.draw()
        pipe.move()
        if pipe.x < -100:
            pipe_list.remove(pipe)

    for event in pygame.event.get():  # event handling
        if event.type == pygame.QUIT:
            sys.exit()
    pygame.display.update()
    clock.tick(60)
