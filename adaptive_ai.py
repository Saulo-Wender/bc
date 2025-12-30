# adaptive_ai.py
import random
from collections import Counter
from config import YELLOW_ALERT, RED_CRITICAL
# --- NOVA IMPORTAÇÃO ---
from events import EVENTOS_DIRECIONADOS_IA

def ia_diretora_avalia_e_reage(game_state):
    """
    Analisa o estado do jogo e o comportamento do jogador para decidir se uma
    intervenção da IA é necessária para manter o jogo dinâmico.
    """
    
    # --- Verificação de Arquétipo 1: Jogador Passivo ---
    if game_state.meses_sem_acao_significativa >= 3:
        chance_de_intervir = (game_state.meses_sem_acao_significativa - 2) * 0.33
        if random.random() < chance_de_intervir:
            game_state.meses_sem_acao_significativa = 0
            # Reutiliza o evento de coletiva de imprensa que já criamos
            # (Poderia estar no novo dicionário também, mas vamos manter assim por enquanto)
            evento_coletiva = {
                "type": "escolha",
                "data": {
                    "nome": "Coletiva de Imprensa Surpresa",
                    "manchete": "Mercado e Imprensa Questionam Inércia do BC",
                    "mensagem_contexto": "Um influente jornalista econômico o surpreende com uma pergunta direta: 'Presidente, o país enfrenta desafios, mas o Banco Central parece em compasso de espera. Qual a estratégia por trás desta aparente inatividade?'",
                    "opcoes": [
                        {"texto": "Reafirmar que o BC age com cautela e no momento certo.", "impactos": {"credibilidade_bc": 2.5, "pressao_politica": 2.0}, "resultado": "Sua resposta cautelosa agrada parte do mercado, mas a imprensa e políticos a veem como uma desculpa para a inação."},
                        {"texto": "Sinalizar que novas medidas estão em estudo.", "impactos": {"credibilidade_bc": -3.0, "pressao_politica": -3.0}, "resultado": "A sinalização de futuras ações alivia a pressão política, mas o mercado teme que o BC aja de forma reativa e não planejada."}
                    ]
                }
            }
            return evento_coletiva

    # --- Verificação de Arquétipo 2: "One-Trick Pony" (Uso excessivo da SELIC) ---
    if len(game_state.historico_acoes) >= 6:
        contagem_acoes = Counter(game_state.historico_acoes)
        if contagem_acoes.get('alterar_selic', 0) / len(game_state.historico_acoes) >= 0.75:
            if random.random() < 0.25:
                game_state.add_log_entry("IA DIRETORA: O mercado nota o uso excessivo da SELIC como única ferramenta.", YELLOW_ALERT)
                game_state.credibilidade_bc = max(0, game_state.credibilidade_bc - random.uniform(1.0, 2.5))
                return None

    # --- Verificação de Arquétipo 3: Falcão Agressivo (Hawk) ---
    inflacao_anual = game_state.inflacao_atual_mensal * 12
    if (game_state.selic_anual > game_state.meta_inflacao_anual + 5.0 and 
        inflacao_anual < game_state.meta_inflacao_anual and 
        game_state.taxa_desemprego_atual > 9.0):
        if random.random() < 0.4:
            # --- MUDANÇA DE LÓGICA ---
            # Em vez de uma penalidade simples, agora retorna o evento narrativo.
            return EVENTOS_DIRECIONADOS_IA["FALCAO_AGRESSIVO_CRISE_INDUSTRIA"]

    # --- Verificação de Arquétipo 4: Pomba Complacente (Dove) ---
    if (inflacao_anual > game_state.meta_inflacao_anual + game_state.banda_inflacao_anual + 1.5 and
        game_state.selic_anual < inflacao_anual):
        if random.random() < 0.4:
            # --- MUDANÇA DE LÓGICA ---
            # Em vez de uma penalidade simples, agora retorna o evento narrativo.
            return EVENTOS_DIRECIONADOS_IA["POMBA_COMPLACENTE_AGENCIA_RISCO"]

    return None