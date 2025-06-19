import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import time
import os  # MUDANÇA 1: Importamos a biblioteca 'os'

# --- FUNÇÃO DE COLETA ÚNICA E ROBUSTA ---

def coletar_noticias_g1():
    """
    Coleta as 5 principais manchetes do G1, incluindo a URL da imagem.
    Usa uma requisição robusta com timeout e headers.
    """
    print("Iniciando a coleta de notícias e imagens do G1...")
    url = 'https://g1.globo.com/'
    noticias_coletadas = []
    
    try:
        # Usando headers e um timeout maior para evitar erros de rede
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=20)
        # Lança um erro se a resposta não for bem-sucedida (ex: 404, 500)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O seletor do G1, que tem se mostrado estável
        posts = soup.find_all('div', class_='feed-post-body')
        
        for post in posts:
            link_tag = post.find('a', class_='feed-post-link')
            imagem_tag = post.find('img')
            
            if link_tag and imagem_tag:
                titulo = link_tag.text.strip()
                link = link_tag.get('href')
                imagem_url = imagem_tag.get('src')
                
                # Garante que todos os dados foram coletados antes de adicionar à lista
                if titulo and link and imagem_url:
                    noticias_coletadas.append({
                        'titulo': titulo, 
                        'link': link, 
                        'imagem': imagem_url
                    })
                    
        print(f"Coletadas {len(noticias_coletadas)} notícias com imagem do G1.")
        
    except requests.exceptions.RequestException as e:
        # Captura erros de rede de forma específica (timeout, conexão, etc.)
        print(f"Erro de rede ao coletar notícias do G1: {e}")
        
    # Retorna as 5 primeiras notícias encontradas
    return noticias_coletadas[:5]


# --- FUNÇÃO DE ENVIO DE E-MAIL SIMPLIFICADA ---

def enviar_email(lista_de_noticias):
    """Envia um e-mail formatado com as notícias de uma única fonte."""
    EMAIL_REMETENTE = "henrydarre.hdm@gmail.com"

    # MUDANÇA 2: A senha agora é lida de forma segura do ambiente
    SENHA_APP = os.getenv('GMAIL_APP_PASSWORD')
    
    EMAIL_DESTINATARIO = "henrydarre.hdm@gmail.com"

    # MUDANÇA 3: Uma verificação de segurança importante
    if not SENHA_APP:
        print("ERRO CRÍTICO: Senha de app não encontrada. Verifique os Secrets no GitHub.")
        return # Para a execução se a senha não for encontrada
    
    # Assunto e título específicos para o G1
    assunto = f"📸 Suas Notícias de Hoje do G1"
    titulo_email = f"📸 Atualizações diárias ({time.strftime('%d/%m/%Y')})"

    # O HTML agora não precisa do loop extra para múltiplas fontes
    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f6f6f6; }}
          .container {{ width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; }}
          h1 {{ color: #C4170C; }} /* Cor do G1 */
          .noticia-link {{ color: #0056b3; text-decoration: none; font-size: 18px; font-weight: bold; }}
          .noticia-link:hover {{ text-decoration: underline; }}
          .noticia-tabela {{ width: 100%; border-spacing: 0; margin-bottom: 20px; border-top: 1px solid #eee; padding-top: 20px; }}
          .imagem-td {{ padding-right: 15px; }}
          .imagem-noticia {{ width: 150px; height: auto; display: block; border-radius: 5px; }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>{titulo_email}</h1>
    """

    for noticia in lista_de_noticias:
        html_content += f"""
        <table class="noticia-tabela">
          <tr>
            <td class="imagem-td" width="150" valign="top">
              <a href="{noticia['link']}"><img src="{noticia['imagem']}" alt="Imagem da notícia" class="imagem-noticia"></a>
            </td>
            <td valign="top">
              <a href="{noticia['link']}" class="noticia-link">{noticia['titulo']}</a>
            </td>
          </tr>
        </table>
        """

    html_content += "</div></body></html>"
    
    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_APP)
            smtp.send_message(msg)
        print(f"E-mail VISUAL com notícias do G1 enviado com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o e-mail: {e}")

# --- BLOCO PRINCIPAL (ORQUESTRADOR) SIMPLIFICADO ---
if __name__ == '__main__':
    # 1. Coleta as notícias do G1
    noticias_g1 = coletar_noticias_g1()
    
    # 2. Se alguma notícia foi coletada, envia o e-mail
    if noticias_g1:
        enviar_email(noticias_g1)
    else:
        print("Nenhuma notícia foi encontrada no G1 para enviar.")
