# game_screens.py
import pygame

from config import (
    DARK_BLUE, WHITE, BLACK, GRAY, LIGHT_GRAY, YELLOW_ALERT, RED_CRITICAL, GREEN_SUCCESS, BLUE_INFO, ORANGE_WARNING,
    FONT_TITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_VERY_SMALL,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    clean_color_codes
)
from ui_elements import Button
# --- NOVA IMPORTAÇÃO ---
# Importa o dicionário de assessores para usar na tela de consulta.
from events import ASSESSORES

# --- Funções Auxiliares de Desenho (Sem alterações) ---
def draw_text(screen, text, font, color, x, y, align="left"):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "right":
        text_rect.right = x
        text_rect.top = y
    elif align == "topright":
        text_rect.topright = (x,y)
    else: # Padrão é topleft
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)
    return text_rect.height

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line_words = []
    if max_width <= 0: # Evita loop infinito se max_width for inválido
        return [text]

    for word in words:
        test_line_words = current_line_words + [word]
        test_line = ' '.join(test_line_words)
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line_words.append(word)
        else:
            if current_line_words: # Adiciona a linha anterior se ela tiver palavras
                lines.append(' '.join(current_line_words))

            word_width_single, _ = font.size(word)
            if word_width_single > max_width:
                # Quebra a palavra longa
                temp_word_part = ""
                for char_idx, char_val in enumerate(word):
                    test_part = temp_word_part + char_val
                    if font.size(test_part)[0] > max_width:
                        if temp_word_part: # Adiciona a parte que coube
                            lines.append(temp_word_part)
                        temp_word_part = char_val # Começa nova parte
                    else:
                        temp_word_part = test_part

                    if char_idx == len(word) - 1: # Último caractere da palavra original
                        if temp_word_part: lines.append(temp_word_part)
                current_line_words = [] # Palavra foi quebrada e adicionada
            else: # Palavra não é mais longa que a linha, mas não coube com as anteriores
                current_line_words = [word]

    if current_line_words:
        lines.append(' '.join(current_line_words))
    return lines

def get_color_for_metric(game_state, metric_name):
    if metric_name == "inflacao":
        val = game_state.inflacao_atual_mensal * 12; meta = game_state.meta_inflacao_anual; banda = game_state.banda_inflacao_anual
        if abs(val - meta) <= banda: return GREEN_SUCCESS
        elif abs(val - meta) <= banda + 2.0: return YELLOW_ALERT
        else: return RED_CRITICAL
    elif metric_name == "pib":
        val = game_state.pib_crescimento_atual_mensal * 12; meta = game_state.meta_pib_anual; banda = game_state.banda_pib_anual
        if abs(val - meta) <= banda: return GREEN_SUCCESS
        elif val >= (meta - banda - 1.0): return YELLOW_ALERT
        else: return RED_CRITICAL
    elif metric_name == "credibilidade":
        if game_state.credibilidade_bc >= 70: return GREEN_SUCCESS
        elif game_state.credibilidade_bc >= 40: return YELLOW_ALERT
        else: return RED_CRITICAL
    elif metric_name == "pressao":
        if game_state.pressao_politica >= 70: return RED_CRITICAL
        elif game_state.pressao_politica >= 40: return YELLOW_ALERT
        else: return GREEN_SUCCESS
    elif metric_name == "desemprego":
        if game_state.taxa_desemprego_atual <= 7.0: return GREEN_SUCCESS
        elif game_state.taxa_desemprego_atual <= 9.5: return YELLOW_ALERT
        else: return RED_CRITICAL
    elif metric_name == "divida_pib":
        if game_state.divida_publica_pib <= 65: return GREEN_SUCCESS
        elif game_state.divida_publica_pib <= 80: return YELLOW_ALERT
        elif game_state.divida_publica_pib <= 95: return ORANGE_WARNING
        else: return RED_CRITICAL
    elif metric_name == "reservas_internacionais":
        if hasattr(game_state, 'reservas_internacionais'):
            if game_state.reservas_internacionais >= 300: return GREEN_SUCCESS
            elif game_state.reservas_internacionais >= 150: return YELLOW_ALERT
            else: return ORANGE_WARNING
    elif metric_name == "cambio":
        val = game_state.cambio_atual
        if val <= 4.85: return GREEN_SUCCESS
        elif val <= 5.25: return YELLOW_ALERT
        elif val <= 5.70: return ORANGE_WARNING
        else: return RED_CRITICAL
    return WHITE


# --- Funções de Desenho dos Ecrãs ---
# (draw_main_menu, draw_game_month_screen, draw_instructions_screen, draw_event_popup, etc. permanecem iguais à versão anterior)

def draw_main_menu(screen, buttons):
    screen.fill(DARK_BLUE)
    title_y = SCREEN_HEIGHT * 0.2
    draw_text(screen, "Presidente do Banco Central", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    if buttons.get("main_menu_start_game"): buttons["main_menu_start_game"].draw(screen)
    if buttons.get("main_menu_instructions"): buttons["main_menu_instructions"].draw(screen)
    if buttons.get("main_menu_exit_game"): buttons["main_menu_exit_game"].draw(screen)

def draw_game_month_screen(screen, game_state, buttons):
    screen.fill(DARK_BLUE)

    header_height = 50; bottom_bar_height = 65; action_bar_height = 70
    log_panel_width = 320; padding = 10
    cor_fundo_painel_central = (40, 42, 58)
    cor_fundo_log = GRAY

    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, header_height)
    log_panel_rect = pygame.Rect(padding, header_height + padding, log_panel_width, SCREEN_HEIGHT - header_height - bottom_bar_height - action_bar_height - (padding * 3))
    central_panel_x = log_panel_width + (padding * 2); central_panel_width = SCREEN_WIDTH - log_panel_width - (padding * 3)
    central_panel_rect = pygame.Rect(central_panel_x, header_height + padding, central_panel_width, log_panel_rect.height)
    status_bar_rect = pygame.Rect(padding, SCREEN_HEIGHT - action_bar_height - bottom_bar_height - padding, SCREEN_WIDTH - (padding * 2), bottom_bar_height)

    pygame.draw.rect(screen, BLACK, header_rect)
    pygame.draw.rect(screen, cor_fundo_log, log_panel_rect, border_radius=5)
    pygame.draw.rect(screen, cor_fundo_painel_central, central_panel_rect, border_radius=5)
    pygame.draw.rect(screen, (30,30,30), status_bar_rect, border_radius=5)

    # --- 1. Header ---
    header_item_padding_horiz = 30; header_item_padding_vert = (header_height - FONT_MEDIUM.get_height()) / 2
    cred_text = f"Cred: {game_state.credibilidade_bc:.1f}"; cred_color = get_color_for_metric(game_state, "credibilidade")
    draw_text(screen, cred_text, FONT_MEDIUM, cred_color, header_item_padding_horiz, header_item_padding_vert)
    date_text = f"Mês {game_state.mes_atual} / {game_state.ano_atual}"; date_text_width, date_text_height = FONT_LARGE.size(date_text)
    draw_text(screen, date_text, FONT_LARGE, WHITE, SCREEN_WIDTH / 2, header_height / 2, align="center")
    press_text = f"Press: {game_state.pressao_politica:.1f}"; press_color = get_color_for_metric(game_state, "pressao"); press_text_width = FONT_MEDIUM.size(press_text)[0]
    draw_text(screen, press_text, FONT_MEDIUM, press_color, SCREEN_WIDTH - header_item_padding_horiz - press_text_width, header_item_padding_vert)
    if hasattr(game_state, 'influencia_duracao') and game_state.influencia_duracao > 0 and hasattr(game_state, 'governo_postura_fiscal_influencia') and game_state.governo_postura_fiscal_influencia:
        tipo_influencia_txt = game_state.governo_postura_fiscal_influencia.capitalize(); cor_influencia = WHITE
        if game_state.governo_postura_fiscal_influencia == "contracionista": tipo_influencia_txt = "BC->Gov: Contração Fiscal"; cor_influencia = ORANGE_WARNING
        elif game_state.governo_postura_fiscal_influencia == "expansionista": tipo_influencia_txt = "BC->Gov: Expansão Fiscal"; cor_influencia = BLUE_INFO
        influencia_msg = f"{tipo_influencia_txt} ({game_state.influencia_duracao}m)"
        influencia_x_pos = SCREEN_WIDTH / 2 + date_text_width / 2 + 25; influencia_y_pos = header_item_padding_vert + (FONT_MEDIUM.get_height() - FONT_SMALL.get_height()) / 2
        influencia_msg_width = FONT_SMALL.size(influencia_msg)[0]
        if influencia_x_pos + influencia_msg_width < SCREEN_WIDTH - header_item_padding_horiz - press_text_width - 10: draw_text(screen, influencia_msg, FONT_SMALL, cor_influencia, influencia_x_pos, influencia_y_pos)
        else:
            cred_text_width = FONT_MEDIUM.size(cred_text)[0]; influencia_x_pos_alt = header_item_padding_horiz + cred_text_width + 25
            if influencia_x_pos_alt + influencia_msg_width < SCREEN_WIDTH / 2 - date_text_width / 2 - 10: draw_text(screen, influencia_msg, FONT_SMALL, cor_influencia, influencia_x_pos_alt, influencia_y_pos)

    # --- 2. Log de Atividades (Painel Esquerdo) ---
    log_content_margin_x = 10; log_padding_y = 10
    log_line_spacing = 1; log_message_spacing = 2; log_entry_group_spacing = 6
    current_y_draw_log = log_panel_rect.top + log_padding_y
    original_clip = screen.get_clip(); screen.set_clip(log_panel_rect)
    last_drawn_month_year_header = None
    log_items_drawn_count = 0; max_log_lines_total_approx = 40
    for entry_dict in reversed(list(game_state.activity_log)):
        if current_y_draw_log >= log_panel_rect.bottom - log_padding_y or log_items_drawn_count >= max_log_lines_total_approx: break
        current_month_year_label = f"Mês {entry_dict['month']}/{entry_dict['year']}"
        if current_month_year_label != last_drawn_month_year_header:
            if last_drawn_month_year_header is not None: current_y_draw_log += log_entry_group_spacing
            month_header_font = FONT_MEDIUM; header_color = YELLOW_ALERT
            if current_y_draw_log + month_header_font.get_height() > log_panel_rect.bottom - log_padding_y: break
            draw_text(screen, current_month_year_label, month_header_font, header_color, log_panel_rect.left + log_content_margin_x, current_y_draw_log)
            current_y_draw_log += month_header_font.get_height() + log_message_spacing
            last_drawn_month_year_header = current_month_year_label
            log_items_drawn_count +=1
        for msg_detail in reversed(entry_dict["messages"]):
            if current_y_draw_log >= log_panel_rect.bottom - log_padding_y or log_items_drawn_count >= max_log_lines_total_approx: break
            text_to_wrap = clean_color_codes(msg_detail['text']); color = msg_detail['color']; font_to_use = FONT_SMALL
            wrapped_lines = wrap_text(text_to_wrap, font_to_use, log_panel_rect.width - (log_content_margin_x * 2))
            for line_idx, line_text in enumerate(wrapped_lines):
                if current_y_draw_log + font_to_use.get_height() > log_panel_rect.bottom - log_padding_y: current_y_draw_log = log_panel_rect.bottom; break
                draw_text(screen, line_text, font_to_use, color, log_panel_rect.left + log_content_margin_x, current_y_draw_log)
                current_y_draw_log += font_to_use.get_height()
                if line_idx < len(wrapped_lines) -1: current_y_draw_log += log_line_spacing
                log_items_drawn_count +=1
            if current_y_draw_log >= log_panel_rect.bottom - log_padding_y: break
            current_y_draw_log += log_message_spacing
        if current_y_draw_log >= log_panel_rect.bottom - log_padding_y: break
    screen.set_clip(original_clip)

    # --- 3. Painel Central (Notícias/Principal) ---
    pygame.draw.rect(screen, cor_fundo_painel_central, central_panel_rect, border_radius=5)
    news_panel_padding = 15; current_y_news = central_panel_rect.top + news_panel_padding
    draw_text(screen, "Painel de Notícias Relevantes", FONT_LARGE, YELLOW_ALERT, central_panel_rect.centerx, current_y_news + FONT_LARGE.get_height() / 2, align="center")
    current_y_news += FONT_LARGE.get_height() + news_panel_padding + 5
    news_items_to_display = []; max_news_items_to_show = 5
    excluded_keywords_news = ["Tendência mensal:", "Impacto mensal:", " (Alvo:", "Resumo Mes Anterior:"]
    priority_keywords_news = ["Manchete:", "Evento:", "QUEBRA DE GUIDANCE:", "BC QUEBROU", "BC CONTRADISSE", "BC REVERTEU", "SUCESSO: Guidance", "META ATINGIDA:", "CRÍTICO:", "URGENTE:", "ALERTA:", "Novo mandato!", "emitido", "alterada para", "Flexibilizada!", "Reuniao Fechada", "Ministro pareceu", "BC vendeu", "BC comprou", "anuncia", "crise", "escandalo", "boom", "surto", "reforma", "protestos"]
    temp_collected_news = []
    for log_entry_dict in reversed(list(game_state.activity_log)):
        if len(temp_collected_news) >= max_news_items_to_show * 3: break
        for message_detail in reversed(log_entry_dict["messages"]):
            text_original = message_detail["text"]; text_cleaned_for_filter = clean_color_codes(text_original)
            is_excluded_by_keyword = any(keyword.lower() in text_cleaned_for_filter.lower() for keyword in excluded_keywords_news)
            if is_excluded_by_keyword: continue
            is_priority = any(keyword.lower() in text_cleaned_for_filter.lower() for keyword in priority_keywords_news)
            is_too_short_and_not_priority = False
            if not is_priority:
                stripped_text = text_cleaned_for_filter.strip()
                if len(stripped_text.split()) < 5 and len(stripped_text) < 30: is_too_short_and_not_priority = True
            if not is_too_short_and_not_priority:
                news_text_with_date = f"[{log_entry_dict['month']}/{log_entry_dict['year']}] {text_cleaned_for_filter}" # Usar texto limpo para adicionar data
                temp_collected_news.append({"text_to_draw": message_detail['text'], "formatted_text": news_text_with_date, "color": message_detail["color"]}) # Guardar original para cor, formatado para wrap
                if len(temp_collected_news) >= max_news_items_to_show * 3: break
        if len(temp_collected_news) >= max_news_items_to_show * 3: break
    news_items_to_display = temp_collected_news[:max_news_items_to_show]
    font_news_item = FONT_SMALL; line_spacing_news = 2; item_spacing_news = 10 # Ajustado espaçamento
    if news_items_to_display:
        for news_item_data in news_items_to_display:
            if current_y_news >= central_panel_rect.bottom - news_panel_padding: break
            text_for_wrap = clean_color_codes(news_item_data['formatted_text']) # Limpa antes do wrap
            wrapped_lines = wrap_text(text_for_wrap, font_news_item, central_panel_rect.width - (news_panel_padding * 2))
            for line_idx, line in enumerate(wrapped_lines):
                current_x_news = central_panel_rect.left + news_panel_padding
                display_line = line
                if line_idx == 0 and "[Mês" in line : display_line = line # Não adiciona marcador se já tem data
                elif line_idx == 0: display_line = f"• {line}"
                else: current_x_news += 10 # Recuo para continuação
                if current_y_news + font_news_item.get_height() > central_panel_rect.bottom - news_panel_padding: current_y_news = central_panel_rect.bottom; break
                draw_text(screen, display_line, font_news_item, news_item_data["color"], current_x_news, current_y_news)
                current_y_news += font_news_item.get_height()
                if line_idx < len(wrapped_lines) -1 : current_y_news += line_spacing_news
            if current_y_news >= central_panel_rect.bottom - news_panel_padding: break
            current_y_news += item_spacing_news
    else:
         draw_text(screen, "(Nenhuma notícia relevante no momento)", FONT_MEDIUM, LIGHT_GRAY, central_panel_rect.centerx, central_panel_rect.top + (central_panel_rect.height / 3), align="center")

    # --- 4. Barra de Status Inferior ---
    num_status_items = 7; status_item_width = status_bar_rect.width / num_status_items; font_indicador = FONT_MEDIUM
    label_height = font_indicador.get_height(); value_height = font_indicador.get_height(); total_text_height = label_height + value_height + 2
    status_text_y_label = status_bar_rect.centery - total_text_height / 2 + label_height / 2 - 2; status_text_y_value = status_bar_rect.centery + total_text_height / 2 - value_height / 2 + 2
    status_items_data = [("SELIC:", f"{game_state.selic_anual:.2f}%", YELLOW_ALERT, "selic"), ("Inflação:", f"{game_state.inflacao_atual_mensal*12:.2f}%", get_color_for_metric(game_state, "inflacao"), "inflacao"), ("PIB:", f"{game_state.pib_crescimento_atual_mensal*12:.2f}%", get_color_for_metric(game_state, "pib"), "pib"), ("Desemp:", f"{game_state.taxa_desemprego_atual:.1f}%", get_color_for_metric(game_state, "desemprego"), "desemprego")]
    reservas_val = "N/A";
    if hasattr(game_state, 'reservas_internacionais'): reservas_val = f"US$ {game_state.reservas_internacionais:.1f}B"
    status_items_data.append(("Reservas:", reservas_val, get_color_for_metric(game_state, "reservas_internacionais"), "reservas_internacionais"))
    status_items_data.append(("Dív/PIB:", f"{game_state.divida_publica_pib:.1f}%", get_color_for_metric(game_state, "divida_pib"), "divida_pib"))
    status_items_data.append(("Câmbio:", f"R$ {game_state.cambio_atual:.2f}", get_color_for_metric(game_state, "cambio"), "cambio"))
    for i, (label, value, color_value, _) in enumerate(status_items_data):
        center_x = status_bar_rect.left + status_item_width * (i + 0.5)
        draw_text(screen, label, font_indicador, WHITE, center_x, status_text_y_label, align="center")
        draw_text(screen, value, font_indicador, color_value, center_x, status_text_y_value, align="center")

    # --- 5. Botões de Ação e Voltar ---
    if buttons.get("month_policy_decisions"): buttons["month_policy_decisions"].draw(screen)
    if buttons.get("month_reports_analysis"): buttons["month_reports_analysis"].draw(screen)
    if buttons.get("month_alter_selic"): buttons["month_alter_selic"].draw(screen)
    if buttons.get("month_advance_month"): buttons["month_advance_month"].draw(screen)
    if buttons.get("month_back_to_main_menu"): buttons["month_back_to_main_menu"].draw(screen)


def draw_instructions_screen(screen, buttons):
    screen.fill(DARK_BLUE); margin_x = 50; margin_y_top = 50; content_width = SCREEN_WIDTH - (margin_x * 2)
    draw_text(screen, "Instrucoes do Jogo", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, margin_y_top, align="center")
    instructions_text = [
        "Voce e o Presidente do Banco Central do Brasil. Seu objetivo e:",
        "1. Manter a inflacao dentro da meta e promover o crescimento economico sustentavel.",
        "   Consulte o 'Status do BC' para ver as metas atuais e outros indicadores.",
        "2. Gerenciar a credibilidade do BC e lidar com a pressao politica.",
        "3. Monitorar a Dívida Pública/PIB e interagir com a política fiscal do Governo.",
        "4. Usar instrumentos como SELIC, Compulsório e Intervenção Cambial.",
        "", "Suas principais ferramentas sao:",
        "   - Taxa SELIC: Principal instrumento para controlar a inflacao e influenciar a economia.",
        "   - Comunicacao: Comunicados e discursos (com tom Hawkish, Dovish ou Neutro) para gerenciar expectativas e Forward Guidance.",
        "   - Deposito Compulsorio: Para influenciar a liquidez bancaria.",
        "   - Intervenção Cambial: Comprar/Vender dólares para influenciar o câmbio (afeta reservas).",
        "   - Reunioes: Com o Ministro da Fazenda para coordenar politicas ou internas para planejamento.",
        "", "Eventos aleatorios, metas presidenciais e decisoes fiscais do Governo (IA) podem afetar a economia.",
        "Cuidado para nao perder totalmente a credibilidade, deixar a pressao politica se tornar insustentavel ou a dívida pública explodir! Seu mandato tem duracao limitada.",
        "Boa sorte!"
    ]
    current_y = margin_y_top + FONT_TITLE.get_height() + 30; line_spacing_instructions = 5
    for line_idx, line in enumerate(instructions_text):
        font_to_use = FONT_MEDIUM if line.startswith("   -") or line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") else FONT_SMALL
        color_to_use = YELLOW_ALERT if line.startswith("   -") else WHITE
        wrapped_lines = wrap_text(line, font_to_use, content_width)
        for sub_line in wrapped_lines:
            if current_y + font_to_use.get_height() > SCREEN_HEIGHT - 80: break
            current_y += draw_text(screen, sub_line, font_to_use, color_to_use, margin_x, current_y) + line_spacing_instructions
        if line_idx in [4, 7, 12]: current_y += 10
        if current_y > SCREEN_HEIGHT - 80: break
    if buttons.get("instructions_back"): buttons["instructions_back"].draw(screen)

def draw_event_popup(screen, event_popup_data, event_popup_message, event_popup_options, buttons_for_popup_dict):
    overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay_surface.fill((0, 0, 0, 180)); screen.blit(overlay_surface, (0, 0))
    popup_width_ratio = 0.6; popup_height_ratio = 0.5 if not event_popup_options else 0.70
    popup_width = SCREEN_WIDTH * popup_width_ratio; popup_height = SCREEN_HEIGHT * popup_height_ratio
    popup_x = (SCREEN_WIDTH - popup_width) / 2; popup_y = (SCREEN_HEIGHT - popup_height) / 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, DARK_BLUE, popup_rect, border_radius=10); pygame.draw.rect(screen, LIGHT_GRAY, popup_rect, 3, border_radius=10)
    manchete_text_clean = clean_color_codes(event_popup_data["data"]["manchete"])
    lines = wrap_text(manchete_text_clean, FONT_LARGE, popup_width - 40); current_y_text = popup_y + 30
    for line in lines: text_height = draw_text(screen, line, FONT_LARGE, YELLOW_ALERT, popup_rect.centerx, current_y_text, align="center"); current_y_text += text_height + 5
    current_y_text += 20; message_text_clean = clean_color_codes(event_popup_message)
    message_lines = wrap_text(message_text_clean, FONT_MEDIUM, popup_width - 40)
    for line in message_lines: text_height = draw_text(screen, line, FONT_MEDIUM, WHITE, popup_rect.centerx, current_y_text, align="center"); current_y_text += text_height + 3
    buttons_for_popup_dict.clear()
    if event_popup_options:
        current_y_text += 30; draw_text(screen, "Escolha sua resposta:", FONT_MEDIUM, WHITE, popup_x + 30, current_y_text); current_y_text += FONT_MEDIUM.get_height() + 15
        button_width_popup = popup_width - 60; button_height_popup = 50
        for i, option_data in enumerate(event_popup_options):
            btn_y = current_y_text + i * (button_height_popup + 15)
            btn = Button(popup_x + 30, btn_y, button_width_popup, button_height_popup, f"{i + 1}. {option_data['texto']}", FONT_MEDIUM, BLUE_INFO, (100, 149, 237)); buttons_for_popup_dict[f"event_choice_{i}"] = btn; btn.draw(screen)
    else:
        btn_ok_width = 180; btn_ok_height = 50
        btn_ok = Button(popup_rect.centerx - btn_ok_width / 2, popup_y + popup_height - btn_ok_height - 30, btn_ok_width, btn_ok_height, "OK", FONT_LARGE, GREEN_SUCCESS, (60, 179, 113)); buttons_for_popup_dict["event_ok"] = btn_ok; btn_ok.draw(screen)

def draw_alter_selic_screen(screen, selic_input_box, selic_input_message, buttons):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.2; input_label_y = SCREEN_HEIGHT * 0.4
    input_box_y_offset = 30; message_y_offset = 90
    draw_text(screen, "Alterar Taxa SELIC", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    draw_text(screen, "Digite a nova taxa SELIC (% a.a.):", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, input_label_y, align="center")
    selic_input_box.rect.centerx = SCREEN_WIDTH / 2; selic_input_box.rect.top = input_label_y + FONT_LARGE.get_height() + input_box_y_offset; selic_input_box.draw(screen)
    if selic_input_message:
        message_lines = wrap_text(selic_input_message, FONT_MEDIUM, SCREEN_WIDTH * 0.8); current_y_msg = selic_input_box.rect.bottom + message_y_offset /2
        for line in message_lines: text_height = draw_text(screen, line, FONT_MEDIUM, YELLOW_ALERT, SCREEN_WIDTH / 2, current_y_msg, align="center"); current_y_msg += text_height + 3
    if buttons.get("selic_confirm"): buttons["selic_confirm"].draw(screen)
    if buttons.get("selic_cancel"): buttons["selic_cancel"].draw(screen)

def draw_selic_warning_popup(screen, buttons_dict):
    overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay_surface.fill((0, 0, 0, 180)); screen.blit(overlay_surface, (0, 0))
    popup_width_ratio = 0.7; popup_height_ratio = 0.45; popup_width = SCREEN_WIDTH * popup_width_ratio; popup_height = SCREEN_HEIGHT * popup_height_ratio
    popup_x = (SCREEN_WIDTH - popup_width) / 2; popup_y = (SCREEN_HEIGHT - popup_height) / 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, DARK_BLUE, popup_rect, border_radius=10); pygame.draw.rect(screen, LIGHT_GRAY, popup_rect, 3, border_radius=10)
    draw_text(screen, "ATENCAO: Mudancas Multiplas na SELIC!", FONT_LARGE, ORANGE_WARNING, popup_rect.centerx, popup_y + 40, align="center")
    warning_message = "Alterar a taxa SELIC mais de uma vez no mesmo mes pode gerar grande instabilidade e afetar seriamente a credibilidade do BC e a pressao politica. Deseja prosseguir?"
    message_lines = wrap_text(warning_message, FONT_MEDIUM, popup_width - 60); current_y_msg = popup_y + FONT_LARGE.get_height() + 70
    for line in message_lines: text_height = draw_text(screen, line, FONT_MEDIUM, WHITE, popup_rect.centerx, current_y_msg, align="center"); current_y_msg += text_height + 5
    if buttons_dict.get("selic_warning_confirm"): buttons_dict["selic_warning_confirm"].draw(screen)
    if buttons_dict.get("selic_warning_cancel"): buttons_dict["selic_warning_cancel"].draw(screen)

def draw_actions_menu(screen, game_state, buttons):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.1
    draw_text(screen, "Decisoes de Politica Monetaria", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    button_keys = ["actions_comunicado", "actions_discurso", "actions_reuniao_bc", "actions_flexibilizar", "actions_compulsorio", "actions_reuniao_ministro", "actions_intervir_cambio", "actions_back_to_game"]
    for key in button_keys:
        if buttons.get(key): buttons[key].draw(screen) # O texto e enabled state são atualizados no main_game.py

def draw_reports_menu(screen, buttons):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.15
    draw_text(screen, "Relatorios e Analises", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    button_keys = ["reports_status_bc", "reports_news_reports", "reports_view_graphs", "reports_forecast_report", "reports_consult_advisors", "reports_back_to_game"]
    for key in button_keys:
        if buttons.get(key): buttons[key].draw(screen)

# --- FUNÇÃO MODIFICADA ---
def draw_status_bc_screen(screen, game_state, back_button):
    screen.fill(DARK_BLUE)
    margin_x = 40
    margin_y_top = 30
    content_width = SCREEN_WIDTH - (margin_x * 2)

    draw_text(screen, "Status do Banco Central", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, margin_y_top + FONT_TITLE.get_height() / 2, align="center")

    current_y = margin_y_top + FONT_TITLE.get_height() + 25
    col_spacing = 40
    col_width = (content_width - col_spacing) / 2
    col_left_x = margin_x
    col_right_x = col_left_x + col_width + col_spacing
    
    # --- Coluna da Esquerda ---
    y_col_left = current_y
    # Seção de Metas
    draw_text(screen, "Metas do Mandato", FONT_LARGE, YELLOW_ALERT, col_left_x, y_col_left)
    y_col_left += FONT_LARGE.get_height() + 5
    pygame.draw.line(screen, YELLOW_ALERT, (col_left_x, y_col_left), (col_left_x + col_width, y_col_left), 2)
    y_col_left += 10
    
    draw_text(screen, f"Meta Inflação: {game_state.meta_inflacao_anual:.1f}% (Banda: +/- {game_state.banda_inflacao_anual:.2f}%)", FONT_MEDIUM, WHITE, col_left_x, y_col_left)
    y_col_left += FONT_MEDIUM.get_height() + 5
    draw_text(screen, f"Meta PIB: {game_state.meta_pib_anual:.1f}% (Banda: +/- {game_state.banda_pib_anual:.2f}%)", FONT_MEDIUM, WHITE, col_left_x, y_col_left)
    y_col_left += FONT_MEDIUM.get_height() + 20

    # Seção de Indicadores Principais
    draw_text(screen, "Indicadores Macroeconômicos", FONT_LARGE, YELLOW_ALERT, col_left_x, y_col_left)
    y_col_left += FONT_LARGE.get_height() + 5
    pygame.draw.line(screen, YELLOW_ALERT, (col_left_x, y_col_left), (col_left_x + col_width, y_col_left), 2)
    y_col_left += 10

    indicadores_esquerda = [
        ("Inflação Anual:", f"{game_state.inflacao_atual_mensal*12:.2f}%", get_color_for_metric(game_state, "inflacao")),
        ("Cresc. PIB Anual:", f"{game_state.pib_crescimento_atual_mensal*12:.2f}%", get_color_for_metric(game_state, "pib")),
        ("Taxa SELIC Anual:", f"{game_state.selic_anual:.2f}%", WHITE),
        ("Taxa de Desemprego:", f"{game_state.taxa_desemprego_atual:.1f}%", get_color_for_metric(game_state, "desemprego")),
        ("Taxa de Câmbio:", f"R$ {game_state.cambio_atual:.2f}", get_color_for_metric(game_state, "cambio")),
    ]
    for label, value, color in indicadores_esquerda:
        label_width = FONT_MEDIUM.size(label)[0]
        draw_text(screen, label, FONT_MEDIUM, WHITE, col_left_x, y_col_left)
        draw_text(screen, value, FONT_MEDIUM, color, col_left_x + label_width + 10, y_col_left)
        y_col_left += FONT_MEDIUM.get_height() + 5
    y_col_left += 15

    # Seção de Governança
    draw_text(screen, "Governança e Confiança", FONT_LARGE, YELLOW_ALERT, col_left_x, y_col_left)
    y_col_left += FONT_LARGE.get_height() + 5
    pygame.draw.line(screen, YELLOW_ALERT, (col_left_x, y_col_left), (col_left_x + col_width, y_col_left), 2)
    y_col_left += 10
    
    indicadores_gov = [
        ("Credibilidade do BC:", f"{game_state.credibilidade_bc:.1f} / 100", get_color_for_metric(game_state, "credibilidade")),
        ("Pressão Política:", f"{game_state.pressao_politica:.1f} / 100", get_color_for_metric(game_state, "pressao")),
    ]
    for label, value, color in indicadores_gov:
        label_width = FONT_MEDIUM.size(label)[0]
        draw_text(screen, label, FONT_MEDIUM, WHITE, col_left_x, y_col_left)
        draw_text(screen, value, FONT_MEDIUM, color, col_left_x + label_width + 10, y_col_left)
        y_col_left += FONT_MEDIUM.get_height() + 5

    # --- Coluna da Direita ---
    y_col_right = current_y
    # Seção Fiscal
    draw_text(screen, "Cenário Fiscal", FONT_LARGE, YELLOW_ALERT, col_right_x, y_col_right)
    y_col_right += FONT_LARGE.get_height() + 5
    pygame.draw.line(screen, YELLOW_ALERT, (col_right_x, y_col_right), (col_right_x + col_width, y_col_right), 2)
    y_col_right += 10

    indicadores_direita = [
        ("Dívida Pública / PIB:", f"{game_state.divida_publica_pib:.1f}%", get_color_for_metric(game_state, "divida_pib")),
        ("Perfil do Governo:", f"{game_state.tipo_governo}", WHITE),
        ("Postura Fiscal Gov.:", f"{game_state.governo_postura_fiscal.capitalize()}", WHITE),
    ]
    for label, value, color in indicadores_direita:
        label_width = FONT_MEDIUM.size(label)[0]
        draw_text(screen, label, FONT_MEDIUM, WHITE, col_right_x, y_col_right)
        draw_text(screen, value, FONT_MEDIUM, color, col_right_x + label_width + 10, y_col_right)
        y_col_right += FONT_MEDIUM.get_height() + 5
    y_col_right += 15

    # Seção de Condições Monetárias
    draw_text(screen, "Condições Monetárias", FONT_LARGE, YELLOW_ALERT, col_right_x, y_col_right)
    y_col_right += FONT_LARGE.get_height() + 5
    pygame.draw.line(screen, YELLOW_ALERT, (col_right_x, y_col_right), (col_right_x + col_width, y_col_right), 2)
    y_col_right += 10
    
    exp_inf_anual = game_state.expectativa_inflacao_mercado_mensal * 12
    indicadores_monetarios = [
        ("Exp. Inflação Mercado:", f"{exp_inf_anual:.2f}% a.a.", WHITE),
        ("Exp. Juros Longos:", f"{game_state.expectativa_juros_longo_prazo_anual:.2f}% a.a.", WHITE),
        ("Dep. Compulsório:", f"{game_state.taxa_deposito_compulsorio*100:.0f}%", WHITE),
        ("Fator de Liquidez:", f"{game_state.fator_liquidez_bancaria:.2f}", WHITE),
        ("Reservas Internac.:", f"US$ {game_state.reservas_internacionais:.1f} Bi", get_color_for_metric(game_state, "reservas_internacionais")),
    ]
    for label, value, color in indicadores_monetarios:
        label_width = FONT_MEDIUM.size(label)[0]
        draw_text(screen, label, FONT_MEDIUM, WHITE, col_right_x, y_col_right)
        draw_text(screen, value, FONT_MEDIUM, color, col_right_x + label_width + 10, y_col_right)
        y_col_right += FONT_MEDIUM.get_height() + 5
    y_col_right += 15

    if back_button: back_button.draw(screen)

# --- FUNÇÃO MODIFICADA ---
def draw_news_reports_screen(screen, game_state, back_button):
    screen.fill(DARK_BLUE)
    margin_x = 30
    margin_y_top = 30
    log_panel_y = margin_y_top + FONT_TITLE.get_height() + 15
    log_panel_height = SCREEN_HEIGHT - log_panel_y - 100 # Espaço para título e botão

    draw_text(screen, "Histórico de Atividades e Notícias (Log Completo)", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, margin_y_top + FONT_TITLE.get_height() / 2, align="center")
    
    log_panel_rect = pygame.Rect(margin_x, log_panel_y, SCREEN_WIDTH - (margin_x * 2), log_panel_height)
    pygame.draw.rect(screen, GRAY, log_panel_rect, border_radius=5)

    # Lógica de desenho do log (similar à da tela principal, mas com mais espaço)
    log_content_margin_x = 15
    log_padding_y = 15
    log_line_spacing = 2
    log_message_spacing = 4
    log_entry_group_spacing = 10
    current_y_draw_log = log_panel_rect.top + log_padding_y

    original_clip = screen.get_clip()
    screen.set_clip(log_panel_rect)

    if not game_state.activity_log:
        draw_text(screen, "(Nenhum registro no log ainda)", FONT_MEDIUM, LIGHT_GRAY, log_panel_rect.centerx, log_panel_rect.centery, align="center")
    else:
        last_drawn_month_year_header = None
        for entry_dict in reversed(list(game_state.activity_log)):
            if current_y_draw_log >= log_panel_rect.bottom - log_padding_y:
                break
            
            current_month_year_label = f"--- Mês {entry_dict['month']} / {entry_dict['year']} ---"
            if current_month_year_label != last_drawn_month_year_header:
                if last_drawn_month_year_header is not None:
                    current_y_draw_log += log_entry_group_spacing
                
                month_header_font = FONT_LARGE
                header_color = YELLOW_ALERT
                if current_y_draw_log + month_header_font.get_height() > log_panel_rect.bottom - log_padding_y:
                    break
                
                draw_text(screen, current_month_year_label, month_header_font, header_color, log_panel_rect.centerx, current_y_draw_log, align="center")
                current_y_draw_log += month_header_font.get_height() + log_message_spacing
                last_drawn_month_year_header = current_month_year_label

            for msg_detail in reversed(entry_dict["messages"]):
                if current_y_draw_log >= log_panel_rect.bottom - log_padding_y:
                    break
                
                text_to_wrap = clean_color_codes(msg_detail['text'])
                color = msg_detail['color']
                font_to_use = FONT_MEDIUM
                wrapped_lines = wrap_text(text_to_wrap, font_to_use, log_panel_rect.width - (log_content_margin_x * 2))

                for line_idx, line_text in enumerate(wrapped_lines):
                    if current_y_draw_log + font_to_use.get_height() > log_panel_rect.bottom - log_padding_y:
                        current_y_draw_log = log_panel_rect.bottom
                        break
                    
                    draw_text(screen, line_text, font_to_use, color, log_panel_rect.left + log_content_margin_x, current_y_draw_log)
                    current_y_draw_log += font_to_use.get_height()
                    if line_idx < len(wrapped_lines) - 1:
                        current_y_draw_log += log_line_spacing

                if current_y_draw_log >= log_panel_rect.bottom - log_padding_y:
                    break
                current_y_draw_log += log_message_spacing

            if current_y_draw_log >= log_panel_rect.bottom - log_padding_y:
                break
    
    screen.set_clip(original_clip)
    
    if back_button:
        back_button.draw(screen)

def draw_view_graphs_screen(screen, back_button):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.3; text_y_offset = 60
    draw_text(screen, "Exibicao de Graficos", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    draw_text(screen, "Os graficos de desempenho sao exibidos", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, title_y + text_y_offset, align="center")
    draw_text(screen, "em uma janela separada do Matplotlib.", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, title_y + text_y_offset + FONT_LARGE.get_height() + 5, align="center")
    draw_text(screen, "Feche a janela do grafico para continuar o jogo.", FONT_LARGE, YELLOW_ALERT, SCREEN_WIDTH / 2, title_y + text_y_offset*2 + (FONT_LARGE.get_height() + 5)*2 + 10, align="center")
    if back_button: back_button.draw(screen)

def draw_forecast_report_screen(screen, game_state, back_button, forecast_data):
    screen.fill(DARK_BLUE); margin_x = 50; margin_y_top = 40; content_width = SCREEN_WIDTH - (margin_x * 2)
    draw_text(screen, "Relatorio de Previsao Economica", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, margin_y_top + FONT_TITLE.get_height()/2, align="center")
    
    previsao_inflacao, previsao_pib, previsao_desemprego, acuracia_previsao, inflacao_cenario, pib_cenario = forecast_data
    
    current_y = margin_y_top + FONT_TITLE.get_height() + 30
    line_h_large = FONT_LARGE.get_height() + 10
    line_h_medium = FONT_MEDIUM.get_height() + 7

    draw_text(screen, f"Análise para os Próximos 6 Meses (a partir de {game_state.mes_atual}/{game_state.ano_atual})", FONT_LARGE, WHITE, SCREEN_WIDTH/2, current_y, align="center")
    current_y += line_h_large
    
    acuracia_color = GREEN_SUCCESS if acuracia_previsao > 75 else YELLOW_ALERT if acuracia_previsao > 50 else ORANGE_WARNING
    draw_text(screen, f"Nível de Acurácia da Previsão (baseado na credibilidade):", FONT_MEDIUM, WHITE, margin_x, current_y)
    draw_text(screen, f"{acuracia_previsao:.1f}%", FONT_MEDIUM, acuracia_color, margin_x + FONT_MEDIUM.size("Nível de Acurácia da Previsão (baseado na credibilidade): ")[0], current_y)
    current_y += line_h_medium * 2

    # Previsões
    draw_text(screen, "Previsões Pontuais (Média para o período):", FONT_LARGE, YELLOW_ALERT, margin_x, current_y)
    current_y += line_h_large
    
    previsoes = [
        ("Inflação Anualizada:", f"{previsao_inflacao:.2f}%", get_color_for_metric(game_state, "inflacao")),
        ("Crescimento do PIB Anualizado:", f"{previsao_pib:.2f}%", get_color_for_metric(game_state, "pib")),
        ("Taxa de Desemprego:", f"{previsao_desemprego:.1f}%", get_color_for_metric(game_state, "desemprego"))
    ]
    for label, value, color in previsoes:
        label_width = FONT_MEDIUM.size(label)[0]
        draw_text(screen, label, FONT_MEDIUM, WHITE, margin_x + 20, current_y)
        draw_text(screen, value, FONT_MEDIUM, color, margin_x + 20 + label_width + 10, current_y)
        current_y += line_h_medium

    current_y += line_h_medium

    # Análise de Cenário
    draw_text(screen, "Análise de Cenário:", FONT_LARGE, YELLOW_ALERT, margin_x, current_y)
    current_y += line_h_large

    draw_text(screen, "Cenário Inflacionário:", FONT_MEDIUM, WHITE, margin_x + 20, current_y)
    current_y += line_h_medium
    for line in wrap_text(inflacao_cenario, FONT_SMALL, content_width - 40):
        current_y += draw_text(screen, line, FONT_SMALL, LIGHT_GRAY, margin_x + 40, current_y) + 4
    current_y += line_h_medium

    draw_text(screen, "Cenário de Crescimento (PIB):", FONT_MEDIUM, WHITE, margin_x + 20, current_y)
    current_y += line_h_medium
    for line in wrap_text(pib_cenario, FONT_SMALL, content_width - 40):
        current_y += draw_text(screen, line, FONT_SMALL, LIGHT_GRAY, margin_x + 40, current_y) + 4

    if back_button: back_button.draw(screen)

# --- FUNÇÃO MODIFICADA ---
def draw_consult_advisors_screen(screen, game_state, back_button):
    screen.fill(DARK_BLUE)
    margin_x = 30
    margin_y_top = 20
    content_width = SCREEN_WIDTH - (margin_x * 2)

    draw_text(screen, "Consultoria com Assessores Econômicos", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, margin_y_top + FONT_TITLE.get_height() / 2, align="center")

    current_y = margin_y_top + FONT_TITLE.get_height() + 20
    col_spacing = 20
    num_cols = 3
    col_width = (content_width - (col_spacing * (num_cols - 1))) / num_cols

    # Lógica para determinar o cenário econômico atual
    inflacao_anual = game_state.inflacao_atual_mensal * 12
    pib_anual = game_state.pib_crescimento_atual_mensal * 12
    cenario_chave = "geral_otimo" # Padrão
    
    # Avalia condições negativas
    if inflacao_anual > game_state.meta_inflacao_anual + game_state.banda_inflacao_anual + 0.5 and pib_anual < 1.0:
        cenario_chave = "estagflacao" # Apenas para o pragmático
    elif inflacao_anual > game_state.meta_inflacao_anual + game_state.banda_inflacao_anual + 1.0:
        cenario_chave = "inflacao_alta"
    elif pib_anual > game_state.meta_pib_anual + game_state.banda_pib_anual + 1.0 and inflacao_anual > game_state.meta_inflacao_anual:
         cenario_chave = "superaquecimento" # Apenas para o pragmático
    elif pib_anual < game_state.meta_pib_anual - game_state.banda_pib_anual:
        cenario_chave = "pib_baixo"
    elif inflacao_anual < game_state.meta_inflacao_anual - game_state.banda_inflacao_anual:
        cenario_chave = "inflacao_baixa"
    elif game_state.credibilidade_bc < 40 or game_state.pressao_politica > 70:
        cenario_chave = "credibilidade_baixa_pressao_alta"
    elif game_state.divida_publica_pib > 90:
        cenario_chave = "divida_alta"


    assessores_a_exibir = ["Liberal", "Desenvolvimentista", "Pragmatico"]
    cores_assessores = {"Liberal": BLUE_INFO, "Desenvolvimentista": ORANGE_WARNING, "Pragmatico": LIGHT_GRAY}

    for i, nome_assessor in enumerate(assessores_a_exibir):
        col_x = margin_x + i * (col_width + col_spacing)
        y_col = current_y
        
        # Desenha o cabeçalho da coluna
        pygame.draw.rect(screen, GRAY, (col_x, y_col, col_width, SCREEN_HEIGHT - y_col - 100), border_radius=8)
        
        y_col += 15
        draw_text(screen, nome_assessor, FONT_LARGE, cores_assessores[nome_assessor], col_x + col_width / 2, y_col, align="center")
        y_col += FONT_LARGE.get_height() + 5
        
        # Descrição da filosofia
        desc_lines = wrap_text(ASSESSORES[nome_assessor]["descricao"], FONT_VERY_SMALL, col_width - 20)
        for line in desc_lines:
            y_col += draw_text(screen, line, FONT_VERY_SMALL, WHITE, col_x + 10, y_col) + 2
        
        y_col += 15
        pygame.draw.line(screen, cores_assessores[nome_assessor], (col_x + 10, y_col), (col_x + col_width - 10, y_col), 2)
        y_col += 15
        
        draw_text(screen, "Conselho para o Momento:", FONT_MEDIUM, WHITE, col_x + 10, y_col)
        y_col += FONT_MEDIUM.get_height() + 5
        
        # Pega o conselho específico
        conselho_chave = cenario_chave
        # Casos especiais para o pragmático
        if nome_assessor != "Pragmatico" and conselho_chave in ["estagflacao", "superaquecimento"]:
             if inflacao_anual > pib_anual: conselho_chave = "inflacao_alta" # Simplifica para os outros
             else: conselho_chave = "pib_baixo"

        conselho_texto = ASSESSORES[nome_assessor].get(conselho_chave, "Neste momento, sugiro manter a calma e analisar os dados com cuidado.")
        
        conselho_lines = wrap_text(conselho_texto, FONT_SMALL, col_width - 20)
        for line in conselho_lines:
            y_col += draw_text(screen, line, FONT_SMALL, LIGHT_GRAY, col_x + 10, y_col) + 3

    if back_button: back_button.draw(screen)

def draw_game_over_screen(screen, game_over_reason, final_performance_summary, back_button):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.15
    reason_y_start = title_y + FONT_TITLE.get_height() + 20
    draw_text(screen, "FIM DE JOGO!", FONT_TITLE, RED_CRITICAL, SCREEN_WIDTH / 2, title_y, align="center")
    current_y = reason_y_start
    for line in wrap_text(game_over_reason, FONT_LARGE, SCREEN_WIDTH * 0.8): current_y += draw_text(screen, line, FONT_LARGE, WHITE, SCREEN_WIDTH / 2, current_y, align="center") + 5
    summary_y_start = current_y + 30
    draw_text(screen, "--- Sumario Final do Mandato ---", FONT_LARGE, YELLOW_ALERT, SCREEN_WIDTH / 2, summary_y_start, align="center")
    current_y = summary_y_start + FONT_LARGE.get_height() + 15
    summary_lines_list = final_performance_summary.split('\n')
    for line_idx, line_text in enumerate(summary_lines_list):
        font_to_use_summary = FONT_MEDIUM; color_to_use_summary = WHITE
        if "Pontuacao Geral" in line_text:
            font_to_use_summary = FONT_LARGE
            try: score = float(line_text.split(":")[-1].strip().split(" ")[0])
            except: score = 0 # fallback
            if score >= 70: color_to_use_summary = GREEN_SUCCESS
            elif score >= 20: color_to_use_summary = YELLOW_ALERT
            else: color_to_use_summary = ORANGE_WARNING
        elif line_idx == len(summary_lines_list) -1 :
            font_to_use_summary = FONT_LARGE
            if "SUCESSO" in line_text.upper() or "BEM-SUCEDIDA" in line_text.upper(): color_to_use_summary = GREEN_SUCCESS
            elif "DIFICULDADES" in line_text.upper() or "INSATISFATORIOS" in line_text.upper() or "INTERROMPIDO" in line_text.upper() : color_to_use_summary = RED_CRITICAL
            else: color_to_use_summary = YELLOW_ALERT
        for sub_line in wrap_text(line_text, font_to_use_summary, SCREEN_WIDTH * 0.9):
            if current_y > SCREEN_HEIGHT - (back_button.rect.height if back_button else 60) - 25: break
            current_y += draw_text(screen, sub_line, font_to_use_summary, color_to_use_summary, SCREEN_WIDTH / 2, current_y, align="center") + 3
        if current_y > SCREEN_HEIGHT - (back_button.rect.height if back_button else 60) - 25: break
        current_y += 4
    if back_button: back_button.draw(screen)

def draw_select_tone_screen(screen, tone_selection_message, buttons):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.15; label_y = title_y + FONT_TITLE.get_height() + 20
    draw_text(screen, tone_selection_message, FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    draw_text(screen, "Escolha o tom da sua comunicacao:", FONT_LARGE, LIGHT_GRAY, SCREEN_WIDTH / 2, label_y, align="center")
    btn_hawkish = buttons.get("tone_hawkish"); btn_dovish = buttons.get("tone_dovish"); btn_neutral = buttons.get("tone_neutral"); btn_cancel_tone = buttons.get("tone_cancel")
    if btn_hawkish: btn_hawkish.draw(screen)
    if btn_dovish: btn_dovish.draw(screen)
    if btn_neutral: btn_neutral.draw(screen)
    hint_start_y = 0
    if btn_cancel_tone: btn_cancel_tone.draw(screen); hint_start_y = btn_cancel_tone.rect.bottom + 30
    if hint_start_y > 0 :
        line_h_medium = FONT_MEDIUM.get_height() + 5; hint_content_width = SCREEN_WIDTH * 0.8
        hawkish_hint = "Hawkish: Enfatiza o controle rigoroso da inflacao, mesmo que possa desacelerar o PIB."
        dovish_hint = "Dovish: Sinaliza preocupacao com o crescimento e emprego, podendo ser mais tolerante com a inflacao."
        neutral_hint = "Neutro: Postura equilibrada, baseada nos dados atuais, sem sinalizacoes fortes."
        current_hint_y = hint_start_y
        for line in wrap_text(hawkish_hint, FONT_MEDIUM, hint_content_width): current_hint_y += draw_text(screen, line, FONT_MEDIUM, ORANGE_WARNING, SCREEN_WIDTH / 2, current_hint_y, align="center") + 2
        current_hint_y += line_h_medium / 2
        for line in wrap_text(dovish_hint, FONT_MEDIUM, hint_content_width): current_hint_y += draw_text(screen, line, FONT_MEDIUM, BLUE_INFO, SCREEN_WIDTH / 2, current_hint_y, align="center") + 2
        current_hint_y += line_h_medium / 2
        for line in wrap_text(neutral_hint, FONT_MEDIUM, hint_content_width): current_hint_y += draw_text(screen, line, FONT_MEDIUM, LIGHT_GRAY, SCREEN_WIDTH / 2, current_hint_y, align="center") + 2

def draw_alter_compulsorio_screen(screen, game_state, compulsorio_input_box, compulsorio_input_message, buttons):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.15; current_rate_y = title_y + FONT_TITLE.get_height() + 20
    input_label_y = current_rate_y + FONT_LARGE.get_height() + 30; input_box_y_offset = 20; message_y_offset = 80
    draw_text(screen, "Alterar Deposito Compulsorio", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    draw_text(screen, f"Taxa Atual: {game_state.taxa_deposito_compulsorio*100:.0f}%", FONT_LARGE, YELLOW_ALERT, SCREEN_WIDTH / 2, current_rate_y, align="center")
    draw_text(screen, "Nova Taxa de Compulsorio (%):", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, input_label_y, align="center")
    compulsorio_input_box.rect.centerx = SCREEN_WIDTH / 2; compulsorio_input_box.rect.top = input_label_y + FONT_LARGE.get_height() + input_box_y_offset; compulsorio_input_box.draw(screen)
    if compulsorio_input_message:
        message_lines = wrap_text(compulsorio_input_message, FONT_MEDIUM, SCREEN_WIDTH * 0.8); current_y_msg = compulsorio_input_box.rect.bottom + message_y_offset / 2
        for line in message_lines: text_height = draw_text(screen, line, FONT_MEDIUM, YELLOW_ALERT, SCREEN_WIDTH / 2, current_y_msg, align="center"); current_y_msg += text_height + 3
    if buttons.get("compulsorio_confirm"): buttons["compulsorio_confirm"].draw(screen)
    if buttons.get("compulsorio_cancel"): buttons["compulsorio_cancel"].draw(screen)

def draw_toasts(screen, active_toasts):
    for toast_item in active_toasts:
        toast_item.draw(screen)

def draw_reuniao_ministro_submenu(screen, game_state, buttons_dict):
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.1; profile_y = title_y + FONT_TITLE.get_height() + 20; question_y = profile_y + FONT_LARGE.get_height() + 35
    draw_text(screen, "Reunião com Ministro da Fazenda", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    ministro_perfil = getattr(game_state, 'tipo_ministro_fazenda', "Indefinido"); desc_ministro = ""; cor_perfil = YELLOW_ALERT
    if ministro_perfil == "Liberal": desc_ministro = "(Foco: Austeridade, Controle Inflacao)"; cor_perfil = BLUE_INFO
    elif ministro_perfil == "Desenvolvimentista": desc_ministro = "(Foco: Crescimento, Emprego, Investimentos)"; cor_perfil = ORANGE_WARNING
    elif ministro_perfil == "Pragmatico": desc_ministro = "(Foco: Equilibrio, Adaptabilidade)"; cor_perfil = LIGHT_GRAY
    draw_text(screen, f"Perfil do Ministro: {ministro_perfil}", FONT_LARGE, cor_perfil, SCREEN_WIDTH / 2, profile_y, align="center")
    if desc_ministro: draw_text(screen, desc_ministro, FONT_MEDIUM, cor_perfil, SCREEN_WIDTH / 2, profile_y + FONT_LARGE.get_height() + 5, align="center")
    draw_text(screen, "Qual será sua principal pauta para a reunião?", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, question_y, align="center")
    if buttons_dict.get("reuniao_sugerir_corte"): buttons_dict["reuniao_sugerir_corte"].draw(screen)
    if buttons_dict.get("reuniao_sugerir_aumento"): buttons_dict["reuniao_sugerir_aumento"].draw(screen)
    if buttons_dict.get("reuniao_discutir_cenario"): buttons_dict["reuniao_discutir_cenario"].draw(screen)
    if buttons_dict.get("reuniao_cancelar_pauta"): buttons_dict["reuniao_cancelar_pauta"].draw(screen)

def draw_intervencao_cambial_input_screen(screen, game_state, buttons, intervencao_tipo_selecionado, input_box, input_message): # Nome corrigido aqui
    screen.fill(DARK_BLUE); title_y = SCREEN_HEIGHT * 0.1; draw_text(screen, "Intervenção Cambial Detalhada", FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center")
    info_y = title_y + FONT_TITLE.get_height() + 20; line_h_info = FONT_LARGE.get_height() + 5
    reservas_texto = f"Reservas Atuais: US$ {game_state.reservas_internacionais:.1f} Bilhões"; reservas_cor = get_color_for_metric(game_state, "reservas_internacionais")
    draw_text(screen, reservas_texto, FONT_LARGE, reservas_cor, SCREEN_WIDTH / 2, info_y, align="center"); info_y += line_h_info
    cambio_texto = f"Câmbio Atual: R$ {game_state.cambio_atual:.2f} / US$"; draw_text(screen, cambio_texto, FONT_LARGE, YELLOW_ALERT, SCREEN_WIDTH / 2, info_y, align="center"); info_y += line_h_info + 20
    if not intervencao_tipo_selecionado:
        draw_text(screen, "Selecione o tipo de intervenção:", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, info_y, align="center")
        if buttons.get("intervencao_escolher_vender"): buttons["intervencao_escolher_vender"].draw(screen)
        if buttons.get("intervencao_escolher_comprar"): buttons["intervencao_escolher_comprar"].draw(screen)
        btn_cancel_geral = buttons.get("intervencao_cancelar_input")
        if btn_cancel_geral: btn_cancel_geral.rect.centerx = SCREEN_WIDTH / 2; btn_cancel_geral.rect.top = SCREEN_HEIGHT * 0.5 + 50; btn_cancel_geral.draw(screen)
    else:
        acao_texto = "Vender Dólares" if intervencao_tipo_selecionado == "venda_dolares" else "Comprar Dólares"
        draw_text(screen, f"Intervenção: {acao_texto}", FONT_LARGE, WHITE, SCREEN_WIDTH / 2, info_y, align="center"); info_y += line_h_info
        draw_text(screen, "Digite o montante em Bilhões de USD (ex: 1.5):", FONT_MEDIUM, WHITE, SCREEN_WIDTH / 2, info_y, align="center"); info_y += FONT_MEDIUM.get_height() + 10
        input_box.rect.centerx = SCREEN_WIDTH / 2; input_box.rect.top = info_y; input_box.draw(screen); info_y += input_box.rect.height + 5
        if input_message:
            msg_lines = wrap_text(input_message, FONT_SMALL, SCREEN_WIDTH * 0.7)
            for line in msg_lines: info_y += draw_text(screen, line, FONT_SMALL, YELLOW_ALERT, SCREEN_WIDTH/2, info_y, align="center") + 2
        if buttons.get("intervencao_confirmar_montante"): buttons["intervencao_confirmar_montante"].draw(screen)
        if buttons.get("intervencao_cancelar_input"): buttons["intervencao_cancelar_input"].draw(screen)

def draw_forward_guidance_selection_screen(screen, game_state, buttons, tom_escolhido, acao_origem):
    screen.fill(DARK_BLUE)
    title_text = f"Orientação Futura para {acao_origem.capitalize() if acao_origem else 'Comunicação'}"
    subtitle_text = f"(Tom Escolhido: {tom_escolhido.capitalize() if tom_escolhido else 'N/A'})"
    prompt_text = "Selecione uma sinalização de Forward Guidance:"
    title_y = SCREEN_HEIGHT * 0.1
    draw_text(screen, title_text, FONT_TITLE, WHITE, SCREEN_WIDTH / 2, title_y, align="center"); title_y += FONT_TITLE.get_height() + 5
    draw_text(screen, subtitle_text, FONT_LARGE, LIGHT_GRAY, SCREEN_WIDTH / 2, title_y, align="center"); title_y += FONT_LARGE.get_height() + 20
    draw_text(screen, prompt_text, FONT_LARGE, YELLOW_ALERT, SCREEN_WIDTH / 2, title_y, align="center")
    option_keys = ["guidance_nenhum", "guidance_manter_selic", "guidance_inclinar_alta", "guidance_inclinar_baixa", "guidance_fim_ciclo_alta", "guidance_fim_ciclo_baixa", "guidance_cancelar"]
    for key in option_keys:
        if buttons.get(key): buttons[key].draw(screen)