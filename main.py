import pygame
import sys
import random
import math
import numpy as np
import os.path

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

bird_amount = 70
epsilon = 0.955
discount_factor = 0.9
learning_rate = 0.9


def get_next_action(x, y, epsilon, q_values):
    # if a randomly chosen value between 0 and 1 is less than epsilon,
    # then choose the most promising value from the Q-table for this state.
    if np.random.random() < epsilon:
        return np.argmax(q_values[x, y])
    else:  # choose a random action
        return np.random.randint(2)


class Bird:
    def __init__(self, q_values=np.zeros((820, 820, 2))):
        self.q_values = q_values
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
        self.collected = False

    def move(self):

        # gravity
        self.vel_y += 0.5
        if self.vel_y > 5:
            self.vel_y = 5
        if self.y < 800:
            self.y += int(self.vel_y)
        if self.fly and not self.dead and self.y > 0:
            self.vel_y = -10
            self.fly = False
        self.hit_box = pygame.Rect(self.x, self.y, 64, 64)
        if len(pipe_list) > 0:
            if self.hit_box.colliderect(pipe_list[0].hit_box_down) or self.hit_box.colliderect(pipe_list[0].hit_box_up):
                self.reward = -1000
                self.dead = True
            if self.hit_box.colliderect(pipe_list[0].hit_box_coin) and not self.collected:
                self.collected = True
                self.reward = 15
                self.score += 1

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
            # print(([dist_up, dist_down]))7


class Pipe:
    def __init__(self):
        self.x = 500
        self.y = random.randint(300, 600)
        self.hit_box_down = pygame.Rect(
            self.x, self.y, img_pipe.get_width(), img_pipe.get_height())
        self.hit_box_up = pygame.Rect(
            self.x, self.y - pipe_gap - img_pipe.get_height(), img_pipe.get_width(), img_pipe.get_height())
        self.hit_box_coin = pygame.Rect(
            self.x+100, self.y-pipe_gap, 2, pipe_gap)

    def draw(self):
        screen.blit(img_pipe, (self.x, self.y))
        screen.blit(pygame.transform.flip(
            img_pipe, False, True), (self.x, self.y - pipe_gap - img_pipe.get_height()))

        pygame.draw.rect(screen, (250, 0, 0), self.hit_box_down, 2)
        pygame.draw.rect(screen, (250, 0, 0), self.hit_box_up, 2)
        pygame.draw.rect(screen, (250, 255, 0), self.hit_box_coin, 2)

    def move(self):
        self.x -= pipe_speed
        self.hit_box_down.move_ip(-pipe_speed, 0)
        self.hit_box_up.move_ip(-pipe_speed, 0)
        self.hit_box_coin.move_ip(-pipe_speed, 0)


if os.path.exists("model.txt"):
    loaded_arr = np.loadtxt("model.txt")
    load_original_arr = loaded_arr.reshape(
        loaded_arr.shape[0], loaded_arr.shape[1] // 2, 2)
    bird_list = [Bird(load_original_arr) for i in range(bird_amount)]

else:
    bird_list = [Bird() for i in range(bird_amount)]


episodes = 0
pipe_list.append(Pipe())
while True:
    screen.blit(background, (0, 0))

    for pipe in pipe_list:
        pipe.draw()
        pipe.move()
        if pipe.x < -150:
            for bird in bird_list:
                bird.collected = False
            pipe_list.remove(pipe)
            pipe_list.append(Pipe())

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

    for bird in bird_list:
        if not bird.dead:
            action_index = get_next_action(
                bird.dist_up, bird.dist_down, epsilon, bird.q_values)
            if action_index == 1:
                bird.fly = True
                # store the old row and column indexes
            old_row_index, old_column_index = bird.dist_up, bird.dist_down
            bird.move()
            bird.draw()

            # receive the reward for moving to the new state, and calculate the temporal difference
            reward = bird.reward
            if action_index == 1:
                reward -= 1
            # print(bird.score)
            # print(bird.hit_box_coin)
            bird.reward = 0
            old_q_value = bird.q_values[old_row_index,
                                        old_column_index, action_index]
            temporal_difference = reward + \
                (discount_factor *
                 np.max(bird.q_values[bird.dist_up, bird.dist_down])) - old_q_value

            # update the Q-value for the previous state and action pair
            new_q_value = old_q_value + (learning_rate * temporal_difference)
            bird.q_values[old_row_index, old_column_index,
                          action_index] = new_q_value
            # print(action_index)
        else:
            if len(bird_list) > 1:
                bird_list.remove(bird)
            else:
                episodes += 1
                if episodes % 10 == 0:
                    reshaped = bird_list[0].q_values.reshape(
                        bird_list[0].q_values.shape[0], -1)
                    np.savetxt("model.txt", reshaped)
                bird_list = [Bird(bird_list[0].q_values)
                             for i in range(bird_amount)]
                pipe_list = [Pipe()]
            # print(q_values)
            # bird.draw()
            # print(bird.dead)
            # print(bird.x, bird.y)
    # print("--------------------------------")
    pygame.display.update()
    clock.tick(60)
