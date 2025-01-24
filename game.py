import sys

from objects.ball import Ball
from objects.block import Block
from objects.paddle import Paddle
import pygame

import sqlite3

from objects.powerups._powerup import Powerup
from objects.powerups.powerups import PowerupCatch, PowerupSlow, PowerupLife


class Game:
    BACKGROUND = pygame.Color('black')

    def __init__(self, screen: pygame.surface.Surface, level: str, fps: int = 120, lives: int = 3):
        self.FPS: int = fps
        self.screen = screen
        self.lives: int = lives
        self.total_score: int = 0
        self.game_over_flag: bool = False

        self.win: bool = False

        self._blocks: list[Block] = []
        self._get_blocks(screen, f"levels/{level}")

        self.paddle = Paddle(screen)
        self.ball = Ball(screen, self.paddle, self._blocks)

        self.all_sprites = pygame.sprite.Group()

        for sprite in (self.ball, self.paddle, *self._blocks):
            self.all_sprites.add(sprite)

    def _get_blocks(self, screen: pygame.surface.Surface, db_name: str):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        query = """SELECT * FROM blocks"""
        blocks_data = cursor.execute(query).fetchall()

        for color, x, y in blocks_data:
            self._blocks.append(Block(screen, color, x, y))

        cursor.close()

    def _handle_collide_with_powerups(self):
        for sprite in self.all_sprites:
            if self.paddle.rect.colliderect(sprite.rect) and isinstance(sprite, Powerup):
                if isinstance(sprite, PowerupCatch):
                    self.ball.switch_catching()
                    self.all_sprites.remove(sprite)

                if isinstance(sprite, PowerupSlow):
                    self.ball.slow()

                if isinstance(sprite, PowerupLife):
                    self.lives += 1

                sprite.kill()



    def _update_game(self) -> None:
        self._handle_collide_with_powerups()

        self.screen.fill(self.BACKGROUND)
        self.all_sprites.draw(self.screen)

        for sprite in self.all_sprites:
            new_sprite: pygame.sprite.Sprite | None = sprite.update()

            if new_sprite:
                self.all_sprites.add(new_sprite)

        if not self._blocks:
            self.win = True
            self.game_over_flag = True

        if self.ball.rect.y >= self.screen.get_height():
            self.lives -= 1

            if not self.lives:
                self.game_over_flag = True

            else:
                self.ball.reset()

    def run(self) -> None:
        clock = pygame.time.Clock()

        stop_flag = False

        while not stop_flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

            if not self.game_over_flag:
                self._update_game()

            else:
                self.screen.fill(self.BACKGROUND)
                return None

            pygame.display.flip()
            clock.tick(self.FPS)

    @property
    def is_win(self) -> bool:
        return self.win

    @staticmethod
    def terminate():
        pygame.quit()
        sys.exit()
