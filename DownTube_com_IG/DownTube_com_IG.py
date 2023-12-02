# Autor: Jésse Aguiar
# Diamantina-MG, 10/11/2023
# jesseaguiar@hotmail.com.br
# +5538999332971

from tkinter import messagebox, Tk, Label, Entry, Button
from tkinter.filedialog import askdirectory
import pytube, os, sys
from webbrowser import open as op
from pyperclip import paste

def downMP4(): #Baixa o vídeo do link em formato MP4
    url = website_entry.get()
    if len(url) == 0:
        messagebox.showinfo(
            title="Erro!",
            message="Por favor insira uma URL do YouTube válida")
    else:
        try:
            yt = pytube.YouTube(url)
            ys = yt.streams.filter(file_extension="mp4").first().download(ler_arquivo_down())
            limpar_campo()
            
        except pytube.exceptions.RegexMatchError:
            messagebox.showinfo(title="Erro!", message=('Não há vídeo correspondente ao link informado: {}'.format(url)))

        except pytube.exceptions.ExtractError:
            messagebox.showinfo(title="Erro!", message=('Ocorreu um erro durante o download do vídeo: {}'.format(url)))

        except pytube.exceptions.VideoUnavailable:
            messagebox.showinfo(title="Erro!", message=('O link informado não está disponível: {}'.format(url)))

def downMP3(): #Baixa o vídeo do link inserido pelo usuário e converte em MP3
    yt = pytube.YouTube(str(website_entry.get()))
    video = yt.streams.filter(only_audio=True).first()
    destination = (ler_arquivo_down()) or '.'
    out_file = video.download(output_path=destination)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    limpar_campo()

def limpar_campo(): #Limpa o campo de entrada de texto que recebe o link copiado
        try:
            website_entry.delete(0, 'end')
            website_entry.insert(0, '')
        except:
            messagebox.showinfo(
            title="Deu ruim!",
            message="Apague manualmente")

def abrir_pasta(): #Abre o explorador de arquivos na pasta de downloads da músicas
    try:
        op(os.path.realpath(ler_arquivo_down()))
    except:
         messagebox.showinfo(
            title="Vish!",
            message="Não consegui abrir a pasta :-(")

def direito(event): #Cola o link copiado ao clicar com o botão direito do mouse
    try:
        website_entry.delete(0, 'end')
        website_entry.insert(0, paste())
    except:
        messagebox.showinfo(
            title="Deu ruim de novo!",
            message="Tenta de novo perdedor")

def ler_arquivo_down():
    with open('path_down_directory.txt', 'r') as arquivo:
        path_download = ''
        path_download = arquivo.read()
        arquivo.close()
        return path_download

def select_path_down():
    path_download = askdirectory()
    arquivo = open('path_down_directory.txt', 'w')
    arquivo.write(path_download)
    arquivo.close()
    ler_arquivo_down()

if __name__ == '__main__':
    
    try:
        path_download = ler_arquivo_down()  
    except:
        messagebox.showinfo(
            title="Importante!",
            message="Selecione a pasta na qual deseja salvar seus arquivos baixados")
        select_path_down()

    window = Tk()
    window.geometry('700x100')
    window.title("DownTube by Jesse Aguiar")
    window.iconbitmap(r'icone.ico')
    window.config(padx=25, pady=20)

    # Entradas
    website_entry = Entry(width=100)
    website_entry.grid(row=0, column=1, columnspan=6)
    website_entry.focus()
    website_label = Label(text = 'Link: ')
    website_label.grid(row=0, column=0)

    #Colar link ao clicar com o botão direito
    window.bind("<Button-3>", direito)

    #lista de midias baixadas
    lista = list()

    # Botões
    button_downloadMP4 = Button(text="Baixar vídeo", width=12, command=downMP4)
    button_downloadMP4.grid(row=2, column=1, padx=10, pady=10)

    button_downloadMP3 = Button(text="Baixar áudio", width=12, command=downMP3)
    button_downloadMP3.grid(row=2, column=2, padx=10, pady=10)

    button_clear = Button(text="Limpar", width=12, command=limpar_campo)
    button_clear.grid(row=2, column=3, padx=10, pady=10)

    button_open_folder = Button(text="Abrir pasta", width=12, command=abrir_pasta)
    button_open_folder.grid(row=2, column=4, padx=10, pady=10)

    button_open_folder = Button(text="Selecionar pasta", width=12, command=select_path_down)
    button_open_folder.grid(row=2, column=5, padx=10, pady=10)

    window.mainloop()