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


def get_next_action(x, y, epsilon):
    # if a randomly chosen value between 0 and 1 is less than epsilon,
    # then choose the most promising value from the Q-table for this state.
    if np.random.random() < epsilon:
        return np.argmax(q_values[x, y])
    else:  # choose a random action
        return np.random.randint(2)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = 400
        self.fly = False
        self.vel_y = 10
        self.dead = False
        self.hit_box = pygame.Rect(self.x, self.y, 64, 64)
        self.score = 0
        self.reward = 0
        self.dist_up = 0
        self.dist_down = 0

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
                self.reward = -100
            if self.hit_box.colliderect(pipe_list[0].hit_box_coin):
                pipe_list[0].hit_box_coin = pygame.Rect(0, 0, 0, 0)
                self.score += 1
                self.reward = 1

    def draw(self):
        screen.blit(img_bird, (self.x, self.y))
        if len(pipe_list) > 0:
            pygame.draw.line(screen, (255, 0, 0), (self.x + 32,
                                                   self.y + 32), (pipe_list[0].x+100, pipe_list[0].y - pipe_gap), 3)
            pygame.draw.line(screen, (255, 0, 0), (self.x + 32,
                                                   self.y + 32), (pipe_list[0].x+100, pipe_list[0].y), 3)
            self.dist_up = round(math.dist((self.x + 32, self.y + 32),
                                           (pipe_list[0].x+100, pipe_list[0].y - pipe_gap)))
            self.dist_down = round(math.dist((self.x + 32, self.y + 32),
                                             (pipe_list[0].x+100, pipe_list[0].y)))
            # print(([dist_up, dist_down]))


bird = Bird()
episodes = 1000


class Pipe:
    def __init__(self):
        self.x = 450
        self.y = random.randint(300, 600)
        self.hit_box_down = pygame.Rect(
            self.x, self.y, img_pipe.get_width(), img_pipe.get_height())
        self.hit_box_up = pygame.Rect(
            self.x, self.y - pipe_gap - img_pipe.get_height(), img_pipe.get_width(), img_pipe.get_height())
        self.hit_box_coin = pygame.Rect(
            self.x+49, self.y-pipe_gap, 2, pipe_gap)

    def draw(self):
        screen.blit(img_pipe, (self.x, self.y))
        screen.blit(pygame.transform.flip(
            img_pipe, False, True), (self.x, self.y - pipe_gap - img_pipe.get_height()))

        pygame.draw.rect(screen, (250, 0, 0), self.hit_box_down, 2)
        pygame.draw.rect(screen, (250, 0, 0), self.hit_box_up, 2)
        pygame.draw.rect(screen, (255, 255, 0), self.hit_box_coin, 2)

    def move(self):
        self.x -= pipe_speed
        self.hit_box_down.move_ip(-pipe_speed, 0)
        self.hit_box_up.move_ip(-pipe_speed, 0)
        self.hit_box_coin.move_ip(-pipe_speed, 0)


frames = 0
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
    if not bird.dead:
        action_index = get_next_action(bird.dist_down, bird.dist_up, epsilon)
        if action_index == 1:
            bird.fly = True
            # store the old row and column indexes
        old_row_index, old_column_index = bird.dist_down, bird.dist_up
        bird.move()
        bird.draw()

        # receive the reward for moving to the new state, and calculate the temporal difference
        reward = bird.reward
        bird.reward = 0
        old_q_value = q_values[old_row_index, old_column_index, action_index]
        temporal_difference = reward + \
            (discount_factor *
             np.max(q_values[bird.dist_down, bird.dist_up])) - old_q_value

        # update the Q-value for the previous state and action pair
        new_q_value = old_q_value + (learning_rate * temporal_difference)
        q_values[old_row_index, old_column_index, action_index] = new_q_value
        print(action_index)
    else:
        bird = Bird()
        pipe_list.remove(pipe)
        # print(q_values)
    # bird.draw()
    # print(bird.dead)
    # print(bird.x, bird.y)

    pygame.display.update()
    clock.tick(60)
