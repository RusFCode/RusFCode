
# All the library imports

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

# intialysing the graphic interface ==> make it not resizable and givig a title

root = tk.Tk()
root.title("Clearings Measurements App")
root.resizable(width = False, height = False)

# Start function to run the App to do the tests

def starting():

    # Destroying the widgets

    RunApp.destroy()
    UseApp.destroy()

    for widget in frame.winfo_children():
        widget.destroy()

    # User input Plot duration and saving the value with validate + begin the process

    PlotDurationLabel = tk.Label(frame, text = "Plot Duration in second", bg = "white", font = ("Helvetica", 26))
    PlotDurationLabel.pack()
    starting.var = tk.Entry(frame, bd = 4, font = ("Helvetica", 26), justify = "center")
    starting.var.pack()
    Validate = tk.Button(frame, text = "Validate", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = getDuration)
    Validate.pack()
    Process = tk.Button(frame, text = "Begin Process", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = core)
    Process.pack()

# Error function if plot duration is not a int

def StartingErrorNumber():

    # Destroying the widgets

    RunApp.destroy()
    UseApp.destroy()

    for widget in frame.winfo_children():
        widget.destroy()

    # Repeating start function with an error label at the top

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

# Error function if Arduino is not plugged on COM3

def StartingErrorArduino():

    # Destroying the widgets

    RunApp.destroy()
    UseApp.destroy()

    for widget in frame.winfo_children():
        widget.destroy()

    # error label at the top + begin process button

    ErrorLabel = tk.Label(frame, text = "Connect your Arduino to the COM3 please", bg = "white", font = ("Helvetica", 26))
    ErrorLabel.pack()
    Process = tk.Button(frame, text = "Begin Process", bg = "white", font = font.Font(family = "Helvetica", size = 26, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = core)
    Process.pack()

# function to transform in int and so verify if the plot duration value is an int

def getDuration():

    # try and raise the exeption if not intable see StartingErrorNumber() for more informations

    try :
        getDuration.var = int(starting.var.get())

    except BaseException :
        StartingErrorNumber()

# Communicating link between Arduino and python function

def core():

    # try and raise the exeption if Arduino not plugged on COM3

    try :
        carte = Arduino("COM3")

    except BaseException :
            StartingErrorArduino()

    # aquisition of the Arduino and taking the value on pin A0

    aquisition = util.Iterator(carte)
    aquisition.start()
    tension_A0 = carte.get_pin("a:0:i")

    # lists and variables for the real time while and the graph at the end

    liste_temps = []
    liste_temps_real = []
    liste_tension = []
    temps_limite = 0
    pics_count = 0
    firstmeasure = True

    # Verify if it's first measure to introduce the loading screen

    if firstmeasure == True:

        firstmeasure = False

        for widget in frame.winfo_children():
            widget.destroy()

        StartLabel = tk.Label(frame, text = "Processing ...", bg = "white", font = ("Helvetica", 26))
        StartLabel.pack()

        LoadingBar = Progressbar(frame, orient = HORIZONTAL, length = 1000, mode = "indeterminate")
        LoadingBar.pack(expand = True)
        frame.update_idletasks()

    # Makes the measurements

    while temps_limite < getDuration.var:

        # Get the real time and tension + Stock in lists

        tension = tension_A0.read()
        temps = time.time()
        liste_temps.append(temps)
        temps_réel = temps - liste_temps[0]
        liste_temps_real.append(temps_réel)

        # First Arduino value is always None so fix it to zero to avoid error

        if tension is None :
            tension = 0

        # Here test for more than 4V tension to append the pics number

        elif tension*5 > 4 :
            pics_count += 1

            # Regetting values while we are in a pic to not count false pics

            while tension*5 > 4 and temps_limite < getDuration.var:

                tension = tension_A0.read()*5
                liste_tension.append(tension)
                temps = time.time()
                liste_temps.append(temps)
                temps_réel = temps - liste_temps[0]
                liste_temps_real.append(temps_réel)
                temps_limite = temps_réel
                LoadingBar["value"] += 0.01
                frame.update_idletasks()

        liste_tension.append(tension)
        temps_limite = temps_réel
        LoadingBar["value"] += 0.01
        frame.update_idletasks()

    carte.exit()

    # Destroying the widgets

    for widget in frame.winfo_children():
        widget.destroy()

    # Label ended process + number clearings + new test button

    EndLabel = tk.Label(frame, text = "Process Ended", bg = "white", font = ("Helvetica", 20))
    EndLabel.pack()

    PicLabel = tk.Label(frame, text = f"The clearings number is : {pics_count}", bg = "white", font = ("Helvetica", 20))
    PicLabel.pack()

    NewTest = tk.Button(frame, text = "New Test", bg = "white", font = font.Font(family = "Helvetica", size = 20, weight = "bold"), activebackground = "#263D42", activeforeground = "white", command = starting)
    NewTest.pack()

    # Matplotlib graphic zone definition + give (V,t) graph on the screen

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

# 3 functions for the differents informations at the start of the App

def infos():

    os.startfile("instructions.mp4")

def InfosDev():

    os.startfile("InfosDev.pdf")

def InfosSchool():

    os.startfile("Introducing a company - HELHa.pdf")

# Canvas definition first window == master 1

canvas = tk.Canvas(root, height = 700, width = 1400, bg = "#263D42" )
canvas.pack()

# Frame definition second window == master 2 + putting image on it and the 4 basic buttons

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

# Lanching and looping the graphic interface

root.mainloop()
