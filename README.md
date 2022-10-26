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

![alt text](https://github.com/AugustMatt/DetectorAssinaturas/blob/master/documentos/base/1.jpg)

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

![alt text](https://github.com/AugustMatt/DetectorAssinaturas/blob/master/exemplo_prescricao.bmp)

Evolução : 
<ul>
  <li>268 pixels de largura</li>
  <li>85 pixels de altura</li>
  <li>Rubrica posicionada na parte esquerda sem tocar as bordas</li>
  <li>Carimbo posicionado ao lado direito da Rubrica</li>
  <li>Tentar deixar o Carimbo o mais centralizado possivel no espaço restante ao mesmo</li>
</ul>

Imagem de exemplo:

![alt text](https://github.com/AugustMatt/DetectorAssinaturas/blob/master/exemplo_evolucao.bmp)


  
