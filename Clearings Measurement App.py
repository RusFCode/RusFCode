import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import tkinter.font as font
from pyfirmata import Arduino, util
import time
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from PIL import ImageTk, Image
import os

root = tk.Tk()
root.title("Clearings Measurements App")
root.resizable(width = False, height = False)

def starting():

    RunApp.destroy()
    UseApp.destroy()

    for widget in frame.winfo_children():
        widget.destroy()

    PlotDurationLabel = tk.Label(frame, text = "Plot Duration in second", bg = "white", font = ("Helvetica", 26))
    PlotDurationLabel.pack()
    starting.var = tk.Entry(frame, bd = 4, font = ("Helvetica", 26), justify = "center")
    starting.var.pack()
    Validate = tk.Button(frame, text = "Validate", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = getDuration)
    Validate.pack()
    Process = tk.Button(frame, text = "Begin Process", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = core)
    Process.pack()

def StartingErrorNumber():

    RunApp.destroy()
    UseApp.destroy()

    for widget in frame.winfo_children():
        widget.destroy()

    ErrorLabel = tk.Label(frame, text = "Enter an int for the plot duration please", bg = "white", font = ("Helvetica", 26))
    ErrorLabel.pack()
    PlotDurationLabel = tk.Label(frame, text = "Plot Duration", bg = "white", font = ("Helvetica", 26))
    PlotDurationLabel.pack()
    starting.var = tk.Entry(frame, bd = 4, font = ("Helvetica", 26), justify = "center")
    starting.var.pack()
    Validate = tk.Button(frame, text = "Validate", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = getDuration)
    Validate.pack()
    Process = tk.Button(frame, text = "Begin Process", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command =  core)
    Process.pack()

def StartingErrorArduino():

    RunApp.destroy()
    UseApp.destroy()

    for widget in frame.winfo_children():
        widget.destroy()

    ErrorLabel = tk.Label(frame, text = "Connect your Arduino to the COM3 please", bg = "white", font = ("Helvetica", 26))
    ErrorLabel.pack()
    Process = tk.Button(frame, text = "Begin Process", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = core)
    Process.pack()

def getDuration():

    try :
        getDuration.var = int(starting.var.get())

    except BaseException :
        StartingErrorNumber()

def core():

    try :
        carte = Arduino("COM3")

    except BaseException :
            StartingErrorArduino()

    aquisition = util.Iterator(carte)
    aquisition.start()
    tension_A0 = carte.get_pin("a:0:i")

    liste_temps = []
    liste_temps_real = []
    liste_tension = []
    temps_limite = 0
    pics_count = 0
    firstmeasure = True

    if firstmeasure == True:

        firstmeasure = False

        for widget in frame.winfo_children():
            widget.destroy()

        StartLabel = tk.Label(frame, text = "Processing ...", bg = "white", font = ("Helvetica", 26))
        StartLabel.pack()

        LoadingBar = Progressbar(frame, orient = HORIZONTAL, length = 1000, mode = "indeterminate")
        LoadingBar.pack(expand = True)
        frame.update_idletasks()

    while temps_limite < getDuration.var:

        tension = tension_A0.read()
        temps = time.time()
        liste_temps.append(temps)
        temps_réel = temps - liste_temps[0]
        liste_temps_real.append(temps_réel)

        if tension is None :
            tension = 0

        elif tension*5 > 4 :
            pics_count += 1

            while tension*5 > 4 and temps_limite < getDuration.var:

                tension = tension_A0.read()*5
                liste_tension.append(tension)
                temps = time.time()
                liste_temps.append(temps)
                temps_réel = temps - liste_temps[0]
                liste_temps_real.append(temps_réel)
                temps_limite = temps_réel
                #print(tension)
                LoadingBar["value"] += 0.01
                frame.update_idletasks()

        liste_tension.append(tension)
        temps_limite = temps_réel
        #print(tension*5)
        LoadingBar["value"] += 0.01
        frame.update_idletasks()

    carte.exit()

    for widget in frame.winfo_children():
        widget.destroy()

    EndLabel = tk.Label(frame, text = "Process Ended", bg = "white", font = ("Helvetica", 20))
    EndLabel.pack()

    PicLabel = tk.Label(frame, text = f"The clearings number is : {pics_count}", bg = "white", font = ("Helvetica", 20))
    PicLabel.pack()

    NewTest = tk.Button(frame, text = "New Test", bg = "white", font = font.Font(family = "Helvetica", size = 20, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = starting)
    NewTest.pack()

    print(f"Vous effectuez 1 mesure toutes les {round(1000000*(getDuration.var/len(liste_temps_real)))} µs")

    matplotlib.use("TkAgg")
    fig = Figure(figsize = (12, 4),dpi = 100)
    PlotData = fig.add_subplot(111)
    PlotData.plot(liste_temps_real, liste_tension)
    canvas = FigureCanvasTkAgg(fig, master = frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()
    canvas.get_tk_widget().pack()

def infos():

    os.startfile("instructions.mp4")

def InfosDev():

    os.startfile("InfosDev.pdf")

def InfosSchool():

    os.startfile("Introducing a company - HELHa.pdf")

canvas = tk.Canvas(root, height = 700, width = 1400, bg = "#263D42" )
canvas.pack()

frame = tk.Frame(root, bg = "white")
frame.place(relwidth = 0.8, relheight = 0.8, relx = 0.1, rely = 0.1)

image = Image.open("Intro.png")
image = image.resize((1120, 615), Image.ANTIALIAS)
intro = ImageTk.PhotoImage(image)
IntroLabel = Label(frame, image = intro)
IntroLabel.pack()

RunApp = tk.Button(root, text = "Run App", padx = 10, pady = 5, fg = "white", bg = "#263D42", command = starting)
RunApp.pack()

UseApp = tk.Button(root, text = "?", padx = 10, pady = 5, fg = "white", bg = "#263D42", command = infos)
UseApp.pack()

InfoDev = tk.Button(root, text = "Info Dev", padx = 10, pady = 5, fg = "white", bg = "#263D42", command = InfosDev)
InfoDev.place(x = 758, y = 703.5)

InfoSchool = tk.Button(root, text = "Info School", padx = 10, pady = 5, fg = "white", bg = "#263D42", command = InfosSchool)
InfoSchool.place(x = 750, y = 738)

root.mainloop()
