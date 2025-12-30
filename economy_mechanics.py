# economy_mechanics.py
import random

from config import (
    RED_CRITICAL, YELLOW_ALERT, WHITE, GREEN_SUCCESS, 
    BLUE_INFO, ORANGE_WARNING
)

SENSITIVITY_FACTOR_INTERVENCAO = 0.015 

def atualizar_expectativa_juros_longo_prazo(estado, tom_comunicacao="neutro"):
    # Esta função já atualiza o estado diretamente e considera o tom/guidance
    base_juros_longos = estado.selic_anual * 0.55 + \
                        (estado.expectativa_inflacao_mercado_mensal * 12 + estado.meta_inflacao_anual) * 0.25
    fator_credibilidade = (100 - estado.credibilidade_bc) * 0.035 # Maior credibilidade, menor prêmio
    base_juros_longos += fator_credibilidade
    
    # Impacto do tom da comunicação ou guidance
    if tom_comunicacao == "hawkish":
        base_juros_longos += 0.50 * (estado.credibilidade_bc / 100.0) # Aumentado impacto
    elif tom_comunicacao == "dovish":
        base_juros_longos -= 0.50 * (estado.credibilidade_bc / 100.0) # Aumentado impacto

    premio_risco_fiscal = max(0, (estado.divida_publica_pib - 70) / 100 * 0.45) # Ajustado
    base_juros_longos += premio_risco_fiscal
    ruido = random.uniform(-0.20, 0.20) # Aumentado um pouco o ruído
    nova_expectativa = base_juros_longos + ruido
    
    estado.expectativa_juros_longo_prazo_anual = round(max(estado.meta_inflacao_anual * 0.7, min(estado.selic_anual + 8.0, nova_expectativa)), 2)


def atualizar_fator_liquidez_bancaria(estado):
    compulsorio_base_neutro = 0.22 
    sensibilidade_compulsorio_liquidez = 2.8 # Aumentada sensibilidade
    estado.alvo_fator_liquidez_bancaria = 1.0 - (estado.taxa_deposito_compulsorio - compulsorio_base_neutro) * \
                                           sensibilidade_compulsorio_liquidez
    estado.alvo_fator_liquidez_bancaria = round(max(0.4, min(1.6, estado.alvo_fator_liquidez_bancaria)), 3)
    
    passo_ajuste_liquidez = 0.07 # Ajuste mais rápido
    if estado.fator_liquidez_bancaria < estado.alvo_fator_liquidez_bancaria:
        estado.fator_liquidez_bancaria = min(estado.fator_liquidez_bancaria + passo_ajuste_liquidez, estado.alvo_fator_liquidez_bancaria)
    elif estado.fator_liquidez_bancaria > estado.alvo_fator_liquidez_bancaria:
        estado.fator_liquidez_bancaria = max(estado.fator_liquidez_bancaria - passo_ajuste_liquidez, estado.alvo_fator_liquidez_bancaria)
    estado.fator_liquidez_bancaria = round(estado.fator_liquidez_bancaria, 3)

def atualizar_inflacao(estado): # Define estado.alvo_inflacao_mensal
    selic_mensal = estado.selic_anual / 12
    juros_reais_mensal_curto = selic_mensal - estado.expectativa_inflacao_mercado_mensal
    cred_factor = estado.credibilidade_bc / 100.0
    
    diff_juros_longos_meta_inflacao = (estado.expectativa_juros_longo_prazo_anual - estado.meta_inflacao_anual) / 12
    impacto_ancoragem_juros_longos = diff_juros_longos_meta_inflacao * 0.15 * cred_factor

    fator_sensibilidade_juros_dinamico = 0.60 + cred_factor * 0.70
    impacto_juros_curto = juros_reais_mensal_curto * fator_sensibilidade_juros_dinamico
    if juros_reais_mensal_curto < 0: impacto_juros_curto *= 1.4
    
    inflacao_anual_para_analise = estado.inflacao_atual_mensal * 12
    meta_inflacao = estado.meta_inflacao_anual; banda_original = estado.banda_inflacao_original
    if inflacao_anual_para_analise <= (meta_inflacao - banda_original - 1.5): impacto_juros_curto *= 0.70 
    elif inflacao_anual_para_analise >= (meta_inflacao + banda_original + 1.5): impacto_juros_curto *= 0.80 

    impacto_expectativa_mercado = (estado.expectativa_inflacao_mercado_mensal - (estado.meta_inflacao_anual / 12)) * 0.50
    impacto_cambio_inflacao = (estado.cambio_atual - 5.0) * 0.010 # Coeficiente do repasse cambial (mensalizado)
    impacto_liquidez_inflacao = (1.0 - estado.fator_liquidez_bancaria) * 0.005 # Coeficiente mensal
    
    impacto_fiscal_inflacao = 0
    if estado.governo_postura_fiscal == "expansionista": impacto_fiscal_inflacao += (0.12 / 12) 
    elif estado.governo_postura_fiscal == "contracionista": impacto_fiscal_inflacao -= (0.07 / 12)
    
    meses_desde_anuncio = (estado.ano_atual * 12 + estado.mes_atual) - estado.mes_ultimo_anuncio_fiscal
    if estado.mes_ultimo_anuncio_fiscal > 0 and meses_desde_anuncio < 3: # Impacto por 3 meses
        impacto_fiscal_inflacao += (estado.ultimo_anuncio_fiscal_valor / 100) * (0.008 / 3) # Diluído em 3 meses
        
    ruido_inflacao = random.uniform(-0.05, 0.05) / 12 # Ruído menor
    
    # O alvo é para onde a inflação CONVERGIRIA neste mês com as condições atuais
    # A inflação ATUAL é o ponto de partida para essa convergência.
    # Usamos o estado.inflacao_atual_mensal como base para os deltas,
    # mas o resultado define o ALVO.
    valor_alvo_calculado = estado.inflacao_atual_mensal - impacto_juros_curto - \
                           impacto_ancoragem_juros_longos + impacto_expectativa_mercado + \
                           impacto_cambio_inflacao - impacto_liquidez_inflacao + \
                           impacto_fiscal_inflacao + ruido_inflacao
                           
    estado.alvo_inflacao_mensal = round(max(-1.0 / 12, min(4.5 / 12, valor_alvo_calculado)), 6)

def atualizar_pib(estado): # Define estado.alvo_pib_crescimento_mensal
    taxa_relevante_investimento_mensal = (estado.expectativa_juros_longo_prazo_anual * 0.60 + estado.selic_anual * 0.40) / 12 # Maior peso para juros longos
    cred_factor = estado.credibilidade_bc / 100.0

    impacto_juros_pib = (taxa_relevante_investimento_mensal - (estado.inflacao_atual_mensal + 0.0020)) * 0.70 # Juro real percebido para investimento
    impacto_credibilidade_pib = (cred_factor - 0.5) * (0.08/12) # Credibilidade acima de 50 ajuda, abaixo atrapalha
    
    inflacao_anual_real = estado.inflacao_atual_mensal * 12
    desvio_inflacao = abs(inflacao_anual_real - estado.meta_inflacao_anual)
    penalidade_inflacao_pib = (desvio_inflacao * 0.015) / 12 if desvio_inflacao > (estado.banda_inflacao_original + 1.0) else 0
    
    impacto_liquidez_pib = (estado.fator_liquidez_bancaria - 0.9) * (0.04 / 12) # Liquidez acima de 0.9 ajuda
    
    impacto_fiscal_pib = 0
    if estado.governo_postura_fiscal == "expansionista": impacto_fiscal_pib += (0.20 / 12) 
    elif estado.governo_postura_fiscal == "contracionista": impacto_fiscal_pib -= (0.12 / 12)
    meses_desde_anuncio = (estado.ano_atual * 12 + estado.mes_atual) - estado.mes_ultimo_anuncio_fiscal
    if estado.mes_ultimo_anuncio_fiscal > 0 and meses_desde_anuncio < 3: 
        impacto_fiscal_pib += (estado.ultimo_anuncio_fiscal_valor / 100) * (0.020 / 3) # Diluído
        
    penalidade_divida_pib = max(0, (estado.divida_publica_pib - 80) / 100 * (0.06 / 12)) # Penalidade a partir de 80%
    ruido_pib = random.uniform(-0.04, 0.04) / 12 
    crescimento_potencial_mensal = 0.0010 # Potencial de crescimento mensal (ex: 1.2% a.a.)
    
    # O alvo é para a TAXA DE CRESCIMENTO MENSAL
    valor_alvo_calculado = crescimento_potencial_mensal - impacto_juros_pib + impacto_credibilidade_pib - \
                           penalidade_inflacao_pib + impacto_liquidez_pib + \
                           impacto_fiscal_pib - penalidade_divida_pib + ruido_pib
                           
    estado.alvo_pib_crescimento_mensal = round(max(-2.0 / 12, min(1.0 / 12, valor_alvo_calculado)), 6)

def atualizar_cambio(estado): # Define estado.alvo_cambio_atual
    selic_mensal = estado.selic_anual / 12.0
    taxa_juros_internacional_mensal = (1.0 / 100) / 12.0 # Ex: 1.0% a.a. internacional
    cred_factor = estado.credibilidade_bc / 100.0
    
    diferencial_juros_efetivo = selic_mensal - estado.expectativa_inflacao_mercado_mensal - taxa_juros_internacional_mensal
    impacto_juros_cambio = diferencial_juros_efetivo * 8.0 # Sensibilidade ao diferencial de juro real
    
    impacto_credibilidade_cambio = (cred_factor - 0.5) * 0.15 # Credibilidade acima de 50 aprecia o Real
    
    # Inflação corrente em relação à externa (implícita na taxa internacional) pode depreciar
    inflacao_relativa_mensal = estado.inflacao_atual_mensal - (0.2/100)/12 # Assumindo inflação externa de 0.2% a.m.
    impacto_inflacao_cambio = inflacao_relativa_mensal * 7.0
    
    impacto_divida_cambio = max(0, (estado.divida_publica_pib - 78) / 100 * 0.10) # Dívida acima de 78% deprecia
    
    impacto_intervencao_direta = 0.0
    if hasattr(estado, 'intervencao_cambial_este_mes_tipo') and estado.intervencao_cambial_este_mes_tipo:
        magnitude = estado.intervencao_cambial_este_mes_magnitude
        if estado.intervencao_cambial_este_mes_tipo == "venda_dolares": impacto_intervencao_direta = - (magnitude * SENSITIVITY_FACTOR_INTERVENCAO * (0.8 + cred_factor * 0.4)) # Intervenção mais eficaz com credibilidade
        elif estado.intervencao_cambial_este_mes_tipo == "compra_dolares": impacto_intervencao_direta = magnitude * SENSITIVITY_FACTOR_INTERVENCAO * (0.8 + cred_factor * 0.4)
    
    ruido_cambio = random.uniform(-0.06, 0.06) 
    
    # O alvo é para onde o câmbio CONVERGIRIA
    valor_alvo_calculado = estado.cambio_atual - impacto_juros_cambio - impacto_credibilidade_cambio + \
                           impacto_inflacao_cambio + impacto_divida_cambio + impacto_intervencao_direta + ruido_cambio
                           
    estado.alvo_cambio_atual = round(max(2.50, min(15.00, valor_alvo_calculado)), 3)

def atualizar_desemprego(estado):
    # Desemprego reage com defasagem ao PIB (Okun's Law simplificada)
    # Crescimento do PIB mensal necessário para manter desemprego estável (considerando crescimento da força de trabalho)
    pib_neutro_desemprego_mensal = 0.0008 # Ex: ~1% a.a. de crescimento do PIB para manter desemprego estável
    
    # Elasticidade do desemprego ao PIB: quanto o desemprego cai para cada 1 p.p. de crescimento do PIB acima do neutro
    elasticidade_desemprego_pib = 0.4 
    
    delta_pib_do_neutro = estado.pib_crescimento_atual_mensal - pib_neutro_desemprego_mensal
    variacao_desemprego = -delta_pib_do_neutro * elasticidade_desemprego_pib * 100 # Converte para pontos percentuais
    
    # Inércia no desemprego + pequeno ruído
    ajuste_inercial_desemprego = (estado.taxa_desemprego_atual + variacao_desemprego * 0.3) # 30% do impacto no mês
    ruido_desemprego = random.uniform(-0.05, 0.05)
    
    # O desemprego do mês anterior influencia 70% do desemprego atual (inércia)
    novo_desemprego = estado.taxa_desemprego_atual * 0.85 + ajuste_inercial_desemprego * 0.15 + ruido_desemprego
    
    return round(max(2.5, min(20.0, novo_desemprego)), 2)


def atualizar_credibilidade_e_pressao(estado): # Define alvos para Credibilidade e Pressão
    cred_potencial = estado.credibilidade_bc 
    press_potencial = estado.pressao_politica 
    inflacao_anual_real = estado.inflacao_atual_mensal * 12
    pib_anual_real = estado.pib_crescimento_atual_mensal * 12
    banda_inflacao_efetiva = estado.banda_inflacao_anual
    tipo_governo = estado.tipo_governo
    delta_cred_mes = 0; delta_press_mes = 0
    mod_pp_pib_baixo = 1.0; mod_pp_desemprego_alto = 1.0; mod_pp_inflacao_alta = 1.0
    mod_cb_pib_baixo = 1.0; mod_cb_inflacao_descontrolada = 1.0
    if tipo_governo == "Liberal":
        mod_pp_pib_baixo = 0.6; mod_pp_desemprego_alto = 0.7; mod_pp_inflacao_alta = 1.2
        mod_cb_pib_baixo = 0.8; mod_cb_inflacao_descontrolada = 1.2
    elif tipo_governo == "Desenvolvimentista":
        mod_pp_pib_baixo = 1.4; mod_pp_desemprego_alto = 1.5; mod_pp_inflacao_alta = 0.7
        mod_cb_pib_baixo = 1.3; mod_cb_inflacao_descontrolada = 0.8
    elif tipo_governo == "Pragmatico": mod_pp_inflacao_alta = 1.05
    desvio_abs_inflacao_meta = abs(inflacao_anual_real - estado.meta_inflacao_anual)
    if desvio_abs_inflacao_meta <= banda_inflacao_efetiva: delta_cred_mes += 2.0; estado.meses_inflacao_fora_meta = 0
    elif inflacao_anual_real < (estado.meta_inflacao_anual - banda_inflacao_efetiva - 1.0): 
        pen_defl = abs(inflacao_anual_real - (estado.meta_inflacao_anual - banda_inflacao_efetiva - 1.0)) * 0.7
        delta_cred_mes -= pen_defl * mod_cb_inflacao_descontrolada; delta_press_mes += (pen_defl * 0.6) * mod_pp_inflacao_alta
        estado.meses_inflacao_fora_meta += 1
        if estado.meses_inflacao_fora_meta == 1: estado.add_log_entry(f"Inflacao muito abaixo da meta ({inflacao_anual_real:.2f}% a.a.)!", RED_CRITICAL)
    else: 
        delta_cred_mes -= desvio_abs_inflacao_meta * 1.0 * mod_cb_inflacao_descontrolada
        delta_press_mes += (desvio_abs_inflacao_meta * 0.4) * mod_pp_inflacao_alta; estado.meses_inflacao_fora_meta += 1
    if estado.meses_inflacao_fora_meta >= 4:
        pen_add_infl = (estado.meses_inflacao_fora_meta - 3) * 1.5
        delta_cred_mes -= pen_add_infl * mod_cb_inflacao_descontrolada; delta_press_mes += (pen_add_infl * 0.7) * mod_pp_inflacao_alta
        if estado.meses_inflacao_fora_meta == 4 : estado.add_log_entry(f"ALERTA: Inflacao fora da meta ha {estado.meses_inflacao_fora_meta} meses!", RED_CRITICAL)
    desvio_abs_pib_meta = abs(pib_anual_real - estado.meta_pib_anual); banda_pib_efetiva = estado.banda_pib_anual
    if desvio_abs_pib_meta <= banda_pib_efetiva: delta_cred_mes += 1.2; estado.meses_pib_fora_meta = 0
    else: 
        delta_cred_mes -= (desvio_abs_pib_meta * 0.8) * mod_cb_pib_baixo; delta_press_mes += (desvio_abs_pib_meta * 0.7) * mod_pp_pib_baixo
        estado.meses_pib_fora_meta += 1
    if estado.meses_pib_fora_meta >= 4:
        pen_add_pib = (estado.meses_pib_fora_meta - 3) * 1.2
        delta_cred_mes -= pen_add_pib * mod_cb_pib_baixo; delta_press_mes += (pen_add_pib * 0.7) * mod_pp_pib_baixo
        if estado.meses_pib_fora_meta == 4: estado.add_log_entry(f"ALERTA: PIB fora da meta ha {estado.meses_pib_fora_meta} meses!", RED_CRITICAL)
    if inflacao_anual_real > (estado.meta_inflacao_anual + 2.5): delta_press_mes += 4.5 * mod_pp_inflacao_alta
    elif inflacao_anual_real > (estado.meta_inflacao_anual + 0.8): delta_press_mes += 2.0 * mod_pp_inflacao_alta
    elif inflacao_anual_real < (estado.meta_inflacao_anual - 2.5): delta_press_mes += 3.5 * mod_pp_inflacao_alta
    if pib_anual_real < (estado.meta_pib_anual - banda_pib_efetiva - 0.8): delta_press_mes += 4.0 * mod_pp_pib_baixo
    elif pib_anual_real < estado.meta_pib_anual: delta_press_mes += 1.0 * mod_pp_pib_baixo
    if estado.taxa_desemprego_atual > 10.0: delta_press_mes += 5.0 * mod_pp_desemprego_alto; estado.meses_desemprego_alto += 1
    elif estado.taxa_desemprego_atual > 7.5: delta_press_mes += 2.0 * mod_pp_desemprego_alto; estado.meses_desemprego_alto += 1
    else: delta_press_mes -= 2.0; estado.meses_desemprego_alto = 0
    if estado.meses_desemprego_alto >= 3:
        aum_add_press = (estado.meses_desemprego_alto - 2) * 2.5
        delta_press_mes += aum_add_press * mod_pp_desemprego_alto
        if estado.meses_desemprego_alto == 3: estado.add_log_entry(f"URGENTE: Desemprego elevado ha {estado.meses_desemprego_alto} meses!", RED_CRITICAL)
    fator_alivio = 1.0
    if tipo_governo == "Liberal" and desvio_abs_inflacao_meta < 0.5: fator_alivio = 1.3
    elif tipo_governo == "Desenvolvimentista" and pib_anual_real > (estado.meta_pib_anual + banda_pib_efetiva*0.5) : fator_alivio = 1.3
    if desvio_abs_inflacao_meta < 0.5 and pib_anual_real > (estado.meta_pib_anual - banda_pib_efetiva / 2): delta_press_mes -= 4.0 * fator_alivio
    else: delta_press_mes -= 0.8
    mod_idc_div_cred = 1.0; mod_idc_div_press = 1.0
    if tipo_governo == "Liberal": mod_idc_div_cred = 1.2; mod_idc_div_press = 1.2
    elif tipo_governo == "Desenvolvimentista": mod_idc_div_cred = 0.7; mod_idc_div_press = 0.7
    if estado.divida_publica_pib > 80:
        delta_cred_mes -= (estado.divida_publica_pib - 80) * 0.20 * mod_idc_div_cred
        delta_press_mes += (estado.divida_publica_pib - 80) * 0.30 * mod_idc_div_press
        # Log de dívida crítica um pouco antes, se estiver subindo para níveis muito altos
        if estado.divida_publica_pib > 90 and (estado.divida_publica_pib - delta_press_mes) <=90 : # Apenas se cruzou 90 neste mes
             estado.add_log_entry(f"CRÍTICO: Dívida Pública em {estado.divida_publica_pib:.1f}%!", RED_CRITICAL)
    elif estado.divida_publica_pib < 55: delta_cred_mes += (55 - estado.divida_publica_pib) * 0.08
    cred_potencial += delta_cred_mes; press_potencial += delta_press_mes
    fator_acel_neg = 0.08; fator_acel_pos = 0.04 
    if press_potencial > estado.tolerancia_pressao_politica: press_potencial += (press_potencial - estado.tolerancia_pressao_politica) * fator_acel_neg
    elif press_potencial < 20: press_potencial -= (20 - press_potencial) * fator_acel_pos
    if cred_potencial < estado.tolerancia_credibilidade_mercado and cred_potencial > 0: cred_potencial -= (estado.tolerancia_credibilidade_mercado - cred_potencial) * fator_acel_neg
    elif cred_potencial > 80: cred_potencial += (cred_potencial - 80) * fator_acel_pos
    estado.alvo_credibilidade_bc = round(max(0.0, min(100.0, cred_potencial)), 1)
    estado.alvo_pressao_politica = round(max(0.0, min(100.0, press_potencial)), 1)
    if abs(delta_cred_mes) > 0.05 or abs(delta_press_mes) > 0.05:
        cred_val_str = f"{'+' if delta_cred_mes >= 0 else ''}{delta_cred_mes:.1f}"; press_val_str = f"{'+' if delta_press_mes >= 0 else ''}{delta_press_mes:.1f}"
        log_color = WHITE
        if (delta_cred_mes < 0 and delta_press_mes >=0) or (delta_cred_mes <=0 and delta_press_mes > 0) : log_color = RED_CRITICAL
        elif (delta_cred_mes > 0 and delta_press_mes <= 0) or (delta_cred_mes >=0 and delta_press_mes <0): log_color = GREEN_SUCCESS
        elif (delta_cred_mes < 0 and delta_press_mes < 0) or (delta_cred_mes > 0 and delta_press_mes > 0): log_color = YELLOW_ALERT
        final_message_parts = ["Tendência mensal: "]
        if abs(delta_cred_mes) > 0.05: final_message_parts.append(f"Cred: {cred_val_str}")
        if abs(delta_press_mes) > 0.05:
            if abs(delta_cred_mes) > 0.05: final_message_parts.append(", ")
            final_message_parts.append(f"Press: {press_val_str}")
        if len(final_message_parts) > 1: estado.add_log_entry("".join(final_message_parts), color=log_color)

def atualizar_divida_publica(estado):
    selic_mensal_nominal = (estado.selic_anual / 100) / 12 
    inflacao_mensal_atual = estado.inflacao_atual_mensal 
    crescimento_real_pib_mensal = estado.pib_crescimento_atual_mensal 
    taxa_juros_real_mensal_divida = selic_mensal_nominal - inflacao_mensal_atual
    resultado_primario_anual_pib_meta = 0.0 
    if estado.governo_postura_fiscal == "expansionista": resultado_primario_anual_pib_meta = random.uniform(-3.5, -1.5) / 100 
    elif estado.governo_postura_fiscal == "contracionista": resultado_primario_anual_pib_meta = random.uniform(0.5, 2.5) / 100  
    else: resultado_primario_anual_pib_meta = random.uniform(-1.0, 0.5) / 100 
    superavit_primario_mensal_pib = resultado_primario_anual_pib_meta / 12
    meses_desde_anuncio = (estado.ano_atual * 12 + estado.mes_atual) - estado.mes_ultimo_anuncio_fiscal
    if estado.mes_ultimo_anuncio_fiscal > 0 and meses_desde_anuncio < 3: 
        impacto_anuncio_no_primario_mensal = (estado.ultimo_anuncio_fiscal_valor / 100) / 3 # Impacto diluído em 3 meses
        superavit_primario_mensal_pib -= impacto_anuncio_no_primario_mensal 
    variacao_divida_pib_proporcao = (estado.divida_publica_pib / 100) * (taxa_juros_real_mensal_divida - crescimento_real_pib_mensal) - superavit_primario_mensal_pib
    estado.divida_publica_pib += variacao_divida_pib_proporcao * 100 
    estado.divida_publica_pib = round(max(30.0, min(150.0, estado.divida_publica_pib)), 2) 

def decisoes_fiscais_governo_ia(estado):
    if estado.cooldown_anuncio_fiscal_governo > 0: estado.cooldown_anuncio_fiscal_governo -= 1; return
    influencia_bc_aplicada_este_mes = False 
    if (hasattr(estado, 'influencia_duracao') and estado.influencia_duracao > 0 and
            hasattr(estado, 'governo_postura_fiscal_influencia') and estado.governo_postura_fiscal_influencia):
        estado.influencia_duracao -= 1 
        if random.random() < 0.75: 
            postura_influenciada = estado.governo_postura_fiscal_influencia; mensagem_log_influencia = ""; cor_log_influencia = BLUE_INFO
            if postura_influenciada == "contracionista":
                magnitude = round(random.uniform(0.7, 2.2), 1); estado.ultimo_anuncio_fiscal_valor = -magnitude
                mensagem_log_influencia = (f"GOVERNO ({estado.tipo_governo}), atendendo BC, anuncia corte de {abs(magnitude):.1f}% PIB.")
                cor_log_influencia = ORANGE_WARNING 
                if estado.governo_postura_fiscal != "contracionista": estado.governo_postura_fiscal = "contracionista"
                estado.pressao_politica = min(100, estado.pressao_politica + random.uniform(1,3)) 
                estado.credibilidade_bc = min(100, estado.credibilidade_bc + random.uniform(0.5,2)) 
            elif postura_influenciada == "expansionista":
                magnitude = round(random.uniform(0.8, 2.8), 1); estado.ultimo_anuncio_fiscal_valor = magnitude
                mensagem_log_influencia = (f"GOVERNO ({estado.tipo_governo}), em linha com BC, anuncia estímulo de {magnitude:.1f}% PIB.")
                cor_log_influencia = GREEN_SUCCESS
                if estado.governo_postura_fiscal != "expansionista": estado.governo_postura_fiscal = "expansionista"
                estado.pressao_politica = max(0, estado.pressao_politica - random.uniform(0.5,2.5))
                estado.credibilidade_bc = max(0, estado.credibilidade_bc - random.uniform(0,0.5)) 
            if mensagem_log_influencia:
                estado.mes_ultimo_anuncio_fiscal = estado.ano_atual * 12 + estado.mes_atual
                estado.add_log_entry(mensagem_log_influencia, cor_log_influencia)
                estado.cooldown_anuncio_fiscal_governo = 3 
                influencia_bc_aplicada_este_mes = True
        if estado.influencia_duracao == 0:
            estado.governo_postura_fiscal_influencia = None 
            if influencia_bc_aplicada_este_mes: estado.add_log_entry("Período de influência do BC sobre decisões fiscais encerrou.", BLUE_INFO)
        if influencia_bc_aplicada_este_mes: return 
    chance_decisao = 0.10 
    pib_anual = estado.pib_crescimento_atual_mensal * 12; inflacao_anual = estado.inflacao_atual_mensal * 12; tipo_governo = estado.tipo_governo 
    if tipo_governo == "Liberal":
        chance_decisao += 0.02
        if estado.divida_publica_pib > 70: chance_decisao += 0.10 
        if inflacao_anual > estado.meta_inflacao_anual + 1.0: chance_decisao += 0.05
        pesos_decisao = [0.2, 0.5, 0.3]  
    elif tipo_governo == "Desenvolvimentista":
        chance_decisao += 0.05
        if pib_anual < 1.0: chance_decisao += 0.15 
        if estado.taxa_desemprego_atual > 8.5: chance_decisao += 0.10
        pesos_decisao = [0.5, 0.2, 0.3]  
    elif tipo_governo == "Pragmatico":
        chance_decisao += 0.03
        if abs(pib_anual - estado.meta_pib_anual) > 1.5 or abs(inflacao_anual - estado.meta_inflacao_anual) > 1.5: chance_decisao += 0.10 
        pesos_decisao = [0.35, 0.3, 0.35] 
    else: pesos_decisao = [0.33, 0.33, 0.34]
    if pib_anual < 0.0: chance_decisao += 0.10 * (0.7 if tipo_governo == "Liberal" else 1.3) 
    elif pib_anual < 1.0: chance_decisao += 0.05 * (0.8 if tipo_governo == "Liberal" else 1.2)
    if estado.divida_publica_pib > 85: chance_decisao -= 0.08 * (1.5 if tipo_governo == "Liberal" else 0.7) 
    elif estado.divida_publica_pib > 75: chance_decisao -= 0.04 * (1.3 if tipo_governo == "Liberal" else 0.8)
    if inflacao_anual > estado.meta_inflacao_anual + estado.banda_inflacao_anual + 1.5: chance_decisao -= 0.07 * (1.2 if tipo_governo != "Desenvolvimentista" else 0.5) 
    chance_decisao = max(0.05, min(0.40, chance_decisao)) 
    if random.random() < chance_decisao:
        tipo_decisao = random.choices(["pacote_estimulo", "corte_gastos", "mudanca_postura"], weights=pesos_decisao, k=1)[0]
        mensagem_log = ""; estado.ultimo_anuncio_fiscal_valor = 0.0; cor_log = BLUE_INFO
        if tipo_decisao == "pacote_estimulo":
            if tipo_governo == "Liberal" and (estado.divida_publica_pib > 80 or pib_anual > -0.5):
                if random.random() < 0.7: tipo_decisao = "mudanca_postura" if random.random() < 0.5 else None
            if tipo_decisao == "pacote_estimulo": 
                magnitude_base = random.uniform(0.5, 2.5)
                if tipo_governo == "Desenvolvimentista": magnitude_base *= 1.2 
                elif tipo_governo == "Liberal": magnitude_base *= 0.7 
                magnitude = round(magnitude_base, 1)
                if estado.divida_publica_pib > 95 and tipo_governo != "Desenvolvimentista": magnitude *= 0.5 
                if magnitude < 0.3: tipo_decisao = None 
                else:
                    estado.ultimo_anuncio_fiscal_valor = magnitude; mensagem_log = f"GOVERNO ({tipo_governo}): Anuncia pacote de estímulo fiscal de {magnitude:.1f}% do PIB."; cor_log = GREEN_SUCCESS
                    if estado.governo_postura_fiscal != "expansionista":
                        if random.random() < (0.6 if tipo_governo == "Desenvolvimentista" else 0.2): estado.governo_postura_fiscal = "expansionista"
                    estado.pressao_politica = max(0, estado.pressao_politica - random.uniform(1, (5 if tipo_governo == "Desenvolvimentista" else 2)))
                    estado.credibilidade_bc = max(0, estado.credibilidade_bc - random.uniform(0, (3 if tipo_governo == "Liberal" and estado.inflacao_atual_mensal*12 > estado.meta_inflacao_anual else 1)))
        elif tipo_decisao == "corte_gastos":
            if tipo_governo == "Desenvolvimentista" and (estado.divida_publica_pib < 85 and inflacao_anual < estado.meta_inflacao_anual + 3.0):
                if random.random() < 0.8: tipo_decisao = "mudanca_postura" if random.random() < 0.5 else None
            if tipo_decisao == "corte_gastos":
                magnitude_base = random.uniform(0.3, 2.0)
                if tipo_governo == "Liberal": magnitude_base *= 1.3 
                elif tipo_governo == "Desenvolvimentista": magnitude_base *= 0.6 
                magnitude = round(magnitude_base, 1)
                if magnitude < 0.2: tipo_decisao = None
                else:
                    estado.ultimo_anuncio_fiscal_valor = -magnitude; mensagem_log = f"GOVERNO ({tipo_governo}): Anuncia corte de gastos de {abs(magnitude):.1f}% do PIB."; cor_log = ORANGE_WARNING
                    if estado.governo_postura_fiscal != "contracionista":
                        if random.random() < (0.7 if tipo_governo == "Liberal" else 0.3): estado.governo_postura_fiscal = "contracionista"
                    estado.pressao_politica = min(100, estado.pressao_politica + random.uniform(2, (4 if tipo_governo == "Desenvolvimentista" else 7)))
                    estado.credibilidade_bc = min(100, estado.credibilidade_bc + random.uniform(1, (4 if tipo_governo == "Liberal" else 2)))
        if tipo_decisao == "mudanca_postura": 
            possiveis_posturas = ["expansionista", "contracionista", "neutra"]
            if estado.governo_postura_fiscal in possiveis_posturas: possiveis_posturas.remove(estado.governo_postura_fiscal)
            if possiveis_posturas:
                nova_postura = estado.governo_postura_fiscal 
                if tipo_governo == "Liberal":
                    if "contracionista" in possiveis_posturas and (estado.divida_publica_pib > 75 or inflacao_anual > estado.meta_inflacao_anual + 1): nova_postura = "contracionista"
                    elif "neutra" in possiveis_posturas: nova_postura = "neutra"
                    else: nova_postura = random.choice(possiveis_posturas) if possiveis_posturas else estado.governo_postura_fiscal
                elif tipo_governo == "Desenvolvimentista":
                    if "expansionista" in possiveis_posturas and (pib_anual < 1.5 or estado.taxa_desemprego_atual > 8.0): nova_postura = "expansionista"
                    elif "neutra" in possiveis_posturas: nova_postura = "neutra"
                    else: nova_postura = random.choice(possiveis_posturas) if possiveis_posturas else estado.governo_postura_fiscal
                elif tipo_governo == "Pragmatico":
                    if pib_anual < 0.5 and inflacao_anual < estado.meta_inflacao_anual + 1.0 and "expansionista" in possiveis_posturas: nova_postura = "expansionista"
                    elif (inflacao_anual > estado.meta_inflacao_anual + 1.5 or estado.divida_publica_pib > 80) and "contracionista" in possiveis_posturas: nova_postura = "contracionista"
                    elif "neutra" in possiveis_posturas: nova_postura = "neutra"
                    else: nova_postura = random.choice(possiveis_posturas) if possiveis_posturas else estado.governo_postura_fiscal
                if nova_postura != estado.governo_postura_fiscal:
                    mensagem_log = f"GOVERNO ({tipo_governo}): Sinaliza mudança para postura fiscal '{nova_postura.capitalize()}' (anterior: '{estado.governo_postura_fiscal.capitalize()}')."
                    estado.governo_postura_fiscal = nova_postura; cor_log = BLUE_INFO
                else: mensagem_log = "" 
            else: mensagem_log = ""
        if mensagem_log: 
            estado.mes_ultimo_anuncio_fiscal = estado.ano_atual * 12 + estado.mes_atual
            estado.add_log_entry(mensagem_log, cor_log); estado.cooldown_anuncio_fiscal_governo = random.randint(2, 4)