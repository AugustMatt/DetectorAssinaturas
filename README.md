# 🤖 Aplicativo para automatizar o de processamento de assinaturas digitais para aplicativo hospitalar.

## Ferramentas utilizadas:
### Python 3.11 🐍 com as seguintes bibliotecas 📚:
<ul>
  <li> OpenCV para processamento digital de imagens 📷</li>
  <li> Numpy para manipulação de arrays 🖥️</li>
  <li> screeninfo para aquisição de informações do monitor 🖥️ </li>
  <li> tkinter para criação da interface 🔧 </li>
  <li> Pillow para manipulação de imagens 📷 </li>
</ul>
  
### Problemática:

Assinaturas médicas digitais são um dos muitos recursos desenvolvidos com o avanço dos sistemas digitais nas ultimas decadas. Tal recurso permite que médicos possam prescrever e evoluir medicamentos sem a necessidade de assinar presencialmente alguns documentos requisitados, agilizando o processo de atendimento aos clientes e possivelmente sendo um diferencial no bem estar dos mesmos.

Geralmente, o cadastro das assinaturas digitais de prescrição e evolução médica ocorrem por meio de um aplicativo utilizado pela empresa da area da saude. Em um determinado aplicativo, em determinada empresa, o fluxo de cadastro das assisnaturas segue da seguinte maneira:
<ul>
  <li>1. Os colaboradores, que necessitam desse recurso, disponibilizam seu carimbo e rubrica em uma folha de formulario pre-determinada</li>
  <li>2. O colaborador, responsavel pelo cadastro, utiliza ferramentas de scanner e edição de imagens para ajustar o carimbo e a rubrica de maneira pre-determinada para o aplicativo.</li>
  <li>3. Apos todos os ajustes necessarios serem feitos, os arquivos gerados são adicionados ao sistema pelo aplicativo.</li>
</ul>

Contudo, esse processo é bastante repetitivo, pois alem do formato dos arquivos gerados terem padrões a SEMPRE serem utilizados, muitas vezes o colaborador responsavel por esse cadastro está em outra atividade no momento e ocorre um acumulo gigantesco de assinaturas para serem cadastradas, podendo levar horas ou até dias de trabalho repetitivo para serem finalizados.

O presente aplicativo propoe uma solução para otimizar esse fluxo, utilizando tecnicas de processamento digital de imagens para realizar a edição das imagens e a geração dos documentos para o usuario 😃

### Detalhes da problemática:

O documento de coleta das informações dos médicos segue o padrão (rubricas de teste geradas pelo autor):

<div align="center">
  <img src="https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/base/1.jpg" width=50% height=50%>
</div>

Os arquivos a serem gerados devem ter formato .bmp de 64 bits e as seguintes medidas:

Prescrição : 
<ul>
  <li>344 pixels de largura</li>
  <li>143 pixels de altura</li> 
  <li>Rubrica posicionada na parte superior direita sem tocar as bordas</li>
  <li>Carimbo posicionado logo abaixo da Rubrica</li>
  <li>Tentar deixar o conjunto (Carimbo + Rubrica) o mais centralizado nesse espaço possivel</li>
</ul>

Imagem de exemplo:

![alt text](https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/imagens_exemplo/exemplo_prescricao.bmp)

Evolução : 
<ul>
  <li>268 pixels de largura</li>
  <li>85 pixels de altura</li>
  <li>Rubrica posicionada na parte esquerda sem tocar as bordas</li>
  <li>Carimbo posicionado ao lado direito da Rubrica</li>
  <li>Tentar deixar o Carimbo o mais centralizado possivel no espaço restante ao mesmo</li>
</ul>

Imagem de exemplo:

![alt text](https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/imagens_exemplo/exemplo_evolucao.bmp)

### Limitações atuais:

1. O carimbo, na grande maioria dos casos, acaba sendo coletado com algum problema de continuidade ou quando não é o caso, possui fontes textuais muito especificas oque torna algoritmos de detecção de text (OCR) inviaveis de serem utilizados. Na pratica oque acaba ocorrendo é a digitalização do carumbo seguindo certas regras de tipo e tamanho de fonte, para deixar o carimbo digital o mais parecido possivel com o original. Dito isso, no presente momento, o algoritmo so se preocupará com o processamento da rubrica.

### O codigo:

Inicialmente temos as importações das bibliotecas necessarias:
```python
from math import floor                  # Método para calcular o "chão" de um numero (inteiro arrendondado para baixo)
import cv2                              # Opencv para PDI
import numpy as np                      # Numpy para manipulação de arrays
import tkinter                          # tkinter para criação de interface grafica
from screeninfo import get_monitors     # Método para adquirir informações sobre o monitor o qual o algoritmo esta executando
from tkinter import filedialog          # Método para permitir a inserção de arquivos pelo usuario
from PIL import Image, ImageTk          # Pillow para PDI
```

Na função principal do algoritmo, executamos a função App():
```python
if __name__ == "__main__":
    App()
```

Na função App(), inicialmente criamos algumas definições para a janela do aplicativo:
```python
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
```

Logo em seguida, carregamos a imagem inserida pelo usuario em escala de cinza e partimos para a função detect_squares() para encontrar contornos retangulares da imagem:
```python
 # Carrega a imagem em escala de cinza
 img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
 
 # Encontra os contornos de retangulos na imagem
 squares = detect_squares(img)
```

Em detect_squares(), inicialmente aplicamos um filtro de borramento na imagem para suavização. Alem disso criamos um array "squares" que armazenará possiveis contornos
retangulares que tentaremos encontrar em breve:
```python
# Retorna os contornos retangulares de uma imagem
def detect_squares(img):

    # Aplica filtro de borramento gaussiano para suavizar a imagem
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # Array que ira armazenar os contornos dos possiveis retangulos das assinaturas
    squares = []
```

Em seguida, pegamos nossa imagem e vamos aplicar o algoritmo de canny para tentar detectar as bordas da imagem, como tambem o algoritmo de threshold binario, utilizando
varios niveis de corte:
```python
# Para toda a matriz de pixels da imagem
    for gray in cv2.split(img):

        # Loop de 10 iterações
        for thrs in range(0, 255, 26):

            # Na primeira iteração, destaca as bordas da imagem com o algoritmo de Canny
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=3)

            # Nas demais iterações, utiliza o threshold binário para destacar as bordas
            # Note que o valor de threshold é incrementado de 26 em 26
            # Para valores de thrs acima de 200, as bordas via threshold são bem distinguiveis
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
```

Um exemplo das bordas detectadas via Canny:
<div align="center">
  <img src="https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/imagens_exemplo/exemplo_canny.PNG" width=50% height=50%>
</div>

Exemplo das bordas utilizando threshold com limiares respectivamente 26, 104 e 208:
<div align="center">
  <img src="https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/imagens_exemplo/exemplo_threshold26.PNG" width=50% height=50%>
  <img src="https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/imagens_exemplo/exemplo_threshold104.PNG" width=50% height=50%>
  <img src="https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/imagens_exemplo/exemplo_threshold208.PNG" width=50% height=50%>
</div>

Em seguida extraimos os contornos da imagem. Contudo precisamos selecionar apenas os contornos retangulares. 
Para isso, inicialmente iremos iterar os contornos obtidos e aproxima-los a um poligono fechado de grau menor que a quantidade de vertices dos contornos obtidos :
```python
# Extrai os contornos da imagem
contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# Para cada contorno encontrado
for cnt in contours:

    # Calcula o perimetro do contorno, supondo que é um contorno fechado
    cnt_len = cv2.arcLength(cnt, True)

    # Aproxima o contorno a um poligono fechado com numero de vertices menor que o contorno original
    # O objetivo é aproximar contornos a retangulos
    cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
```

Se esse poligono aproximado possuir 4 vertices, é um quadrilateró. Alem disso podemos utilizar outras metricas para ter melhor precisão de que aquele contorno é de fato
um retangulo. Nesse caso, usarei inicialmente a area desse poligono e se o mesmo é convexo:
```python
if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
```

Uma outra métrica interressante é o angulo entre suas arestas. Em um retangulo ideal, as arestas adjacentes tem um angulo de 90 graus. Vamos então calcular atraves do produto escalar o cosseno do angulo entre todas as arestas adjacentes desse poligono. Se todas elas forem suficientemente pequenas, serão bem proximas de 90 graus, logo
considerarei aquele poligono um retangulo:
```python
# Vamos verificar se o contorno é um retangulo ou algo muito proximo atraves do angulo entre os lados

# Reajusta o array de pontos do contorno 
cnt = cnt.reshape(-1, 2)

# Acha o maior angulo entre os vetores que ligam os pontos do contorno
max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in range(4)])

# Se o angulo for menor que 0.1, consideremos que o contorno é um retangulo
if max_cos < 0.1:
```

A função angle_cos() utilizada:
```python
# Retorna o angulo entre dois vetores que compartilham um mesmo ponto
def angle_cos(p0, p1, p2):

    # Cosseno do angulo entre os vetores
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')

    # Normalização
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))
```

Por fim, usaremos agora algumas metricas para tentar ignorar alguns contornos que possam aparecer mas que não são os contornos que envolvem as rubricas:
```python
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
```

Apos o armazenamento dos contornos, retorna o array que os contem:
```python
return squares
```




  
