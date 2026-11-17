import csv
import json
import os
from typing import Dict, List, Tuple, Optional
import requests
from requests.exceptions import RequestException

CHANNEL_ID = "SEU_CHANNEL_ID_AQUI"
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=20"
BACKUP_FILE = "backup.json"
HISTORICO_FILE = "historico.json"
RELATORIO_CSV = "relatorio.csv"

PESO_NIVEL_AGUA = 0.6
PESO_INTENSIDADE_CHUVA = 0.4
LIMITE_ATENCAO = 40.0
LIMITE_ALERTA = 70.0


def carregar_backup() -> List[Dict]:
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                print(f"[Plano B] Dados carregados com sucesso do ficheiro '{BACKUP_FILE}'.")
                return dados.get("feeds", [])
        except json.JSONDecodeError:
            print(f"Erro: O ficheiro '{BACKUP_FILE}' está corrompido.")
            return []
    print(f"Erro: Ficheiro '{BACKUP_FILE}' não encontrado.")
    return []


def buscar_dados_thingspeak() -> List[Dict]:
    try:
        response = requests.get(THINGSPEAK_URL, timeout=5)
        response.raise_for_status()
        dados = response.json()
        print("Dados obtidos com sucesso do ThingSpeak!")
        return dados.get("feeds", [])
    except (RequestException, ValueError) as err:
        print(f"[Aviso] Falha ao comunicar com o ThingSpeak ({err}). A ativar o Plano B...")
        return carregar_backup()


def calcular_indice_risco(
    nivel_agua: float,
    chuva: float,
    peso_agua: float = PESO_NIVEL_AGUA,
    peso_chuva: float = PESO_INTENSIDADE_CHUVA,
) -> float:
    if peso_agua < 0 or peso_chuva < 0 or (peso_agua + peso_chuva) == 0:
        raise ValueError("Configuração inválida: os pesos devem ser não-negativos e a sua soma maior que zero.")

    if not (0 <= nivel_agua <= 100) or not (0 <= chuva <= 100):
        raise ValueError("Configuração inválida: os valores dos sensores devem estar entre 0 e 100.")

    indice = (nivel_agua * peso_agua) + (chuva * peso_chuva)
    return round(indice, 2)


def classificar_faixa(indice: float) -> str:
    if indice < LIMITE_ATENCAO:
        return "Normal"
    elif indice < LIMITE_ALERTA:
        return "Atenção"
    return "Crítico"


def processar_leituras(feeds: List[Dict]) -> List[Dict]:
    registos_processados = []
    for f in feeds:
        try:
            val_agua = float(f.get("field1", 0) or 0)
            val_chuva = float(f.get("field2", 0) or 0)
            
            idx = calcular_indice_risco(val_agua, val_chuva)
            faixa = classificar_faixa(idx)

            registos_processados.append({
                "entry_id": f.get("entry_id"),
                "created_at": f.get("created_at"),
                "nivel_agua": val_agua,
                "chuva": val_chuva,
                "indice_risco": idx,
                "faixa": faixa
            })
        except ValueError as e:
            print(f"[Erro de Leitura] ID {f.get('entry_id')}: {e}")
    return registos_processados


def guardar_historico_acumulado(novos_dados: List[Dict]) -> None:
    historico = []
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except json.JSONDecodeError:
            historico = []

    ids_existentes = {item["entry_id"] for item in historico if "entry_id" in item}
    adicionados = 0

    for item in novos_dados:
        if item["entry_id"] not in ids_existentes:
            historico.append(item)
            ids_existentes.add(item["entry_id"])
            adicionados += 1

    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

    print(f"Histórico atualizado: {adicionados} novos registos adicionados a '{HISTORICO_FILE}'.")


def exportar_csv(dados: List[Dict]) -> None:
    if not dados:
        print("Nenhum dado disponível para exportar em CSV.")
        return

    campos = ["entry_id", "created_at", "nivel_agua", "chuva", "indice_risco", "faixa"]
    with open(RELATORIO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"Relatório exportado com sucesso para '{RELATORIO_CSV}'.")


def gerar_relatorio_analitico(dados: List[Dict]) -> None:
    if not dados:
        print("Sem dados suficientes para gerar relatório.")
        return

    contagem = {"Normal": 0, "Atenção": 0, "Crítico": 0}
    episodios_alerta = []

    for d in dados:
        faixa = d["faixa"]
        contagem[faixa] = contagem.get(faixa, 0) + 1
        if faixa in ["Atenção", "Crítico"]:
            episodios_alerta.append(d)

    primeiro_idx = dados[0]["indice_risco"]
    ultimo_idx = dados[-1]["indice_risco"]
    diferenca = ultimo_idx - primeiro_idx

    if diferenca > 2:
        tendencia = "EM PIORA ⚠️ (Situação a agravar-se)"
    elif diferenca < -2:
        tendencia = "EM MELHORIA 🟢"
    else:
        tendencia = "ESTÁVEL 🟡"

    print("\n" + "=" * 50)
    print("         RELATÓRIO DE ÍNDICE DE RISCO")
    print("=" * 50)
    print(f"Tendência Atual: {tendencia}")
    print(f"Variação do Índice: {primeiro_idx} ➔ {ultimo_idx} ({diferenca:+.2f})")
    print("\nContagem por Faixa de Risco:")
    for faixa, qtd in contagem.items():
        print(f"  - {faixa}: {qtd} leitura(s)")

    print(f"\nEpisódios de Alerta/Atenção ({len(episodios_alerta)} detetados):")
    for ep in episodios_alerta:
        print(f"  [ID {ep['entry_id']} | {ep['created_at']}] Risco: {ep['indice_risco']} ({ep['faixa']})")
    print("=" * 50 + "\n")


def menu_principal() -> None:
    dados_atuais: List[Dict] = []

    while True:
        print("\n--- CITIZENTECH: BOLSÃO ALERTA ---")
        print("1. Buscar dados do ThingSpeak (com Plano B)")
        print("2. Processar e Calcular Índice de Risco")
        print("3. Exibir Relatório Analítico (Tendência e Alertas)")
        print("4. Guardar no Histórico Acumulado (historico.json)")
        print("5. Exportar Relatório em CSV (relatorio.csv)")
        print("6. Sair")
        
        opcao = input("Escolha uma opção (1-6): ").strip()

        if opcao == "1":
            raw_feeds = buscar_dados_thingspeak()
            if raw_feeds:
                dados_atuais = processar_leituras(raw_feeds)
        elif opcao == "2":
            if not dados_atuais:
                print("Por favor, execute primeiro a Opção 1 para obter os dados.")
            else:
                print(f"{len(dados_atuais)} registos processados com sucesso!")
        elif opcao == "3":
            gerar_relatorio_analitico(dados_atuais)
        elif opcao == "4":
            if dados_atuais:
                guardar_historico_acumulado(dados_atuais)
            else:
                print("Nenhum dado processado para guardar.")
        elif opcao == "5":
            if dados_atuais:
                exportar_csv(dados_atuais)
            else:
                print("Nenhum dado processado para exportar.")
        elif opcao == "6":
            print("A encerrar o programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()