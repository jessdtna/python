# Autor: Jésse Aguiar
# Diamantina-MG, 10/11/2023
# jesseaguiar@hotmail.com.br
# +5538999332971

from tkinter import Tk, Toplevel, Canvas, Scrollbar, Frame, Listbox, Checkbutton, IntVar, END, messagebox
from tkinter.ttk import Button, Label, Entry, Progressbar, Style
from tkinter.filedialog import askdirectory
from webbrowser import open as op
from pyperclip import paste
import pytubefix, os, threading

HISTORICO_ARQUIVO = 'historico.txt'
interromper = False

def salvar_historico(titulo, formato):
    try:
        with open(HISTORICO_ARQUIVO, 'a') as f:
            f.write(f"{titulo} ({formato})\n")
        carregar_historico()
    except:
        pass

def carregar_historico():
    historico_listbox.delete(0, END)
    try:
        with open(HISTORICO_ARQUIVO, 'r') as f:
            linhas = f.readlines()[-25:]
            for linha in linhas:
                historico_listbox.insert(END, linha.strip())
    except:
        pass

def downMP4():
    url = website_entry.get()
    if not url:
        messagebox.showinfo(title="Erro!", message="Por favor insira uma URL do YouTube válida")
        return
    try:
        yt = pytubefix.YouTube(url, on_progress_callback=atualizar_progresso)
        ys = yt.streams.get_highest_resolution()
        destination = ler_arquivo_down() or '.'
        ys.download(output_path=destination)
        salvar_historico(yt.title, "MP4")
        limpar_campo()
    except Exception as e:
        messagebox.showinfo(title="Erro!", message=str(e))

def downMP3():
    url = website_entry.get()
    if not url:
        messagebox.showinfo(title="Erro!", message="Por favor insira uma URL do YouTube válida")
        return
    try:
        yt = pytubefix.YouTube(url, on_progress_callback=atualizar_progresso)
        video = yt.streams.filter(only_audio=True).first()
        destination = ler_arquivo_down() or '.'
        out_file = video.download(output_path=destination)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        salvar_historico(yt.title, "MP3")
        limpar_campo()
    except Exception as e:
        messagebox.showinfo(title="Erro!", message=str(e))

def abrir_opcoes_playlist(url):
    if not url:
        messagebox.showinfo(title="Erro!", message="Por favor insira uma URL do YouTube válida")
    else:
        opcoes = Toplevel(window)
        opcoes.title("O que deseja fazer?")
        opcoes.geometry("400x200")

        Label(opcoes, text="O que você deseja fazer?", font=("Segoe UI", 10)).pack(pady=10)

        Button(opcoes, text="📥 Baixar todos os vídeos", command=lambda: iniciar_download_playlist(url, opcoes)).pack(pady=5)
        Button(opcoes, text="📝 Selecionar vídeos manualmente", command=lambda: [opcoes.destroy(), abrir_seletor_playlist(url)]).pack(pady=5)

def iniciar_download_playlist(url, janela_opcoes):
    global interromper
    interromper = False
    janela_opcoes.destroy()
    controle = Toplevel(window)
    controle.title("Baixando playlist")
    controle.geometry("300x100")

    Label(controle, text="Baixando vídeos da playlist...").pack(pady=10)
    Button(controle, text="🛑 Interromper", command=lambda: parar_download(controle)).pack()

    def baixar_tudo():
        global interromper
        try:
            pl = pytubefix.Playlist(url)
            destino = ler_arquivo_down() or '.'
            for video in pl.videos:
                if interromper:
                    break
                stream = video.streams.get_highest_resolution()
                stream.download(output_path=destino)
                salvar_historico(video.title, "MP4")
        except Exception as e:
            messagebox.showinfo(title="Erro!", message=str(e))
        controle.destroy()
        interromper = False

    threading.Thread(target=baixar_tudo, daemon=True).start()

def parar_download(controle):
    global interromper
    interromper = True
    controle.destroy()

def abrir_seletor_playlist(url):
    if not url:
        messagebox.showinfo(title="Erro!", message="Por favor insira uma URL do YouTube válida")
    try:
        seletor = Toplevel(window)
        seletor.title("Selecione os vídeos da playlist")
        seletor.geometry("600x500")

        canvas = Canvas(seletor)
        scrollbar = Scrollbar(seletor, orient="vertical", command=canvas.yview)
        scroll_frame = Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        status_label = Label(scroll_frame, text="🔄 Carregando vídeos da playlist...", font=("Segoe UI", 10))
        status_label.pack(pady=(10, 10))

        vars = []
    except:
        print("Except: deu ruim!")

    def carregar_videos():
        try:
            pl = pytubefix.Playlist(url)
            for video in pl.videos:
                var = IntVar()
                chk = Checkbutton(scroll_frame, text=video.title, variable=var, wraplength=550, anchor='w', justify='left')
                chk.pack(anchor='w', pady=2)
                vars.append((var, video))
            status_label.config(text="✅ Selecione os vídeos que deseja baixar:")

            def selecionar_todos():
                for var, _ in vars:
                    var.set(1)

            Button(scroll_frame, text="☑️ Selecionar todos", command=selecionar_todos).pack(pady=(5, 0))
            Button(scroll_frame, text="📥 Baixar selecionados", command=lambda: baixar_selecionados(vars, seletor)).pack(pady=10)

        except Exception as e:
            status_label.config(text=f"❌ Erro ao carregar playlist: {str(e)}")

    threading.Thread(target=carregar_videos, daemon=True).start()

def baixar_selecionados(vars, seletor):
    destino = ler_arquivo_down() or '.'
    for var, video in vars:
        if var.get():
            stream = video.streams.get_highest_resolution()
            stream.download(output_path=destino)
            salvar_historico(video.title, "MP4")
    seletor.destroy()

def limpar_campo():
    website_entry.delete(0, END)
    progress['value'] = 0

def abrir_pasta():
    try:
        op(os.path.realpath(ler_arquivo_down()))
    except:
        messagebox.showinfo(title="Erro!", message="Não consegui abrir a pasta")

def direito(event):
    try:
        website_entry.delete(0, END)
        url = paste()
        website_entry.insert(0, url)
        if "playlist" in url:
            abrir_opcoes_playlist(url)
    except:
        messagebox.showinfo(title="Erro!", message="Erro ao colar link")

def ler_arquivo_down():
    try:
        with open('path_down_directory.txt', 'r') as f:
            return f.read()
    except:
        return None

def select_path_down():
    path_download = askdirectory()
    with open('path_down_directory.txt', 'w') as f:
        f.write(path_download)

def atualizar_progresso(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    porcentagem = int((bytes_downloaded / total_size) * 100)
    progress['value'] = porcentagem
    window.update_idletasks()

# Janela principal
window = Tk()
window.title("DownTube by Jesse Aguiar")
window.geometry("900x370")
try:
    window.iconbitmap("icone.ico")
except:
    print("⚠️ Ícone não encontrado. Continuando sem ícone.")
window.bind("<Button-3>", direito)

style = Style()
style.theme_use('clam')
style.configure('TButton', font=('Segoe UI', 10), padding=6)
style.configure('TLabel', font=('Segoe UI', 10))
style.configure('TEntry', font=('Segoe UI', 10))

for i in range(3):
    window.columnconfigure(i, weight=1)

Label(window, text="🔗Link:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
website_entry = Entry(window, width=135)
website_entry.grid(row=0, column=1, columnspan=2, sticky='ew', padx=10)
website_entry.focus()

progress = Progressbar(window, orient='horizontal', mode='determinate')
progress.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

button_frame = Frame(window)
button_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=10)

for i in range(3):
    button_frame.columnconfigure(i, weight=1, minsize=150)

Button(button_frame, text="🎬 Baixar vídeo", command=downMP4).grid(row=0, column=0, sticky='ew', padx=5, pady=5)
Button(button_frame, text="🎵 Baixar áudio", command=downMP3).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
Button(button_frame, text="📃 Baixar playlist", command=lambda: abrir_opcoes_playlist(website_entry.get())).grid(row=0, column=2, sticky='ew', padx=5, pady=5)

Button(button_frame, text="🧹 Limpar", command=limpar_campo).grid(row=1, column=0, sticky='ew', padx=5, pady=5)
Button(button_frame, text="📂 Abrir pasta", command=abrir_pasta).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
Button(button_frame, text="📁 Selecionar pasta", command=select_path_down).grid(row=1, column=2, sticky='ew', padx=5, pady=5)

Label(window, text="🕘 Últimos downloads:").grid(row=3, column=0, columnspan=3, sticky='w', padx=10, pady=(10, 0))
historico_listbox = Listbox(window, height=8, width=100)
historico_listbox.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)
historico_listbox.bind("<MouseWheel>", lambda e: historico_listbox.yview_scroll(int(-1*(e.delta/120)), "units"))

# Garante que o arquivo de pasta de download exista
if not os.path.exists("path_down_directory.txt"):
    with open("path_down_directory.txt", "w") as f:
        f.write(".")

carregar_historico()

# Mantém a janela principal aberta
window.mainloop()