from math import cos, sin
import pygame
from pygame.locals import *

from config import *
import objects

PLAYER_ACCELERATION_MAGNITUDE = 0.6
PLAYER_WALK_SPEED = 5
PLAYER_RUN_SPEED = 10
PLAYER_DASH_SPEED = 14
FRICTION_MAGNITUDE = 0.4
PLAYER_DASH_COOLDOWN = 2
PLAYER_DASH_DISTANCE = 50

# Player states
PLAYER_IDLE = 0
PLAYER_WALKING = 1
PLAYER_RUNNING = 2
PLAYER_DASHING = 3


class Entity(pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2, group: pygame.sprite.Group) -> None:
        super().__init__(group)
        self.position = position
        self.velocity = pygame.Vector2()
        self.acceleration = pygame.Vector2()

    def applyForce(self, force: pygame.Vector2) -> None:
        self.acceleration += force

    def move(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity

        self.rect = self.image.get_rect(center=self.position)
        self.acceleration *= 0


class Player(Entity):
    def __init__(self, position: pygame.Vector2, group: pygame.sprite.Group) -> None:
        super().__init__(position, group)
        self.group = group
        self.image = pygame.image.load(
            "src/Assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(
            self.image, (50, 50))
        self.rect = self.image.get_rect(center=self.position)

        self.dash_indicator_image = pygame.image.load(
            "src/Assets/dash_indicator_active.png").convert_alpha()
        self.dash_indicator_image = pygame.transform.scale(
            self.dash_indicator_image, (32, 32))

        self.dash_indicator = objects.Sprite(
            self.dash_indicator_image, self.position + pygame.Vector2(50, 0), ui_group)
        self.prev_angle = 0

        self.state = PLAYER_IDLE

        self.current_time = PLAYER_DASH_COOLDOWN * 1000
        self.last_dash = 0

    def move(self) -> None:
        super().move()

        # Velocity constains
        if self.state != PLAYER_DASHING:
            if self.state == PLAYER_WALKING and self.velocity.magnitude() > PLAYER_WALK_SPEED:
                self.velocity = self.velocity.normalize() * PLAYER_WALK_SPEED
            elif self.state == PLAYER_RUNNING and self.velocity.magnitude() > PLAYER_RUN_SPEED:
                self.velocity = self.velocity.normalize() * (PLAYER_RUN_SPEED)

        elif self.velocity.magnitude() > PLAYER_DASH_SPEED:
            self.velocity = self.velocity.normalize() * (PLAYER_DASH_SPEED)

            # Deceleration
        if self.state != PLAYER_WALKING and self.state != PLAYER_RUNNING and self.velocity.magnitude() > 0:
            self.applyForce(self.velocity.normalize() * -FRICTION_MAGNITUDE)
        if self.velocity.magnitude() < FRICTION_MAGNITUDE:
            self.velocity *= 0

        self.current_time += clock.get_time()

        if self.state != PLAYER_DASHING or self.velocity.magnitude() < FRICTION_MAGNITUDE:
            self.state = PLAYER_IDLE

    def keyup(self, key):
        if key == K_SPACE:
            self.dash_indicator.kill()
            if self.current_time - self.last_dash >= PLAYER_DASH_COOLDOWN * 1000:
                self.last_dash = self.current_time
                mouse_vector = pygame.Vector2(pygame.mouse.get_pos())
                relative_distance = mouse_vector.distance_to(
                    pygame.Vector2(CENTER))
                print(relative_distance)
                if relative_distance > self.rect.size[0]:
                    relative_vector = (
                        mouse_vector - pygame.Vector2(CENTER)) * 0.2
                    print(mouse_vector, CENTER, relative_vector)

                    if relative_vector.magnitude() > PLAYER_DASH_DISTANCE:
                        relative_vector = relative_vector.normalize() * PLAYER_DASH_DISTANCE

                    self.applyForce(relative_vector)
                    self.state = PLAYER_DASHING

    def handleInput(self):
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            if self.current_time - self.last_dash >= PLAYER_DASH_COOLDOWN * 1000:
                self.dash_indicator_image = pygame.image.load(
                    "src/Assets/dash_indicator_active.png").convert_alpha()
            else:
                self.dash_indicator_image = pygame.image.load(
                    "src/Assets/dash_indicator_inactive.png").convert_alpha()

            self.dash_indicator_image = pygame.transform.scale(
                self.dash_indicator_image, (32, 32))
            mouse_vector = pygame.Vector2(pygame.mouse.get_pos())
            relative_vector = mouse_vector - pygame.Vector2(CENTER)
            relative_distance = relative_vector.magnitude()

            if relative_distance > self.rect.size[0]:
                angle = relative_vector.angle_to(pygame.Vector2(1, 0))
                offset = pygame.Vector2(
                    50 * cos(angle/60), 50 * -sin(angle/60))

                self.dash_indicator.image = pygame.transform.rotozoom(
                    self.dash_indicator_image, angle, 1)
                self.dash_indicator.rect = self.dash_indicator.image.get_rect(
                    center=self.position + offset)
                self.dash_indicator.add(self.group)

                self.prev_angle = angle

        if keys[K_LCTRL]:
            self.state = PLAYER_RUNNING

        if keys[K_UP] or keys[K_w] and self.state != PLAYER_DASHING:
            if self.state != PLAYER_RUNNING:
                self.state = PLAYER_WALKING
            self.applyForce(pygame.Vector2(
                0, -PLAYER_ACCELERATION_MAGNITUDE))

        if keys[K_DOWN] or keys[K_s] and self.state != PLAYER_DASHING:
            if self.state != PLAYER_RUNNING:
                self.state = PLAYER_WALKING
            self.applyForce(pygame.Vector2(
                0, PLAYER_ACCELERATION_MAGNITUDE))

        if keys[K_LEFT] or keys[K_a] and self.state != PLAYER_DASHING:
            if self.state != PLAYER_RUNNING:
                self.state = PLAYER_WALKING
            self.applyForce(
                pygame.Vector2(-PLAYER_ACCELERATION_MAGNITUDE, 0))

        if keys[K_RIGHT] or keys[K_d] and self.state != PLAYER_DASHING:
            if self.state != PLAYER_RUNNING:
                self.state = PLAYER_WALKING
            self.applyForce(pygame.Vector2(
                PLAYER_ACCELERATION_MAGNITUDE, 0))
