import random

# Não precisamos importar EstadoEconomia aqui, pois gerar_evento_aleatorio
# recebe uma instância de EstadoEconomia como parâmetro e opera sobre ela.
# As constantes de cor para logs de eventos também não são necessárias aqui,
# pois a função gerar_evento_aleatorio ou a lógica de popup no main_game
# se encarregarão de passar as cores corretas para estado.add_log_entry.

EVENTOS = [
    {
        "nome": "Choque de Oferta Global (Petroleo)", "tipo": "economico", "probabilidade_base": 0.025, # Probabilidade reduzida
        "impactos": {"inflacao_atual_mensal": 0.4/12, "pib_crescimento_atual_mensal": -0.1/12, "cambio_atual": 0.3, "expectativa_inflacao_mercado_mensal": 0.1/12},
        "manchete": "Crise no Oriente Medio eleva preco do petroleo!",
        "mensagem_impacto": "O custo de energia disparou, afetando precos e produção."
    },
    {
        "nome": "Crise Politica (Escandalo de Corrupcao)", "tipo": "politico", "probabilidade_base": 0.020, # Probabilidade reduzida
        "impactos": {"credibilidade_bc": -5, "pressao_politica": 10, "cambio_atual": 0.2, "pib_crescimento_atual_mensal": -0.05/12},
        "manchete": "Novo escandalo de corrupcao abala Brasilia!",
        "mensagem_impacto": "A instabilidade politica causa fuga de capital e incerteza."
    },
    {
        "nome": "Delegacao Presidencial: Meta de Crescimento Ambiciosa", "tipo": "presidencial", "probabilidade_base": 0.015, # Probabilidade reduzida
        "impactos": {"meta_pib_anual": 4.0, "pressao_politica": 15, "credibilidade_bc": -3}, # meta_pib_anual é um valor, não um delta
        "manchete": "Presidente anuncia: 'Crescimento de 4% e inegociavel!'",
        "mensagem_impacto": "A pressao sobre o BC para estimular a economia aumenta."
    },
    {
        "nome": "Boom Agricola Inesperado", "tipo": "economico_positivo", "probabilidade_base": 0.020, # Probabilidade reduzida
        "impactos": {"inflacao_atual_mensal": -0.2/12, "pib_crescimento_atual_mensal": 0.1/12, "cambio_atual": -0.1},
        "manchete": "Super-safra recorde surpreende e derruba precos de alimentos!",
        "mensagem_impacto": "Abundancia nas lavouras promete alivio inflacionario e impulsiona PIB."
    },
    {
        "nome": "Surto de Doenca Global", "tipo": "economico", "probabilidade_base": 0.010, # Probabilidade reduzida
        "impactos": {"pib_crescimento_atual_mensal": -0.2/12, "taxa_desemprego_atual": 1.0, "pressao_politica": 10},
        "manchete": "Novo surto de doenca global impacta cadeias de suprimentos e economias!",
        "mensagem_impacto": "Paralisacao de setores e reducao do comercio freiam a economia global e local."
    },
    {
        "nome": "Descoberta de Grandes Reservas Naturais", "tipo": "economico_positivo", "probabilidade_base": 0.005, # Mais raro
        "impactos": {"pib_crescimento_atual_mensal": 0.3/12, "credibilidade_bc": 10, "cambio_atual": -0.4, "expectativa_inflacao_mercado_mensal": -0.05/12},
        "manchete": "Gigantesca Reserva Natural Descoberta! Economia em Festa!",
        "mensagem_impacto": "Nova riqueza promete onda de investimentos, crescimento e melhora nas contas externas."
    },
    {
        "nome": "Melhora Inesperada do Cenário Global", "tipo": "economico_positivo", "probabilidade_base": 0.015, # Probabilidade reduzida
        "impactos": {"inflacao_atual_mensal": -0.1/12, "pib_crescimento_atual_mensal": 0.05/12, "cambio_atual": -0.2, "expectativa_inflacao_mercado_mensal": -0.03/12},
        "manchete": "Tensao Geopolitica Diminui, Comercio Global Aquece!",
        "mensagem_impacto": "Acordos globais e maior estabilidade impulsionam confianca e fluxos de capital."
    },
    {
        "nome": "Reforma Estrutural Aprovada", "tipo": "politico_positivo", "probabilidade_base": 0.008, # Mais raro
        "impactos": {"credibilidade_bc": 12, "pib_crescimento_atual_mensal": 0.1/12, "pressao_politica": -5, "expectativa_inflacao_mercado_mensal": -0.02/12},
        "manchete": "Congresso Aprova Reforma Crucial! Sinal de Estabilidade e Eficiencia!",
        "mensagem_impacto": "Medidas economicas estruturais simplificam ambiente de negocios e atraem investimentos de longo prazo."
    }
]

EVENTOS_COM_ESCOLHAS = [
    {
        "nome": "Onda de Protestos Sociais", "tipo": "social", "probabilidade_base": 0.015, # Probabilidade reduzida
        "condicao_ativacao": {"inflacao_acima_meta_banda": 2.0, "desemprego_min": 9.5, "selic_muito_alta": 15.0},
        "condicao_inibicao": {"inflacao_abaixo_meta_banda": -1.0, "desemprego_max": 7.0, "selic_muito_baixa": 5.0},
        "manchete": "Populacao vai as ruas contra politicas economicas!",
        "mensagem_contexto": "Manifestacoes populares massivas exigem uma postura diferente do Banco Central frente ao cenário econômico. O que voce faz?",
        "opcoes": [
            {
                "texto": "Manter a linha dura, priorizando controle da inflacao.",
                "impactos": {"pressao_politica": 15, "credibilidade_bc": 5, "expectativa_inflacao_mercado_mensal": -0.02/12},
                "resultado": "BC demonstra firmeza e é visto como rigoroso pelo mercado, mas a pressao popular aumenta consideravelmente."
            },
            {
                "texto": "Sinalizar dialogo e possivel flexibilizacao para aliviar tensoes.",
                "impactos": {"pressao_politica": -10, "credibilidade_bc": -7, "expectativa_inflacao_mercado_mensal": 0.05/12},
                "resultado": "A pressao popular diminui com a sinalizacao, mas o mercado financeiro fica apreensivo com a possível perda de foco no controle inflacionário."
            }
        ]
    },
    {
        "nome": "Pressao por Gasto Publico", "tipo": "politico_economico", "probabilidade_base": 0.018, # Probabilidade reduzida
        "condicao_ativacao": {"pib_muito_baixo": 1.0, "desemprego_min": 10.0}, # PIB anualizado
        "condicao_inibicao": {"pib_muito_alto": 4.0, "desemprego_max": 6.0}, # PIB anualizado
        "manchete": "Parlamentares exigem aumento de gastos para impulsionar economia!",
        "mensagem_contexto": "O Congresso Nacional pressiona por um aumento significativo nos gastos publicos para estimular o crescimento do PIB e reduzir o desemprego. Isso pode gerar inflacao. Como o Banco Central se posiciona?",
        "opcoes": [
            {
                "texto": "Reforcar publicamente a necessidade de responsabilidade fiscal.",
                "impactos": {"pressao_politica": 10, "credibilidade_bc": 8, "pib_crescimento_atual_mensal": -0.03/12}, # Pequeno impacto negativo no PIB por adiar estímulos
                "resultado": "O BC ganha confianca de investidores internacionais, mas irrita alguns setores do parlamento e do governo."
            },
            {
                "texto": "Mostrar-se receptivo as discussoes, afirmando que o BC acompanhara os impactos.",
                "impactos": {"pressao_politica": -5, "credibilidade_bc": -5, "inflacao_atual_mensal": 0.05/12}, # Aumento direto na inflação por expectativas
                "resultado": "A postura agrada o congresso e alivia a tensao politica, mas levanta preocupacoes no mercado sobre a autonomia do BC e o futuro da inflacao."
            }
        ]
    }
]

ASSESSORES = {
    "Liberal": {
        "descricao": "Prioriza estabilidade monetaria, controle fiscal rigoroso e minima intervencao estatal. Acredita que o mercado se ajusta eficientemente com juros altos para combater a inflacao e politicas pro-mercado.",
        "conselho_inflacao_alta": "Inflacao descontrolada e o maior inimigo! Um choque de juros e necessario para ancorar expectativas e restaurar a confianca. Suba a SELIC imediatamente e sinalize mais altas se preciso!",
        "conselho_inflacao_baixa": "Deflacao e um perigo para a atividade economica. Juros baixos sao adequados, sim, mas evite desespero e criacao artificial de demanda. Mantenha a estabilidade dos precos como foco.",
        "conselho_pib_baixo": "O crescimento sustentavel vira da liberdade economica e da confianca gerada pela responsabilidade fiscal. O BC deve focar na inflacao; o crescimento e consequencia de boas politicas estruturais.",
        "conselho_credibilidade_baixa_pressao_alta": "Sua credibilidade esta em jogo! A unica saida e reafirmar o compromisso com a disciplina fiscal e monetaria. Comunique com firmeza e atue sem hesitar para restaurar a confianca.",
        "conselho_geral_otimo": "Excelente trabalho! A estabilidade monetaria e fiscal e a base da prosperidade. Mantenha a disciplina e a previsibilidade, o mercado agradece.",
        "conselho_divida_alta": "Dívida pública em trajetória explosiva! Responsabilidade fiscal é urgente ou o país enfrentará uma crise de confiança sem precedentes. O BC não pode resolver isso sozinho, mas deve sinalizar os riscos."
    },
    "Desenvolvimentista": {
        "descricao": "Foca em crescimento economico acelerado e pleno emprego, mesmo que isso implique tolerar uma inflacao um pouco mais alta. Defende politicas de estimulo e investimento publico.",
        "conselho_inflacao_alta": "Inflacao e um custo do crescimento, mas claro que precisa de cuidado. Juros excessivamente altos matam o PIB e o emprego! Considere medidas alternativas, não apenas a SELIC.",
        "conselho_inflacao_baixa": "Deflacao e sintoma de estagnacao e desemprego! E preciso estimular a economia a qualquer custo. Reduza os juros drasticamente e incentive o credito para reaquecer a demanda.",
        "conselho_pib_baixo": "O pais precisa crescer e gerar empregos urgentemente! Juros baixos sao essenciais para impulsionar a producao e o investimento. O Banco Central deve ser um motor do desenvolvimento.",
        "conselho_credibilidade_baixa_pressao_alta": "A populacao e o setor produtivo sofrem com a estagnacao! O BC precisa ser mais ativo e direto no fomento ao desenvolvimento. Acoes urgentes sao necessarias para reverter o quadro.",
        "conselho_geral_otimo": "O pais esta crescendo e a inflacao esta sob controle razoavel! Este e o caminho para o bem-estar social e a prosperidade de longo prazo. Continue assim!",
        "conselho_divida_alta": "A dívida é uma preocupação, mas não podemos permitir que o ajuste fiscal sufoque o crescimento necessário. Investimentos estratégicos podem aumentar o PIB e, assim, reduzir a razão Dívida/PIB no futuro."
    },
    "Pragmatico": {
        "descricao": "Busca um equilibrio entre controle da inflacao e crescimento economico, adaptando as politicas conforme o cenario. Valoriza dados, comunicacao clara e a reacao do mercado.",
        "conselho_estagflacao": "Estamos numa encruzilhada: inflacao alta com PIB baixo. E a situacao mais delicada. Requer uma calibracao fina da SELIC e, possivelmente, outras ferramentas. Comunique-se com transparencia.",
        "conselho_inflacao_alta": "A inflacao corrente exige atencao e acao. E preciso calibrar a SELIC para combater a alta dos precos, mas com cuidado para nao sufocar uma eventual recuperacao do crescimento. Acao moderada e bem comunicada.",
        "conselho_inflacao_baixa": "A deflacao e um alerta de possivel estagnacao. Ajustar os juros para baixo pode ser necessario, mas sem panico. O objetivo e crescimento sustentavel com estabilidade de precos.",
        "conselho_pib_baixo": "O PIB precisa de folego, mas a inflacao pode ser uma ameaca. Os juros devem ser flexiveis, baseados em dados concretos e expectativas. Considere o cenario global.",
        "conselho_superaquecimento": "O PIB esta aquecido e a inflacao comeca a dar sinais preocupantes. E preciso cautela para nao desancorar as expectativas. Uma leve alta nos juros pode ser preventiva.",
        "conselho_credibilidade_baixa_pressao_alta": "Pragmatismo e agilidade sao chave agora. Reavalie todos os dados, considere todas as opcoes de politica e comunique suas decisoes de forma clara. A prioridade e reverter a instabilidade.",
        "conselho_geral_otimo": "As coisas parecem estar indo bem! Adaptacao as circunstancias e analise fria dos indicadores estao dando resultado. Continue monitorando de perto todos os fronts.",
        "conselho_divida_alta": "A trajetória da dívida pública atingiu um nível perigoso. É necessário um plano crível de ajuste fiscal por parte do governo. O BC deve monitorar os impactos disso sobre os juros e a inflação."
    }
}

# --- NOVA SEÇÃO DE EVENTOS ---

EVENTOS_DIRECIONADOS_IA = {
    "FALCAO_AGRESSIVO_CRISE_INDUSTRIA": {
        "type": "escolha",
        "data": {
            "nome": "Crise na Indústria",
            "manchete": "Indústria Protesta Contra Juros Altos",
            "mensagem_contexto": "O Ministro da Indústria e Comércio convoca a imprensa e declara: 'A política de juros do Banco Central está sufocando o setor produtivo. Estamos vendo fábricas fechando e o desemprego aumentar. É uma política irresponsável!'",
            "opcoes": [
                {
                    "texto": "Ignorar a crítica e manter o foco na inflação.",
                    "impactos": {"pressao_politica": 12, "credibilidade_bc": 4, "pib_crescimento_atual_mensal": -0.05/12},
                    "resultado": "O mercado aplaude sua firmeza, mas a pressão do governo e dos empresários atinge um novo patamar. A atividade econômica sofre um pouco mais."
                },
                {
                    "texto": "Emitir uma nota defendendo a política, mas sinalizando sensibilidade.",
                    "impactos": {"pressao_politica": -5, "credibilidade_bc": -5},
                    "resultado": "Sua nota acalma um pouco os ânimos políticos, mas o mercado financeiro interpreta isso como um sinal de fraqueza, temendo que você ceda às pressões."
                }
            ]
        }
    },
    "POMBA_COMPLACENTE_AGENCIA_RISCO": {
        "type": "escolha",
        "data": {
            "nome": "Rating Sob Ameaça",
            "manchete": "Agência de Risco 'Mundial Ratings' Ameaça Rebaixar o País",
            "mensagem_contexto": "A agência de classificação de risco emite um duro comunicado: 'A contínua tolerância do Banco Central com a inflação acima da meta ameaça desancorar as expectativas de forma permanente. Colocamos a nota de crédito do país em perspectiva negativa.'",
            "opcoes": [
                {
                    "texto": "Afirmar que a inflação é temporária e o foco é o crescimento.",
                    "impactos": {"credibilidade_bc": -15, "cambio_atual": 0.4, "expectativa_inflacao_mercado_mensal": 0.2/12},
                    "resultado": "Sua credibilidade é destruída. O mercado entra em pânico, o câmbio dispara e as expectativas de inflação se deterioram drasticamente."
                },
                {
                    "texto": "Reconhecer o risco e prometer uma postura mais dura à frente.",
                    "impactos": {"credibilidade_bc": -4, "pressao_politica": 5},
                    "resultado": "O mercado se acalma um pouco, mas a credibilidade já foi arranhada. O governo, que gostava dos juros baixos, aumenta a pressão."
                }
            ]
        }
    }
}


def calcular_impacto_total(evento):
    """Calcula um 'peso' para o impacto total de um evento, usado para seleção."""
    total_impacto = 0
    # Pesos para dar mais importância a certas variáveis no cálculo do "tamanho" do evento
    pesos = {
        "inflacao_atual_mensal": 10, "pib_crescimento_atual_mensal": 15,
        "cambio_atual": 5, "expectativa_inflacao_mercado_mensal": 8,
        "credibilidade_bc": 20, "pressao_politica": 18,
        "meta_pib_anual": 25, "taxa_desemprego_atual": 12
    }
    for k, v in evento["impactos"].items():
        # Normaliza impactos mensais para uma base comparável (ex, anualizando)
        # Esta normalização é uma simplificação e pode ser ajustada
        valor_ajustado = v
        if k in ["inflacao_atual_mensal", "pib_crescimento_atual_mensal", "expectativa_inflacao_mercado_mensal"]:
            valor_ajustado *= 12 
        total_impacto += abs(valor_ajustado * pesos.get(k, 1))
    return total_impacto

def gerar_evento_aleatorio(estado):
    """Gera um evento aleatório (normal ou com escolha) para o mês atual."""
    if estado.evento_ocorrido_este_mes:
        return None # Já ocorreu um evento neste mês

    # Cooldown após evento negativo grande ou muitos eventos consecutivos
    if estado.meses_apos_evento_negativo_grande > 0:
        estado.meses_apos_evento_negativo_grande -= 1
        estado.meses_sem_evento_forçado += 1
        estado.eventos_consecutivos = 0
        return None
    if estado.eventos_consecutivos >= 3: # Limite de 3 eventos seguidos
        estado.meses_sem_evento_forçado += 1
        estado.eventos_consecutivos = 0
        return None

    # Probabilidade base de ocorrer qualquer evento, aumenta se não houver eventos por um tempo
    prob_base_ocorrer = 0.08 # Reduzida a probabilidade base geral de eventos por mês
    prob_base_ocorrer += (estado.meses_sem_evento_forçado - 1) * 0.05 # Aumenta 5% por mês sem evento, após o primeiro
    prob_base_ocorrer = min(prob_base_ocorrer, 0.35) # Limite máximo de chance de evento

    if random.random() > prob_base_ocorrer:
        estado.eventos_consecutivos = 0
        estado.meses_sem_evento_forçado += 1
        return None

    # Tenta gerar um evento com escolha primeiro
    eventos_com_escolha_candidatos = []
    for evento_data in EVENTOS_COM_ESCOLHAS:
        prob_ajustada = evento_data["probabilidade_base"]
        inibido = False
        # Verifica condições de inibição
        if "condicao_inibicao" in evento_data:
            if "inflacao_abaixo_meta_banda" in evento_data["condicao_inibicao"] and \
               (estado.inflacao_atual_mensal * 12) < (estado.meta_inflacao_anual - estado.banda_inflacao_anual + evento_data["condicao_inibicao"]["inflacao_abaixo_meta_banda"]):
                inibido = True
            if "desemprego_max" in evento_data["condicao_inibicao"] and \
               estado.taxa_desemprego_atual < evento_data["condicao_inibicao"]["desemprego_max"]:
                inibido = True
            # Adicionar outras condições de inibição aqui...

        if inibido:
            prob_ajustada *= 0.1 # Muito menos provável se inibido
        else:
            # Verifica condições de ativação
            condicoes_cumpridas = 0
            num_condicoes_ativacao = len(evento_data.get("condicao_ativacao", {}))
            if num_condicoes_ativacao > 0:
                ativacao = evento_data["condicao_ativacao"]
                if "inflacao_acima_meta_banda" in ativacao and \
                   (estado.inflacao_atual_mensal * 12) > (estado.meta_inflacao_anual + estado.banda_inflacao_anual + ativacao["inflacao_acima_meta_banda"]):
                    condicoes_cumpridas +=1
                if "desemprego_min" in ativacao and estado.taxa_desemprego_atual >= ativacao["desemprego_min"]:
                    condicoes_cumpridas +=1
                if "selic_muito_alta" in ativacao and estado.selic_anual >= ativacao["selic_muito_alta"]:
                    condicoes_cumpridas +=1
                if "pib_muito_baixo" in ativacao and (estado.pib_crescimento_atual_mensal * 12) <= ativacao["pib_muito_baixo"]:
                    condicoes_cumpridas +=1
                
                if condicoes_cumpridas == num_condicoes_ativacao: # Todas cumpridas
                    prob_ajustada *= 2.5
                elif condicoes_cumpridas > 0: # Alguma cumprida
                    prob_ajustada *= 1.5
                else: # Nenhuma cumprida
                    prob_ajustada *= 0.5
        
        if random.random() < prob_ajustada:
            eventos_com_escolha_candidatos.append(evento_data)

    # Chance de escolher um evento com escolha se houver candidatos
    if eventos_com_escolha_candidatos and random.random() < 0.4: # 40% de chance se houver candidatos
        evento_escolhido = random.choice(eventos_com_escolha_candidatos)
        estado.eventos_consecutivos += 1
        estado.meses_sem_evento_forçado = 0
        estado.evento_ocorrido_este_mes = True
        # Os impactos de eventos com escolha são aplicados após a escolha do jogador no main_game
        return {"type": "escolha", "data": evento_escolhido}

    # Se não for evento com escolha, tenta um evento normal
    eventos_normais_candidatos = []
    for evento_data in EVENTOS:
        if random.random() < evento_data["probabilidade_base"]:
            eventos_normais_candidatos.append(evento_data)
    
    if not eventos_normais_candidatos:
        # Se nenhum candidato pela probabilidade, 50% de chance de escolher um evento normal aleatoriamente de todos
        if random.random() < 0.5: 
            evento_escolhido = random.choice(EVENTOS)
        else: # Ou nenhum evento este mês
            estado.eventos_consecutivos = 0
            estado.meses_sem_evento_forçado += 1
            return None
    else:
        # Escolhe entre os candidatos com base no impacto (inversamente proporcional, eventos menores são mais comuns)
        eventos_com_impacto = [{"evento": ev, "impacto": calcular_impacto_total(ev)} for ev in eventos_normais_candidatos]
        eventos_com_impacto.sort(key=lambda x: x["impacto"]) # Ordena por impacto (menor primeiro)

        # Dá mais peso a eventos de menor impacto
        pesos_selecao = [1.0 / (item["impacto"] + 0.1) for item in eventos_com_impacto] # Adiciona 0.1 para evitar divisão por zero
        
        # Normaliza os pesos para que somem 1 (probabilidades)
        total_pesos = sum(pesos_selecao)
        if not pesos_selecao or total_pesos == 0: # Fallback se algo der errado com os pesos
            evento_escolhido = random.choice([item["evento"] for item in eventos_com_impacto])
        else:
            probabilidades_selecao = [p / total_pesos for p in pesos_selecao]
            evento_escolhido = random.choices([item["evento"] for item in eventos_com_impacto], weights=probabilidades_selecao, k=1)[0]

    # Aplica impactos do evento normal escolhido
    impacto_total_evento_gerado = calcular_impacto_total(evento_escolhido)
    for k, v_delta in evento_escolhido["impactos"].items():
        if k == "meta_pib_anual": # "meta_pib_anual" é um valor absoluto, não um delta
            estado.meta_pib_anual = v_delta
        elif hasattr(estado, k):
            setattr(estado, k, getattr(estado, k) + v_delta)
    
    estado.eventos_consecutivos += 1
    estado.meses_sem_evento_forçado = 0
    estado.evento_ocorrido_este_mes = True
    
    # Se o evento for negativo e grande, ativa um cooldown para o próximo evento
    # Considera "negativo" se houver impactos que pioram indicadores chave (ex: credibilidade cai, inflação sobe)
    e_negativo = False
    if evento_escolhido["impactos"].get("credibilidade_bc", 0) < 0 or \
       evento_escolhido["impactos"].get("inflacao_atual_mensal", 0) > 0 or \
       evento_escolhido["impactos"].get("pib_crescimento_atual_mensal", 0) < 0 or \
       evento_escolhido["impactos"].get("pressao_politica", 0) > 0:
        e_negativo = True

    if impacto_total_evento_gerado > 30 and e_negativo: # Limiar arbitrário para "grande"
        estado.meses_apos_evento_negativo_grande = 2 # Cooldown de 2 meses

    return {"type": "normal", "data": evento_escolhido}