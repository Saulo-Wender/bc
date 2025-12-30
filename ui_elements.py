# ui_elements.py
import pygame
from config import WHITE, BLACK, INPUT_BOX_ACTIVE_COLOR, INPUT_BOX_INACTIVE_COLOR, DISABLED_COLOR, DISABLED_HOVER_COLOR, LIGHT_GRAY

# Classe Button (permanece como na última versão que você tem)
class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_enabled = True

    def draw(self, screen):
        current_color = self.color
        current_text_color = self.text_color
        if not self.is_enabled:
            current_color = DISABLED_COLOR
            if self.is_hovered: current_color = DISABLED_HOVER_COLOR
            current_text_color = LIGHT_GRAY
        elif self.is_hovered:
            current_color = self.hover_color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, current_text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if not self.is_enabled:
            if event.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(event.pos)
            else: self.is_hovered = False
            return False
        if event.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos): return True
        return False

# --- CLASSE TEXTBOX MODIFICADA ---
class TextBox:
    def __init__(self, x, y, width, height, font, initial_text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = INPUT_BOX_INACTIVE_COLOR
        self.text = initial_text
        self.font = font
        self.active = False
        self.text_surface = None 
        self.update_surface() 

        self.cursor_visible = True
        self.cursor_timer = 0

    def update_surface(self):
        render_text_display = self.text
        if not self.text and self.active:
            render_text_display = " " 
        self.text_surface = self.font.render(render_text_display, True, BLACK)
        if not self.text and not self.active:
            self.text_surface = self.font.render("", True, BLACK)

    def handle_event(self, event):
        # Retorna True APENAS se K_RETURN (submissão) for pressionado.
        # Para outras modificações de texto, retorna False (evento tratado internamente).
        # Para eventos não tratados pelo textbox, também retorna False.
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    if not self.active: 
                        self.active = True
                        self.cursor_timer = pygame.time.get_ticks()
                        self.update_surface() 
                else: # Clicou fora
                    if self.active: 
                        self.active = False
                        self.update_surface() 
            return False # Evento de clique não é uma submissão de texto.
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # self.active = False # Opcional: desativar com Enter
                    return True # Sinaliza SUBMISSÃO (Enter)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.update_surface()
                    return False # Evento tratado internamente, não é submissão
                elif event.key == pygame.K_PERIOD or event.key == pygame.K_COMMA:
                    if '.' not in self.text:
                        self.text += '.'
                        self.update_surface()
                    return False # Evento tratado internamente, não é submissão
                elif event.unicode.isdigit(): 
                    self.text += event.unicode
                    self.update_surface()
                    return False # Evento tratado internamente, não é submissão
                # Outras teclas (ex: setas, shift) não são tratadas pelo TextBox para modificar texto
                # e não devem impedir outros processamentos, então retorna False.
                return False # Tecla não modificou o texto E NÃO É SUBMISSÃO
        return False # Evento não foi de interesse para este textbox ou não é submissão

    def draw(self, screen):
        current_box_color = INPUT_BOX_ACTIVE_COLOR if self.active else INPUT_BOX_INACTIVE_COLOR
        pygame.draw.rect(screen, current_box_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5) 

        text_rect_to_blit = self.text_surface.get_rect()
        text_rect_to_blit.centery = self.rect.centery
        box_content_width = self.rect.width - 10 

        if self.text_surface.get_width() > box_content_width:
            text_rect_to_blit.right = self.rect.right - 5
        else:
            text_rect_to_blit.left = self.rect.left + 5
        screen.blit(self.text_surface, text_rect_to_blit)

        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.cursor_timer > 500: 
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = current_time
            if self.cursor_visible:
                cursor_x_offset = self.text_surface.get_width() if self.text or (not self.text and self.text_surface.get_width() > 0) else 0
                if self.text_surface.get_width() >= box_content_width -1 :
                     cursor_x_final = self.rect.right - 5
                else:
                     cursor_x_final = self.rect.left + 5 + cursor_x_offset
                cursor_x_final = min(cursor_x_final, self.rect.right - 5)
                pygame.draw.line(screen, BLACK, (cursor_x_final, self.rect.top + 5), (cursor_x_final, self.rect.bottom - 5), 2)

# Classe Toast (permanece como na última versão que você tem)
class Toast:
    def __init__(self, text, duration_ms, font, text_color, bg_color, 
                 position_y_start, screen_width, 
                 padding=10, border_radius=8, 
                 fade_in_duration_ms=250, fade_out_duration_ms=500):
        self.text = text; self.total_duration_ms = duration_ms; self.font = font
        self.text_color = text_color; self.bg_color = bg_color; self.screen_width = screen_width
        self.padding = padding; self.border_radius = border_radius
        self.fade_in_duration_ms = fade_in_duration_ms; self.fade_out_duration_ms = fade_out_duration_ms
        self.fade_out_start_time = self.total_duration_ms - self.fade_out_duration_ms
        if self.fade_out_start_time < self.fade_in_duration_ms:
            self.fade_out_start_time = self.fade_in_duration_ms 
            self.fade_out_duration_ms = self.total_duration_ms - self.fade_out_start_time
            if self.fade_out_duration_ms <= 0 :
                 self.fade_out_duration_ms = min(250, self.total_duration_ms / 2)
                 self.fade_out_start_time = self.total_duration_ms - self.fade_out_duration_ms
        self.alpha = 0; self.creation_time = pygame.time.get_ticks(); self.current_y = position_y_start
        self.is_alive = True; self.text_surface_render = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface_render.get_rect()
        self.bg_rect = self.text_rect.inflate(self.padding * 2, self.padding * 2)
        self.bg_rect.width = self.text_surface_render.get_width() + self.padding * 2
        self.bg_rect.height = self.text_surface_render.get_height() + self.padding * 2
        self.bg_rect.centerx = self.screen_width / 2; self.bg_rect.top = self.current_y
        self.text_rect.center = self.bg_rect.center

    def update(self, dt_seconds):
        if not self.is_alive: return False
        current_time = pygame.time.get_ticks(); elapsed_time = current_time - self.creation_time
        if elapsed_time < self.fade_in_duration_ms and self.fade_in_duration_ms > 0:
            self.alpha = (elapsed_time / self.fade_in_duration_ms) * 255
        elif elapsed_time >= self.fade_out_start_time and self.fade_out_duration_ms > 0:
            time_into_fade_out = elapsed_time - self.fade_out_start_time
            self.alpha = 255 - (time_into_fade_out / self.fade_out_duration_ms) * 255
        else: self.alpha = 255
        self.alpha = max(0, min(255, int(self.alpha)))
        if elapsed_time >= self.total_duration_ms: self.is_alive = False
        return self.is_alive

    def draw(self, screen):
        if not self.is_alive or self.alpha == 0: return
        self.bg_rect.top = self.current_y; self.bg_rect.centerx = self.screen_width / 2
        self.text_rect.center = self.bg_rect.center
        toast_surface_to_draw = pygame.Surface(self.bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(toast_surface_to_draw, (*self.bg_color, int(self.alpha)),
                         (0, 0, *self.bg_rect.size), border_radius=self.border_radius)
        temp_text_surface = self.text_surface_render.copy(); temp_text_surface.set_alpha(int(self.alpha))
        text_blit_pos_x = self.padding; text_blit_pos_y = self.padding
        toast_surface_to_draw.blit(temp_text_surface, (text_blit_pos_x, text_blit_pos_y))
        screen.blit(toast_surface_to_draw, self.bg_rect.topleft)