from math import floor
import cv2
import numpy as np
import tkinter
from screeninfo import get_monitors
from tkinter import filedialog
from PIL import Image, ImageTk

# Limpa bordas da imagem
def ClearBorder(img):
    vertical_value = 15
    horizontal_value = 15
    img_copy = img
    for y in range(0, img_copy.shape[1]):
        for x in range(0, img_copy.shape[0]):
            if(y < horizontal_value or y > img_copy.shape[1] - horizontal_value):
                img_copy[x][y] = 255
            elif(x < vertical_value or x > img_copy.shape[0] - vertical_value):
                img_copy[x][y] = 255

    return img_copy

# Inverte imagem
def InvertImage(img):
    img_copy = img
    for y in range(0, img_copy.shape[1]):
        for x in range(0, img_copy.shape[0]):
            img_copy[x][y] = 255 - img_copy[x][y]

    return img_copy

# Remove conjuntos de pixels conectados com min_pixels_quant ou menos
def RemoveConectedComponentes(img, min_pixels_quant):

    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        img, connectivity=8)
    sizes = stats[1:, -1]
    nb_components = nb_components - 1
    min_size = min_pixels_quant
    img_processada2 = np.zeros((output.shape))
    for i in range(0, nb_components):
        if sizes[i] >= min_size:
            img_processada2[output == i + 1] = 255

    return img_processada2

# Fatia a imagem para remover os espaços em branco
def GetBoundRectangle(img):
    black_pixels = []
    for y in range(0, img.shape[0]):
        for x in range(0, img.shape[1]):
            if(img[y][x] == 0):
                black_pixels.append((y, x))

    try:
        min_x = min(black_pixels, key=lambda x: x[1])[1]
        min_y = min(black_pixels, key=lambda x: x[0])[0]
        max_x = max(black_pixels, key=lambda x: x[1])[1]
        max_y = max(black_pixels, key=lambda x: x[0])[0]
        cropped = img[min_y-2:max_y+2, min_x-2:max_x+2]
        return cropped
    except:
        return False

# Redimensiona a imagem para o tamanho necessario no aplicativo
def Resize(img):

    # Inicialmente, a imagem está em 100% do seu tamanho
    scale_percent = 100
    resized = img

    # Enquanto a escala de tamanho da largura for maior que 85% ou a escala de tamanho da altura for maior que 89%
    while resized.shape[0] > 85 or resized.shape[1] > 89:

        # Reduz a escala de tamanho da imagem em 1%
        scale_percent += -1
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    return resized

# Cria o arquivo da evolução
def CreateEvolution(img):
    img_background = np.zeros((85, 268))
    img_background = InvertImage(img_background)
    y_offset = floor((85 - img.shape[0])/2)
    x_offset = 2
    img_background[y_offset:y_offset+img.shape[0],
                   x_offset:x_offset+img.shape[1]] = img
    return img_background

# Cria o arquivo da prescrição
def CreatePrescription(img):

    img_background = np.zeros((143, 344))
    img_background = InvertImage(img_background)

    middle_x = floor(img_background.shape[1]/2)
    x_offset = middle_x + floor( ( (img_background.shape[1]/2) - img.shape[1] ) / 2 )

    y_offset = 0

    img_background[y_offset:y_offset + img.shape[0], x_offset:x_offset + img.shape[1]] = img
    return img_background

# Retorna o angulo entre dois vetores que compartilham um mesmo ponto
def angle_cos(p0, p1, p2):

    # cosinus of angle between vectors
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')

    # normalize
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))

# Verifica se um contorno ja está no array de contornos
def VerifyBorder(squares, cnt):
    
    margin = 10

    # Bordas do contorno
    max_x = max(cnt[0][0], cnt[2][0])
    min_x = min(cnt[0][0], cnt[2][0])
    max_y = max(cnt[0][1], cnt[2][1])
    min_y = min(cnt[0][1], cnt[2][1])

    # verifica se o contorno atual e seus deslocamentos batem com algum contorno dentro de squares
    verify = False
    for square in squares:
        if(
            min_x - margin < max(square[0][0], square[2][0]) 
        and max_x + margin > min(square[0][0], square[2][0]) 
        and min_y - margin < max(square[0][1], square[2][1]) 
        and max_y + margin > min(square[0][1], square[2][1])):
        
            verify = True
            break
        
    return verify

# Retorna os contornos retangulares de uma imagem
def detect_squares(img):

    # Aplica filtro de borramento gaussiano para suavizar a imagem
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # Array que ira armazenar os contornos dos possiveis retangulos das assinaturas
    squares = []
   
    # Para toda a matriz de pixels da imagem
    for gray in cv2.split(img):

        # Loop de 10 iterações
        for thrs in range(0, 255, 26):

            # Na primeira iteração, destaca as bordas da imagem com o algoritmo de canny
            if thrs == 0:

                bin = cv2.Canny(gray, 0, 50, apertureSize=3)
                #cv2.imshow('bin canny', bin)

            # Nas demais iterações, utiliza o threshold binário para destacar as bordas
            # Note que o valor de threshold é incrementado de 26 em 26
            # Para valores de thrs acima de 200, as bordas via threshold são bem distinguiveis
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
                #cv2.imshow('bin threshold limit ' + str(thrs), bin)
           

            # Extrai os contornos da imagem
            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            #print("iteração: ", thrs, " contornos: ", len(contours))
            
            # Para cada contorno encontrado
            for cnt in contours:

                # Calcula o perimetro do contorno, supondo que é um contorno fechado
                cnt_len = cv2.arcLength(cnt, True)

                # Aproxima o contorno a um poligono fechado com numero de vertices menor que o contorno original
                # O objetivo é aproximar contornos a retangulos
                cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)

                # Se o contorno possui 4 vertices, é um poligono de 4 lados
                # e se o contorno possui area maior que 1000 pixels
                # e se o contorno é é convexo, ou seja se é uma forma "arredondada" para fora
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):

                    # Vamos verificar se o contorno é um retangulo ou algo muito proximo atraves do angulo entre os lados

                    # Reajusta o array de pontos do contorno 
                    cnt = cnt.reshape(-1, 2)
                    
                    # Acha o maior angulo entre os vetores que ligam os pontos do contorno
                    max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in range(4)])

                    # Se o angulo for menor que 0.1, consideremos que o contorno é um retangulo
                    if max_cos < 0.1:
                        
                        # Se o retangulo tiver largura menor que 5% da largura da imagem completa, é um retangulo pequeno demais para ser da assinatura
                        # Ou se o retangulo tiver largura maior que o 50% da largura da imagem completa, é um quadrado muito grande para ser da assinatura
                        # Em ambos os casos, descartamos o retangulo
                        if(cnt[1][1] - cnt[0][1] < 0.05*img.shape[1] or cnt[1][1] - cnt[0][1]  > 0.5*img.shape[1]):
                            continue

                        # Se o retangulo estiver na esquerda da imagem, descartamos o retangulo
                        # Pois a assinatura deve estar na direita da imagem
                        # Talvez seja uma boa ideia adicionar uma margem de erro para casos em que a assinatura esteja um pouco deslocada
                        minimal = min(cnt[0][0], cnt[2][0])
                        if(minimal < (img.shape[1]/2)):
                            continue

                        # Verifica se o contorno atual ja está no array de contornos evitando assim contornos duplicados
                        if(VerifyBorder(squares, cnt)):
                            continue

                        # Armazena o contorno do retangulo
                        squares.append(cnt)
    return squares

# Evento de clique no campo de texto
def EntryOnClick(event):
    entry = event.widget
    print(str(entry))
    if entry.get()=="Digite o nome da assinatura":
        entry.delete(0, tkinter.END)
        entry.insert(0, "")

# Pega todos os textos em todos os campos de texto na aplicação
def GetEntries(janela):
    entries = []
    for entry in janela.winfo_children():    
        if isinstance(entry, tkinter.Entry):
            if(entry.get() =="Digite o nome da assinatura" or entry.get()==""):
                continue
            entries.append(entry)
        
    return entries

# Salva as assinaturas em um caminho escolhido pelo usuario
def SaveSignatures(janela, signatures):

    save_path = filedialog.askdirectory(title="Salvar assinaturas")

    entries = GetEntries(janela)
    
    for entry in entries:
        signature_id = int(str(entry).replace('.', ''))
        
        evolution = CreateEvolution(signatures[signature_id])
        prescription = CreatePrescription(signatures[signature_id])

        signature_name = str(entry.get()).upper()
        cv2.imwrite(f"{save_path}\\assina {signature_name} evolucao.bmp", evolution)
        cv2.imwrite(f"{save_path}\\assina {signature_name} prescricao.bmp", prescription)
    
    janela.destroy()

def App():

    # Cria uma janela para a aplicação
    janela = tkinter.Tk()

    # Titulo da janela
    janela.title("Assinatura Digital")

    # Pega a resolução da tela primária, onde a aplicação é executada
    for m in get_monitors():
        if(m.is_primary):
            primary_monitor = m
            break
    
    # Define a resolução da janela da aplicação
    app_width = 800
    app_height = 600
    
    # Calcula a posição da janela para que ela fique centralizada na tela
    positionRight = int(primary_monitor.width/2 - app_width/2)
    positionDown = int(primary_monitor.height/2 - app_height/2)
    
    # Posiciona a janela na tela
    janela.geometry(f"{app_width}x{app_height}+{positionRight}+{positionDown}")

    # Cor de fundo da janela
    janela['bg'] = '#7A7473' 
    
    # Ao abrir a janela, pede para o usuario selecionar um arquivo para ser processado
    janela.update()
    image_path = janela.filename = filedialog.askopenfilename(title = "Selecionar Arquivo de Assinaturas", filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    
    # Carrega a imagem em escala de cinza
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Encontra os contornos de retangulos na imagem
    squares = detect_squares(img)

    # Array para armazenar as imagens das assinaturas recortadas e processadas
    signatures = []

    # Array para armazenar as imagens processadas no formato legivel pela biblioteca TKinter
    signatures_pil = []

    # Array para armazenar os campos de texto das assinaturas
    signatures_entrys = []

    # Iterador para inserção de dados em arrays
    i = 0

    # Para cada retangulo encontrado
    for square in squares:

        # Encontra as coordenadas do retangulo na imagem e extrai
        x, y, w, h = cv2.boundingRect(square)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi = img[y:y + h, x:x + w]

        # Limpa possiveis bordas pretas do recorte
        cleaned_crop = ClearBorder(roi)

        # Processos para tentar remover possiveis ruidos do recorte
        # Isso pode danificar a assinatura
        eroded_crop = cv2.erode(cleaned_crop, np.ones((3, 3), np.uint8), iterations=1)    
        ret, bin_eroded_crop = cv2.threshold(eroded_crop, 200, 255, cv2.THRESH_BINARY)

        inverted_crop = cv2.bitwise_not(bin_eroded_crop)
        processed_crop = RemoveConectedComponentes(inverted_crop, 100)
        processed_crop = InvertImage(processed_crop)

        # Adquire o exato recorte da assinatura removendo o fundo branco
        processed_crop = GetBoundRectangle(processed_crop) 

        # Caso a imagem tenha completamente deteriorada devido o processamento, descarta a assinatura
        if(isinstance(processed_crop, bool)):
            continue

        # Redimensiona a assinatura para um tamanho padrao
        resized_crop = Resize(processed_crop)

        # Adiciona a assinatura no array de assinaturas
        signatures.append(resized_crop)

        # Converte a assinatura para o formato PIL para ser exibida na tela do aplicativo
        signatures_pil.append(ImageTk.PhotoImage(image=Image.fromarray(resized_crop)))

        # Cria um entrada de texto para aquela imagem
        signatures_entrys.append(tkinter.Entry(janela, width=50, name=str(i)))

        i+=1
        
    # Cria os campos de texto do aplicativo
    for i in range(0, len(signatures_pil)):
        tkinter.Label(janela, image=signatures_pil[i]).pack(expand=True)
        signatures_entrys[i].insert(0, "Digite o nome da assinatura. Mantenha em branco para não utilizar a assinatura")
        signatures_entrys[i].pack(expand=True)
        signatures_entrys[i].bind("<Button-1>", EntryOnClick)
    
    # Cria o botão de salvar assinaturas
    tkinter.Button(janela, text="Salvar", width=42, command=lambda: SaveSignatures(janela, signatures)).pack(side=tkinter.BOTTOM, pady=5)
    
    # Inicia a aplicação
    janela.mainloop()

if __name__ == "__main__":
    App()
