import sys
import pygame
from bullet import Bullet
from alien import Alien
from boss import Boss
from game_stats import GameStats
from time import sleep

def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets):
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
            break

def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    if stats.ships_left > 0:
        stats.ships_left -= 1
        sb.prep_ships()
        aliens.empty()
        bullets.empty()
        create_fleet(ai_settings, screen, ship, aliens, stats)
        ship.center_ship()
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_fleet_edges(ai_settings, aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
    
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)

def get_number_rows(ai_settings, ship_height, alien_height):
    available_space_y = (ai_settings.screen_height - 
                         (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def get_number_aliens_x(ai_settings, alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens, stats):
    aliens.empty()
    
    if stats.level % 3 == 0:  
        boss = Boss(ai_settings, screen)
        boss.rect.centerx = screen.get_rect().centerx
        boss.rect.top = 100  
        boss.x = float(boss.rect.x)
        aliens.add(boss)
    else:
        alien = Alien(ai_settings, screen)
        number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
        number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
        
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                create_alien(ai_settings, screen, aliens, alien_number, row_number)

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    
    ship.blitme()
    
    
    for alien in aliens.sprites():
        alien.blitme()
        if isinstance(alien, Boss):
            health_ratio = alien.current_health / alien.max_health
            health_bar_length = alien.health_bar_length
            health_bar_height = alien.health_bar_height
            
            pygame.draw.rect(screen, alien.health_bar_background, 
                           (alien.rect.x, alien.rect.y - 20, 
                            health_bar_length, health_bar_height))
            
            pygame.draw.rect(screen, alien.health_bar_color, 
                           (alien.rect.x, alien.rect.y - 20, 
                            health_bar_length * health_ratio, health_bar_height))
    
    sb.show_score()
    
    if not stats.game_active:
        play_button.draw_button()
    
    pygame.display.flip()

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()

def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, 
                            ship, aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, sb, play_button, ship, 
                     aliens, bullets, mouse_x, mouse_y):
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()
        stats.reset_stats()
        stats.game_active = True
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()
        aliens.empty()
        bullets.empty()
        create_fleet(ai_settings, screen, ship, aliens, stats)
        ship.center_ship()
        pygame.mouse.set_visible(False)

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    bullets.update()
    
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    
    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)

def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, False)
    
    if collisions:
        for alien_list in collisions.values():
            for alien in alien_list:
                if isinstance(alien, Boss):
                    if alien.hit():
                        stats.score += ai_settings.boss_points
                        sb.prep_score()
                        check_high_score(stats, sb)
                        aliens.remove(alien)
                        bullets.empty()
                        stats.level += 1
                        sb.prep_level()
                        create_fleet(ai_settings, screen, ship, aliens, stats)
                else:
                    stats.score += ai_settings.alien_points
                    aliens.remove(alien)
                    sb.prep_score()
                    check_high_score(stats, sb)
    
    if len(aliens) == 0 and stats.game_active:
        bullets.empty()
        ai_settings.increase_speed()
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings, screen, ship, aliens, stats)

def check_high_score(stats, sb):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()