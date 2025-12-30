# reports.py
import random
import matplotlib.pyplot as plt
from economy_state import EstadoEconomia # Para criar instâncias temporárias

# Importar as funções de economy_mechanics que agora definem ALVOS
from economy_mechanics import (
    atualizar_inflacao, # Continua com o nome original aqui, mas define estado.alvo_inflacao_mensal
    atualizar_pib,      # Define estado.alvo_pib_crescimento_mensal
    atualizar_cambio,   # Define estado.alvo_cambio_atual
    atualizar_desemprego, # Esta já atualiza o estado diretamente de forma suave
    atualizar_expectativa_juros_longo_prazo, # Atualiza o estado diretamente
    atualizar_divida_publica, # Atualiza o estado diretamente
    atualizar_fator_liquidez_bancaria # Atualiza o estado diretamente
)

# Constantes de ajuste para a simulação (podem ser importadas ou passadas como argumento no futuro)
PASSO_AJUSTE_INFLACAO_MENSAL_SIM = 0.00060
PASSO_AJUSTE_PIB_MENSAL_SIM = 0.00015
PASSO_AJUSTE_CAMBIO_SIM = 0.035

def exibir_graficos_matplotlib(estado):
    # ... (função como na última versão completa, sem alterações aqui) ...
    if not estado.historico_inflacao or len(estado.historico_inflacao) < 2:
        print("DEBUG: Dados insuficientes para gerar graficos (chamada a exibir_graficos_matplotlib).")
        return
    meses = range(len(estado.historico_inflacao))
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axs = plt.subplots(4, 2, figsize=(16, 22)) 
    fig.suptitle('Desempenho Economico e Fiscal do Mandato', fontsize=18, y=0.99)
    axs[0, 0].plot(meses, estado.historico_inflacao, label='Inflacao Anualizada (%)', color='red', marker='o', markersize=4, linestyle='-')
    axs[0, 0].axhline(y=estado.meta_inflacao_anual, color='gray', linestyle='--', label=f'Meta ({estado.meta_inflacao_anual:.1f}%)')
    axs[0, 0].axhspan(estado.meta_inflacao_anual - estado.banda_inflacao_original, estado.meta_inflacao_anual + estado.banda_inflacao_original, color='lightgreen', alpha=0.3, label=f'Banda Original (+/-{estado.banda_inflacao_original:.1f}%)')
    if estado.banda_inflacao_anual != estado.banda_inflacao_original: 
        axs[0, 0].axhspan(estado.meta_inflacao_anual - estado.banda_inflacao_anual, estado.meta_inflacao_anual + estado.banda_inflacao_anual, color='lightcoral', alpha=0.2, label=f'Banda Flex. Atual (+/-{estado.banda_inflacao_anual:.1f}%)')
    axs[0, 0].set_title('Inflacao Anualizada (%)'); axs[0, 0].set_xlabel('Meses de Mandato'); axs[0, 0].set_ylabel('% a.a.'); axs[0, 0].legend(fontsize='small'); axs[0, 0].grid(True, linestyle=':', alpha=0.7)
    axs[0, 1].plot(meses, estado.historico_pib, label='PIB Crescimento Anualizado (%)', color='blue', marker='s', markersize=4, linestyle='-')
    axs[0, 1].axhline(y=estado.meta_pib_anual, color='gray', linestyle='--', label=f'Meta ({estado.meta_pib_anual:.1f}%)')
    axs[0, 1].axhspan(estado.meta_pib_anual - estado.banda_pib_anual, estado.meta_pib_anual + estado.banda_pib_anual, color='lightblue', alpha=0.3, label=f'Banda Meta (+/-{estado.banda_pib_anual:.1f}%)')
    axs[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5) 
    axs[0, 1].set_title('PIB Crescimento Anualizado (%)'); axs[0, 1].set_xlabel('Meses de Mandato'); axs[0, 1].set_ylabel('% a.a.'); axs[0, 1].legend(fontsize='small'); axs[0, 1].grid(True, linestyle=':', alpha=0.7)
    axs[1, 0].plot(meses, estado.historico_selic, label='SELIC Anualizada (%)', color='purple', marker='^', markersize=4, linestyle='-')
    if estado.historico_juros_longo_prazo and len(estado.historico_juros_longo_prazo) == len(meses):
        axs[1, 0].plot(meses, estado.historico_juros_longo_prazo, label='Exp. Juros Longos Anual. (%)', color='cyan', marker='D', markersize=4, linestyle='--')
    axs[1, 0].set_title('Taxas de Juros Anualizadas (%)'); axs[1, 0].set_xlabel('Meses de Mandato'); axs[1, 0].set_ylabel('% a.a.'); axs[1, 0].legend(fontsize='small'); axs[1, 0].grid(True, linestyle=':', alpha=0.7)
    if estado.historico_divida_pib and len(estado.historico_divida_pib) == len(meses):
        axs[1, 1].plot(meses, estado.historico_divida_pib, label='Dívida/PIB (%)', color='black', marker='P', markersize=4, linestyle='-')
        axs[1, 1].axhline(y=75, color='red', linestyle=':', label='Nível Alerta (75%)', alpha=0.8); axs[1, 1].axhline(y=60, color='green', linestyle=':', label='Nível Confortável (60%)', alpha=0.8)
    axs[1, 1].set_title('Dívida Pública / PIB (%)'); axs[1, 1].set_xlabel('Meses de Mandato'); axs[1, 1].set_ylabel('% do PIB')
    if estado.historico_divida_pib: axs[1, 1].set_ylim(bottom=max(0, min(estado.historico_divida_pib or [30]) - 10)) 
    axs[1, 1].legend(fontsize='small'); axs[1, 1].grid(True, linestyle=':', alpha=0.7)
    axs[2, 0].plot(meses, estado.historico_credibilidade, label='Credibilidade BC', color='green', marker='P', markersize=4, linestyle='-')
    axs[2, 0].plot(meses, estado.historico_pressao_politica, label='Pressao Politica', color='orange', marker='X', markersize=4, linestyle='-')
    axs[2, 0].axhline(y=50, color='gray', linestyle=':', label='Referencia 50pts', alpha=0.7)
    axs[2, 0].set_title('Indicadores de Governanca'); axs[2, 0].set_xlabel('Meses de Mandato'); axs[2, 0].set_ylabel('Pontos (0-100)'); axs[2, 0].set_ylim(-10, 110); axs[2, 0].legend(fontsize='small'); axs[2, 0].grid(True, linestyle=':', alpha=0.7)
    axs[2, 1].plot(meses, estado.historico_cambio, label='Cambio (R$/US$)', color='brown', marker='d', markersize=4, linestyle='-')
    axs[2, 1].set_title('Taxa de Cambio (R$/US$)'); axs[2, 1].set_xlabel('Meses de Mandato'); axs[2, 1].set_ylabel('R$/US$')
    if estado.historico_cambio: axs[2, 1].set_ylim(bottom=max(0, min(estado.historico_cambio or [3.0]) - 0.5)) 
    axs[2, 1].legend(fontsize='small'); axs[2, 1].grid(True, linestyle=':', alpha=0.7)
    axs[3, 0].plot(meses, estado.historico_desemprego, label='Desemprego (%)', color='teal', marker='v', markersize=4, linestyle='-')
    axs[3, 0].set_title('Taxa de Desemprego (%)'); axs[3, 0].set_xlabel('Meses de Mandato'); axs[3, 0].set_ylabel('% da Forca de Trabalho'); axs[3, 0].set_ylim(bottom=0); axs[3, 0].legend(fontsize='small'); axs[3, 0].grid(True, linestyle=':', alpha=0.7)
    if (estado.historico_compulsorio and len(estado.historico_compulsorio) == len(meses) and estado.historico_expectativa_inflacao and len(estado.historico_expectativa_inflacao) == len(meses)):
        ax_comp = axs[3, 1]; line_comp, = ax_comp.plot(meses, estado.historico_compulsorio, label='Dep. Compulsorio (%)', color='magenta', marker='H', markersize=4, linestyle='-')
        ax_comp.set_title('Compulsorio e Exp. Inflacao Mercado'); ax_comp.set_xlabel('Meses de Mandato'); ax_comp.set_ylabel('Compulsorio (%)', color='magenta'); ax_comp.tick_params(axis='y', labelcolor='magenta'); ax_comp.set_ylim(0, max(50, max(estado.historico_compulsorio or [50]))) 
        ax_exp_inf = ax_comp.twinx(); line_exp_inf, = ax_exp_inf.plot(meses, estado.historico_expectativa_inflacao, label='Exp. Infl. Mercado (Anual. %)', color='lime', linestyle=':', marker='*', markersize=5)
        ax_exp_inf.set_ylabel('Exp. Inflacao (% a.a.)', color='lime'); ax_exp_inf.tick_params(axis='y', labelcolor='lime'); ax_exp_inf.set_ylim(bottom=min(0, min(estado.historico_expectativa_inflacao or [0])-1), top=max(estado.historico_expectativa_inflacao or [10])+2)
        lines = [line_comp, line_exp_inf]; ax_comp.legend(lines, [l.get_label() for l in lines], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize='small'); ax_comp.grid(True, linestyle=':', alpha=0.7) 
    elif estado.historico_expectativa_inflacao and len(estado.historico_expectativa_inflacao) == len(meses) and estado.historico_inflacao and len(estado.historico_inflacao) == len(meses): 
        axs[3,1].plot(meses, estado.historico_expectativa_inflacao, label='Exp. Infl. Mercado (Anual %)', color='magenta', linestyle=':', marker='*'); axs[3,1].plot(meses, estado.historico_inflacao, label='Inflacao Real (%)', color='red', linestyle=':', alpha=0.7)
        axs[3,1].set_title('Expectativa de Inflacao do Mercado'); axs[3,1].set_xlabel('Meses de Mandato'); axs[3,1].set_ylabel('% a.a.'); axs[3,1].legend(fontsize='small'); axs[3,1].grid(True, linestyle=':', alpha=0.7)
    else: 
        axs[3,1].text(0.5, 0.5, "Dados insuficientes para este gráfico", horizontalalignment='center', verticalalignment='center', transform=axs[3,1].transAxes); axs[3,1].set_title('Outros Indicadores')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97]); plt.show(block=True)


# --- FUNÇÃO MODIFICADA ---
def gerar_relatorio_previsao_data(estado_atual_real):
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
        # Adicionar os atributos de alvo para que a simulação comece com eles corretos
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

            # --- LÓGICA DE SIMULAÇÃO CORRIGIDA ---
            # 1. Fatores que afetam os alvos e o estado diretamente
            atualizar_divida_publica(estado_sub_sim) 
            atualizar_fator_liquidez_bancaria(estado_sub_sim) # Ajusta-se gradualmente ao seu próprio alvo

            # 2. Calcular os ALVOS para os indicadores principais
            atualizar_inflacao(estado_sub_sim)  # Define estado_sub_sim.alvo_inflacao_mensal
            atualizar_pib(estado_sub_sim)       # Define estado_sub_sim.alvo_pib_crescimento_mensal
            atualizar_cambio(estado_sub_sim)    # Define estado_sub_sim.alvo_cambio_atual
            
            # 3. Aplicar AJUSTE GRADUAL dos indicadores REAIS em direção aos seus ALVOS
            # Inflação
            if estado_sub_sim.inflacao_atual_mensal < estado_sub_sim.alvo_inflacao_mensal:
                estado_sub_sim.inflacao_atual_mensal = min(estado_sub_sim.inflacao_atual_mensal + PASSO_AJUSTE_INFLACAO_MENSAL_SIM, estado_sub_sim.alvo_inflacao_mensal)
            elif estado_sub_sim.inflacao_atual_mensal > estado_sub_sim.alvo_inflacao_mensal:
                estado_sub_sim.inflacao_atual_mensal = max(estado_sub_sim.inflacao_atual_mensal - PASSO_AJUSTE_INFLACAO_MENSAL_SIM, estado_sub_sim.alvo_inflacao_mensal)
            estado_sub_sim.inflacao_atual_mensal = round(estado_sub_sim.inflacao_atual_mensal, 6)

            # PIB
            if estado_sub_sim.pib_crescimento_atual_mensal < estado_sub_sim.alvo_pib_crescimento_mensal:
                estado_sub_sim.pib_crescimento_atual_mensal = min(estado_sub_sim.pib_crescimento_atual_mensal + PASSO_AJUSTE_PIB_MENSAL_SIM, estado_sub_sim.alvo_pib_crescimento_mensal)
            elif estado_sub_sim.pib_crescimento_atual_mensal > estado_sub_sim.alvo_pib_crescimento_mensal:
                estado_sub_sim.pib_crescimento_atual_mensal = max(estado_sub_sim.pib_crescimento_atual_mensal - PASSO_AJUSTE_PIB_MENSAL_SIM, estado_sub_sim.alvo_pib_crescimento_mensal)
            estado_sub_sim.pib_crescimento_atual_mensal = round(estado_sub_sim.pib_crescimento_atual_mensal, 6)

            # Câmbio
            if estado_sub_sim.cambio_atual < estado_sub_sim.alvo_cambio_atual:
                estado_sub_sim.cambio_atual = min(estado_sub_sim.cambio_atual + PASSO_AJUSTE_CAMBIO_SIM, estado_sub_sim.alvo_cambio_atual)
            elif estado_sub_sim.cambio_atual > estado_sub_sim.alvo_cambio_atual:
                estado_sub_sim.cambio_atual = max(estado_sub_sim.cambio_atual - PASSO_AJUSTE_CAMBIO_SIM, estado_sub_sim.alvo_cambio_atual)
            estado_sub_sim.cambio_atual = round(estado_sub_sim.cambio_atual, 3)
            
            # 4. Atualizar outros indicadores que dependem dos valores REAIS
            estado_sub_sim.taxa_desemprego_atual = atualizar_desemprego(estado_sub_sim)
            
            # Atualizar expectativas dentro da simulação (simplificado)
            estado_sub_sim.expectativa_inflacao_mercado_mensal = (estado_sub_sim.meta_inflacao_anual / 12 * 0.4 + estado_sub_sim.inflacao_atual_mensal * 0.6) + random.uniform(-0.015/12, 0.015/12)
            estado_sub_sim.expectativa_inflacao_mercado_mensal = max(0.005/12, min(3.0/12, estado_sub_sim.expectativa_inflacao_mercado_mensal))
            atualizar_expectativa_juros_longo_prazo(estado_sub_sim) # Usa o tom "neutro" padrão aqui
            # --- FIM DA LÓGICA DE SIMULAÇÃO CORRIGIDA ---
            
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
        
        # Recalcula os alvos para o estado base para o próximo mês da simulação
        atualizar_inflacao(estado_base_para_mes_previsao)
        atualizar_pib(estado_base_para_mes_previsao)
        atualizar_cambio(estado_base_para_mes_previsao)
        atualizar_fator_liquidez_bancaria(estado_base_para_mes_previsao)
        atualizar_divida_publica(estado_base_para_mes_previsao) # Dívida também evolui na simulação base
        
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
    # ... (função como na última versão completa, sem alterações aqui) ...
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