import pandas as pd
import webbrowser
import time
import os
from urllib.parse import quote

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'phones_full.csv'
LINK_PROJETO = "https://psitelemedicina.netlify.app/"

# TUA COPY
COPY = "Olá {nome}! Tudo bem? Vi seu perfil no PsyMeet e achei seu trabalho fantástico. Estou expandindo um projeto para viabilizar atendimentos online com mais tecnologia e gostaria de te convidar para conhecer: {link}"

def disparar_mensagens():
    if not os.path.exists(ARQUIVO_CSV):
        print(f"ERRO: O arquivo '{ARQUIVO_CSV}' não foi encontrado!")
        return

    try:
        # Carrega o CSV
        df = pd.read_csv(ARQUIVO_CSV)
        
        # Como o seu CSV tem colunas repetidas, vamos garantir que pegamos a correta
        if 'normalized' in df.columns:
            # Seleciona a coluna normalized (se houver mais de uma, pega a primeira)
            # Converte para String para evitar o erro "AttributeError"
            coluna_tel = df['normalized']
            if isinstance(coluna_tel, pd.DataFrame): # Caso existam duas colunas com mesmo nome
                df['tel_limpo'] = coluna_tel.iloc[:, 0].astype(str)
            else:
                df['tel_limpo'] = coluna_tel.astype(str)
        else:
            print("Erro: Coluna 'normalized' não encontrada.")
            return

        # 1. Limpeza: Remove duplicados e o número do suporte do PsyMeet
        df = df.drop_duplicates(subset=['tel_limpo'])
        # Filtra o número do suporte (convertendo para string antes)
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total = len(contatos)

        print(f"=== DISPARADOR ATIVADO ===")
        print(f"Total de contactos únicos encontrados: {total}")
        
        confirmar = input("\nDeseja abrir as 10 primeiras janelas do WhatsApp? (s/n): ")
        if confirmar.lower() != 's':
            return

        # 2. Loop de 10 em 10
        for i in range(0, total, 10):
            bloco = contatos[i : i + 10]
            print(f"\n>>> Abrindo bloco { (i//10) + 1 }...")
            
            for pessoa in bloco:
                # Usa o telefone que limpamos
                numero = str(pessoa['tel_limpo']).replace('+', '').strip()
                
                # Trata o nome
                nome_completo = str(pessoa['name']) if 'name' in pessoa and pd.notna(pessoa['name']) else "Doutor(a)"
                primeiro_nome = nome_completo.split()[0].capitalize()
                
                # Monta a mensagem e a URL
                texto_msg = COPY.format(nome=primeiro_nome, link=LINK_PROJETO)
                link_whatsapp = f"https://web.whatsapp.com/send?phone={numero}&text={quote(texto_msg)}"
                
                print(f"A abrir: {primeiro_nome} ({numero})")
                webbrowser.open(link_whatsapp)
                time.sleep(1.2)

            print(f"\n[PAUSA] 10 abas abertas.")
            input("Mande as mensagens e dê ENTER aqui para abrir as próximas 10...")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    disparar_mensagens()