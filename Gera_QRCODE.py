
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Lista completa de instrumentos da Finetornos
dados_brutos = """
7-05-00007-N11
7-05-00008-N06
7-05-00004-N06
"""

LOGO_PATH = "LOGO.jpg"
OUTPUT_DIR = "qrcodes_finetornos"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def gerar_qr_com_id_embaixo(id_codigo, nome_instrumento):
    # 1. Gerar o QR Code básico (em preto)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(id_codigo)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    qr_w, qr_h = img_qr.size

    # 2. Inserir a Logo Colorida no meio
    try:
        logo = Image.open(LOGO_PATH)
        logo_size = qr_w // 5
        logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
        pos_x = (qr_w - logo.size[0]) // 2
        pos_y = (qr_h - logo.size[1]) // 2
        img_qr.paste(logo, (pos_x, pos_y))
    except:
        pass

    # 3. Criar imagem maior para o texto do CÓDIGO apenas
    espaco_texto = 50  
    img_final = Image.new('RGB', (qr_w, qr_h + espaco_texto), color='white')
    img_final.paste(img_qr, (0, 0))

    # 4. Escrever o CÓDIGO (ID) embaixo
    draw = ImageDraw.Draw(img_final)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24) # Fonte um pouco maior para o ID
    except:
        font = ImageFont.load_default()

    # Centralizar apenas o ID
    bbox = draw.textbbox((0, 0), id_codigo, font=font)
    tw = bbox[2] - bbox[0]
    tx = (qr_w - tw) / 2
    ty = qr_h + (espaco_texto - (bbox[3] - bbox[1])) / 2 - 10

    draw.text((tx, ty), id_codigo, fill="black", font=font)

    # 5. Salvar o arquivo (Mantemos o nome completo no arquivo para você organizar)
    nome_arquivo = f"{id_codigo}_{nome_instrumento}"
    for char in ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", "Ø"]:
        nome_arquivo = nome_arquivo.replace(char, "_")
    
    img_final.save(os.path.join(OUTPUT_DIR, f"{nome_arquivo}.png"))
    print(f"Sucesso: {id_codigo}")

# Execução
linhas = [l.strip() for l in dados_brutos.strip().split('\n') if l.strip()]
for linha in linhas:
    if len(linha) >= 14:
        id_part = linha[:14]
        name_part = linha[14:]
        gerar_qr_com_id_embaixo(id_part, name_part)

print(f"\nFinalizado! {len(linhas)} QRs com IDs gerados em '{OUTPUT_DIR}'.")