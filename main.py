from cgi import print_arguments
from hashlib import new
import pygame
import sys
import random
import math
import numpy as np
import os.path
# np.set_printoptions(threshold=sys.maxsize)

pygame.init()
pygame.font.init()
myFont = pygame.font.SysFont("monospace", 35)

screen = pygame.display.set_mode((450, 800))

background = pygame.image.load("bg.png")
background = pygame.transform.scale(background, (450, 800))
img_pipe = pygame.image.load("pipe.png")
img_pipe = pygame.transform.scale(img_pipe, (100, 800))
clock = pygame.time.Clock()
pipe_speed = 5
pipe_gap = 220
pipe_list = []
img_bird = pygame.image.load("bird.png")
img_bird = pygame.transform.scale(img_bird, (64, 48))
bird_color = pygame.image.load("bird_color.png").convert_alpha()
bird_color = pygame.transform.scale(bird_color, (64, 48))

x, y = 600, 800

bird_amount = 10
epsilon = 0.9
discount_factor = 0.9
learning_rate = 0.6
highscore = 0

# print(type(np.zeros((1, 1))))


def changColor(image, hue):
    color = pygame.Color(0)
    color.hsla = (hue, 100, 50, 100)
    colouredImage = pygame.Surface(image.get_size())
    colouredImage.fill(color)

    finalImage = image.copy()
    finalImage.blit(colouredImage, (0, 0), special_flags=pygame.BLEND_MULT)
    return finalImage


def get_next_action(x, y, lower, epsilon, q_values):
    # if a randomly chosen value between 0 and 1 is less than epsilon,
    # then choose the most promising value from the Q-table for this state.
    # print(type(q_values))
    if np.random.random() < epsilon:
        if np.argmax(q_values[x][y][lower]) == np.argmin(q_values[x][y][lower]):
            np.random.randint(2)
        else:
            np.argmax(q_values[x][y][lower])
    else:  # choose a random action
        return np.random.randint(2)


class Bird:
    def __init__(self, q_values=np.zeros((x, y, 2, 2))):
        self.q_values = q_values
        self.x = 100
        self.y = 400
        self.color = changColor(bird_color, random.randint(1, 360))
        self.fly = False
        self.vel_y = 10
        self.dead = False
        self.hit_box = pygame.Rect(self.x, self.y, 64, 64)
        self.score = 0
        self.reward = 0
        self.horizontal_dif = 0
        self.height_dif = 0
        self.collected = False
        self.lower = 0

    def move(self):

        # gravity
        self.vel_y += 0.5
        if self.vel_y > 5:
            self.vel_y = 5
        if self.y < 800 and self.y > 0:
            self.y += int(self.vel_y)
        else:
            self.dead = True
            self.reward = -100
        if self.fly and not self.dead and self.y > 0:
            self.vel_y = -10
            self.fly = False
        self.hit_box = pygame.Rect(self.x, self.y, 64, 64)
        if len(pipe_list) > 0:
            if self.y-32 > pipe_list[0].y-pipe_gap/2:
                self.lower = 1
            else:
                self.lower = 0
            if self.hit_box.colliderect(pipe_list[0].hit_box_down) or self.hit_box.colliderect(pipe_list[0].hit_box_up):
                self.reward = -1000
                self.dead = True
            if self.hit_box.colliderect(pipe_list[0].hit_box_coin) and not self.collected:
                self.collected = True
                self.reward = 100
                self.score += 1

    def draw(self):
        screen.blit(img_bird, (self.x, self.y))
        screen.blit(self.color, (self.x, self.y))
        if len(pipe_list) > 0:
            # pygame.draw.line(screen, (255, 0, 0), (self.x + 32,
            #                                        self.y + 32), (pipe_list[0].x+100, pipe_list[0].y - pipe_gap), 3)
            # pygame.draw.line(screen, (255, 0, 0), (self.x + 32,
            #                                        self.y + 32), (pipe_list[0].x+100, pipe_list[0].y), 3)
            # self.dist_up = round(math.dist((self.x + 32, self.y + 32),
            #                                (pipe_list[0].x+100, pipe_list[0].y - pipe_gap)))
            # self.dist_down = round(math.dist((self.x + 32, self.y + 32),
            #                                  (pipe_list[0].x+100, pipe_list[0].y)))
            # print(([dist_up, dist_down]))7
            self.horizontal_dif = abs(round(self.x+32 - pipe_list[0].x-100))
            self.height_dif = abs(
                round(self.y+32 - pipe_list[0].y + pipe_gap/2))
            pygame.draw.line(screen, (255, 0, 0), (self.x+32, pipe_list[0].y-pipe_gap/2),
                             (pipe_list[0].x+100, pipe_list[0].y - pipe_gap/2), 3)
            pygame.draw.line(screen, (255, 0, 0), (self.x+32, self.y+32),
                             (self.x+32, pipe_list[0].y-pipe_gap/2), 3)


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


if os.path.exists("model.npy"):
    loaded_arr = np.load('model.npy')
    if np.all(loaded_arr == np.zeros((x, y, 2, 2))):
        print("Model not found")
    # else:
    #     print(loaded_arr)

    bird_list = [Bird(loaded_arr) for i in range(bird_amount)]

else:
    bird_list = [Bird() for i in range(bird_amount)]
# bird_list = [Bird() for i in range(bird_amount)]


dead_birds = []
episodes = 9
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
                bird.horizontal_dif, bird.height_dif, bird.lower, epsilon, bird.q_values)
            if action_index == 1:
                bird.fly = True
                # store the old row and column indexes
            old_horizontal_dif, old_height_dif, old_lower = bird.horizontal_dif, bird.height_dif, bird.lower
            # print(bird.horizontal_dif, bird.height_dif, bird.lower)
            bird.move()
            bird.draw()

            # receive the reward for moving to the new state, and calculate the temporal difference
            reward = bird.reward
            if not bird.dead:
                reward += 1
            # print(bird.height_dif)
            # if reward > 0:
            #     print("Reward: ", reward)

            bird.reward = 0
            old_q_value = bird.q_values[old_horizontal_dif,
                                        old_height_dif, old_lower, action_index]
            # if om == old_q_value:
            #     print("same")
            # else:
            #     print("different")
            temporal_difference = reward + (discount_factor * np.max(
                bird.q_values[bird.horizontal_dif][bird.height_dif][bird.lower])) - old_q_value

            # update the Q-value for the previous state and action pair
            new_q_value = old_q_value + (learning_rate * temporal_difference)

            bird.q_values[old_horizontal_dif][old_height_dif][old_lower][action_index] = new_q_value

            if bird.score > highscore:
                highscore = bird.score
        else:
            # print("still alive")
            # action_index = 0
            # # store the old row and column indexes
            # old_horizontal_dif, old_height_dif, old_lower = bird.horizontal_dif, bird.height_dif, bird.lower
            # bird.move()
            # bird.draw()

            # # receive the reward for moving to the new state, and calculate the temporal difference
            # reward = -100
            # # print(bird.height_dif)

            # bird.reward = 0
            # old_q_value = bird.q_values[old_horizontal_dif,
            #                             old_height_dif, old_lower, action_index]
            # # if om == old_q_value:
            # #     print("same")
            # # else:
            # #     print("different")
            # temporal_difference = reward + \
            #     (discount_factor *
            #      np.max(bird.q_values[bird.horizontal_dif, bird.height_dif, bird.lower])) - old_q_value

            # # update the Q-value for the previous state and action pair
            # new_q_value = old_q_value + (learning_rate * temporal_difference)

            # bird.q_values[old_horizontal_dif][old_height_dif][old_lower][action_index] = round(
            #     new_q_value)
            # if bird.score > highscore:
            #     highscore = bird.score

            if len(bird_list) > 1:
                dead_birds.append(bird.q_values)
                bird_list.remove(bird)
            else:
                episodes += 1
                # super_bird = np.zeros((x, y, 2, 2))
                # for bird in dead_birds:
                #     super_bird = np.add(bird, super_bird)
                # print(super_bird.shape)
                super_bird = bird_list[0].q_values
                if episodes % 10 == 0:
                    np.save('model.npy', super_bird)
                bird_list = [Bird(super_bird)
                             for i in range(bird_amount)]
                pipe_list = [Pipe()]
                dead_birds = []
            # print(q_values)
            # bird.draw()
            # print(bird.dead)
            # print(bird.x, bird.y)
    # print("--------------------------------")
    screen.blit(myFont.render(
        (f'Episodes: {episodes}'), True, (255, 255, 255)), (0, 0))
    screen.blit(myFont.render(
        (f'Highscore: {highscore}'), True, (255, 255, 255)), (0, 30))
    pygame.display.update()
    clock.tick(60000000)
