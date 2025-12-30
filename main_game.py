import pygame
import sys
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TITLE,
    GREEN_SUCCESS, RED_CRITICAL, ORANGE_WARNING, BLUE_INFO, PURPLE_ACTION,
    LIGHT_GRAY, GRAY, DARK_BLUE, TEXT_COLOR, YELLOW_ALERT, WHITE
)
from ui_elements import Button, TextBox, Toast
from economy_state import EstadoEconomia
from player_actions import (
    acao_comunicado_meta, acao_discurso_publico, acao_reuniao_fechada,
    acao_flexibilizar_meta, acao_alterar_compulsorio,
    acao_reuniao_ministro,
    acao_intervir_cambio
)
from economy_mechanics import (
    atualizar_inflacao as calcular_alvo_inflacao, 
    atualizar_pib as calcular_alvo_pib,
    atualizar_cambio as calcular_alvo_cambio,
    atualizar_expectativa_juros_longo_prazo, 
    atualizar_fator_liquidez_bancaria,
    atualizar_desemprego, 
    atualizar_credibilidade_e_pressao, 
    atualizar_divida_publica,
    decisoes_fiscais_governo_ia
)
from events import gerar_evento_aleatorio
from game_screens import (
    draw_text, wrap_text, get_color_for_metric, draw_toasts,
    draw_main_menu, draw_game_month_screen, draw_instructions_screen,
    draw_event_popup, draw_alter_selic_screen, draw_selic_warning_popup,
    draw_actions_menu, draw_reports_menu, draw_status_bc_screen,
    draw_news_reports_screen, draw_view_graphs_screen,
    draw_forecast_report_screen, draw_consult_advisors_screen,
    draw_game_over_screen, draw_select_tone_screen, draw_alter_compulsorio_screen,
    draw_reuniao_ministro_submenu, 
    draw_intervencao_cambial_input_screen,
    draw_forward_guidance_selection_screen
)
from reports import exibir_graficos_matplotlib, gerar_relatorio_previsao_data, evaluate_performance_final
from ui_setup import (
    create_main_menu_buttons, create_game_month_buttons, create_instructions_buttons,
    create_actions_menu_buttons, create_reports_menu_buttons, create_common_back_buttons,
    create_game_over_buttons, create_selic_input_buttons, create_selic_warning_buttons,
    create_tone_selection_buttons, create_compulsorio_input_buttons,
    create_minister_submenu_buttons,
    create_intervencao_cambial_input_screen_buttons,
    create_forward_guidance_buttons
)
# --- NOVA IMPORTAÇÃO DA IA ---
from adaptive_ai import ia_diretora_avalia_e_reage

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Presidente do Banco Central")

PASSO_AJUSTE_INFLACAO_MENSAL = 0.00060
PASSO_AJUSTE_PIB_MENSAL = 0.00015       
PASSO_AJUSTE_CAMBIO = 0.035             
PASSO_AJUSTE_CREDIBILIDADE = 1.0  
PASSO_AJUSTE_PRESSAO = 1.0      

class GameController:
    def __init__(self):
        self.screen = SCREEN
        self.state = "main_menu"
        self.game_state = EstadoEconomia()
        self.buttons = {}
        self.buttons_for_popup = {}
        self.event_popup_data = None
        self.event_popup_message = ""; self.event_popup_options = []
        self.current_event_choice_data = None
        self.game_over_reason = ""; self.final_performance_summary = ""
        self.selic_input_box = TextBox(SCREEN_WIDTH / 2 - 75, SCREEN_HEIGHT / 2 - 20, 150, 40, FONT_LARGE)
        self.selic_input_message = ""; self.selic_warning_popup_active = False
        self.action_pending_tone = None 
        self.tone_selection_message = ""
        self.compulsorio_input_box = TextBox(SCREEN_WIDTH / 2 - 75, SCREEN_HEIGHT / 2 - 20, 150, 40, FONT_LARGE)
        self.compulsorio_input_message = ""
        self.intervencao_cambial_tipo_selecionado = None 
        self.intervencao_input_box = TextBox(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 50, 200, 45, FONT_LARGE)
        self.intervencao_input_message = ""
        self.active_toasts = []; self.toast_font = FONT_SMALL
        self.toast_default_start_y = SCREEN_HEIGHT - 50; self.toast_spacing = 10
        self.max_toasts_on_screen = 3
        self.pending_guidance_action_origin = None 
        self.pending_guidance_tone = None          
        self.screen_draw_functions = {
            "main_menu": lambda: draw_main_menu(self.screen, self.buttons),
            "game_month": lambda: draw_game_month_screen(self.screen, self.game_state, self.buttons),
            "instructions": lambda: draw_instructions_screen(self.screen, self.buttons),
            "actions_menu": lambda: draw_actions_menu(self.screen, self.game_state, self.buttons),
            "reports_menu": lambda: draw_reports_menu(self.screen, self.buttons),
            "status_bc": lambda: draw_status_bc_screen(self.screen, self.game_state, self.buttons.get("back_from_status")),
            "news_reports": lambda: draw_news_reports_screen(self.screen, self.game_state, self.buttons.get("back_from_news")),
            "view_graphs": lambda: draw_view_graphs_screen(self.screen, self.buttons.get("back_from_graphs")),
            "forecast_report": lambda: draw_forecast_report_screen(self.screen, self.game_state, self.buttons.get("back_from_forecast"), gerar_relatorio_previsao_data(self.game_state)),
            "consult_advisors": lambda: draw_consult_advisors_screen(self.screen, self.game_state, self.buttons.get("back_from_advisors")),
            "game_over_demitted": lambda: draw_game_over_screen(self.screen, self.game_over_reason, self.final_performance_summary, self.buttons.get("game_over_back_to_main_menu")),
            "game_over_mandate_end": lambda: draw_game_over_screen(self.screen, self.game_over_reason, self.final_performance_summary, self.buttons.get("game_over_back_to_main_menu")),
            "alter_selic_screen": lambda: draw_alter_selic_screen(self.screen, self.selic_input_box, self.selic_input_message, self.buttons),
            "selic_warning_popup": lambda: draw_selic_warning_popup(self.screen, self.buttons),
            "select_tone_screen": lambda: draw_select_tone_screen(self.screen, self.tone_selection_message, self.buttons),
            "alter_compulsorio_screen": lambda: draw_alter_compulsorio_screen(self.screen, self.game_state, self.compulsorio_input_box, self.compulsorio_input_message, self.buttons),
            "reuniao_ministro_submenu": lambda: draw_reuniao_ministro_submenu(self.screen, self.game_state, self.buttons),
            "intervencao_cambial_input_screen": lambda: draw_intervencao_cambial_input_screen(
                self.screen, self.game_state, self.buttons,
                self.intervencao_cambial_tipo_selecionado,
                self.intervencao_input_box, self.intervencao_input_message
            ),
            "select_forward_guidance": lambda: draw_forward_guidance_selection_screen(
                self.screen, self.game_state, self.buttons,
                self.pending_guidance_tone, self.pending_guidance_action_origin
            ),
        }
        self._setup_all_buttons()
        self.initialize_game_state_data()

    def _setup_all_buttons(self):
        self.buttons = {}
        self.buttons.update(create_main_menu_buttons())
        self.buttons.update(create_game_month_buttons())
        self.buttons.update(create_instructions_buttons())
        self.buttons.update(create_actions_menu_buttons())
        self.buttons.update(create_reports_menu_buttons())
        self.buttons.update(create_common_back_buttons())
        self.buttons.update(create_game_over_buttons())
        self.buttons.update(create_selic_input_buttons())
        self.buttons.update(create_selic_warning_buttons())
        self.buttons.update(create_tone_selection_buttons())
        self.buttons.update(create_compulsorio_input_buttons())
        self.buttons.update(create_minister_submenu_buttons())
        self.buttons.update(create_intervencao_cambial_input_screen_buttons())
        self.buttons.update(create_forward_guidance_buttons()) 
    
    def add_toast(self, message, bg_color=GRAY, text_color=WHITE, duration_ms=3000, fade_in_ms=300, fade_out_ms=500, force_show=False):
        can_add = True
        if not force_show and self.active_toasts:
            if self.active_toasts[-1].text == message: can_add = False
        if can_add:
            new_toast = Toast(text=message, duration_ms=duration_ms, font=self.toast_font, text_color=text_color,
                              bg_color=bg_color, position_y_start=self.toast_default_start_y,
                              screen_width=SCREEN_WIDTH, fade_in_duration_ms=fade_in_ms,
                              fade_out_duration_ms=fade_out_ms)
            while len(self.active_toasts) >= self.max_toasts_on_screen: self.active_toasts.pop(0)
            self.active_toasts.append(new_toast)
            current_y_for_toast = self.toast_default_start_y
            for i in range(len(self.active_toasts) -1, -1, -1):
                toast = self.active_toasts[i]
                toast.current_y = current_y_for_toast - toast.bg_rect.height
                current_y_for_toast = toast.current_y - self.toast_spacing

    def initialize_game_state_data(self):
        self.game_state = EstadoEconomia()
        self.game_state.historico_inflacao = [self.game_state.inflacao_atual_mensal * 12]
        self.game_state.historico_pib = [self.game_state.pib_crescimento_atual_mensal * 12]
        self.game_state.historico_credibilidade = [self.game_state.credibilidade_bc]
        self.game_state.historico_pressao_politica = [self.game_state.pressao_politica]
        self.game_state.historico_selic = [self.game_state.selic_anual]
        self.game_state.historico_cambio = [self.game_state.cambio_atual]
        self.game_state.historico_desemprego = [self.game_state.taxa_desemprego_atual]
        self.game_state.historico_expectativa_inflacao = [self.game_state.expectativa_inflacao_mercado_mensal * 12]
        self.game_state.historico_juros_longo_prazo = [self.game_state.expectativa_juros_longo_prazo_anual]
        self.game_state.historico_compulsorio = [self.game_state.taxa_deposito_compulsorio * 100]
        self.game_state.historico_divida_pib = [self.game_state.divida_publica_pib]
        if hasattr(self.game_state, 'reservas_internacionais') and self.game_state.reservas_internacionais is not None:
             self.game_state.historico_reservas_internacionais = [self.game_state.reservas_internacionais]
        else: 
            self.game_state.reservas_internacionais = 300.0 
            self.game_state.historico_reservas_internacionais = [self.game_state.reservas_internacionais]
        self.event_popup_data = None; self.event_popup_message = ""; self.event_popup_options = []
        self.current_event_choice_data = None; self.game_over_reason = ""; self.final_performance_summary = ""
        self.selic_input_message = ""; self.selic_warning_popup_active = False
        self.action_pending_tone = None; self.tone_selection_message = ""
        self.compulsorio_input_message = ""
        self.active_toasts = []
        self.intervencao_cambial_tipo_selecionado = None 
        self.intervencao_input_message = "" 
        self.intervencao_input_box.text = ""; self.intervencao_input_box.active = False
        self.pending_guidance_action_origin = None 
        self.pending_guidance_tone = None          
        self.game_state.forward_guidance_ativo = None 
        if hasattr(self.game_state, 'cooldown_forward_guidance'): self.game_state.cooldown_forward_guidance = 0

    def check_critical_game_over_conditions(self):
        game_ended = False; reason = None
        if self.game_state.credibilidade_bc <= 0: reason = "Credibilidade do BC chegou a zero ou menos! Voce foi demitido!"; game_ended = True
        elif self.game_state.pressao_politica >= 100: reason = "Pressao Politica tornou-se insustentavel (100+)! Voce foi demitido!"; game_ended = True
        elif self.game_state.divida_publica_pib >= 120: reason = f"Dívida Pública atingiu {self.game_state.divida_publica_pib:.1f}% do PIB! Crise fiscal e demissao!"; game_ended = True
        if game_ended: 
            self.state = "game_over_demitted"; self.game_over_reason = reason
            self.final_performance_summary = evaluate_performance_final(self.game_state, True)
            self.game_state.add_log_entry(self.game_over_reason, RED_CRITICAL)
        return game_ended

    def handle_event_popup_input(self, event):
        action_taken = False
        if self.event_popup_options: 
            for i, btn_key in enumerate([f"event_choice_{j}" for j in range(len(self.event_popup_options))]):
                if btn_key in self.buttons_for_popup and self.buttons_for_popup[btn_key].handle_event(event):
                    selected_option = self.current_event_choice_data["opcoes"][i]
                    for k, v_delta in selected_option["impactos"].items():
                        if hasattr(self.game_state, k):
                            valor_aplicar = v_delta
                            if k in ["inflacao_atual_mensal", "pib_crescimento_atual_mensal"] and abs(v_delta) > 0.009: valor_aplicar = v_delta / 12 
                            elif k == "expectativa_inflacao_mercado_mensal" and abs(v_delta) > 0.001 : valor_aplicar = v_delta / 12
                            setattr(self.game_state, k, getattr(self.game_state, k) + valor_aplicar)
                    self.event_popup_message = selected_option["resultado"]; self.event_popup_options = []
                    self.game_state.add_log_entry(f"Evento: {self.current_event_choice_data['nome']} - Escolha: {selected_option['texto']}. Resultado: {selected_option['resultado']}", BLUE_INFO)
                    self.current_event_choice_data = None; action_taken = True; break 
        else: 
            if "event_ok" in self.buttons_for_popup and self.buttons_for_popup["event_ok"].handle_event(event):
                self.event_popup_data = None; self.event_popup_message = ""; self.buttons_for_popup = {}; action_taken = True
        if action_taken and not self.event_popup_data:
             if self.check_critical_game_over_conditions(): return True
        return action_taken

    def advance_month_logic(self, month_consumed_by_action=False):
        if self.check_critical_game_over_conditions(): return True
        gs = self.game_state
        
        # A IA Diretora avalia o cenário ANTES de qualquer outra coisa no mês.
        evento_forcado = ia_diretora_avalia_e_reage(gs)
        
        # O contador de inatividade só aumenta se o jogador clicar em "AVANÇAR MÊS".
        if not month_consumed_by_action:
            gs.meses_sem_acao_significativa += 1

        if not month_consumed_by_action: decisoes_fiscais_governo_ia(gs)
        atualizar_divida_publica(gs); atualizar_fator_liquidez_bancaria(gs)
        calcular_alvo_inflacao(gs); calcular_alvo_pib(gs); calcular_alvo_cambio(gs) 
        atualizar_credibilidade_e_pressao(gs)
        if gs.inflacao_atual_mensal < gs.alvo_inflacao_mensal: gs.inflacao_atual_mensal = min(gs.inflacao_atual_mensal + PASSO_AJUSTE_INFLACAO_MENSAL, gs.alvo_inflacao_mensal)
        elif gs.inflacao_atual_mensal > gs.alvo_inflacao_mensal: gs.inflacao_atual_mensal = max(gs.inflacao_atual_mensal - PASSO_AJUSTE_INFLACAO_MENSAL, gs.alvo_inflacao_mensal)
        gs.inflacao_atual_mensal = round(gs.inflacao_atual_mensal, 6)
        if gs.pib_crescimento_atual_mensal < gs.alvo_pib_crescimento_mensal: gs.pib_crescimento_atual_mensal = min(gs.pib_crescimento_atual_mensal + PASSO_AJUSTE_PIB_MENSAL, gs.alvo_pib_crescimento_mensal)
        elif gs.pib_crescimento_atual_mensal > gs.alvo_pib_crescimento_mensal: gs.pib_crescimento_atual_mensal = max(gs.pib_crescimento_atual_mensal - PASSO_AJUSTE_PIB_MENSAL, gs.alvo_pib_crescimento_mensal)
        gs.pib_crescimento_atual_mensal = round(gs.pib_crescimento_atual_mensal, 6)
        if gs.cambio_atual < gs.alvo_cambio_atual: gs.cambio_atual = min(gs.cambio_atual + PASSO_AJUSTE_CAMBIO, gs.alvo_cambio_atual)
        elif gs.cambio_atual > gs.alvo_cambio_atual: gs.cambio_atual = max(gs.cambio_atual - PASSO_AJUSTE_CAMBIO, gs.alvo_cambio_atual)
        gs.cambio_atual = round(gs.cambio_atual, 3)
        if gs.credibilidade_bc < gs.alvo_credibilidade_bc: gs.credibilidade_bc = min(gs.credibilidade_bc + PASSO_AJUSTE_CREDIBILIDADE, gs.alvo_credibilidade_bc)
        elif gs.credibilidade_bc > gs.alvo_credibilidade_bc: gs.credibilidade_bc = max(gs.credibilidade_bc - PASSO_AJUSTE_CREDIBILIDADE, gs.alvo_credibilidade_bc)
        gs.credibilidade_bc = round(max(0.0, min(100.0, gs.credibilidade_bc)), 1)
        if gs.pressao_politica < gs.alvo_pressao_politica: gs.pressao_politica = min(gs.pressao_politica + PASSO_AJUSTE_PRESSAO, gs.alvo_pressao_politica)
        elif gs.pressao_politica > gs.alvo_pressao_politica: gs.pressao_politica = max(gs.pressao_politica - PASSO_AJUSTE_PRESSAO, gs.alvo_pressao_politica)
        gs.pressao_politica = round(max(0.0, min(100.0, gs.pressao_politica)), 1)
        gs.taxa_desemprego_atual = atualizar_desemprego(gs); gs.taxa_desemprego_atual = round(gs.taxa_desemprego_atual, 2)
        if hasattr(gs, 'intervencao_cambial_este_mes_tipo'): gs.intervencao_cambial_este_mes_tipo = None
        if hasattr(gs, 'intervencao_cambial_este_mes_magnitude'): gs.intervencao_cambial_este_mes_magnitude = 0.0
        peso_meta_cred = gs.credibilidade_bc / 100.0 * 0.5 + 0.3; influencia_meta = (gs.meta_inflacao_anual / 12) * peso_meta_cred
        peso_inflacao_atual = 1.0 - peso_meta_cred; influencia_inflacao_atual = gs.inflacao_atual_mensal * peso_inflacao_atual
        juro_real_esperado_curto = (gs.selic_anual / 12) - gs.expectativa_inflacao_mercado_mensal
        influencia_selic_expectativa = juro_real_esperado_curto * 0.15 
        ruido_expectativa = random.uniform(-0.02, 0.02) / 12
        nova_expectativa = (influencia_meta + influencia_inflacao_atual - influencia_selic_expectativa) * 0.7 + gs.expectativa_inflacao_mercado_mensal * 0.3 + ruido_expectativa
        gs.expectativa_inflacao_mercado_mensal = round(max(0.01 / 12, min(2.5 / 12, nova_expectativa)), 6)
        tom_para_juros_longos = "neutro" 
        if gs.forward_guidance_ativo and gs.forward_guidance_ativo.get("tipo") and not gs.forward_guidance_ativo.get("quebrado_este_mes"): 
            tipo_fg = gs.forward_guidance_ativo["tipo"]
            if tipo_fg == "manter_selic":
                if gs.selic_anual > (gs.meta_inflacao_anual + 2.0): tom_para_juros_longos = "hawkish"
                elif gs.selic_anual < (gs.meta_inflacao_anual + 1.0): tom_para_juros_longos = "dovish"  
            elif tipo_fg == "inclinar_alta" or tipo_fg == "fim_ciclo_baixa": tom_para_juros_longos = "hawkish"
            elif tipo_fg == "inclinar_baixa" or tipo_fg == "fim_ciclo_alta": tom_para_juros_longos = "dovish"
        atualizar_expectativa_juros_longo_prazo(gs, tom_para_juros_longos) 
        if self.check_critical_game_over_conditions(): return True
        self.game_state.add_log_entry(f"Mês {gs.mes_atual}/{gs.ano_atual}: Inf {gs.inflacao_atual_mensal*12:.2f}%, PIB {gs.pib_crescimento_atual_mensal*12:.2f}%, Cambio R${gs.cambio_atual:.2f}, Desemp {gs.taxa_desemprego_atual:.1f}%", TEXT_COLOR)
        self.game_state.add_log_entry(f"Cred: {gs.credibilidade_bc:.1f} (Alvo: {gs.alvo_credibilidade_bc:.1f}), Press: {gs.pressao_politica:.1f} (Alvo: {gs.alvo_pressao_politica:.1f})", LIGHT_GRAY) 
        if gs.forward_guidance_ativo:
            fg_info = gs.forward_guidance_ativo
            log_guidance_msg = f"Guidance Ativo: {fg_info['tipo'].replace('_', ' ').capitalize()}"
            if fg_info.get('duracao_total', 0) > 0 and fg_info.get('duracao_restante', -1) >=0 :
                log_guidance_msg += f" (Restam: {fg_info['duracao_restante']}m)"
            if fg_info.get("quebrado_este_mes"): log_guidance_msg += " [QUEBRADO!]"
            self.game_state.add_log_entry(log_guidance_msg, BLUE_INFO if not fg_info.get("quebrado_este_mes") else RED_CRITICAL)
        self.game_state.historico_inflacao.append(gs.inflacao_atual_mensal*12); self.game_state.historico_pib.append(gs.pib_crescimento_atual_mensal*12); self.game_state.historico_credibilidade.append(gs.credibilidade_bc); self.game_state.historico_pressao_politica.append(gs.pressao_politica); self.game_state.historico_selic.append(gs.selic_anual); self.game_state.historico_cambio.append(gs.cambio_atual); self.game_state.historico_desemprego.append(gs.taxa_desemprego_atual); self.game_state.historico_expectativa_inflacao.append(gs.expectativa_inflacao_mercado_mensal*12); self.game_state.historico_juros_longo_prazo.append(gs.expectativa_juros_longo_prazo_anual); self.game_state.historico_compulsorio.append(gs.taxa_deposito_compulsorio * 100); self.game_state.historico_divida_pib.append(gs.divida_publica_pib)
        if hasattr(gs, 'reservas_internacionais'): self.game_state.historico_reservas_internacionais.append(gs.reservas_internacionais)
        if gs.cambio_atual >= gs.cambio_crise_limiar:
            gs.cambio_crise_contador+=1
            if gs.cambio_crise_contador >= gs.cambio_crise_meses: self.state="game_over_demitted"; self.game_over_reason=f"CRÍTICO: Cambio a {gs.cambio_atual:.2f} por {gs.cambio_crise_meses} meses!"; self.final_performance_summary = evaluate_performance_final(gs, True); gs.add_log_entry(self.game_over_reason,RED_CRITICAL); return True
            else: gs.add_log_entry(f"ALERTA: Cambio elevado ({gs.cambio_atual:.2f}) ha {gs.cambio_crise_contador} mes(es).",ORANGE_WARNING)
        else: gs.cambio_crise_contador=0
        if not month_consumed_by_action:
            gs.mes_atual += 1
            if gs.mes_atual > 12: gs.mes_atual = 1; gs.ano_atual += 1; gs.anos_restantes_mandato -= 1
        gs.mudancas_selic_este_mes = 0; gs.evento_ocorrido_este_mes = False 
        
        if evento_forcado:
            self.event_popup_data = evento_forcado
            event_data_payload = evento_forcado.get("data", {})
            self.event_popup_message = event_data_payload.get("mensagem_contexto", "")
            self.event_popup_options = event_data_payload.get("opcoes", [])
            self.current_event_choice_data = event_data_payload
            gs.add_log_entry(f"Manchete Urgente: {event_data_payload.get('manchete', '')}", YELLOW_ALERT)
        elif not month_consumed_by_action and not (gs.ano_atual == 2024 and gs.mes_atual == 1 and len(gs.historico_inflacao) <= 1) :
            generated_event_data = gerar_evento_aleatorio(gs)
            if generated_event_data and isinstance(generated_event_data, dict):
                self.event_popup_data = generated_event_data; event_type = generated_event_data.get("type"); event_data_payload = generated_event_data.get("data")
                if event_type and event_data_payload:
                    self.event_popup_message = event_data_payload.get("mensagem_impacto", "") if event_type == "normal" else event_data_payload.get("mensagem_contexto", "")
                    self.event_popup_options = event_data_payload.get("opcoes", []); self.current_event_choice_data = event_data_payload if event_type == "escolha" else None
                    if event_type == "normal": 
                        manchete = event_data_payload.get("manchete") 
                        if manchete: gs.add_log_entry(f"Manchete: {manchete}", YELLOW_ALERT)
                else: gs.evento_ocorrido_este_mes = True 
            else: gs.evento_ocorrido_este_mes = True 
        else: gs.evento_ocorrido_este_mes = True

        cooldown_attributes = ['cooldown_comunicado_meta', 'cooldown_discurso_publico', 'cooldown_reuniao_fechada', 'cooldown_flexibilizar_meta', 'cooldown_deposito_compulsorio', 'cooldown_reuniao_ministro', 'cooldown_intervencao_cambial', 'cooldown_forward_guidance']
        for cooldown_attr in cooldown_attributes:
            if hasattr(gs, cooldown_attr) and getattr(gs, cooldown_attr) > 0: setattr(gs, cooldown_attr, getattr(gs, cooldown_attr) - 1)
        if gs.meses_banda_flexibilizada > 0:
            gs.meses_banda_flexibilizada -= 1
            if gs.meses_banda_flexibilizada == 0: gs.banda_inflacao_anual = gs.banda_inflacao_original; gs.add_log_entry("Flexibilizacao da meta de inflacao expirou.", BLUE_INFO)
        if gs.forward_guidance_ativo:
            if gs.forward_guidance_ativo.get("quebrado_este_mes"):
                self.add_toast(f"Guidance '{gs.forward_guidance_ativo['tipo'].replace('_',' ')}' quebrado foi removido.", ORANGE_WARNING, force_show=True)
                gs.add_log_entry(f"Guidance '{gs.forward_guidance_ativo['tipo'].replace('_',' ')}' quebrado e removido do acompanhamento.", ORANGE_WARNING)
                gs.forward_guidance_ativo = None
            elif "duracao_restante" in gs.forward_guidance_ativo:
                gs.forward_guidance_ativo["duracao_restante"] -= 1
                if gs.forward_guidance_ativo["duracao_restante"] < 0:
                    tipo_guidance = gs.forward_guidance_ativo["tipo"]
                    if tipo_guidance == "manter_selic":
                         self.add_toast("Guidance de manter SELIC cumprido com sucesso!", GREEN_SUCCESS, force_show=True)
                         gs.add_log_entry("SUCESSO: Guidance de manter SELIC foi cumprido.", GREEN_SUCCESS)
                         gs.credibilidade_bc = min(100, gs.credibilidade_bc + random.uniform(3.5, 7.0)) 
                    gs.forward_guidance_ativo = None 
        if gs.taxa_desemprego_atual <= 6.0: gs.consecutive_low_unemployment_months += 1
        else: gs.consecutive_low_unemployment_months = 0
        if gs.consecutive_low_unemployment_months >= 6 and not gs.mandate_goals["reduzir_desemprego"]: gs.mandate_goals["reduzir_desemprego"] = True; gs.add_log_entry("META ATINGIDA: Desemprego baixo!", GREEN_SUCCESS)
        if abs(gs.cambio_atual - 5.0) <= 0.15: gs.consecutive_stable_currency_months += 1
        else: gs.consecutive_stable_currency_months = 0
        if gs.consecutive_stable_currency_months >= 12 and not gs.mandate_goals["estabilidade_cambial"]: gs.mandate_goals["estabilidade_cambial"] = True; gs.add_log_entry("META ATINGIDA: Estabilidade Cambial!", GREEN_SUCCESS)
        if gs.anos_restantes_mandato < 0 : self.state = "game_over_mandate_end"; self.game_over_reason = "Seu mandato de 4 anos chegou ao fim!"; self.final_performance_summary = evaluate_performance_final(gs, False); return True
        return False

    def _process_selic_input(self):
        try:
            new_selic = float(self.selic_input_box.text)
            if 0.0 <= new_selic <= 30.0: 
                gs = self.game_state 
                
                gs.historico_acoes.append('alterar_selic')
                gs.meses_sem_acao_significativa = 0

                selic_anterior_para_guidance = gs.selic_anual 
                diferenca_selic = abs(new_selic - gs.selic_anual); current_message_parts = []; cred_change_total = 0; press_change_total = 0
                if gs.mudancas_selic_este_mes > 0: multiplicador_penalidade = gs.mudancas_selic_este_mes; cred_change_total -= 5 * multiplicador_penalidade; press_change_total += 7 * multiplicador_penalidade; current_message_parts.append("ATENCAO: Multiplas alteracoes SELIC!")
                if diferenca_selic > 5.0: cred_change_total -= (5 + (diferenca_selic - 5.0) * 1.0); press_change_total += (8 + (diferenca_selic - 5.0) * 1.5); current_message_parts.append("Mudanca brusca SELIC!")
                elif diferenca_selic > 2.0: cred_change_total -= (2 + (diferenca_selic - 2.0) * 0.5); press_change_total += (3 + (diferenca_selic - 2.0) * 1.0); current_message_parts.append("Mudanca significativa SELIC!")
                                             
                guidance_foi_resolvido_ou_quebrado_agora = False
                if gs.forward_guidance_ativo and not gs.forward_guidance_ativo.get("quebrado_este_mes"):
                    tipo_guidance = gs.forward_guidance_ativo["tipo"]
                    selic_no_anuncio = gs.forward_guidance_ativo.get("selic_no_anuncio")
                    quebrou_guidance_nesta_acao = False

                    if tipo_guidance == "manter_selic":
                        if new_selic != selic_no_anuncio:
                            quebrou_guidance_nesta_acao = True
                            self.add_toast("BC QUEBROU guidance de manter SELIC!", RED_CRITICAL, duration_ms=5000, force_show=True)
                            gs.add_log_entry("QUEBRA DE GUIDANCE: BC alterou SELIC apesar de sinalizar manutenção.", RED_CRITICAL)
                            cred_change_total -= random.uniform(12, 18) 
                    elif tipo_guidance == "inclinar_alta":
                        guidance_foi_resolvido_ou_quebrado_agora = True 
                        if new_selic < selic_anterior_para_guidance: 
                            quebrou_guidance_nesta_acao = True
                            self.add_toast("BC CONTRADISSE guidance de inclinação de alta (cortou juros)!", RED_CRITICAL, duration_ms=5000, force_show=True)
                            gs.add_log_entry("QUEBRA DE GUIDANCE: BC cortou SELIC após sinalizar viés de alta.", RED_CRITICAL)
                            cred_change_total -= random.uniform(10, 15)
                        elif new_selic == selic_anterior_para_guidance: 
                            gs.add_log_entry("Guidance de inclinação de alta não totalmente concretizado (SELIC mantida). Credibilidade pouco afetada.", YELLOW_ALERT)
                            cred_change_total -= random.uniform(2, 5) 
                        else: 
                             gs.add_log_entry("BC seguiu guidance de inclinação de alta da SELIC.", GREEN_SUCCESS)
                             cred_change_total += random.uniform(3, 6) 
                    elif tipo_guidance == "inclinar_baixa":
                        guidance_foi_resolvido_ou_quebrado_agora = True
                        if new_selic > selic_anterior_para_guidance: 
                            quebrou_guidance_nesta_acao = True
                            self.add_toast("BC CONTRADISSE guidance de inclinação de baixa (subiu juros)!", RED_CRITICAL, duration_ms=5000, force_show=True)
                            gs.add_log_entry("QUEBRA DE GUIDANCE: BC subiu SELIC após sinalizar viés de baixa.", RED_CRITICAL)
                            cred_change_total -= random.uniform(10, 15)
                        elif new_selic == selic_anterior_para_guidance: 
                            gs.add_log_entry("Guidance de inclinação de baixa não totalmente concretizado (SELIC mantida). Credibilidade pouco afetada.", YELLOW_ALERT)
                            cred_change_total -= random.uniform(2, 5)
                        else: 
                            gs.add_log_entry("BC seguiu guidance de inclinação de baixa da SELIC.", GREEN_SUCCESS)
                            cred_change_total += random.uniform(3, 6)
                    elif tipo_guidance == "fim_ciclo_alta":
                        guidance_foi_resolvido_ou_quebrado_agora = True
                        if new_selic > selic_anterior_para_guidance:
                            quebrou_guidance_nesta_acao = True
                            self.add_toast("BC REVERTEU guidance de fim de ciclo de alta!", RED_CRITICAL, duration_ms=5000, force_show=True)
                            gs.add_log_entry("QUEBRA DE GUIDANCE: BC subiu SELIC novamente após sinalizar fim do ciclo de alta.", RED_CRITICAL)
                            cred_change_total -= random.uniform(10, 15) # Penalidade maior
                        else: 
                            gs.add_log_entry("BC respeitou guidance de fim de ciclo de alta.", GREEN_SUCCESS)
                            cred_change_total += random.uniform(2.5, 5.0) 
                    elif tipo_guidance == "fim_ciclo_baixa":
                        guidance_foi_resolvido_ou_quebrado_agora = True
                        if new_selic < selic_anterior_para_guidance:
                            quebrou_guidance_nesta_acao = True
                            self.add_toast("BC REVERTEU guidance de fim de ciclo de baixa!", RED_CRITICAL, duration_ms=5000, force_show=True)
                            gs.add_log_entry("QUEBRA DE GUIDANCE: BC cortou SELIC novamente após sinalizar fim do ciclo de baixa.", RED_CRITICAL)
                            cred_change_total -= random.uniform(10, 15)
                        else: 
                            gs.add_log_entry("BC respeitou guidance de fim de ciclo de baixa.", GREEN_SUCCESS)
                            cred_change_total += random.uniform(2.5, 5.0)

                    if quebrou_guidance_nesta_acao:
                        if gs.forward_guidance_ativo : gs.forward_guidance_ativo["quebrado_este_mes"] = True 
                        gs.cooldown_forward_guidance = max(gs.cooldown_forward_guidance, 6) 
                    elif guidance_foi_resolvido_ou_quebrado_agora: # Se foi resolvido (cumprido ou parcialmente) e não quebrado agora
                        gs.forward_guidance_ativo = None 
                
                if cred_change_total != 0: gs.credibilidade_bc = max(0, min(100, gs.credibilidade_bc + cred_change_total)) 
                if press_change_total != 0: gs.pressao_politica = max(0, min(100, gs.pressao_politica + press_change_total))
                
                gs.selic_anterior_anual = gs.selic_anual; gs.selic_anual = new_selic
                tom_para_juros_longos = "neutro" 
                if gs.forward_guidance_ativo and not gs.forward_guidance_ativo.get("quebrado_este_mes"):
                    tipo_fg = gs.forward_guidance_ativo.get("tipo")
                    if tipo_fg == "manter_selic":
                        if gs.selic_anual > (gs.meta_inflacao_anual + 2.0): tom_para_juros_longos = "hawkish"
                        elif gs.selic_anual < (gs.meta_inflacao_anual + 1.0): tom_para_juros_longos = "dovish"
                    elif tipo_fg in ["inclinar_alta", "fim_ciclo_baixa"]: tom_para_juros_longos = "hawkish"
                    elif tipo_fg in ["inclinar_baixa", "fim_ciclo_alta"]: tom_para_juros_longos = "dovish"
                atualizar_expectativa_juros_longo_prazo(gs, tom_para_juros_longos)
                
                impacto_selic_exp_infl_mensal = (gs.selic_anterior_anual - gs.selic_anual) * (0.005 / 12) 
                gs.expectativa_inflacao_mercado_mensal -= impacto_selic_exp_infl_mensal; gs.expectativa_inflacao_mercado_mensal = max(0.01/12, gs.expectativa_inflacao_mercado_mensal)
                gs.mudancas_selic_este_mes += 1; log_color = YELLOW_ALERT
                if cred_change_total < 0 or press_change_total > 0 : log_color = ORANGE_WARNING 
                if new_selic > gs.selic_anterior_anual : log_color = RED_CRITICAL 
                elif new_selic < gs.selic_anterior_anual : log_color = GREEN_SUCCESS 
                final_log_msg_parts=[f"SELIC alterada para {new_selic:.2f}%!"]
                if cred_change_total!=0:final_log_msg_parts.append(f" Efeito Cred. (Ação/Guidance): {cred_change_total:+.1f}")
                if press_change_total!=0:final_log_msg_parts.append(f" Efeito Press. (Ação): {press_change_total:+.1f}")
                self.selic_input_message = f"SELIC alterada para {new_selic:.2f}%! " + " ".join(current_message_parts); gs.add_log_entry(" ".join(final_log_msg_parts), log_color)
                if self.check_critical_game_over_conditions(): return
                self.state = "game_month"; self.selic_input_box.text = ""; self.selic_input_box.active = False
            else: self.selic_input_message = "Valor SELIC invalido (0% a 30%)."
        except ValueError: self.selic_input_message = "Entrada invalida. Use numeros."
  
    def _process_compulsorio_input(self):
        message, success = acao_alterar_compulsorio(self.game_state, self.compulsorio_input_box.text)
        self.compulsorio_input_message = message
        if success:
            if self.check_critical_game_over_conditions(): return
            self.state = "actions_menu"; self.compulsorio_input_box.text = ""; self.compulsorio_input_box.active = False
        else: self.compulsorio_input_box.active = True
    
    def _handle_game_over_events(self, event):
        if self.buttons.get("game_over_back_to_main_menu") and self.buttons["game_over_back_to_main_menu"].handle_event(event):
            self.state = "main_menu"; self.initialize_game_state_data(); return False
        return True

    def _handle_main_menu_events(self, event, current_screen_buttons):
        if current_screen_buttons.get("main_menu_start_game") and current_screen_buttons["main_menu_start_game"].handle_event(event):
            self.initialize_game_state_data(); self.state = "game_month"; self.game_state.add_log_entry(f"Novo mandato! Governo: {self.game_state.tipo_governo}.", GREEN_SUCCESS); return False
        elif current_screen_buttons.get("main_menu_instructions") and current_screen_buttons["main_menu_instructions"].handle_event(event): self.state = "instructions"; return False
        elif current_screen_buttons.get("main_menu_exit_game") and current_screen_buttons["main_menu_exit_game"].handle_event(event): return "quit"
        return True

    def _handle_game_month_events(self, event, current_screen_buttons):
        btn_alter_selic = current_screen_buttons.get("month_alter_selic"); btn_advance_month = current_screen_buttons.get("month_advance_month"); btn_policy_decisions = current_screen_buttons.get("month_policy_decisions"); btn_reports_analysis = current_screen_buttons.get("month_reports_analysis"); btn_back_to_main_menu = current_screen_buttons.get("month_back_to_main_menu")
        if btn_alter_selic and btn_alter_selic.handle_event(event):
            if self.game_state.mudancas_selic_este_mes > 0: self.selic_warning_popup_active = True; self.state = "selic_warning_popup"
            else: 
                self.state = "alter_selic_screen"; self.selic_input_box.text = f"{self.game_state.selic_anual:.2f}"
                self.selic_input_box.active = True; 
                if hasattr(self.selic_input_box, 'update_surface'): self.selic_input_box.update_surface()
                self.selic_input_message = ""
            return False
        elif btn_advance_month and btn_advance_month.handle_event(event):
            if self.advance_month_logic(): return False
            return False
        elif btn_policy_decisions and btn_policy_decisions.handle_event(event): self.state = "actions_menu"; return False
        elif btn_reports_analysis and btn_reports_analysis.handle_event(event): self.state = "reports_menu"; return False
        elif btn_back_to_main_menu and btn_back_to_main_menu.handle_event(event): self.state = "main_menu"; self.initialize_game_state_data(); return False
        return True
        
    def _handle_actions_menu_events(self, event, current_screen_buttons): 
        action_performed_this_click = False; original_actions_menu_state = self.state
        btn_comunicado = current_screen_buttons.get("actions_comunicado"); btn_discurso = current_screen_buttons.get("actions_discurso"); btn_reuniao_bc = current_screen_buttons.get("actions_reuniao_bc"); btn_flexibilizar = current_screen_buttons.get("actions_flexibilizar"); btn_compulsorio = current_screen_buttons.get("actions_compulsorio"); btn_reuniao_ministro = current_screen_buttons.get("actions_reuniao_ministro"); btn_back_to_game = current_screen_buttons.get("actions_back_to_game")
        cooldown_guidance = getattr(self.game_state, 'cooldown_forward_guidance', 0)

        if btn_comunicado and btn_comunicado.handle_event(event):
            if self.game_state.cooldown_comunicado_meta == 0 and cooldown_guidance == 0:
                self.action_pending_tone = "comunicado"; self.tone_selection_message = "Tom do Comunicado:"; self.state = "select_tone_screen"
            else: self.add_toast(f"Comunicado/Guidance em cooldown.", ORANGE_WARNING)
            return False 
        elif btn_discurso and btn_discurso.handle_event(event):
            if self.game_state.cooldown_discurso_publico == 0 and cooldown_guidance == 0:
                self.action_pending_tone = "discurso"; self.tone_selection_message = "Tom do Discurso:"; self.state = "select_tone_screen"
            else: self.add_toast(f"Discurso/Guidance em cooldown.", ORANGE_WARNING)
            return False
        elif btn_reuniao_bc and btn_reuniao_bc.handle_event(event):
            msg, success, month_consumed_info = acao_reuniao_fechada(self.game_state)
            if success: action_performed_this_click = True
            else: self.add_toast(msg, ORANGE_WARNING)
            if month_consumed_info == "month_consumed" and success : 
                if self.advance_month_logic(month_consumed_by_action=True): return False
            if action_performed_this_click: self.state = "game_month"
            return False
        elif btn_flexibilizar and btn_flexibilizar.handle_event(event):
            msg, success = acao_flexibilizar_meta(self.game_state)
            if success: action_performed_this_click = True
            else: self.add_toast(msg, ORANGE_WARNING)
            if action_performed_this_click: self.state = "game_month"
            return False
        elif btn_compulsorio and btn_compulsorio.handle_event(event):
            if self.game_state.cooldown_deposito_compulsorio == 0: 
                self.state = "alter_compulsorio_screen"; self.compulsorio_input_box.text = f"{self.game_state.taxa_deposito_compulsorio*100:.0f}"
                self.compulsorio_input_box.active = True; 
                if hasattr(self.compulsorio_input_box, 'update_surface'): self.compulsorio_input_box.update_surface()
                self.compulsorio_input_message = ""
            else: self.add_toast(f"Alt. Compulsorio em cooldown ({self.game_state.cooldown_deposito_compulsorio}m).", ORANGE_WARNING)
            return False
        elif btn_reuniao_ministro and btn_reuniao_ministro.handle_event(event):
            if self.game_state.cooldown_reuniao_ministro == 0: self.state = "reuniao_ministro_submenu"
            else: self.add_toast(f"Reunião Ministro em cooldown ({self.game_state.cooldown_reuniao_ministro}m).", ORANGE_WARNING)
            return False
        elif btn_back_to_game and btn_back_to_game.handle_event(event): self.state = "game_month"; return False
        
        if self.state != original_actions_menu_state: pass
        elif action_performed_this_click:
            if self.check_critical_game_over_conditions(): return False
            self.state = "game_month"
        return True

    def _handle_reuniao_ministro_submenu_events(self, event, current_screen_buttons):
        sugestao_para_ministro = None; btn_corte = current_screen_buttons.get("reuniao_sugerir_corte"); btn_aumento = current_screen_buttons.get("reuniao_sugerir_aumento"); btn_cenario = current_screen_buttons.get("reuniao_discutir_cenario"); btn_cancelar = current_screen_buttons.get("reuniao_cancelar_pauta")
        if btn_corte and btn_corte.handle_event(event): sugestao_para_ministro = "pedir_austeridade"
        elif btn_aumento and btn_aumento.handle_event(event): sugestao_para_ministro = "sugerir_estimulo"
        elif btn_cenario and btn_cenario.handle_event(event): sugestao_para_ministro = "discutir_cenario_neutro"
        elif btn_cancelar and btn_cancelar.handle_event(event): self.state = "actions_menu"; return False
        if sugestao_para_ministro:
            msg, success = acao_reuniao_ministro(self.game_state, sugestao_para_ministro)
            if not success and msg: self.add_toast(msg, ORANGE_WARNING)
            elif success and msg: self.add_toast(msg, GREEN_SUCCESS if "receptivo" in msg.lower() else BLUE_INFO, duration_ms=4000)
            if self.check_critical_game_over_conditions(): return False
            self.state = "game_month"; return False
        return True

    def _handle_intervencao_cambial_input_events(self, event, current_screen_buttons):
        if not self.intervencao_cambial_tipo_selecionado: 
            btn_vender = current_screen_buttons.get("intervencao_escolher_vender"); btn_comprar = current_screen_buttons.get("intervencao_escolher_comprar"); btn_cancel_geral = current_screen_buttons.get("intervencao_cancelar_input") 
            if btn_vender and btn_vender.handle_event(event):
                self.intervencao_cambial_tipo_selecionado = "venda_dolares"; self.intervencao_input_box.text = ""; self.intervencao_input_box.active = True 
                if hasattr(self.intervencao_input_box, 'update_surface'): self.intervencao_input_box.update_surface()
                self.intervencao_input_message = ""; return False
            elif btn_comprar and btn_comprar.handle_event(event):
                self.intervencao_cambial_tipo_selecionado = "compra_dolares"; self.intervencao_input_box.text = ""; self.intervencao_input_box.active = True
                if hasattr(self.intervencao_input_box, 'update_surface'): self.intervencao_input_box.update_surface()
                self.intervencao_input_message = ""; return False
            elif btn_cancel_geral and btn_cancel_geral.handle_event(event):
                self.state = "actions_menu"; self.intervencao_cambial_tipo_selecionado = None; self.intervencao_input_message = ""; self.intervencao_input_box.active = False; 
                if hasattr(self.intervencao_input_box, 'update_surface'): self.intervencao_input_box.update_surface()
                return False
        else: 
            btn_confirmar = current_screen_buttons.get("intervencao_confirmar_montante"); btn_cancelar_input = current_screen_buttons.get("intervencao_cancelar_input")
            if btn_confirmar and btn_confirmar.handle_event(event):
                montante_str = self.intervencao_input_box.text; msg, success, _ = acao_intervir_cambio(self.game_state, self.intervencao_cambial_tipo_selecionado, montante_str)
                if success:
                    calcular_alvo_cambio(self.game_state) 
                    if self.game_state.cambio_atual < self.game_state.alvo_cambio_atual: self.game_state.cambio_atual = min(self.game_state.cambio_atual + PASSO_AJUSTE_CAMBIO, self.game_state.alvo_cambio_atual)
                    elif self.game_state.cambio_atual > self.game_state.alvo_cambio_atual: self.game_state.cambio_atual = max(self.game_state.cambio_atual - PASSO_AJUSTE_CAMBIO, self.game_state.alvo_cambio_atual)
                    self.game_state.cambio_atual = round(self.game_state.cambio_atual, 3)
                    self.add_toast(msg, GREEN_SUCCESS, duration_ms=4000); self.state = "game_month"; self.intervencao_cambial_tipo_selecionado = None; self.intervencao_input_box.active = False
                else: self.intervencao_input_message = msg; self.add_toast(msg, RED_CRITICAL, duration_ms=4000)
                if self.check_critical_game_over_conditions(): return False
                return False
            elif btn_cancelar_input and btn_cancelar_input.handle_event(event):
                self.state = "actions_menu"; self.intervencao_cambial_tipo_selecionado = None; self.intervencao_input_message = ""; self.intervencao_input_box.active = False; 
                if hasattr(self.intervencao_input_box, 'update_surface'): self.intervencao_input_box.update_surface()
                return False
        return True

    def _handle_select_tone_screen_events(self, event, current_screen_buttons):
        chosen_tone = None; btn_hawk = current_screen_buttons.get("tone_hawkish"); btn_dove = current_screen_buttons.get("tone_dovish"); btn_neutral = current_screen_buttons.get("tone_neutral"); btn_cancel = current_screen_buttons.get("tone_cancel")
        if btn_hawk and btn_hawk.handle_event(event): chosen_tone = "hawkish"
        elif btn_dove and btn_dove.handle_event(event): chosen_tone = "dovish"
        elif btn_neutral and btn_neutral.handle_event(event): chosen_tone = "neutro"
        elif btn_cancel and btn_cancel.handle_event(event):
            self.state = "actions_menu"; self.action_pending_tone = None; self.tone_selection_message = ""; return False
        if chosen_tone and self.action_pending_tone:
            self.pending_guidance_action_origin = self.action_pending_tone 
            self.pending_guidance_tone = chosen_tone
            self.action_pending_tone = None; self.tone_selection_message = ""
            self.state = "select_forward_guidance"; return False
        return True

    def _handle_forward_guidance_selection_events(self, event, current_screen_buttons):
        chosen_guidance_key = None; guidance_info = None
        buttons_to_check = ["guidance_nenhum", "guidance_manter_selic", "guidance_inclinar_alta", "guidance_inclinar_baixa", "guidance_fim_ciclo_alta", "guidance_fim_ciclo_baixa", "guidance_cancelar"]
        for btn_key_str in buttons_to_check:
            btn = current_screen_buttons.get(btn_key_str)
            if btn and btn.handle_event(event): chosen_guidance_key = btn_key_str; break
        if chosen_guidance_key:
            if chosen_guidance_key == "guidance_cancelar":
                self.state = "select_tone_screen"; self.action_pending_tone = self.pending_guidance_action_origin 
                self.tone_selection_message = f"Tom do {self.pending_guidance_action_origin.capitalize()}:"
                self.pending_guidance_action_origin = None; self.pending_guidance_tone = None; return False
            if chosen_guidance_key == "guidance_nenhum": guidance_info = {"tipo": "nenhum"}
            elif chosen_guidance_key == "guidance_manter_selic": guidance_info = {"tipo": "manter_selic", "duracao": 3, "selic_no_anuncio": self.game_state.selic_anual}
            elif chosen_guidance_key == "guidance_inclinar_alta": guidance_info = {"tipo": "inclinar_alta"}
            elif chosen_guidance_key == "guidance_inclinar_baixa": guidance_info = {"tipo": "inclinar_baixa"}
            elif chosen_guidance_key == "guidance_fim_ciclo_alta": guidance_info = {"tipo": "fim_ciclo_alta"}
            elif chosen_guidance_key == "guidance_fim_ciclo_baixa": guidance_info = {"tipo": "fim_ciclo_baixa"}
            if self.pending_guidance_action_origin == "comunicado":
                acao_comunicado_meta(self.game_state, self.pending_guidance_tone, guidance_info)
            elif self.pending_guidance_action_origin == "discurso":
                acao_discurso_publico(self.game_state, self.pending_guidance_tone, guidance_info)
            self.pending_guidance_action_origin = None; self.pending_guidance_tone = None
            if self.check_critical_game_over_conditions(): return False
            self.state = "game_month"; return False
        return True

    def _handle_input_confirmation_screen_events(self, event, current_screen_buttons, confirm_button_key, cancel_button_key, process_input_method, next_state_on_cancel):
        btn_confirm = current_screen_buttons.get(confirm_button_key); btn_cancel = current_screen_buttons.get(cancel_button_key)
        if btn_confirm and btn_confirm.handle_event(event): process_input_method(); return False
        elif btn_cancel and btn_cancel.handle_event(event):
            self.state = next_state_on_cancel
            if process_input_method == self._process_selic_input: 
                self.selic_input_box.text = ""; self.selic_input_box.active = False; 
                if hasattr(self.selic_input_box, 'update_surface'): self.selic_input_box.update_surface()
                self.selic_input_message = ""
            elif process_input_method == self._process_compulsorio_input: 
                self.compulsorio_input_box.text = ""; self.compulsorio_input_box.active = False; 
                if hasattr(self.compulsorio_input_box, 'update_surface'): self.compulsorio_input_box.update_surface()
                self.compulsorio_input_message = ""
            return False
        return True
        
    def _handle_reports_menu_events(self, event, current_screen_buttons):
        btn_status = current_screen_buttons.get("reports_status_bc"); btn_news = current_screen_buttons.get("reports_news_reports"); btn_graphs = current_screen_buttons.get("reports_view_graphs"); btn_forecast = current_screen_buttons.get("reports_forecast_report"); btn_advisors = current_screen_buttons.get("reports_consult_advisors"); btn_back = current_screen_buttons.get("reports_back_to_game")
        if btn_status and btn_status.handle_event(event): self.state = "status_bc"
        elif btn_news and btn_news.handle_event(event): self.state = "news_reports"
        elif btn_graphs and btn_graphs.handle_event(event):
            if len(self.game_state.historico_inflacao) >= 2: exibir_graficos_matplotlib(self.game_state)
            else: self.add_toast("Dados insuficientes para graficos (min. 2 meses).", ORANGE_WARNING)
        elif btn_forecast and btn_forecast.handle_event(event): self.state = "forecast_report"
        elif btn_advisors and btn_advisors.handle_event(event): self.state = "consult_advisors"
        elif btn_back and btn_back.handle_event(event): self.state = "game_month"
        else: return True
        return False

    def _handle_simple_back_screen_events(self, event, current_screen_buttons, back_button_key, next_state):
        btn_back = current_screen_buttons.get(back_button_key)
        if btn_back and btn_back.handle_event(event): self.state = next_state; return False
        return True

    def run(self):
        running = True; clock = pygame.time.Clock(); dt = 0
        while running:
            current_screen_buttons = {}; keys_for_state = []
            if self.state == "main_menu":
                keys_for_state = ["main_menu_start_game", "main_menu_instructions", "main_menu_exit_game"]
            elif self.state == "game_month":
                keys_for_state = ["month_alter_selic", "month_advance_month", "month_policy_decisions", "month_reports_analysis", "month_back_to_main_menu"]
            elif self.state == "instructions": keys_for_state = ["instructions_back"]
            elif self.state == "actions_menu": 
                keys_for_state = ["actions_comunicado", "actions_discurso", "actions_reuniao_bc", "actions_flexibilizar", "actions_compulsorio", "actions_reuniao_ministro", "actions_intervir_cambio", "actions_back_to_game"]
                btn_com = self.buttons.get("actions_comunicado"); btn_disc = self.buttons.get("actions_discurso"); btn_rbc = self.buttons.get("actions_reuniao_bc"); btn_flex = self.buttons.get("actions_flexibilizar"); btn_comp = self.buttons.get("actions_compulsorio"); btn_rmin = self.buttons.get("actions_reuniao_ministro"); btn_icamb = self.buttons.get("actions_intervir_cambio")
                cooldown_guidance = getattr(self.game_state, 'cooldown_forward_guidance', 0)
                if btn_com: btn_com.text = f"1. Comunicado ({self.game_state.cooldown_comunicado_meta}m)"; btn_com.is_enabled = (self.game_state.cooldown_comunicado_meta == 0 and cooldown_guidance == 0)
                if btn_disc: btn_disc.text = f"2. Discurso ({self.game_state.cooldown_discurso_publico}m)"; btn_disc.is_enabled = (self.game_state.cooldown_discurso_publico == 0 and cooldown_guidance == 0)
                if btn_rbc: btn_rbc.text = f"3. Reunião Interna ({self.game_state.cooldown_reuniao_fechada}m)"; btn_rbc.is_enabled = (self.game_state.cooldown_reuniao_fechada == 0)
                if btn_flex: btn_flex.text = f"4. Flexibilizar Meta ({self.game_state.cooldown_flexibilizar_meta}m)"; btn_flex.is_enabled = (self.game_state.cooldown_flexibilizar_meta == 0)
                if btn_comp: btn_comp.text = f"5. Alt. Compulsório ({self.game_state.cooldown_deposito_compulsorio}m)"; btn_comp.is_enabled = (self.game_state.cooldown_deposito_compulsorio == 0)
                if btn_rmin: btn_rmin.text = f"6. Reunião Ministro ({self.game_state.cooldown_reuniao_ministro}m)"; btn_rmin.is_enabled = (self.game_state.cooldown_reuniao_ministro == 0)
                if btn_icamb: cooldown_c = getattr(self.game_state, 'cooldown_intervencao_cambial', 0); btn_icamb.text = f"7. Intervir Câmbio ({cooldown_c}m)"; btn_icamb.is_enabled = (cooldown_c == 0)
            elif self.state == "select_forward_guidance": 
                 keys_for_state = ["guidance_nenhum", "guidance_manter_selic", "guidance_inclinar_alta", "guidance_inclinar_baixa", "guidance_fim_ciclo_alta", "guidance_fim_ciclo_baixa", "guidance_cancelar"]
            elif self.state == "reports_menu": keys_for_state = ["reports_status_bc", "reports_news_reports", "reports_view_graphs", "reports_forecast_report", "reports_consult_advisors", "reports_back_to_game"]
            elif self.state == "status_bc": keys_for_state = ["back_from_status"]
            elif self.state == "news_reports": keys_for_state = ["back_from_news"]
            elif self.state == "view_graphs": keys_for_state = ["back_from_graphs"]
            elif self.state == "forecast_report": keys_for_state = ["back_from_forecast"]
            elif self.state == "consult_advisors": keys_for_state = ["back_from_advisors"]
            elif self.state == "alter_selic_screen": keys_for_state = ["selic_confirm", "selic_cancel"]
            elif self.state == "selic_warning_popup": keys_for_state = ["selic_warning_confirm", "selic_warning_cancel"]
            elif self.state == "select_tone_screen": keys_for_state = ["tone_hawkish", "tone_dovish", "tone_neutral", "tone_cancel"]
            elif self.state == "alter_compulsorio_screen": keys_for_state = ["compulsorio_confirm", "compulsorio_cancel"]
            elif self.state == "reuniao_ministro_submenu": keys_for_state = ["reuniao_sugerir_corte", "reuniao_sugerir_aumento", "reuniao_discutir_cenario", "reuniao_cancelar_pauta"]
            elif self.state == "intervencao_cambial_input_screen": keys_for_state = ["intervencao_escolher_vender", "intervencao_escolher_comprar", "intervencao_confirmar_montante", "intervencao_cancelar_input"]
            elif self.state in ["game_over_demitted", "game_over_mandate_end"]: keys_for_state = ["game_over_back_to_main_menu"]
            current_screen_buttons = {k: self.buttons[k] for k in keys_for_state if k in self.buttons}
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False; continue
                if self.state in ["game_over_demitted", "game_over_mandate_end"]: self._handle_game_over_events(event); continue
                if self.event_popup_data: 
                    if self.handle_event_popup_input(event):
                        if self.state in ["game_over_demitted", "game_over_mandate_end"]: continue
                    if self.event_popup_data: continue
                if self.selic_warning_popup_active:
                    _btn_confirm_warn = self.buttons.get("selic_warning_confirm"); _btn_cancel_warn = self.buttons.get("selic_warning_cancel")
                    if _btn_confirm_warn and _btn_confirm_warn.handle_event(event):
                        self.selic_warning_popup_active = False; self.state = "alter_selic_screen"; self.selic_input_box.active = True
                        if hasattr(self.selic_input_box, 'update_surface'): self.selic_input_box.update_surface()
                        self.selic_input_message = "CUIDADO: Multiplas alterações SELIC."
                    elif _btn_cancel_warn and _btn_cancel_warn.handle_event(event):
                        self.selic_warning_popup_active = False; self.state = "game_month"; self.selic_input_box.text = ""; self.selic_input_box.active = False
                        if hasattr(self.selic_input_box, 'update_surface'): self.selic_input_box.update_surface()
                    continue 
                
                process_event_for_other_ui = True 
                if self.state == "alter_selic_screen" and self.selic_input_box.active:
                    selic_textbox_result = self.selic_input_box.handle_event(event)
                    if selic_textbox_result is True: self._process_selic_input(); process_event_for_other_ui = False 
                    elif selic_textbox_result is False and event.type == pygame.KEYDOWN: process_event_for_other_ui = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and self.selic_input_box.rect.collidepoint(event.pos): process_event_for_other_ui = False
                elif self.state == "alter_compulsorio_screen" and self.compulsorio_input_box.active:
                    comp_textbox_result = self.compulsorio_input_box.handle_event(event)
                    if comp_textbox_result is True: self._process_compulsorio_input(); process_event_for_other_ui = False
                    elif comp_textbox_result is False and event.type == pygame.KEYDOWN: process_event_for_other_ui = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and self.compulsorio_input_box.rect.collidepoint(event.pos): process_event_for_other_ui = False
                elif self.state == "intervencao_cambial_input_screen" and self.intervencao_cambial_tipo_selecionado and self.intervencao_input_box.active:
                    interv_textbox_result = self.intervencao_input_box.handle_event(event)
                    if interv_textbox_result is True and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN : process_event_for_other_ui = False 
                    elif interv_textbox_result is False and event.type == pygame.KEYDOWN: process_event_for_other_ui = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and self.intervencao_input_box.rect.collidepoint(event.pos): process_event_for_other_ui = False
                
                action_result = True 
                if process_event_for_other_ui:
                    if self.state == "main_menu": action_result = self._handle_main_menu_events(event, current_screen_buttons)
                    elif self.state == "game_month": action_result = self._handle_game_month_events(event, current_screen_buttons)
                    elif self.state == "instructions": action_result = self._handle_simple_back_screen_events(event, current_screen_buttons, "instructions_back", "main_menu")
                    elif self.state == "actions_menu": 
                        if self.buttons.get("actions_intervir_cambio") and self.buttons["actions_intervir_cambio"].handle_event(event):
                            if hasattr(self.game_state, 'cooldown_intervencao_cambial') and self.game_state.cooldown_intervencao_cambial == 0:
                                self.state = "intervencao_cambial_input_screen"; self.intervencao_cambial_tipo_selecionado = None 
                                self.intervencao_input_box.text = ""; self.intervencao_input_box.active = False 
                                if hasattr(self.intervencao_input_box, 'update_surface'): self.intervencao_input_box.update_surface()
                                self.intervencao_input_message = ""
                            else:
                                cooldown = getattr(self.game_state, 'cooldown_intervencao_cambial', 'N/A')
                                self.add_toast(f"Intervenção Cambial em cooldown ({cooldown}m).", ORANGE_WARNING)
                            action_result = False 
                        else: action_result = self._handle_actions_menu_events(event, current_screen_buttons)
                    elif self.state == "select_tone_screen": action_result = self._handle_select_tone_screen_events(event, current_screen_buttons)
                    elif self.state == "select_forward_guidance": action_result = self._handle_forward_guidance_selection_events(event, current_screen_buttons)
                    elif self.state == "intervencao_cambial_input_screen": action_result = self._handle_intervencao_cambial_input_events(event, current_screen_buttons)
                    elif self.state == "reuniao_ministro_submenu": action_result = self._handle_reuniao_ministro_submenu_events(event, current_screen_buttons)
                    elif self.state == "alter_compulsorio_screen": action_result = self._handle_input_confirmation_screen_events(event, current_screen_buttons, "compulsorio_confirm", "compulsorio_cancel", self._process_compulsorio_input, "actions_menu")
                    elif self.state == "reports_menu": action_result = self._handle_reports_menu_events(event, current_screen_buttons)
                    elif self.state == "status_bc": action_result = self._handle_simple_back_screen_events(event, current_screen_buttons, "back_from_status", "reports_menu")
                    elif self.state == "news_reports": action_result = self._handle_simple_back_screen_events(event, current_screen_buttons, "back_from_news", "reports_menu")
                    elif self.state == "view_graphs": action_result = self._handle_simple_back_screen_events(event, current_screen_buttons, "back_from_graphs", "reports_menu")
                    elif self.state == "forecast_report": action_result = self._handle_simple_back_screen_events(event, current_screen_buttons, "back_from_forecast", "reports_menu")
                    elif self.state == "consult_advisors": action_result = self._handle_simple_back_screen_events(event, current_screen_buttons, "back_from_advisors", "reports_menu")
                    elif self.state == "alter_selic_screen": action_result = self._handle_input_confirmation_screen_events(event, current_screen_buttons, "selic_confirm", "selic_cancel", self._process_selic_input, "game_month")
                if action_result == "quit": running = False
            if not running: break
            if self.state == "reports_menu":
                can_view_graphs = len(self.game_state.historico_inflacao) >= 2
                if "reports_view_graphs" in self.buttons: self.buttons["reports_view_graphs"].is_enabled = can_view_graphs
            elif "reports_view_graphs" in self.buttons: self.buttons["reports_view_graphs"].is_enabled = True
            current_draw_func = self.screen_draw_functions.get(self.state)
            if current_draw_func: current_draw_func()
            if self.event_popup_data: draw_event_popup(self.screen, self.event_popup_data, self.event_popup_message, self.event_popup_options, self.buttons_for_popup)
            elif self.selic_warning_popup_active: draw_selic_warning_popup(self.screen, self.buttons)
            dt_seconds = dt / 1000.0
            for toast_item in list(self.active_toasts):
                if not toast_item.update(dt_seconds): self.active_toasts.remove(toast_item)
            draw_toasts(self.screen, self.active_toasts)
            pygame.display.flip()
            dt = clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game_controller = GameController()
    game_controller.run()
    