# reports.py
import pygame
import matplotlib
import matplotlib.pyplot as plt
import io

# Configura o backend para 'Agg' (não-interativo, para gerar imagens)
matplotlib.use("Agg") 

from economy_state import EstadoEconomia
from economy_mechanics import (
    atualizar_inflacao, atualizar_pib, atualizar_cambio,
    atualizar_desemprego, atualizar_expectativa_juros_longo_prazo,
    atualizar_divida_publica, atualizar_fator_liquidez_bancaria
)

# Constantes de simulação (mantidas)
PASSO_AJUSTE_INFLACAO_MENSAL_SIM = 0.00060
PASSO_AJUSTE_PIB_MENSAL_SIM = 0.00015
PASSO_AJUSTE_CAMBIO_SIM = 0.035

def gerar_surface_graficos(estado):
    """
    Gera uma Surface do Pygame contendo os gráficos do Matplotlib.
    Não bloqueia o jogo e não abre nova janela.
    """
    if not estado.historico_inflacao or len(estado.historico_inflacao) < 2:
        return None

    meses = range(len(estado.historico_inflacao))
    
    # Define o estilo e tamanho da figura (em polegadas)
    # DPI 100 com size 12x8 gera uma imagem de 1200x800 aprox
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axs = plt.subplots(2, 2, figsize=(10, 6)) # Reduzi para 2x2 para caber melhor na tela, ou ajuste conforme necessario
    # Se quiser todos os 8 gráficos, precisará de uma superficie maior ou paginação.
    # Vamos focar nos 4 principais por enquanto para teste de performance.
    
    fig.suptitle('Principais Indicadores Econômicos', fontsize=14)

    # Gráfico 1: Inflação
    axs[0, 0].plot(meses, estado.historico_inflacao, color='red', marker='o', markersize=3)
    axs[0, 0].axhline(y=estado.meta_inflacao_anual, color='gray', linestyle='--')
    axs[0, 0].set_title('Inflação Anualizada (%)', fontsize=10)
    axs[0, 0].grid(True, alpha=0.5)

    # Gráfico 2: PIB
    axs[0, 1].plot(meses, estado.historico_pib, color='blue', marker='s', markersize=3)
    axs[0, 1].axhline(y=estado.meta_pib_anual, color='gray', linestyle='--')
    axs[0, 1].set_title('Crescimento PIB (%)', fontsize=10)
    axs[0, 1].grid(True, alpha=0.5)

    # Gráfico 3: Juros (SELIC)
    axs[1, 0].plot(meses, estado.historico_selic, color='purple', marker='^', markersize=3)
    axs[1, 0].set_title('Taxa SELIC (%)', fontsize=10)
    axs[1, 0].grid(True, alpha=0.5)

    # Gráfico 4: Câmbio
    axs[1, 1].plot(meses, estado.historico_cambio, color='green', marker='d', markersize=3)
    axs[1, 1].set_title('Câmbio (R$/US$)', fontsize=10)
    axs[1, 1].grid(True, alpha=0.5)

    plt.tight_layout()

    # Salva o gráfico em um buffer de memória
    canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()

    # Fecha a figura para liberar memória
    plt.close(fig)

    # Converte para Surface do Pygame
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    return surf

# ... (Mantenha as funções gerar_relatorio_previsao_data e evaluate_performance_final originais abaixo, elas não precisam mudar agora) ...
# RECOPIAR O RESTO DO ARQUIVO reports.py ORIGINAL A PARTIR DAQUI (gerar_relatorio_previsao_data, etc)
# Se precisar, eu reescrevo o arquivo todo, mas a mudança principal é substituir exibir_graficos_matplotlib por gerar_surface_graficos
def gerar_relatorio_previsao_data(estado_atual_real):
    # (Copie o código original desta função aqui, sem alterações)
    # ... código original ...
    estado_sim = EstadoEconomia() 
    attrs_to_copy = [
        'inflacao_atual_mensal', 'pib_crescimento_atual_mensal', 'selic_anual',
        'expectativa_inflacao_mercado_mensal', 'credibilidade_bc', 'cambio_atual',
        'taxa_desemprego_atual', 'meta_inflacao_anual', 'banda_inflacao_anual',
        'banda_inflacao_original', 'meta_pib_anual', 'banda_pib_anual',
        'expectativa_juros_longo_prazo_anual', 'taxa_deposito_compulsorio',
        'fator_liquidez_bancaria', 'alvo_fator_liquidez_bancaria',
        'divida_publica_pib', 'governo_postura_fiscal',
        'ultimo_anuncio_fiscal_valor', 'mes_ultimo_anuncio_fiscal',
        'ano_atual', 'mes_atual', 
        'tipo_governo', 'tipo_ministro_fazenda',
        'governo_postura_fiscal_influencia', 'influencia_duracao',
        'alvo_inflacao_mensal', 'alvo_pib_crescimento_mensal', 'alvo_cambio_atual'
    ]
    for attr in attrs_to_copy:
        if hasattr(estado_atual_real, attr):
            setattr(estado_sim, attr, getattr(estado_atual_real, attr))
    
    estado_sim.activity_log.clear()
    for attr_name in dir(estado_sim):
        if attr_name.startswith('historico_'): setattr(estado_sim, attr_name, [])

    previsao_inflacao_mensal_vals = []
    previsao_pib_mensal_vals = []
    previsao_desemprego_vals = [] 

    num_simulacoes_por_mes_interno = 3 
    num_meses_previsao = 6

    estado_base_para_mes_previsao = EstadoEconomia()
    for attr in attrs_to_copy: 
        if hasattr(estado_sim, attr):
            setattr(estado_base_para_mes_previsao, attr, getattr(estado_sim, attr))
    estado_base_para_mes_previsao.activity_log.clear()
    for attr_name in dir(estado_base_para_mes_previsao):
        if attr_name.startswith('historico_'): setattr(estado_base_para_mes_previsao, attr_name, [])

    for mes_simulado_idx in range(num_meses_previsao):
        temp_infl_mes_sim = []; temp_pib_mes_sim = []; temp_des_mes_sim = []
        for _ in range(num_simulacoes_por_mes_interno):
            estado_sub_sim = EstadoEconomia() 
            for attr in attrs_to_copy:
                if hasattr(estado_base_para_mes_previsao, attr):
                    setattr(estado_sub_sim, attr, getattr(estado_base_para_mes_previsao, attr))
            estado_sub_sim.activity_log.clear()
            for attr_name in dir(estado_sub_sim):
                if attr_name.startswith('historico_'): setattr(estado_sub_sim, attr_name, [])

            atualizar_divida_publica(estado_sub_sim) 
            atualizar_fator_liquidez_bancaria(estado_sub_sim) 

            atualizar_inflacao(estado_sub_sim)
            atualizar_pib(estado_sub_sim)       
            atualizar_cambio(estado_sub_sim)    
            
            if estado_sub_sim.inflacao_atual_mensal < estado_sub_sim.alvo_inflacao_mensal:
                estado_sub_sim.inflacao_atual_mensal = min(estado_sub_sim.inflacao_atual_mensal + PASSO_AJUSTE_INFLACAO_MENSAL_SIM, estado_sub_sim.alvo_inflacao_mensal)
            elif estado_sub_sim.inflacao_atual_mensal > estado_sub_sim.alvo_inflacao_mensal:
                estado_sub_sim.inflacao_atual_mensal = max(estado_sub_sim.inflacao_atual_mensal - PASSO_AJUSTE_INFLACAO_MENSAL_SIM, estado_sub_sim.alvo_inflacao_mensal)
            estado_sub_sim.inflacao_atual_mensal = round(estado_sub_sim.inflacao_atual_mensal, 6)

            if estado_sub_sim.pib_crescimento_atual_mensal < estado_sub_sim.alvo_pib_crescimento_mensal:
                estado_sub_sim.pib_crescimento_atual_mensal = min(estado_sub_sim.pib_crescimento_atual_mensal + PASSO_AJUSTE_PIB_MENSAL_SIM, estado_sub_sim.alvo_pib_crescimento_mensal)
            elif estado_sub_sim.pib_crescimento_atual_mensal > estado_sub_sim.alvo_pib_crescimento_mensal:
                estado_sub_sim.pib_crescimento_atual_mensal = max(estado_sub_sim.pib_crescimento_atual_mensal - PASSO_AJUSTE_PIB_MENSAL_SIM, estado_sub_sim.alvo_pib_crescimento_mensal)
            estado_sub_sim.pib_crescimento_atual_mensal = round(estado_sub_sim.pib_crescimento_atual_mensal, 6)

            if estado_sub_sim.cambio_atual < estado_sub_sim.alvo_cambio_atual:
                estado_sub_sim.cambio_atual = min(estado_sub_sim.cambio_atual + PASSO_AJUSTE_CAMBIO_SIM, estado_sub_sim.alvo_cambio_atual)
            elif estado_sub_sim.cambio_atual > estado_sub_sim.alvo_cambio_atual:
                estado_sub_sim.cambio_atual = max(estado_sub_sim.cambio_atual - PASSO_AJUSTE_CAMBIO_SIM, estado_sub_sim.alvo_cambio_atual)
            estado_sub_sim.cambio_atual = round(estado_sub_sim.cambio_atual, 3)
            
            estado_sub_sim.taxa_desemprego_atual = atualizar_desemprego(estado_sub_sim)
            
            estado_sub_sim.expectativa_inflacao_mercado_mensal = (estado_sub_sim.meta_inflacao_anual / 12 * 0.4 + estado_sub_sim.inflacao_atual_mensal * 0.6) + random.uniform(-0.015/12, 0.015/12)
            estado_sub_sim.expectativa_inflacao_mercado_mensal = max(0.005/12, min(3.0/12, estado_sub_sim.expectativa_inflacao_mercado_mensal))
            atualizar_expectativa_juros_longo_prazo(estado_sub_sim)
            
            temp_infl_mes_sim.append(estado_sub_sim.inflacao_atual_mensal)
            temp_pib_mes_sim.append(estado_sub_sim.pib_crescimento_atual_mensal)
            temp_des_mes_sim.append(estado_sub_sim.taxa_desemprego_atual)

        avg_infl_sim_mes = sum(temp_infl_mes_sim) / num_simulacoes_por_mes_interno if temp_infl_mes_sim else 0
        avg_pib_sim_mes = sum(temp_pib_mes_sim) / num_simulacoes_por_mes_interno if temp_pib_mes_sim else 0
        avg_des_sim_mes = sum(temp_des_mes_sim) / num_simulacoes_por_mes_interno if temp_des_mes_sim else estado_base_para_mes_previsao.taxa_desemprego_atual
        
        previsao_inflacao_mensal_vals.append(avg_infl_sim_mes)
        previsao_pib_mensal_vals.append(avg_pib_sim_mes)
        previsao_desemprego_vals.append(avg_des_sim_mes)

        estado_base_para_mes_previsao.inflacao_atual_mensal = avg_infl_sim_mes
        estado_base_para_mes_previsao.pib_crescimento_atual_mensal = avg_pib_sim_mes
        estado_base_para_mes_previsao.taxa_desemprego_atual = avg_des_sim_mes
        
        atualizar_inflacao(estado_base_para_mes_previsao)
        atualizar_pib(estado_base_para_mes_previsao)
        atualizar_cambio(estado_base_para_mes_previsao)
        atualizar_fator_liquidez_bancaria(estado_base_para_mes_previsao)
        atualizar_divida_publica(estado_base_para_mes_previsao)
        
        estado_base_para_mes_previsao.expectativa_inflacao_mercado_mensal = (estado_base_para_mes_previsao.meta_inflacao_anual / 12 * 0.4 + avg_infl_sim_mes * 0.6) + random.uniform(-0.015/12, 0.015/12)
        estado_base_para_mes_previsao.expectativa_inflacao_mercado_mensal = max(0.005/12, min(3.0/12, estado_base_para_mes_previsao.expectativa_inflacao_mercado_mensal))
        atualizar_expectativa_juros_longo_prazo(estado_base_para_mes_previsao) 

        estado_base_para_mes_previsao.mes_atual += 1
        if estado_base_para_mes_previsao.mes_atual > 12:
            estado_base_para_mes_previsao.mes_atual = 1
            estado_base_para_mes_previsao.ano_atual += 1

    avg_inflacao_anual = (sum(previsao_inflacao_mensal_vals) / len(previsao_inflacao_mensal_vals)) * 12 if previsao_inflacao_mensal_vals else 0
    avg_pib_anual = (sum(previsao_pib_mensal_vals) / len(previsao_pib_mensal_vals)) * 12 if previsao_pib_mensal_vals else 0
    avg_desemprego_periodo = sum(previsao_desemprego_vals) / len(previsao_desemprego_vals) if previsao_desemprego_vals else estado_atual_real.taxa_desemprego_atual

    acuracia_percentual = (estado_atual_real.credibilidade_bc / 100.0 * 0.75 + 0.20) * random.uniform(0.90, 1.00) * 100 
    acuracia_percentual = max(30.0, min(98.0, acuracia_percentual)) 

    inflacao_cenario_text = "tende a se manter proxima da meta atual, mas requer monitoramento constante das pressoes."
    if avg_inflacao_anual > estado_atual_real.meta_inflacao_anual + estado_atual_real.banda_inflacao_anual + 1.0:
        inflacao_cenario_text = "projecao indica inflacao significativamente acima do teto da meta, exigindo atencao."
    elif avg_inflacao_anual < estado_atual_real.meta_inflacao_anual - estado_atual_real.banda_inflacao_anual - 1.0:
        inflacao_cenario_text = "ha risco de inflacao muito abaixo do piso da meta, podendo indicar deflacao."
    pib_cenario_text = "deve se manter em ritmo de crescimento moderado e relativamente estavel nos proximos meses."
    if avg_pib_anual < estado_atual_real.meta_pib_anual - estado_atual_real.banda_pib_anual - 0.5: 
        pib_cenario_text = "o crescimento do PIB pode desacelerar ou ficar abaixo do esperado, indicando fragilidade economica."
    elif avg_pib_anual > estado_atual_real.meta_pib_anual + estado_atual_real.banda_pib_anual + 1.0:
        pib_cenario_text = "apresenta forte ritmo de crescimento, mas e preciso observar sinais de superaquecimento."
    return avg_inflacao_anual, avg_pib_anual, avg_desemprego_periodo, acuracia_percentual, inflacao_cenario_text, pib_cenario_text

def evaluate_performance_final(estado, demissao_precoce=False):
    # (Copie o código original desta função aqui também, sem alterações)
    avg_inflacao = sum(estado.historico_inflacao) / len(estado.historico_inflacao) if estado.historico_inflacao else estado.inflacao_atual_mensal * 12
    avg_pib = sum(estado.historico_pib) / len(estado.historico_pib) if estado.historico_pib else estado.pib_crescimento_atual_mensal * 12
    avg_credibilidade = sum(estado.historico_credibilidade) / len(estado.historico_credibilidade) if estado.historico_credibilidade else estado.credibilidade_bc
    avg_pressao = sum(estado.historico_pressao_politica) / len(estado.historico_pressao_politica) if estado.historico_pressao_politica else estado.pressao_politica
    avg_divida_pib = sum(estado.historico_divida_pib) / len(estado.historico_divida_pib) if estado.historico_divida_pib else estado.divida_publica_pib
    avg_desemprego = sum(estado.historico_desemprego) / len(estado.historico_desemprego) if estado.historico_desemprego else estado.taxa_desemprego_atual
    pontuacao_inflacao = 0; desvio_infl_meta = abs(avg_inflacao - estado.meta_inflacao_anual)
    if desvio_infl_meta <= estado.banda_inflacao_original: pontuacao_inflacao = 50
    elif desvio_infl_meta <= estado.banda_inflacao_original + 1.0: pontuacao_inflacao = 30
    elif desvio_infl_meta <= estado.banda_inflacao_original + 3.0: pontuacao_inflacao = 10
    else: pontuacao_inflacao = -20 if avg_inflacao > estado.meta_inflacao_anual else -10 
    pontuacao_pib = 0
    if avg_pib >= estado.meta_pib_anual - estado.banda_pib_anual / 2: pontuacao_pib = 50 
    elif avg_pib >= estado.meta_pib_anual - estado.banda_pib_anual - 1.0: pontuacao_pib = 30 
    elif avg_pib > 0: pontuacao_pib = 10 
    else: pontuacao_pib = -30 
    pontuacao_divida = 0
    if avg_divida_pib <= 60: pontuacao_divida = 30  
    elif avg_divida_pib <= 75: pontuacao_divida = 15 
    elif avg_divida_pib <= 90: pontuacao_divida = -15 
    else: pontuacao_divida = -40 
    pontuacao_governanca = (avg_credibilidade * 0.7) - (avg_pressao * 0.3) 
    pontuacao_desemprego = 0
    if avg_desemprego <= 6.0: pontuacao_desemprego = 25
    elif avg_desemprego <= 8.0: pontuacao_desemprego = 10
    elif avg_desemprego > 12.0: pontuacao_desemprego = -20
    pontuacao_total = pontuacao_inflacao + pontuacao_pib + pontuacao_governanca + pontuacao_divida + pontuacao_desemprego
    metas_atingidas_count = sum(1 for meta, atingida in estado.mandate_goals.items() if atingida)
    pontuacao_total += metas_atingidas_count * 20 
    if demissao_precoce: pontuacao_total *= 0.6 
    tempo_mandato_anos = (estado.ano_atual - 2024) + (estado.mes_atual -1) /12
    summary_lines = [f"--- SUMARIO DO MANDATO ({tempo_mandato_anos:.1f} de {estado.mandato_anos} anos) ---", f"Inflacao Media Anualizada: {avg_inflacao:.2f}% (Meta Original: {estado.meta_inflacao_anual:.1f}% +/- {estado.banda_inflacao_original:.1f}%)", f"Crescimento Medio do PIB Anualizado: {avg_pib:.2f}% (Meta: {estado.meta_pib_anual:.1f}% +/- {estado.banda_pib_anual:.1f}%)", f"Taxa Media de Desemprego: {avg_desemprego:.1f}%", f"Credibilidade Media do BC: {avg_credibilidade:.0f}/100", f"Pressao Politica Media: {avg_pressao:.0f}/100", f"Dívida Pública/PIB Média: {avg_divida_pib:.1f}%", f"Metas de Mandato Opcionais Atingidas: {metas_atingidas_count}/{len(estado.mandate_goals)}", "", f"Pontuacao Geral de Desempenho: {pontuacao_total:.0f} pontos."]
    veredito = ""
    if demissao_precoce:
        veredito = "MANDATO INTERROMPIDO PRECOCEMENTE. Desafios insuperaveis levaram a sua saida."
        if estado.credibilidade_bc <=0 : veredito += " A perda total de credibilidade foi crucial."
        elif estado.pressao_politica >= 100: veredito += " A pressao politica tornou-se insustentavel."
        elif estado.divida_publica_pib >= 120: veredito += " A crise fiscal da divida elevada foi determinante."
    else: 
        if pontuacao_total >= 120: veredito = "MANDATO DE SUCESSO EXCEPCIONAL! Voce navegou a economia com maestria."
        elif pontuacao_total >= 70: veredito = "GESTAO SOLIDA E BEM-SUCEDIDA! Cumpriu os principais objetivos."
        elif pontuacao_total >= 20: veredito = "GESTAO ACEITAVEL, COM ALTOS E BAIXOS. Manteve a economia nos trilhos."
        elif pontuacao_total >= -20: veredito = "GESTAO COM DIFICULDADES NOTAVEIS. Resultados aquem do esperado."
        else: veredito = "MANDATO MUITO DIFICIL E COM RESULTADOS INSATISFATORIOS."
    summary_lines.append(veredito)
    return "\n".join(summary_lines)
