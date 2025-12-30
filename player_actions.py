# player_actions.py
import random
from config import BLUE_INFO, GREEN_SUCCESS, RED_CRITICAL, YELLOW_ALERT, ORANGE_WARNING, WHITE

def aplicar_impactos_comunicacao(estado, cred_change, press_change, exp_inf_mensal_change):
    """Aplica impactos comuns de comunicação e garante limites."""
    estado.credibilidade_bc += cred_change
    estado.pressao_politica += press_change
    estado.expectativa_inflacao_mercado_mensal += exp_inf_mensal_change
    
    estado.credibilidade_bc = round(max(0, min(100, estado.credibilidade_bc)), 1)
    estado.pressao_politica = round(max(0, min(100, estado.pressao_politica)), 1)
    estado.expectativa_inflacao_mercado_mensal = round(max(-1.0/12, min(5.0/12, estado.expectativa_inflacao_mercado_mensal)), 6)


def acao_comunicado_meta(estado, tom="neutro", guidance_info=None):
    if estado.cooldown_comunicado_meta > 0:
        return f"Comunicado sobre metas em cooldown ({estado.cooldown_comunicado_meta}m).", False

    estado.historico_acoes.append('comunicado_meta')
    estado.meses_sem_acao_significativa = 0

    cred_factor = estado.credibilidade_bc / 100.0
    cred_change_base = 0; press_change_base = 0; exp_inf_mensal_change_base = 0
    log_parts = [f"Comunicado ({tom.capitalize()}):"]

    if tom == "hawkish":
        cred_change_base += random.uniform(0.5, 1.2) * (cred_factor if estado.inflacao_atual_mensal * 12 > estado.meta_inflacao_anual else 0.6)
        press_change_base += random.uniform(0.1, 0.5)
        exp_inf_mensal_change_base -= random.uniform(0.00025, 0.0005) * (0.5 + cred_factor) 
    elif tom == "dovish":
        if estado.inflacao_atual_mensal * 12 > estado.meta_inflacao_anual + estado.banda_inflacao_anual:
            cred_change_base -= random.uniform(0.5, 1.5) * (1.2 - cred_factor)
        else:
            cred_change_base += random.uniform(0.2, 0.8) * cred_factor
        press_change_base -= random.uniform(0.1, 0.5)
        exp_inf_mensal_change_base += random.uniform(0.00015, 0.00035) * (1.1 - cred_factor)
    else: # Neutro
        cred_change_base += random.uniform(-0.2, 0.2)

    msg_guidance_retorno = "."
    cred_g_eff = 0; press_g_eff = 0; exp_inf_mensal_g_eff = 0
    
    if guidance_info and guidance_info["tipo"] != "nenhum":
        if hasattr(estado, 'cooldown_forward_guidance') and estado.cooldown_forward_guidance > 0:
            msg_guidance_retorno = f" (Guidance não emitido: cooldown {estado.cooldown_forward_guidance}m)"
        else:
            tipo_g = guidance_info["tipo"]
            duracao_g = guidance_info.get("duracao", 0)
            selic_anuncio_g = guidance_info.get("selic_no_anuncio", estado.selic_anual)

            estado.forward_guidance_ativo = {
                "tipo": tipo_g, "selic_no_anuncio": selic_anuncio_g,
                "duracao_total": duracao_g, "duracao_restante": duracao_g,
                "mes_anuncio_absoluto": (estado.ano_atual * 12 + estado.mes_atual),
                "quebrado_este_mes": False
            }
            estado.cooldown_forward_guidance = 3
            
            msg_guidance_retorno = f" Sinal.Futura: {tipo_g.replace('_', ' ').capitalize()}"
            if duracao_g > 0: msg_guidance_retorno += f" por {duracao_g}m."
            
            inconsistencia_penalidade = 0
            if (tom == "hawkish" and tipo_g in ["inclinar_baixa", "fim_ciclo_alta", "manter_selic"] and estado.selic_anual < estado.meta_inflacao_anual + 1.0) or \
               (tom == "dovish" and tipo_g in ["inclinar_alta", "fim_ciclo_baixa", "manter_selic"] and estado.selic_anual > estado.meta_inflacao_anual + 2.0):
                inconsistencia_penalidade = -random.uniform(1.5, 3.0)
                log_parts.append("[Tom inconsistente com Guidance!]")

            if tipo_g == "manter_selic":
                cred_g_eff += (1.8 * cred_factor) + inconsistencia_penalidade
                if (estado.selic_anual > estado.meta_inflacao_anual + 1.0 and estado.inflacao_atual_mensal*12 > estado.meta_inflacao_anual + estado.banda_inflacao_anual*0.5) or \
                   (estado.selic_anual < estado.meta_inflacao_anual + 1.5 and estado.inflacao_atual_mensal*12 < estado.meta_inflacao_anual - estado.banda_inflacao_anual*0.5):
                    exp_inf_mensal_g_eff -= random.uniform(0.0004, 0.0008) * cred_factor
                else:
                    cred_g_eff -= random.uniform(0.5, 1.5); exp_inf_mensal_g_eff += random.uniform(0.0002, 0.0004)
            elif tipo_g == "inclinar_alta":
                cred_g_eff += (1.2 * cred_factor) + inconsistencia_penalidade
                exp_inf_mensal_g_eff -= random.uniform(0.0006, 0.0012) * cred_factor
                press_g_eff += random.uniform(0.3, 1.2) if estado.tipo_governo == "Desenvolvimentista" else 0.1
            elif tipo_g == "inclinar_baixa":
                cred_g_eff += (0.8 * cred_factor) + inconsistencia_penalidade
                exp_inf_mensal_g_eff += random.uniform(0.0005, 0.0010) * (1.2 - cred_factor)
                press_g_eff -= random.uniform(0.3, 1.2)
            elif tipo_g == "fim_ciclo_alta":
                cred_g_eff += (1.5 * cred_factor) + inconsistencia_penalidade
                exp_inf_mensal_g_eff -= random.uniform(0.0002, 0.0004) * cred_factor
            elif tipo_g == "fim_ciclo_baixa":
                cred_g_eff += (1.2 * cred_factor) + inconsistencia_penalidade
                exp_inf_mensal_g_eff += random.uniform(0.0001, 0.0003) * (1.1 - cred_factor)
    else:
        msg_guidance_retorno = "."
        if guidance_info and guidance_info["tipo"] == "nenhum":
            log_parts.append(" (Sem orientação futura específica.)")
            if estado.forward_guidance_ativo and getattr(estado, 'cooldown_forward_guidance', 1) == 0 :
                log_parts.append(" [Guidance anterior cancelado.]")
                estado.forward_guidance_ativo = None
        elif not guidance_info : 
             log_parts.append(" (Sem orientação futura específica.)")

    aplicar_impactos_comunicacao(estado, cred_change_base + cred_g_eff, press_change_base + press_g_eff, exp_inf_mensal_change_base + exp_inf_mensal_g_eff)
    
    if guidance_info and guidance_info["tipo"] != "nenhum" and (not hasattr(estado, 'cooldown_forward_guidance') or estado.cooldown_forward_guidance == 3):
        if abs(cred_g_eff) > 0.01: log_parts.append(f"GuidCred:{cred_g_eff:+.1f}")
        if abs(press_g_eff) > 0.01: log_parts.append(f"GuidPress:{press_g_eff:+.1f}")
        if abs(exp_inf_mensal_g_eff*12) > 0.01: log_parts.append(f"GuidExpInf:{(exp_inf_mensal_g_eff*12):+.2f}%a.a.")

    estado.cooldown_comunicado_meta = 3 
    estado.add_log_entry(" ".join(log_parts), BLUE_INFO)
    return f"Comunicado ({tom}) emitido{msg_guidance_retorno}", True

def acao_discurso_publico(estado, tom="neutro", guidance_info=None):
    if estado.cooldown_discurso_publico > 0:
        return f"Discurso publico em cooldown ({estado.cooldown_discurso_publico}m).", False

    estado.historico_acoes.append('discurso_publico')
    estado.meses_sem_acao_significativa = 0

    cred_factor = estado.credibilidade_bc / 100.0
    chance_sucesso_tom = max(0.1, min(0.9, 0.50 + (cred_factor * 0.4) - (estado.pressao_politica / 250.0)))
    msg_tom_discurso = ""; mod_cred_sucesso_tom_mult=1.0; mod_pressao_sucesso_tom_mult=1.0
    mod_cred_falha_tom_mult=1.0; mod_pressao_falha_tom_mult=1.0; exp_inf_mensal_change_tom_discurso = 0

    if tom == "hawkish": msg_tom_discurso=f"Discurso (Hawkish): "; mod_cred_sucesso_tom_mult=1.2; mod_pressao_falha_tom_mult=1.1; exp_inf_mensal_change_tom_discurso = -random.uniform(0.0005, 0.0010) * (0.6 + cred_factor)
    elif tom == "dovish": msg_tom_discurso=f"Discurso (Dovish): "; mod_pressao_sucesso_tom_mult=1.2; mod_cred_falha_tom_mult=1.1; exp_inf_mensal_change_tom_discurso = random.uniform(0.0004, 0.0007) * (1.2 - cred_factor)
    else: msg_tom_discurso=f"Discurso (Neutro): "; exp_inf_mensal_change_tom_discurso = random.uniform(-0.0003, 0.0003)

    resultado_msg_tom = ""; log_color_tom = YELLOW_ALERT
    cred_change_tom_discurso = 0; press_change_tom_discurso = 0

    if random.random() < chance_sucesso_tom:
        cred_change_tom_discurso = random.uniform(2.5, 5.0) * mod_cred_sucesso_tom_mult * (0.5 + cred_factor)
        press_change_tom_discurso = -random.uniform(1.5, 4.0) * mod_pressao_sucesso_tom_mult
        resultado_msg_tom = f"{msg_tom_discurso}Discurso bem recebido!"
        log_color_tom = GREEN_SUCCESS
    else:
        cred_change_tom_discurso = -random.uniform(2.0, 4.5) * mod_cred_falha_tom_mult * (1.3 - cred_factor)
        press_change_tom_discurso = random.uniform(2.5, 7.0) * mod_pressao_falha_tom_mult
        resultado_msg_tom = f"{msg_tom_discurso}Discurso gerou controvérsia."
        log_color_tom = ORANGE_WARNING
    
    log_discurso_parts = [resultado_msg_tom]
    if abs(cred_change_tom_discurso) > 0.01 : log_discurso_parts.append(f"TomCred:{cred_change_tom_discurso:+.1f}")
    if abs(press_change_tom_discurso) > 0.01 : log_discurso_parts.append(f"TomPress:{press_change_tom_discurso:+.1f}")
    if abs(exp_inf_mensal_change_tom_discurso*12) > 0.01: log_discurso_parts.append(f"TomExpInf:{(exp_inf_mensal_change_tom_discurso*12):+.2f}%a.a.")
    
    msg_guidance_discurso_retorno = "."
    cred_g_eff_disc = 0; press_g_eff_disc = 0; exp_inf_mensal_g_eff_disc = 0
    
    if guidance_info and guidance_info["tipo"] != "nenhum":
        if hasattr(estado, 'cooldown_forward_guidance') and estado.cooldown_forward_guidance > 0:
            msg_guidance_discurso_retorno = f" (Guidance não emitido: cooldown {estado.cooldown_forward_guidance}m)."
            log_discurso_parts.append(msg_guidance_discurso_retorno)
        else:
            tipo_g = guidance_info["tipo"]
            duracao_g = guidance_info.get("duracao", 0)
            selic_anuncio_g = guidance_info.get("selic_no_anuncio", estado.selic_anual)
            estado.forward_guidance_ativo = {
                "tipo": tipo_g, "selic_no_anuncio": selic_anuncio_g,
                "duracao_total": duracao_g, "duracao_restante": duracao_g,
                "mes_anuncio_absoluto": (estado.ano_atual * 12 + estado.mes_atual),
                "quebrado_este_mes": False
            }
            estado.cooldown_forward_guidance = 3
            msg_guidance_discurso_retorno = f" Adic. Sinalização: {tipo_g.replace('_', ' ').capitalize()}"
            if duracao_g > 0: msg_guidance_discurso_retorno += f" por {duracao_g}m."
            log_discurso_parts.append(msg_guidance_discurso_retorno)

            inconsistencia_penalidade_disc = 0
            if (tom == "hawkish" and tipo_g in ["inclinar_baixa", "fim_ciclo_alta", "manter_selic"] and estado.selic_anual < estado.meta_inflacao_anual + 1.0) or \
               (tom == "dovish" and tipo_g in ["inclinar_alta", "fim_ciclo_baixa", "manter_selic"] and estado.selic_anual > estado.meta_inflacao_anual + 2.0):
                inconsistencia_penalidade_disc = -random.uniform(2.5, 5.0)
                log_discurso_parts.append("[Guidance FORTEMENTE inconsistente com Tom do Discurso!]")

            if tipo_g == "manter_selic":
                cred_g_eff_disc += (2.5 * cred_factor) + inconsistencia_penalidade_disc
                if (estado.selic_anual > estado.meta_inflacao_anual + 1.0 and estado.inflacao_atual_mensal*12 > estado.meta_inflacao_anual + estado.banda_inflacao_anual*0.5) or \
                   (estado.selic_anual < estado.meta_inflacao_anual + 1.5 and estado.inflacao_atual_mensal*12 < estado.meta_inflacao_anual - estado.banda_inflacao_anual*0.5):
                    exp_inf_mensal_g_eff_disc -= random.uniform(0.0006, 0.0010) * cred_factor
                else: cred_g_eff_disc -= random.uniform(1.5, 2.5); exp_inf_mensal_g_eff_disc += random.uniform(0.0003, 0.0005)
            elif tipo_g == "inclinar_alta":
                cred_g_eff_disc += (1.8 * cred_factor) + inconsistencia_penalidade_disc; exp_inf_mensal_g_eff_disc -= random.uniform(0.0008, 0.0015) * cred_factor
                press_g_eff_disc += random.uniform(0.5, 1.8) if estado.tipo_governo == "Desenvolvimentista" else 0.2
            elif tipo_g == "inclinar_baixa":
                cred_g_eff_disc += (1.2 * cred_factor) + inconsistencia_penalidade_disc; exp_inf_mensal_g_eff_disc += random.uniform(0.0006, 0.0012) * (1.2 - cred_factor)
                press_g_eff_disc -= random.uniform(0.5, 1.8)
            elif tipo_g == "fim_ciclo_alta":
                cred_g_eff_disc += (2.2 * cred_factor) + inconsistencia_penalidade_disc; exp_inf_mensal_g_eff_disc -= random.uniform(0.0003, 0.0006) * cred_factor
            elif tipo_g == "fim_ciclo_baixa":
                cred_g_eff_disc += (1.8 * cred_factor) + inconsistencia_penalidade_disc; exp_inf_mensal_g_eff_disc += random.uniform(0.0002, 0.0005) * (1.1 - cred_factor)
            
            if abs(cred_g_eff_disc) > 0.01: log_discurso_parts.append(f"GuidCred:{cred_g_eff_disc:+.1f}")
            if abs(press_g_eff_disc) > 0.01: log_discurso_parts.append(f"GuidPress:{press_g_eff_disc:+.1f}")
            if abs(exp_inf_mensal_g_eff_disc*12) > 0.01: log_discurso_parts.append(f"GuidExpInf:{(exp_inf_mensal_g_eff_disc*12):+.2f}%a.a.")
    else:
        msg_guidance_discurso_retorno = "."
        if guidance_info and guidance_info["tipo"] == "nenhum":
            log_discurso_parts.append(" (Sem orientação futura específica.)")
            if estado.forward_guidance_ativo and getattr(estado, 'cooldown_forward_guidance', 1) == 0:
                log_discurso_parts.append(" [Guidance anterior cancelado.]")
                estado.forward_guidance_ativo = None
        elif not guidance_info:
            log_discurso_parts.append(" (Sem orientação futura específica.)")

    aplicar_impactos_comunicacao(estado, cred_change_tom_discurso + cred_g_eff_disc, 
                                 press_change_tom_discurso + press_g_eff_disc, 
                                 exp_inf_mensal_change_tom_discurso + exp_inf_mensal_g_eff_disc)
    
    estado.cooldown_discurso_publico = 6
    final_log_color_discurso = log_color_tom
    if guidance_info and guidance_info["tipo"] != "nenhum" and (not hasattr(estado, 'cooldown_forward_guidance') or estado.cooldown_forward_guidance == 3):
        final_log_color_discurso = BLUE_INFO
        
    estado.add_log_entry(" ".join(log_discurso_parts), final_log_color_discurso)
    return f"{resultado_msg_tom}{msg_guidance_discurso_retorno}", True

def acao_reuniao_fechada(estado):
    if estado.cooldown_reuniao_fechada > 0:
        return f"Reuniao interna do BC está em cooldown ({estado.cooldown_reuniao_fechada}m restantes).", False, None 

    estado.historico_acoes.append('reuniao_fechada')
    estado.meses_sem_acao_significativa = 0

    custo_cred = random.uniform(1, 2) 
    custo_pressao = random.uniform(1, 2) 
    
    estado.credibilidade_bc = max(0, min(100, estado.credibilidade_bc - custo_cred))
    estado.pressao_politica = max(0, min(100, estado.pressao_politica + custo_pressao))
    estado.cooldown_reuniao_fechada = 12 
    
    log_msg = f"Reuniao Fechada (BC). Mes dedicado a planejamento interno. Cred:{-custo_cred:.1f}, Pressao:{+custo_pressao:.1f}."
    estado.add_log_entry(log_msg, YELLOW_ALERT)
    return f"Mes dedicado a planejamento interno do BC. Cred:{-custo_cred:.1f}, Pressao:{+custo_pressao:.1f}.", True, "month_consumed"

def acao_flexibilizar_meta(estado):
    if estado.cooldown_flexibilizar_meta > 0:
        return f"Flexibilizacao da Meta de Inflacao está em cooldown ({estado.cooldown_flexibilizar_meta}m restantes).", False
    
    estado.historico_acoes.append('flexibilizar_meta')
    estado.meses_sem_acao_significativa = 0

    penalidade_cred = random.uniform(15, 25)
    aumento_pressao = random.uniform(10, 20) 
    
    estado.credibilidade_bc = max(0, min(100, estado.credibilidade_bc - penalidade_cred))
    estado.pressao_politica = max(0, min(100, estado.pressao_politica + aumento_pressao))
    
    estado.banda_inflacao_anual = estado.banda_inflacao_original + 1.0 
    estado.meses_banda_flexibilizada = 6 
    estado.cooldown_flexibilizar_meta = 24 
    
    log_msg = (f"Meta de Inflacao Flexibilizada! Nova banda: +/-{estado.banda_inflacao_anual:.1f}% "
               f"(por {estado.meses_banda_flexibilizada}m). Cred:{-penalidade_cred:.1f}, Pressao:{+aumento_pressao:.1f}.")
    estado.add_log_entry(log_msg, RED_CRITICAL)
    return (f"Meta de Inflacao Flexibilizada! Banda agora e de +/-{estado.banda_inflacao_anual:.1f}% "
            f"por {estado.meses_banda_flexibilizada} meses. Credibilidade: {estado.credibilidade_bc:.0f}, "
            f"Pressao Politica: {estado.pressao_politica:.0f}."), True

def acao_alterar_compulsorio(estado, nova_taxa_compulsorio_input_str):
    if estado.cooldown_deposito_compulsorio > 0:
        return f"Alteracao do Deposito Compulsorio está em cooldown ({estado.cooldown_deposito_compulsorio}m restantes).", False

    try:
        nova_taxa_percentual = float(nova_taxa_compulsorio_input_str)
        if not (10.0 <= nova_taxa_percentual <= 45.0): 
            return "Taxa de Compulsorio invalida (deve ser entre 10% e 45%).", False
        nova_taxa_decimal = nova_taxa_percentual / 100.0
    except ValueError:
        return "Entrada invalida para taxa de compulsório. Use numeros.", False

    estado.historico_acoes.append('alterar_compulsorio')
    estado.meses_sem_acao_significativa = 0

    diferenca_compulsorio = abs(nova_taxa_decimal - estado.taxa_deposito_compulsorio)
    cred_change = 0
    press_change = 0
    msg_impacto_adicional = ""

    if diferenca_compulsorio > 0.10: 
        cred_change = -random.uniform(3, 6)
        press_change = random.uniform(2, 5)
        msg_impacto_adicional = "Mudanca brusca no compulsório gerou instabilidade e surpresa no mercado."
    elif diferenca_compulsorio > 0.05: 
        cred_change = -random.uniform(1, 3)
        press_change = random.uniform(1, 2)
        msg_impacto_adicional = "Mudanca significativa no compulsório notada pelo mercado."
    
    estado.taxa_deposito_compulsorio = round(nova_taxa_decimal, 2)
    estado.credibilidade_bc = max(0, min(100, estado.credibilidade_bc + cred_change))
    estado.pressao_politica = max(0, min(100, estado.pressao_politica + press_change))
    estado.cooldown_deposito_compulsorio = 4 

    log_msg = f"Deposito Compulsorio alterado para {estado.taxa_deposito_compulsorio*100:.0f}%."
    if cred_change != 0 or press_change != 0:
        log_msg += f" Impactos: Cred {cred_change:+.1f}, Pressao {press_change:+.1f}."
    if msg_impacto_adicional:
        log_msg += f" ({msg_impacto_adicional})"
    
    estado.add_log_entry(log_msg, BLUE_INFO)
    return f"Deposito Compulsorio alterado para {estado.taxa_deposito_compulsorio*100:.0f}%. {msg_impacto_adicional}", True

def acao_reuniao_ministro(estado, tipo_sugestao):
    if estado.cooldown_reuniao_ministro > 0:
        return f"Reunião com Ministro da Fazenda está em cooldown ({estado.cooldown_reuniao_ministro}m restantes).", False

    estado.historico_acoes.append('reuniao_ministro')
    estado.meses_sem_acao_significativa = 0

    perfil_ministro = estado.tipo_ministro_fazenda 
    cred_bc = estado.credibilidade_bc
    
    cred_change = -random.uniform(0.2, 1.0) 
    press_change = random.uniform(0.5, 1.5) 

    chance_sucesso_base = 0.30 + (cred_bc / 300.0) 
    
    modificador_chance = 0.0
    modificador_cred_sucesso = 0.0
    modificador_pressao_sucesso = 0.0
    modificador_cred_falha = 0.0
    modificador_pressao_falha = 0.0
    
    mensagem_acao = f"BC sugere ao Ministro ({perfil_ministro}): "
    feedback_especifico = ""

    if tipo_sugestao == "pedir_austeridade":
        mensagem_acao += "Corte de Gastos / Austeridade Fiscal."
        if perfil_ministro == "Liberal":
            modificador_chance = 0.35 
            modificador_cred_sucesso = random.uniform(1, 3)
            modificador_pressao_sucesso = -random.uniform(2, 5) 
            modificador_cred_falha = -random.uniform(0.5, 1) 
            modificador_pressao_falha = random.uniform(1, 2)
            feedback_especifico = "Ministro Liberal vê a sugestão com bons olhos."
        elif perfil_ministro == "Desenvolvimentista":
            modificador_chance = -0.25 
            modificador_cred_sucesso = random.uniform(2, 4) 
            modificador_pressao_sucesso = random.uniform(3, 6) 
            modificador_cred_falha = -random.uniform(2, 4) 
            modificador_pressao_falha = random.uniform(5, 10) 
            feedback_especifico = "Ministro Desenvolvimentista demonstra forte resistência à austeridade."
        elif perfil_ministro == "Pragmatico":
            modificador_chance = 0.10 
            if estado.divida_publica_pib > 85: modificador_chance += 0.20
            if estado.inflacao_atual_mensal * 12 > estado.meta_inflacao_anual + 2: modificador_chance += 0.10
            modificador_cred_sucesso = random.uniform(1, 2.5)
            modificador_pressao_sucesso = -random.uniform(1, 3)
            modificador_cred_falha = -random.uniform(1, 2)
            modificador_pressao_falha = random.uniform(2, 4)
            feedback_especifico = "Ministro Pragmático analisa a sugestão com base nos indicadores."

    elif tipo_sugestao == "sugerir_estimulo":
        mensagem_acao += "Aumento de Investimentos / Estímulo Econômico."
        if perfil_ministro == "Liberal":
            modificador_chance = -0.20 
            if estado.pib_crescimento_atual_mensal * 12 < -1.0: modificador_chance += 0.15 
            modificador_cred_sucesso = random.uniform(1, 2)
            modificador_pressao_sucesso = random.uniform(0, 2) 
            modificador_cred_falha = -random.uniform(1.5, 3)
            modificador_pressao_falha = random.uniform(3, 6)
            feedback_especifico = "Ministro Liberal é cético quanto a mais gastos, mas pode ceder em crise."
        elif perfil_ministro == "Desenvolvimentista":
            modificador_chance = 0.40 
            modificador_cred_sucesso = random.uniform(0.5, 1.5)
            modificador_pressao_sucesso = -random.uniform(3, 6)
            modificador_cred_falha = -random.uniform(0.5, 1)
            modificador_pressao_falha = random.uniform(1, 3)
            feedback_especifico = "Ministro Desenvolvimentista apoia estímulos para o crescimento."
        elif perfil_ministro == "Pragmatico":
            modificador_chance = 0.15
            if estado.pib_crescimento_atual_mensal * 12 < 1.0 : modificador_chance += 0.20 
            if estado.taxa_desemprego_atual > 9.0 : modificador_chance += 0.10
            modificador_cred_sucesso = random.uniform(1, 2)
            modificador_pressao_sucesso = -random.uniform(1, 4)
            modificador_cred_falha = -random.uniform(1, 2.5)
            modificador_pressao_falha = random.uniform(2, 5)
            feedback_especifico = "Ministro Pragmático considera o estímulo se a economia estiver fraca."

    elif tipo_sugestao == "discutir_cenario_neutro":
        mensagem_acao += "Discussão Geral sobre o Cenário Econômico."
        modificador_chance = -0.10 
        modificador_cred_sucesso = random.uniform(0.5, 1.5) 
        modificador_pressao_sucesso = -random.uniform(0.5, 2) 
        modificador_cred_falha = -random.uniform(0, 0.5)
        modificador_pressao_falha = random.uniform(0, 1)
        feedback_especifico = "Conversa neutra para alinhar visões com o Ministro."

    chance_final_sucesso = max(0.05, min(0.95, chance_sucesso_base + modificador_chance))
    
    sucesso_influencia = random.random() < chance_final_sucesso
    mensagem_final_reuniao = ""
    cor_log_reuniao = YELLOW_ALERT

    if sucesso_influencia:
        cred_change += modificador_cred_sucesso
        press_change += modificador_pressao_sucesso
        mensagem_final_reuniao = f"Ministro pareceu receptivo à sugestão. {feedback_especifico}"
        cor_log_reuniao = GREEN_SUCCESS
        
        if tipo_sugestao == "pedir_austeridade":
            estado.governo_postura_fiscal_influencia = "contracionista"
            estado.influencia_duracao = 2 
        elif tipo_sugestao == "sugerir_estimulo":
            estado.governo_postura_fiscal_influencia = "expansionista"
            estado.influencia_duracao = 2
        
    else: 
        cred_change += modificador_cred_falha
        press_change += modificador_pressao_falha
        mensagem_final_reuniao = f"Ministro ouviu, mas não demonstrou concordância com a pauta. {feedback_especifico}"
        cor_log_reuniao = ORANGE_WARNING if tipo_sugestao != "discutir_cenario_neutro" else YELLOW_ALERT
        if perfil_ministro == "Desenvolvimentista" and tipo_sugestao == "pedir_austeridade": cor_log_reuniao = RED_CRITICAL
        if perfil_ministro == "Liberal" and tipo_sugestao == "sugerir_estimulo": cor_log_reuniao = RED_CRITICAL

    estado.credibilidade_bc = round(max(0, min(100, estado.credibilidade_bc + cred_change)), 1)
    estado.pressao_politica = round(max(0, min(100, estado.pressao_politica + press_change)), 1)
    estado.cooldown_reuniao_ministro = 6

    log_completo = (f"{mensagem_acao} {mensagem_final_reuniao} "
                    f"(CredBC: {cred_change:+.1f}, PressaoP: {press_change:+.1f})")
    estado.add_log_entry(log_completo, cor_log_reuniao)
    
    return mensagem_final_reuniao, True


def acao_intervir_cambio(estado, tipo_intervencao, montante_float_str):
    if not hasattr(estado, 'cooldown_intervencao_cambial'):
        estado.cooldown_intervencao_cambial = 0
    if not hasattr(estado, 'reservas_internacionais'):
        estado.reservas_internacionais = 300.0 

    if estado.cooldown_intervencao_cambial > 0:
        return f"Intervenção cambial em cooldown ({estado.cooldown_intervencao_cambial}m restantes).", False, "COOLDOWN"

    try:
        montante_intervencao = float(montante_float_str)
    except ValueError:
        return "Montante inválido. Use números (ex: 1.5 para 1.5 bilhões).", False, "INVALID_INPUT"

    if montante_intervencao <= 0:
        return "Montante da intervenção deve ser positivo.", False, "INVALID_INPUT"
    
    limite_max_intervencao_abs = 50.0
    if montante_intervencao > limite_max_intervencao_abs:
        return f"Montante excede o limite máximo por intervenção ({limite_max_intervencao_abs:.1f} Bi).", False, "INVALID_INPUT"

    estado.historico_acoes.append('intervir_cambio')
    estado.meses_sem_acao_significativa = 0

    mensagem_log = ""
    cor_log = BLUE_INFO
    impacto_cred = 0
    impacto_pressao = 0
    sucesso_acao = False
    motivo_falha = None

    if tipo_intervencao == "venda_dolares":
        if estado.reservas_internacionais >= montante_intervencao:
            estado.reservas_internacionais -= montante_intervencao
            estado.intervencao_cambial_este_mes_tipo = "venda_dolares"
            estado.intervencao_cambial_este_mes_magnitude = montante_intervencao
            
            mensagem_log = (f"BC vendeu US$ {montante_intervencao:.1f} Bi no mercado. "
                            f"Reservas: US$ {estado.reservas_internacionais:.1f} Bi.")
            cor_log = GREEN_SUCCESS
            
            if montante_intervencao > 10.0:
                impacto_cred -= random.uniform(3, 6) * (montante_intervencao / 10.0)
                impacto_pressao += random.uniform(1, 3)
                mensagem_log += " (Intervenção de grande porte!)"
            elif montante_intervencao > 2.5:
                impacto_cred -= random.uniform(1, 3)
            
            if estado.reservas_internacionais < 100:
                impacto_cred -= random.uniform(2, 5)
                mensagem_log += " (Nível de reservas perigosamente baixo!)"
            
            if estado.cambio_atual > 5.5 : impacto_pressao -= random.uniform(1, 3)
            sucesso_acao = True
        else:
            mensagem_log = f"Venda de US$ {montante_intervencao:.1f} Bi falhou. Reservas insuficientes (US$ {estado.reservas_internacionais:.1f} Bi)."
            cor_log = RED_CRITICAL
            impacto_cred -= random.uniform(3,5) 
            sucesso_acao = False
            motivo_falha = "RESERVAS_INSUFICIENTES"

    elif tipo_intervencao == "compra_dolares":
        estado.reservas_internacionais += montante_intervencao
        estado.intervencao_cambial_este_mes_tipo = "compra_dolares"
        estado.intervencao_cambial_este_mes_magnitude = montante_intervencao
        
        mensagem_log = (f"BC comprou US$ {montante_intervencao:.1f} Bi no mercado. "
                        f"Reservas: US$ {estado.reservas_internacionais:.1f} Bi.")
        cor_log = BLUE_INFO
        
        if montante_intervencao > 10.0:
            impacto_cred -= random.uniform(1,2)
            impacto_pressao += random.uniform(2,4)
            mensagem_log += " (Acumulação agressiva de reservas!)"
        elif estado.cambio_atual < 4.7 and montante_intervencao > 2.0:
            impacto_cred -= random.uniform(0.5, 1.5)
            impacto_pressao += random.uniform(1, 2)
        sucesso_acao = True
        
    if sucesso_acao:
        estado.credibilidade_bc = round(max(0, min(100, estado.credibilidade_bc + impacto_cred)), 1)
        estado.pressao_politica = round(max(0, min(100, estado.pressao_politica + impacto_pressao)), 1)
        estado.cooldown_intervencao_cambial = 2 

        if impacto_cred != 0 or impacto_pressao != 0:
            mensagem_log += f" (Cred: {impacto_cred:+.1f}, Press: {impacto_pressao:+.1f})"
    
    estado.add_log_entry(mensagem_log, cor_log)
    return mensagem_log.split(" (Cred")[0], sucesso_acao, motivo_falha