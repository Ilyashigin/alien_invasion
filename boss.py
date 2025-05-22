import pygame
from alien import Alien

class Boss(Alien):
    def __init__(self, ai_settings, screen):
        super().__init__(ai_settings, screen)
        self.image = pygame.image.load('boss.png')
        self.rect = self.image.get_rect()
        self.max_health = 50
        self.current_health = self.max_health
        self.health_bar_length = 200
        self.health_bar_height = 10
        self.health_bar_color = (255, 0, 0)
        self.health_bar_background = (60, 60, 60)
        
    def blitme(self):
        self.screen.blit(self.image, self.rect)
        
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(self.screen, self.health_bar_background, 
                         (self.rect.x, self.rect.y - 15, 
                          self.health_bar_length, self.health_bar_height))
        pygame.draw.rect(self.screen, self.health_bar_color, 
                         (self.rect.x, self.rect.y - 15, 
                          self.health_bar_length * health_ratio, self.health_bar_height))
        
    def update(self):
        self.x += (self.ai_settings.alien_speed_factor * 1.5 * self.ai_settings.fleet_direction)
        self.rect.x = self.x
        
    def check_edges(self):
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True
            
    def hit(self):
        self.current_health -= 1
        return self.current_health <= 0