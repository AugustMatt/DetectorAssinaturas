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

def Resize(img):

    scale_percent = 100  # percent of original size
    resized = img

    while resized.shape[0] > 85 or resized.shape[1] > 89:
        scale_percent += -1
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    return resized

def CreateEvolution(img):
    img_background = np.zeros((85, 268))
    img_background = InvertImage(img_background)
    y_offset = floor((85 - img.shape[0])/2)
    x_offset = 2
    img_background[y_offset:y_offset+img.shape[0],
                   x_offset:x_offset+img.shape[1]] = img
    return img_background

def CreatePrescription(img):

    img_background = np.zeros((143, 344))
    img_background = InvertImage(img_background)

    middle_x = floor(img_background.shape[1]/2)
    x_offset = middle_x + floor( ( (img_background.shape[1]/2) - img.shape[1] ) / 2 )

    y_offset = 0

    img_background[y_offset:y_offset + img.shape[0], x_offset:x_offset + img.shape[1]] = img
    return img_background

def Run(img_path):

    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    start = [555, 1310]
    altura = 335
    largura = 1010
    x = start[1]
    signatures = []

    for i in range(0, 5):

        incremento_y = 505*i
        y = start[0] + incremento_y
        crop_img = image[y: y + altura, x: x + largura]

        cleaned_crop = ClearBorder(crop_img)
        eroded_crop = cv2.erode(cleaned_crop, np.ones((3, 3), np.uint8), iterations=1)
        ret, bin_eroded_crop = cv2.threshold(eroded_crop, 200, 255, cv2.THRESH_BINARY)
        inverted_crop = cv2.bitwise_not(bin_eroded_crop)
        processed_crop = RemoveConectedComponentes(inverted_crop, 100)
        processed_crop = InvertImage(processed_crop)
        processed_crop = GetBoundRectangle(processed_crop)
        if processed_crop!=False:
            resized_crop = Resize(processed_crop)
            signatures.append(resized_crop)

    return signatures

def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))

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

def detect_squares(img, use_dilate=True):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    margin_middle = 150
    for gray in cv2.split(img):
        for thrs in range(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=3)
                if(use_dilate):
                    bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in range(4)])
                    if max_cos < 0.1:
                        
                        if(cnt[1][1] - cnt[0][1] < 200 or cnt[1][1] - cnt[0][1]  > img.shape[1] - 200):
                            continue

                        minimal = min(cnt[0][0], cnt[2][0])

                        if(minimal < (img.shape[1]/2) - margin_middle):
                            continue

                        if(VerifyBorder(squares, cnt)):
                            continue

                        squares.append(cnt)
    return squares

def EntryOnClick(event):
    entry = event.widget
    print(str(entry))
    if entry.get()=="Digite o nome da assinatura":
        entry.delete(0, tkinter.END)
        entry.insert(0, "")

# get all entries elements
def GetEntries(janela):
    entries = []
    for entry in janela.winfo_children():    
        if isinstance(entry, tkinter.Entry):
            if(entry.get() =="Digite o nome da assinatura" or entry.get()==""):
                continue
            entries.append(entry)
        
    return entries

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
    janela = tkinter.Tk()
    janela.title("Assinatura Digital")

    for m in get_monitors():
        if(m.is_primary):
            primary_monitor = m
            break
    
    app_width = 800
    app_height = 600
    
    # Gets both half the screen width/height and window width/height
    positionRight = int(primary_monitor.width/2 - app_width/2)
    positionDown = int(primary_monitor.height/2 - app_height/2)
    
    # Positions the window in the center of the page.
    janela.geometry(f"{app_width}x{app_height}+{positionRight}+{positionDown}")
    janela['bg'] = '#7A7473' 
    
    # Path temporário
    initial_dir = r"\\localhost\scanner"
    janela.update()
    image_path = janela.filename = filedialog.askopenfilename(title = "Select file", filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    
    signatures = Run(image_path)
    signatures_pil = []
    signatures_entrys = []

    i = 0
    for signature in signatures:
        signatures_pil.append(ImageTk.PhotoImage(image=Image.fromarray(signature)))
        signatures_entrys.append(tkinter.Entry(janela, width=50, name=str(i)))
        i+=1

    for i in range(0, len(signatures_pil)):
        tkinter.Label(janela, image=signatures_pil[i]).pack(expand=True)
        signatures_entrys[i].insert(0, "Digite o nome da assinatura")
        signatures_entrys[i].pack(expand=True)
        signatures_entrys[i].bind("<Button-1>", EntryOnClick)
    
    tkinter.Button(janela, text="Salvar", width=42, command=lambda: SaveSignatures(janela, signatures)).pack(side=tkinter.BOTTOM, pady=5)
    
    janela.mainloop()

def App_v2():

    janela = tkinter.Tk()
    janela.title("Assinatura Digital")

    for m in get_monitors():
        if(m.is_primary):
            primary_monitor = m
            break
    
    app_width = 800
    app_height = 600
    
    # Gets both half the screen width/height and window width/height
    positionRight = int(primary_monitor.width/2 - app_width/2)
    positionDown = int(primary_monitor.height/2 - app_height/2)
    
    # Positions the window in the center of the page.
    janela.geometry(f"{app_width}x{app_height}+{positionRight}+{positionDown}")
    janela['bg'] = '#7A7473' 
    
    janela.update()
    image_path = janela.filename = filedialog.askopenfilename(title = "Selecionar Arquivo de Assinaturas", filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Encontra os contornos de quadrados na imagem
    squares = detect_squares(img)
    if(len(squares)!=5):
        new_squares = detect_squares(img, False)
        if(len(new_squares) > len(squares)) :
            squares = new_squares


    signatures = []
    signatures_pil = []
    signatures_entrys = []

    # Recortar contornos destacados na imagem
    i = 0
    for square in squares:
        x, y, w, h = cv2.boundingRect(square)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi = img[y:y + h, x:x + w]

        cleaned_crop = ClearBorder(roi)
        eroded_crop = cv2.erode(cleaned_crop, np.ones((3, 3), np.uint8), iterations=1)
        ret, bin_eroded_crop = cv2.threshold(eroded_crop, 200, 255, cv2.THRESH_BINARY)
        inverted_crop = cv2.bitwise_not(bin_eroded_crop)
        processed_crop = RemoveConectedComponentes(inverted_crop, 100)
        processed_crop = InvertImage(processed_crop)
        processed_crop = GetBoundRectangle(processed_crop) 


        if(isinstance(processed_crop, bool)):
            continue

        resized_crop = Resize(processed_crop)
        signatures.append(resized_crop)
        signatures_pil.append(ImageTk.PhotoImage(image=Image.fromarray(resized_crop)))
        signatures_entrys.append(tkinter.Entry(janela, width=50, name=str(i)))
        i+=1
        
    for i in range(0, len(signatures_pil)):
        tkinter.Label(janela, image=signatures_pil[i]).pack(expand=True)
        signatures_entrys[i].insert(0, "Digite o nome da assinatura")
        signatures_entrys[i].pack(expand=True)
        signatures_entrys[i].bind("<Button-1>", EntryOnClick)
    
    tkinter.Button(janela, text="Salvar", width=42, command=lambda: SaveSignatures(janela, signatures)).pack(side=tkinter.BOTTOM, pady=5)
    janela.mainloop()

if __name__ == "__main__":
    App_v2()
