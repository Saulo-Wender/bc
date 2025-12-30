# ui_setup.py

import pygame
from ui_elements import Button
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_LARGE, FONT_MEDIUM, FONT_SMALL,
    GREEN_SUCCESS, RED_CRITICAL, ORANGE_WARNING, BLUE_INFO, PURPLE_ACTION,
    LIGHT_GRAY, GRAY, WHITE, YELLOW_ALERT
)

def create_main_menu_buttons():
    buttons = {}
    button_width = 300
    button_height = 60
    start_y = SCREEN_HEIGHT * 0.4 
    spacing = 80
    buttons["main_menu_start_game"] = Button(
        (SCREEN_WIDTH - button_width) / 2, start_y, button_width, button_height,
        "Iniciar Novo Jogo", FONT_LARGE, GREEN_SUCCESS, (60, 179, 113)
    )
    buttons["main_menu_instructions"] = Button(
        (SCREEN_WIDTH - button_width) / 2, start_y + spacing, button_width, button_height,
        "Instrucoes", FONT_LARGE, BLUE_INFO, (100, 149, 237)
    )
    buttons["main_menu_exit_game"] = Button(
        (SCREEN_WIDTH - button_width) / 2, start_y + 2 * spacing, button_width, button_height,
        "Sair do Jogo", FONT_LARGE, RED_CRITICAL, (220, 20, 60)
    )
    return buttons

def create_game_month_buttons():
    buttons = {}
    action_button_height = 50
    action_button_y = SCREEN_HEIGHT - action_button_height - 20

    back_button_width = 220
    back_button_height = 40
    back_button_x = 20
    back_button_y = SCREEN_HEIGHT - back_button_height - 10
    buttons["month_back_to_main_menu"] = Button(
        back_button_x, back_button_y,
        back_button_width, back_button_height,
        "Voltar ao Menu Principal", FONT_SMALL, LIGHT_GRAY, GRAY
    )

    action_button_width = 190 
    spacing_horizontal = 15
    start_x_actions = back_button_x + back_button_width + 55 

    buttons["month_policy_decisions"] = Button(
        start_x_actions, action_button_y, action_button_width, action_button_height,
        "Decisões Políticas", FONT_MEDIUM, BLUE_INFO, (100, 149, 237)
    )
    buttons["month_reports_analysis"] = Button(
        start_x_actions + (action_button_width + spacing_horizontal), action_button_y,
        action_button_width, action_button_height,
        "Relatórios", FONT_MEDIUM, BLUE_INFO, (100, 149, 237)
    )
    buttons["month_alter_selic"] = Button(
        start_x_actions + (action_button_width + spacing_horizontal) * 2, action_button_y,
        action_button_width, action_button_height,
        "Alterar SELIC", FONT_MEDIUM, PURPLE_ACTION, (153, 50, 204)
    )
    buttons["month_advance_month"] = Button(
        start_x_actions + (action_button_width + spacing_horizontal) * 3, action_button_y,
        action_button_width, action_button_height,
        "AVANÇAR MÊS", FONT_MEDIUM, GREEN_SUCCESS, (60, 179, 113)
    )
    return buttons

# O restante do arquivo é idêntico à versão estável que tínhamos.
def create_instructions_buttons():
    buttons = {}
    button_width = 250
    button_height = 50
    buttons["instructions_back"] = Button(
        (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT - button_height - 30, # Mais para baixo
        button_width, button_height,
        "Voltar ao Menu Principal", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    return buttons

def create_actions_menu_buttons():
    buttons = {}
    button_width_actions = 320 # Um pouco maior para melhor clique
    button_height_actions = 45
    num_buttons = 7 # Comunicado, Discurso, Reunião BC, Flexibilizar, Compulsório, Reunião Ministro, Intervir Câmbio
    total_buttons_height = num_buttons * button_height_actions + (num_buttons - 1) * 10 # 10px de espaçamento
    start_y_actions = (SCREEN_HEIGHT - total_buttons_height - 80) / 2 + 40 # Centraliza e deixa espaço para título e voltar

    buttons_data = [
        ("actions_comunicado", "", BLUE_INFO, (100, 149, 237)),
        ("actions_discurso", "", BLUE_INFO, (100, 149, 237)),
        ("actions_reuniao_bc", "", BLUE_INFO, (100, 149, 237)),
        ("actions_flexibilizar", "", ORANGE_WARNING, (255, 165, 0)),
        ("actions_compulsorio", "", PURPLE_ACTION, (153, 50, 204)),
        ("actions_reuniao_ministro", "", PURPLE_ACTION, (153, 50, 204)),
        ("actions_intervir_cambio", "", YELLOW_ALERT, (218, 165, 32))
    ]

    for i, (key, text, color, hover_color) in enumerate(buttons_data):
        buttons[key] = Button(
            (SCREEN_WIDTH - button_width_actions) / 2, start_y_actions + i * (button_height_actions + 10),
            button_width_actions, button_height_actions,
            text, FONT_MEDIUM, color, hover_color
        )

    buttons["actions_back_to_game"] = Button(
        (SCREEN_WIDTH - button_width_actions) / 2, start_y_actions + num_buttons * (button_height_actions + 10) + 20,
        button_width_actions, button_height_actions,
        "Voltar", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    return buttons

def create_reports_menu_buttons():
    buttons = {}
    button_width_reports = 320
    button_height_reports = 45
    num_buttons = 5 # Status, Notícias, Gráficos, Previsão, Assessores
    total_buttons_height = num_buttons * button_height_reports + (num_buttons - 1) * 10
    start_y_reports = (SCREEN_HEIGHT - total_buttons_height - 80) / 2 + 40

    buttons_data = [
        ("reports_status_bc", "1. Status do BC", BLUE_INFO, (100, 149, 237)),
        ("reports_news_reports", "2. Noticias e Relatorios", BLUE_INFO, (100, 149, 237)),
        ("reports_view_graphs", "3. Ver Graficos", BLUE_INFO, (100, 149, 237)),
        ("reports_forecast_report", "4. Relatorio de Previsao", BLUE_INFO, (100, 149, 237)),
        ("reports_consult_advisors", "5. Consultar Assessores", BLUE_INFO, (100, 149, 237))
    ]

    for i, (key, text, color, hover_color) in enumerate(buttons_data):
        buttons[key] = Button(
            (SCREEN_WIDTH - button_width_reports) / 2, start_y_reports + i * (button_height_reports + 10),
            button_width_reports, button_height_reports,
            text, FONT_MEDIUM, color, hover_color
        )

    buttons["reports_back_to_game"] = Button(
        (SCREEN_WIDTH - button_width_reports) / 2, start_y_reports + num_buttons * (button_height_reports + 10) + 20,
        button_width_reports, button_height_reports,
        "Voltar", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    return buttons

def create_common_back_buttons():
    buttons = {}
    common_back_width = 220
    common_back_height = 45
    common_back_y = SCREEN_HEIGHT - common_back_height - 20

    keys = ["back_from_status", "back_from_news", "back_from_graphs", "back_from_forecast", "back_from_advisors"]
    for key in keys:
        buttons[key] = Button(
            (SCREEN_WIDTH - common_back_width) / 2, common_back_y, common_back_width, common_back_height,
            "Voltar", FONT_MEDIUM, LIGHT_GRAY, GRAY
        )
    return buttons

def create_game_over_buttons():
    buttons = {}
    button_width = 300
    button_height = 60
    buttons["game_over_back_to_main_menu"] = Button(
        (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT - button_height - 50, button_width, button_height,
        "Voltar ao Menu Principal", FONT_LARGE, GREEN_SUCCESS, (60, 179, 113)
    )
    return buttons

def create_selic_input_buttons():
    buttons = {}
    button_width = 200
    button_height = 50
    popup_center_x = SCREEN_WIDTH / 2
    popup_center_y = SCREEN_HEIGHT / 2

    buttons["selic_confirm"] = Button(
        popup_center_x - button_width / 2, popup_center_y + 50, button_width, button_height,
        "Confirmar", FONT_LARGE, GREEN_SUCCESS, (60, 179, 113)
    )
    buttons["selic_cancel"] = Button(
        popup_center_x - button_width / 2, popup_center_y + 120, button_width, button_height,
        "Cancelar", FONT_LARGE, RED_CRITICAL, (220, 20, 60)
    )
    return buttons

def create_selic_warning_buttons():
    buttons = {}
    selic_warn_btn_width = 180
    selic_warn_btn_height = 45
    popup_center_x = SCREEN_WIDTH / 2
    popup_center_y = SCREEN_HEIGHT / 2

    buttons["selic_warning_confirm"] = Button(
        popup_center_x - selic_warn_btn_width - 10, popup_center_y + 60,
        selic_warn_btn_width, selic_warn_btn_height,
        "Prosseguir", FONT_MEDIUM, ORANGE_WARNING, (255, 165, 0)
    )
    buttons["selic_warning_cancel"] = Button(
        popup_center_x + 10, popup_center_y + 60,
        selic_warn_btn_width, selic_warn_btn_height,
        "Cancelar", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    return buttons

def create_tone_selection_buttons():
    buttons = {}
    tone_button_width = 300
    tone_button_height = 50
    start_y = SCREEN_HEIGHT / 2 - (tone_button_height * 4 + 10 * 3) / 2 + 50
    spacing = tone_button_height + 15

    buttons["tone_hawkish"] = Button(
        (SCREEN_WIDTH - tone_button_width) / 2, start_y, tone_button_width, tone_button_height,
        "Hawkish (Contracionista)", FONT_MEDIUM, ORANGE_WARNING, (255, 180, 50)
    )
    buttons["tone_dovish"] = Button(
        (SCREEN_WIDTH - tone_button_width) / 2, start_y + spacing, tone_button_width, tone_button_height,
        "Dovish (Expansionista)", FONT_MEDIUM, BLUE_INFO, (100, 149, 237)
    )
    buttons["tone_neutral"] = Button(
        (SCREEN_WIDTH - tone_button_width) / 2, start_y + 2 * spacing, tone_button_width, tone_button_height,
        "Neutro (Equilibrado)", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    buttons["tone_cancel"] = Button(
        (SCREEN_WIDTH - tone_button_width) / 2, start_y + 3 * spacing + 20, tone_button_width, tone_button_height,
        "Cancelar", FONT_MEDIUM, RED_CRITICAL, (220, 60, 60)
    )
    return buttons

def create_compulsorio_input_buttons():
    buttons = {}
    button_width = 200
    button_height = 50
    popup_center_x = SCREEN_WIDTH / 2
    popup_center_y = SCREEN_HEIGHT / 2

    buttons["compulsorio_confirm"] = Button(
        popup_center_x - button_width / 2, popup_center_y + 50, button_width, button_height,
        "Confirmar", FONT_LARGE, GREEN_SUCCESS, (60, 179, 113)
    )
    buttons["compulsorio_cancel"] = Button(
        popup_center_x - button_width / 2, popup_center_y + 120, button_width, button_height,
        "Cancelar", FONT_LARGE, RED_CRITICAL, (220, 20, 60)
    )
    return buttons

def create_minister_submenu_buttons():
    buttons = {}
    submenu_btn_width = 550 
    submenu_btn_height = 45
    start_y_buttons = SCREEN_HEIGHT * 0.40

    num_main_buttons = 3 
    button_spacing = 15

    buttons_data = [
        ("reuniao_sugerir_corte", "1. Sugerir Corte de Gastos / Austeridade", ORANGE_WARNING, (255, 180, 50)),
        ("reuniao_sugerir_aumento", "2. Sugerir Aumento de Investimentos / Estímulo", BLUE_INFO, (100, 149, 237)),
        ("reuniao_discutir_cenario", "3. Discutir Cenário (Postura Neutra)", LIGHT_GRAY, GRAY)
    ]
    for i, (key, text, color, hover_color) in enumerate(buttons_data):
        buttons[key] = Button(
            (SCREEN_WIDTH - submenu_btn_width) / 2, 
            start_y_buttons + i * (submenu_btn_height + button_spacing),
            submenu_btn_width, submenu_btn_height,
            text, FONT_MEDIUM, color, hover_color
        )
        
    buttons["reuniao_cancelar_pauta"] = Button(
        (SCREEN_WIDTH - submenu_btn_width) / 2, 
        start_y_buttons + num_main_buttons * (submenu_btn_height + button_spacing) + button_spacing * 2,
        submenu_btn_width, submenu_btn_height,
        "4. Cancelar / Voltar", FONT_MEDIUM, RED_CRITICAL, (220, 60, 60)
    )
    return buttons
def create_intervencao_cambial_input_screen_buttons():
    buttons = {}
    btn_width = SCREEN_WIDTH * 0.45
    btn_height = 50
    btn_x_centered = (SCREEN_WIDTH - btn_width) / 2
    
    buttons["intervencao_escolher_vender"] = Button(
        btn_x_centered, SCREEN_HEIGHT * 0.3, btn_width, btn_height,
        "Vender Dólares (Apreciar Real)", FONT_MEDIUM, GREEN_SUCCESS, (60, 179, 113)
    )
    buttons["intervencao_escolher_comprar"] = Button(
        btn_x_centered, SCREEN_HEIGHT * 0.3 + btn_height + 20, btn_width, btn_height,
        "Comprar Dólares (Depreciar Real / Acumular Reservas)", FONT_MEDIUM, RED_CRITICAL, (220, 20, 60)
    )

    confirm_btn_width = 200
    buttons["intervencao_confirmar_montante"] = Button(
        SCREEN_WIDTH / 2 - confirm_btn_width - 10, SCREEN_HEIGHT * 0.65, confirm_btn_width, btn_height,
        "Confirmar Intervenção", FONT_MEDIUM, GREEN_SUCCESS, (60, 179, 113)
    )
    buttons["intervencao_cancelar_input"] = Button(
        SCREEN_WIDTH / 2 + 10, SCREEN_HEIGHT * 0.65, confirm_btn_width, btn_height,
        "Cancelar", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    
    return buttons

def create_forward_guidance_buttons():
    buttons = {}
    btn_width = SCREEN_WIDTH * 0.6
    btn_height = 45
    btn_x = (SCREEN_WIDTH - btn_width) / 2
    
    start_y = SCREEN_HEIGHT * 0.25
    spacing = btn_height + 10

    options = [
        ("guidance_nenhum", "0. Nenhuma orientação futura específica"),
        ("guidance_manter_selic", "1. Sinalizar SELIC estável por 3 meses"),
        ("guidance_inclinar_alta", "2. Sinalizar forte viés de ALTA da SELIC"),
        ("guidance_inclinar_baixa", "3. Sinalizar forte viés de BAIXA da SELIC"),
        ("guidance_fim_ciclo_alta", "4. Sinalizar provável FIM do ciclo de ALTA"),
        ("guidance_fim_ciclo_baixa", "5. Sinalizar provável FIM do ciclo de BAIXA")
    ]

    for i, (key, text) in enumerate(options):
        buttons[key] = Button(
            btn_x, start_y + i * spacing, btn_width, btn_height,
            text, FONT_MEDIUM, BLUE_INFO, (100, 149, 237) 
        )
    
    buttons["guidance_cancelar"] = Button(
        btn_x, start_y + len(options) * spacing + 15, btn_width, btn_height,
        "Cancelar Guidance (Usar apenas Tom)", FONT_MEDIUM, LIGHT_GRAY, GRAY
    )
    return buttons