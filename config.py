import pygame
import re

# --- Inicialização do Pygame ---
pygame.init()

# --- Cores (RGB) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
DARK_BLUE = (25, 25, 112)  # Cor de fundo principal
GREEN_SUCCESS = (34, 139, 34)
RED_CRITICAL = (178, 34, 34)
YELLOW_ALERT = (255, 215, 0)
BLUE_INFO = (0, 191, 255)
PURPLE_ACTION = (128, 0, 128)
ORANGE_WARNING = (255, 140, 0)
INPUT_BOX_ACTIVE_COLOR = (255, 255, 255)  # Branco quando ativo
INPUT_BOX_INACTIVE_COLOR = (200, 200, 200)  # Cinza claro quando inativo
TEXT_COLOR = (255, 255, 255)  # Cor do texto padrão
DISABLED_COLOR = (100, 100, 100)  # Cor para botoes desabilitados
DISABLED_HOVER_COLOR = (120, 120, 120)

# --- Dimensões da tela (HD - 16:9) ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# A criação do SCREEN (tela) em si será feita no main_game.py,
# mas as dimensões são definidas aqui.
# SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Comentado, pois a instância da tela será única no main_game
# pygame.display.set_caption("Presidente do Banco Central") # O caption também pode ser definido no main_game

# --- Fontes (usaremos fontes padrão do Pygame ou do sistema) ---
# É importante que pygame.init() tenha sido chamado antes de pygame.font.Font()
FONT_VERY_SMALL = pygame.font.Font(None, 18) # Ajustado para melhor leitura em tela maior
FONT_SMALL = pygame.font.Font(None, 22)      # Ajustado
FONT_MEDIUM = pygame.font.Font(None, 28)     # Ajustado
FONT_LARGE = pygame.font.Font(None, 36)      # Ajustado
FONT_TITLE = pygame.font.Font(None, 48)      # Ajustado

# --- Regex para remover códigos de cor do colorama ---
COLOR_CODE_REGEX = re.compile(r'\x1b\[[0-9;]*m')

def clean_color_codes(text):
    """Remove códigos de formatação de cor ANSI (colorama) de uma string."""
    return COLOR_CODE_REGEX.sub('', text)