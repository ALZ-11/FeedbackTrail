import os
from dotenv import load_dotenv
from tkinter import *
import openai
import wave
import pyaudio
import tkinter as tk
from tkinter import ttk
import threading
import speech_recognition as sr
import io  
import googleapiclient.discovery
from google.oauth2 import service_account
import csv

# load environment vars
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

current_language = "French"
complaint_text = "Choix direct de la catégorie"

class AudioRecorder:
    def __init__(self, chunk=1024, channels=1, rate=44100, output_file="output.wav"):
        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.output_file = output_file
        self.frames = []
        self.is_recording = False
        self.audio = None
        self.stream = None

    def start_recording(self, input_device_index, output_device_index):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index=input_device_index,
                                      output_device_index=output_device_index,
                                      frames_per_buffer=self.chunk)
        self.is_recording = True
        self.frames = []
        print("Recording started...")
        threading.Thread(target=self.record).start()

    def record(self):
        while self.is_recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def stop_recording(self):
        self.is_recording = False
        print("Recording stopped.")

        # stop and close the stream
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        # save the recorded audio to a file
        wave_file = wave.open(self.output_file, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()
    def handle_record_button(self, input_device_index, output_device_index):
        if not self.is_recording:
            self.start_recording(input_device_index, output_device_index)
            record_text.configure(text="Recording", fg="red")
            
        else:
            self.stop_recording()
            record_text.configure(text="Record", fg="green")
            

def traitement():
    global solution
    global timeT, loading_dotsT, loadingButton_hiddenT

    try:
        Saisir.destroy()
    except:
        pass
    try:
        Deposer.destroy()
    except:
        pass

    Traitement = Tk()
    Traitement.geometry("1920x1080")

    def point_updateT():
        global timeT, loading_dotsT, loadingButton_hiddenT
        if timeT <= 7000:
            if loadingButton_hiddenT.cget("text") != "Traitement en cours...":
                loading_dotsT += "."
                timeT += 500
            else:
                loading_dotsT = "Traitement en cours."
                timeT += 500
        else:
            loadingButton_hiddenT.destroy()
            Merci1 = Label(Traitement, text="Votre réclamation rentre dans la catégorie:",
                          font="TkDefaultFont 24 bold", fg="#F77C3F", bd=0)
            Merci2 = Label(Traitement,  font="TkDefaultFont 35 bold", fg="red", bd=0)
            Merci2.config(text=f"{response_text}")
            Merci3 = Label(Traitement, text="Merci d'avoir utilisé FeedbackTrail", font="TkDefaultFont 24 bold", fg="#F77C3F", bd=0)
            Merci1.place(relx=0.5, rely=0.3, anchor=CENTER)
            Merci2.place(relx=0.5, rely=0.5, anchor=CENTER)
            Merci3.place(relx=0.5, rely=0.7, anchor=CENTER)
            return
        loadingButton_hiddenT.configure(text=loading_dotsT)
        Traitement.after(500, point_updateT)

    loading_dotsT = "Traitement en cours"
    loadingButton_hiddenT = Button(Traitement, text=loading_dotsT, font="TkDefaultFont 24 bold", fg="#F77C3F",
                                   command=point_updateT, bd=0)
    timeT = 0

    loadingButton_hiddenT.place(relx=0.5, rely=0.5, anchor=CENTER)
    loadingButton_hiddenT.invoke()
    solution = [response_text,Tram]
    print(Tram, response_text)
    
    
    # Drive API
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

    file_id = os.getenv("GOOGLE_DRIVE_FILE_ID")

    # get the csv from Drive
    request = drive_service.files().get_media(fileId=file_id)
    response = request.execute()

    # read the csv
    content = response.decode('utf-8').splitlines()
    rows = list(csv.reader(content))

    # add new row
    with open("categories.txt", "r", encoding="utf-8", errors="ignore") as f:
        lista = [line.rstrip('\n') for line in f.readlines()]
    if response_text in lista:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lat, lon = 33.5350, -7.6322  # Fixed coordinates of the Technopark kiosk
        
        new_row = [timestamp, current_language, response_text, Tram, "Technopark", lat, lon, complaint_text]
        rows.append(new_row)

        # convert rows back to csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)

        # update file on Drive
        media = googleapiclient.http.MediaIoBaseUpload(io.BytesIO(output.getvalue().encode()), mimetype='text/csv')
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    Traitement.mainloop()

    

def saisir_ar():
    global Saisir 
    global record_text
    global micro_image
    global aide_image
    global retour_image
    try:
        Deposer.destroy()
    except:
        pass

    Saisir = Tk()
    Saisir.geometry("1920x1080")

    def func():
        pass

    def classify():
        global lista
        global response_text
        with open("categories.txt","r", encoding="utf-8", errors = "ignore") as f:
            lista = [line.rstrip('\n') for line in f.readlines()]
        print(lista)
        complaint = saisie.get("1.0","end-1c")

        # generate response from GPT-3
        model_engine = "text-davinci-003"

        prompt = f"choose one word from the following list : {lista} that corresponds to the following problem{complaint}. If the problem doesn't correspond to any word from the list, give exactly one new word in french that describs the problem.\nChatGPT: "
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        # extract response text from API response
        response_text = response.choices[0].text.strip()
        #if response_text not in lista:
         #  with open('categories.txt', 'a') as file:
          #  file.write('\n')  # Add a new line
           # file.write(response_text)
        category = response_text
        print(category)
        global complaint_text
        complaint_text = saisie.get("1.0", "end-1c")
        traitement()


    saisirLabel = Label(Saisir, justify= CENTER, text = "أدخل شكواك", font = "Roboto 24 bold", fg= "#F77C3F")
    saisie = Text(Saisir, width=60, height=15, wrap="word")  
    micro_image = PhotoImage(file = "images/micro.png")
    micro_button = Button(Saisir, image = micro_image,height=50,width=50, bd = 1, relief= RAISED)
    record_text = Label(Saisir, text= "تسجيل", font = "haha 20 bold", fg="green")
    soumettre_button = Button(Saisir, width = 10, bg = "#416FEC", text = "إرسال", font ="haha 24 bold", relief= RAISED, bd = 5, command= classify)

    aide_image = PhotoImage(file = "images/aide2.png")
    retour_image = PhotoImage(file = "images/retour.png")
    retour_button = Button(Saisir, command = deposer_fr, image = retour_image, bd = 1, relief= RAISED)
    aide_button = Button(Saisir, command = func, image = aide_image, bd = 1, relief= RAISED)
    retour_label = Label(Saisir, text = "عودة", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)
    aide_label = Label(Saisir, text = "مساعدة", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)

    saisirLabel.place(relx = 0.5, rely = 0.05, anchor = CENTER)
    saisie.place(relx = 0.5, rely = 0.35, anchor = CENTER)
    micro_button.place(relx = 0.5, rely = 0.65, anchor = CENTER)
    record_text.place(relx = 0.5, rely = 0.70, anchor = CENTER)
    soumettre_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)


    retour_label.place(relx = 0.1, rely = 0.85, anchor = CENTER)
    retour_button.place(relx = 0.1, rely = 0.9, anchor = CENTER)
    aide_label.place(relx = 0.9, rely = 0.85, anchor = CENTER)
    aide_button.place(relx = 0.9, rely = 0.9, anchor = CENTER)

    # function to handle the button click
    def handle_record_button():
        saisie.delete("1.0", "end")
        if not audio_recorder.is_recording:

            input_device_index = 1  
            output_device_index = 3 
            audio_recorder.handle_record_button(input_device_index, output_device_index)

        else:

            audio_recorder.handle_record_button(None, None)
            #----------------------------Recognize----------------------------------------------------------

            # create a recognizer object
            recognizer = sr.Recognizer()

            # load the audio file
            audio_file = "output.wav"

            # use the recognizer to open the audio file
            with sr.AudioFile(audio_file) as source:
                # read the entire audio file
                audio = recognizer.record(source)

                # convert speech to text
                text = recognizer.recognize_google(audio, language="ar")

                # print the transcribed text
            saisie.insert("1.0",text)

        
        


    # create an instance of AudioRecorder
    audio_recorder = AudioRecorder()
    # configure the button's command to the handle_record_button function
    micro_button.configure(command=handle_record_button)
    

    Saisir.mainloop()

def saisir_en():
    global Saisir 
    global record_text
    global micro_image
    global aide_image
    global retour_image
    try:
        Deposer.destroy()
    except:
        pass

    Saisir = Tk()
    Saisir.geometry("1920x1080")

    def func():
        pass

    def classify():
        global lista
        global response_text
        with open("categories.txt","r", encoding="utf-8", errors = "ignore") as f:
            lista = [line.rstrip('\n') for line in f.readlines()]
        print(lista)
        complaint = saisie.get("1.0","end-1c")

        
        model_engine = "text-davinci-003"

        prompt = f"choose one word from the following list : {lista} that corresponds to the following problem{complaint}. If the problem doesn't correspond to any word from the list, give exactly one new word in french that describs the problem.\nChatGPT: "
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        response_text = response.choices[0].text.strip()
        #if response_text not in lista:
         #   with open('categories.txt', 'a') as file:
          #      file.write('\n')  # Add a new line
           #     file.write(response_text)
        category = response_text
        print(category)
        global complaint_text
        complaint_text = saisie.get("1.0", "end-1c")
        traitement()

    saisirLabel = Label(Saisir, justify= CENTER, text = "Enter your complaint", font = "Roboto 24 bold", fg= "#F77C3F")
    saisie = Text(Saisir, width=60, height=15, wrap="word")  
    micro_image = PhotoImage(file = "images/micro.png")
    micro_button = Button(Saisir, image = micro_image,height=50,width=50, bd = 1, relief= RAISED)
    record_text = Label(Saisir, text= "Record", font = "haha 20 bold", fg="green")
    soumettre_button = Button(Saisir, width = 10, bg = "#416FEC", text = "Submit", font ="haha 24 bold", relief= RAISED, bd = 5, command= classify)

    aide_image = PhotoImage(file = "images/aide2.png")
    retour_image = PhotoImage(file = "images/retour.png")
    retour_button = Button(Saisir, command = deposer_fr, image = retour_image, bd = 1, relief= RAISED)
    aide_button = Button(Saisir, command = func, image = aide_image, bd = 1, relief= RAISED)
    retour_label = Label(Saisir, text = "Back", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)
    aide_label = Label(Saisir, text = "Help", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)

    saisirLabel.place(relx = 0.5, rely = 0.05, anchor = CENTER)
    saisie.place(relx = 0.5, rely = 0.35, anchor = CENTER)
    micro_button.place(relx = 0.5, rely = 0.65, anchor = CENTER)
    record_text.place(relx = 0.5, rely = 0.70, anchor = CENTER)
    soumettre_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)

    retour_label.place(relx = 0.1, rely = 0.85, anchor = CENTER)
    retour_button.place(relx = 0.1, rely = 0.9, anchor = CENTER)
    aide_label.place(relx = 0.9, rely = 0.85, anchor = CENTER)
    aide_button.place(relx = 0.9, rely = 0.9, anchor = CENTER)

    # function to handle button click
    def handle_record_button():
        saisie.delete("1.0", "end")
        if not audio_recorder.is_recording:

            input_device_index = 1  
            output_device_index = 3  
            audio_recorder.handle_record_button(input_device_index, output_device_index)

        else:

            audio_recorder.handle_record_button(None, None)
            #----------------------------Recognize----------------------------------------------------------

            # create a recognizer object
            recognizer = sr.Recognizer()

            # load the audio file
            audio_file = "output.wav"

            # use the recognizer to open the audio file
            with sr.AudioFile(audio_file) as source:
                # read the entire audio file
                audio = recognizer.record(source)

                # convert speech to text
                text = recognizer.recognize_google(audio, language="en")

                # print the transcribed text
            saisie.insert("1.0",text)

        
        


    # create an instance of AudioRecorder
    audio_recorder = AudioRecorder()
    # configure the button's command to the handle_record_button function
    micro_button.configure(command=handle_record_button)
    

    Saisir.mainloop()

def saisir_fr():
    global Saisir 
    global record_text
    global audio_recorder
    try:
        Deposer.destroy()
    except:
        pass


    Saisir = Tk()
    Saisir.geometry("1920x1080")

    def func():
        pass

    def classify():
        global lista
        global response_text
        with open("categories.txt","r", encoding="utf-8", errors = "ignore") as f:
            lista = [line.rstrip('\n') for line in f.readlines()]
        print(lista)
        complaint = saisie.get("1.0","end-1c")

        # generate response from GPT-3
        model_engine = "text-davinci-003"

        prompt = f"choose one word from the following list : {lista} that corresponds to the following problem{complaint}. If the problem doesn't correspond to any word from the list, give exactly one new word in french that describs the problem.\nChatGPT: "
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        # extract the response text from the openai api response
        response_text = response.choices[0].text.strip()
        #if response_text not in lista:
         #  with open('categories.txt', 'a') as file:
          #  file.write('\n')  # Add a new line
           # file.write(response_text)
        category = response_text
        print(category)
        global complaint_text
        complaint_text = saisie.get("1.0", "end-1c")
        traitement()
    

    saisirLabel = Label(Saisir, justify= CENTER, text = "Saisissez votre réclamation", font = "Roboto 24 bold", fg= "#F77C3F")
    saisie = Text(Saisir, width=60, height=15, wrap="word")  
    micro_image = PhotoImage(file = "images/micro.png")
    micro_button = Button(Saisir, image = micro_image,height=50,width=50, bd = 1, relief= RAISED)
    record_text = Label(Saisir, text= "Record", font = "haha 20 bold", fg="green")
    soumettre_button = Button(Saisir, width = 10, bg = "#416FEC", text = "Soumettre", font ="haha 24 bold", relief= RAISED, bd = 5, command= classify)

    aide_image = PhotoImage(file = "images/aide2.png")
    retour_image = PhotoImage(file = "images/retour.png")
    retour_button = Button(Saisir, command = deposer_fr, image = retour_image, bd = 1, relief= RAISED)
    aide_button = Button(Saisir, command = func, image = aide_image, bd = 1, relief= RAISED)
    retour_label = Label(Saisir, text = "Retour", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)
    aide_label = Label(Saisir, text = "Aide", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)

    saisirLabel.place(relx = 0.5, rely = 0.05, anchor = CENTER)
    saisie.place(relx = 0.5, rely = 0.35, anchor = CENTER)
    micro_button.place(relx = 0.5, rely = 0.65, anchor = CENTER)
    record_text.place(relx = 0.5, rely = 0.70, anchor = CENTER)
    soumettre_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)
    

    retour_label.place(relx = 0.1, rely = 0.85, anchor = CENTER)
    retour_button.place(relx = 0.1, rely = 0.9, anchor = CENTER)
    aide_label.place(relx = 0.9, rely = 0.85, anchor = CENTER)
    aide_button.place(relx = 0.9, rely = 0.9, anchor = CENTER)

    # function to handle button click
    def handle_record_button():
        saisie.delete("1.0", "end")
        if not audio_recorder.is_recording:
            
            input_device_index = 1  
            output_device_index = 3  
            audio_recorder.handle_record_button(input_device_index, output_device_index)
            
        else:
            
            audio_recorder.handle_record_button(None, None)
            #----------------------------Recognize----------------------------------------------------------

            # create a recognizer object
            recognizer = sr.Recognizer()

            # load the audio file
            audio_file = "output.wav"

            # use the recognizer to open the audio file
            with sr.AudioFile(audio_file) as source:
                # read the entire audio file
                audio = recognizer.record(source)

                # convert speech to text
                text = recognizer.recognize_google(audio, language="fr")

                # print transcribed text
            saisie.insert("1.0",text)
        
        


    # create an instance of AudioRecorder
    audio_recorder = AudioRecorder()
    # configure the button's command to the handle_record_button function
    micro_button.configure(command=handle_record_button)
    

    Saisir.mainloop()



def deposer_ar():
    global Deposer
    global cat
    global response_text
    cat = 0
    def assign(value):
        global response_text, complaint_text
        cat = value
        if cat == 7:
            saisir_ar()
        else:
            complaint_text = "Choix direct de la catégorie"
            with open("categories.txt","r", encoding="utf-8", errors = "ignore") as f:
                lista = [line.rstrip('\n') for line in f.readlines()]
            response_text = lista[cat-1]
            traitement()

    try:
        Welcome.destroy()
    except:
        pass
    try:
         Saisir.destroy()
    except:
         pass

    Deposer = Tk()
    Deposer.geometry("1920x1080")

    def func():
        pass

    deposerLabel = Label(Deposer, text="اختر فئة شكواك", font="Roboto 24 bold", fg="#F77C3F")

    aide_image = PhotoImage(file="images/aide2.png")
    retour_image = PhotoImage(file="images/retour.png")

    autre_image = PhotoImage(file="images/deposer.png")

    retour_button = Button(Deposer, command=welcome_ar, image=retour_image, bd=1, relief=RAISED)
    aide_button = Button(Deposer, command=func, image=aide_image, bd=1, relief=RAISED)
    retour_label = Label(Deposer, text = "عودة", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)
    aide_label = Label(Deposer, text = "مساعدة", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)

    deposerLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

    retour_button.place(relx=0.1, rely=0.85, anchor=CENTER)
    aide_button.place(relx=0.9, rely=0.9, anchor=CENTER)
    retour_label.place(relx = 0.1, rely = 0.85, anchor = CENTER)
    aide_label.place(relx = 0.9, rely = 0.85, anchor = CENTER)
    retour_button.place(relx = 0.1, rely = 0.9, anchor = CENTER)

    # Category 1
    placeholder1_image = PhotoImage(file="images/punctuality.png")
    placeholder1_button = Button(Deposer, image=placeholder1_image, bd=0, relief=RAISED, command = lambda: assign(1))
    placeholder1_label = Label(Deposer, text="الدقة\nوالانتظام", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 2
    placeholder2_image = PhotoImage(file="images/travinfo.png")
    placeholder2_button = Button(Deposer, image=placeholder2_image, bd=0, relief=RAISED, command = lambda: assign(2))
    placeholder2_label = Label(Deposer, text="معلومات\nالمسافر", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 3
    placeholder3_image = PhotoImage(file="images/equipment.png")
    placeholder3_button = Button(Deposer, image=placeholder3_image, bd=0, relief=RAISED, command = lambda: assign(3))
    placeholder3_label = Label(Deposer, text="المعدات", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 4
    placeholder4_image = PhotoImage(file="images/tarif.png")
    placeholder4_button = Button(Deposer, image=placeholder4_image, bd=0, relief=RAISED, command = lambda: assign(4))
    placeholder4_label = Label(Deposer, text="الأسعار", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 5
    placeholder5_image = PhotoImage(file="images/relationel.png")
    placeholder5_button = Button(Deposer, image=placeholder5_image, bd=0, relief=RAISED, command = lambda: assign(5))
    placeholder5_label = Label(Deposer, text="سلوك\nالموظفين", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 6
    placeholder6_image = PhotoImage(file="images/security.png")
    placeholder6_button = Button(Deposer, image=placeholder6_image, bd=0, relief=RAISED, command = lambda: assign(6))
    placeholder6_label = Label(Deposer, text="الأمان\nوالسلامة", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category "أخرى"
    autre_button = Button(Deposer, image=autre_image, bd=0, relief=RAISED, command = lambda: assign(7))
    autre_label = Label(Deposer, text="أخرى", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER, )

    # Category 1 placement
    placeholder1_button.place(relx=0.2, rely=0.3, anchor=CENTER)
    placeholder1_label.place(relx=0.2, rely=0.4, anchor=CENTER)

    # Category 2 placement
    placeholder2_button.place(relx=0.5, rely=0.3, anchor=CENTER)
    placeholder2_label.place(relx=0.5, rely=0.4, anchor=CENTER)

    # Category 3 placement
    placeholder3_button.place(relx=0.8, rely=0.3, anchor=CENTER)
    placeholder3_label.place(relx=0.8, rely=0.4, anchor=CENTER)

    # Category 4 placement
    placeholder4_button.place(relx=0.2, rely=0.5, anchor=CENTER)
    placeholder4_label.place(relx=0.2, rely=0.6, anchor=CENTER)

    # Category 5 placement
    placeholder5_button.place(relx=0.5, rely=0.5, anchor=CENTER)
    placeholder5_label.place(relx=0.5, rely=0.6, anchor=CENTER)

    # Category 6 placement
    placeholder6_button.place(relx=0.8, rely=0.5, anchor=CENTER)
    placeholder6_label.place(relx=0.8, rely=0.6, anchor=CENTER)

    # Category "أخرى" placement
    autre_button.place(relx=0.5, rely=0.7, anchor=CENTER)
    autre_label.place(relx=0.5, rely=0.8, anchor=CENTER)

    Deposer.mainloop()

def deposer_en():
    global response_text
    global Deposer
    global cat
    cat = 0
    def assign(value):
        global response_text, complaint_text
        cat = value
        if cat == 7:
            saisir_en()
        else:
            complaint_text = "Choix direct de la catégorie"
            with open("categories.txt","r", encoding="utf-8", errors = "ignore") as f:
                lista = [line.rstrip('\n') for line in f.readlines()]
            response_text = lista[cat-1]
            traitement()

    try:
        Welcome.destroy()
    except:
        pass
    try:
         Saisir.destroy()
    except:
         pass
    
    Deposer = Tk()
    Deposer.geometry("1920x1080")

    def func():
        pass

    deposerLabel = Label(Deposer, text="Choose the category of your complaint", font="Roboto 24 bold", fg="#F77C3F")

    aide_image = PhotoImage(file="images/aide2.png")
    retour_image = PhotoImage(file="images/retour.png")

    autre_image = PhotoImage(file="images/deposer.png")

    retour_button = Button(Deposer, command=welcome_en, image=retour_image, bd=1, relief=RAISED)
    aide_button = Button(Deposer, command=func, image=aide_image, bd=1, relief=RAISED)
    retour_label = Label(Deposer, text = "Back", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)
    aide_label = Label(Deposer, text = "Help", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)

    deposerLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

    retour_button.place(relx=0.1, rely=0.85, anchor=CENTER)
    aide_button.place(relx=0.9, rely=0.9, anchor=CENTER)
    retour_label.place(relx = 0.1, rely = 0.85, anchor = CENTER)
    aide_label.place(relx = 0.9, rely = 0.85, anchor = CENTER)
    retour_button.place(relx = 0.1, rely = 0.9, anchor = CENTER)

    # Category 1
    placeholder1_image = PhotoImage(file="images/punctuality.png")
    placeholder1_button = Button(Deposer, image=placeholder1_image, bd=0, relief=RAISED, command = lambda: assign(1))
    placeholder1_label = Label(Deposer, text="Punctuality\n& Regularity", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 2
    placeholder2_image = PhotoImage(file="images/travinfo.png")
    placeholder2_button = Button(Deposer, image=placeholder2_image, bd=0, relief=RAISED, command = lambda: assign(2))
    placeholder2_label = Label(Deposer, text="Passenger\nInformation", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 3
    placeholder3_image = PhotoImage(file="images/equipment.png")
    placeholder3_button = Button(Deposer, image=placeholder3_image, bd=0, relief=RAISED, command = lambda: assign(3))
    placeholder3_label = Label(Deposer, text="Equipments", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 4
    placeholder4_image = PhotoImage(file="images/tarif.png")
    placeholder4_button = Button(Deposer, image=placeholder4_image, bd=0, relief=RAISED, command = lambda: assign(4))
    placeholder4_label = Label(Deposer, text="Tariff", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 5
    placeholder5_image = PhotoImage(file="images/relationel.png")
    placeholder5_button = Button(Deposer, image=placeholder5_image, bd=0, relief=RAISED, command = lambda: assign(5))
    placeholder5_label = Label(Deposer, text="Staff Behavior", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 6
    placeholder6_image = PhotoImage(file="images/security.png")
    placeholder6_button = Button(Deposer, image=placeholder6_image, bd=0, relief=RAISED, command = lambda: assign(6))
    placeholder6_label = Label(Deposer, text="Security\n& Safety", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category "Other"
    autre_button = Button(Deposer, image=autre_image, bd=0, relief=RAISED, command = lambda: assign(7))
    autre_label = Label(Deposer, text="Others", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER, )

    # Category 1 placement
    placeholder1_button.place(relx=0.2, rely=0.3, anchor=CENTER)
    placeholder1_label.place(relx=0.2, rely=0.4, anchor=CENTER)

    # Category 2 placement
    placeholder2_button.place(relx=0.5, rely=0.3, anchor=CENTER)
    placeholder2_label.place(relx=0.5, rely=0.4, anchor=CENTER)

    # Category 3 placement
    placeholder3_button.place(relx=0.8, rely=0.3, anchor=CENTER)
    placeholder3_label.place(relx=0.8, rely=0.4, anchor=CENTER)

    # Category 4 placement
    placeholder4_button.place(relx=0.2, rely=0.5, anchor=CENTER)
    placeholder4_label.place(relx=0.2, rely=0.6, anchor=CENTER)

    # Category 5 placement
    placeholder5_button.place(relx=0.5, rely=0.5, anchor=CENTER)
    placeholder5_label.place(relx=0.5, rely=0.6, anchor=CENTER)

    # Category 6 placement
    placeholder6_button.place(relx=0.8, rely=0.5, anchor=CENTER)
    placeholder6_label.place(relx=0.8, rely=0.6, anchor=CENTER)

    # Category "Others" placement
    autre_button.place(relx=0.5, rely=0.7, anchor=CENTER)
    autre_label.place(relx=0.5, rely=0.8, anchor=CENTER)

    Deposer.mainloop()

def deposer_fr():
    global response_text
    global Deposer
    global cat
    cat = 0
    def assign(value):
        global response_text, complaint_text
        cat = value
        if cat == 7:
            saisir_fr()
        else:
            complaint_text = "Choix direct de la catégorie"
            with open("categories.txt","r", encoding="utf-8", errors = "ignore") as f:
                lista = [line.rstrip('\n') for line in f.readlines()]
            response_text = lista[cat-1]
            traitement()

    try:
        Welcome.destroy()
    except:
        pass
    try:
         Saisir.destroy()
    except:
         pass

    Deposer = Tk()
    Deposer.geometry("1920x1080")

    def func():
        pass

    deposerLabel = Label(Deposer, text="Choisissez la catégorie de votre réclamation", font="Roboto 24 bold", fg="#F77C3F")

    aide_image = PhotoImage(file="images/aide2.png")
    retour_image = PhotoImage(file="images/retour.png")

    autre_image = PhotoImage(file="images/deposer.png")

    retour_button = Button(Deposer, command=welcome_fr, image=retour_image, bd=1, relief=RAISED)
    aide_button = Button(Deposer, command=func, image=aide_image, bd=1, relief=RAISED)
    retour_label = Label(Deposer, text = "Retour", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)
    aide_label = Label(Deposer, text = "Aide", font = "Roboto 12 bold", fg= "#F77C3F", justify= CENTER)

    deposerLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

    retour_button.place(relx=0.1, rely=0.85, anchor=CENTER)
    aide_button.place(relx=0.9, rely=0.9, anchor=CENTER)
    retour_label.place(relx = 0.1, rely = 0.85, anchor = CENTER)
    aide_label.place(relx = 0.9, rely = 0.85, anchor = CENTER)
    retour_button.place(relx = 0.1, rely = 0.9, anchor = CENTER)

    # Category 1
    placeholder1_image = PhotoImage(file="images/punctuality.png")
    placeholder1_button = Button(Deposer, image=placeholder1_image, bd=0, relief=RAISED, command = lambda: assign(1))
    placeholder1_label = Label(Deposer, text="Ponctualité\n& régularité", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 2
    placeholder2_image = PhotoImage(file="images/travinfo.png")
    placeholder2_button = Button(Deposer, image=placeholder2_image, bd=0, relief=RAISED, command = lambda: assign(2))
    placeholder2_label = Label(Deposer, text="Informations\nvoyageur", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 3
    placeholder3_image = PhotoImage(file="images/equipment.png")
    placeholder3_button = Button(Deposer, image=placeholder3_image, bd=0, relief=RAISED, command = lambda: assign(3))
    placeholder3_label = Label(Deposer, text="Equipements", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 4
    placeholder4_image = PhotoImage(file="images/tarif.png")
    placeholder4_button = Button(Deposer, image=placeholder4_image, bd=0, relief=RAISED, command = lambda: assign(4))
    placeholder4_label = Label(Deposer, text="Tarification", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 5
    placeholder5_image = PhotoImage(file="images/relationel.png")
    placeholder5_button = Button(Deposer, image=placeholder5_image, bd=0, relief=RAISED, command = lambda: assign(5))
    placeholder5_label = Label(Deposer, text="Comportement du\npersonel", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category 6
    placeholder6_image = PhotoImage(file="images/security.png")
    placeholder6_button = Button(Deposer, image=placeholder6_image, bd=0, relief=RAISED, command = lambda: assign(6))
    placeholder6_label = Label(Deposer, text="Sécurité\n& sûreté", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)

    # Category "Autres"
    autre_button = Button(Deposer, image=autre_image, bd=0, relief=RAISED, command = lambda: assign(7))
    autre_label = Label(Deposer, text="Autres", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER, )

    # Category 1 placement
    placeholder1_button.place(relx=0.2, rely=0.3, anchor=CENTER)
    placeholder1_label.place(relx=0.2, rely=0.4, anchor=CENTER)

    # Category 2 placement
    placeholder2_button.place(relx=0.5, rely=0.3, anchor=CENTER)
    placeholder2_label.place(relx=0.5, rely=0.4, anchor=CENTER)

    # Category 3 placement
    placeholder3_button.place(relx=0.8, rely=0.3, anchor=CENTER)
    placeholder3_label.place(relx=0.8, rely=0.4, anchor=CENTER)

    # Category 4 placement
    placeholder4_button.place(relx=0.2, rely=0.5, anchor=CENTER)
    placeholder4_label.place(relx=0.2, rely=0.6, anchor=CENTER)

    # Category 5 placement
    placeholder5_button.place(relx=0.5, rely=0.5, anchor=CENTER)
    placeholder5_label.place(relx=0.5, rely=0.6, anchor=CENTER)

    # Category 6 placement
    placeholder6_button.place(relx=0.8, rely=0.5, anchor=CENTER)
    placeholder6_label.place(relx=0.8, rely=0.6, anchor=CENTER)

    # Category "Autres" placement
    autre_button.place(relx=0.5, rely=0.7, anchor=CENTER)
    autre_label.place(relx=0.5, rely=0.8, anchor=CENTER)

    Deposer.mainloop()



def welcome_ar():
    global Welcome
    global Tram
    Tram = selected_option.get()

    def deposer_func_ar():
        deposer_ar()

    def about_func_ar():
        about_ar()

    try:
        Deposer.destroy()
    except:
        pass

    try:
        About.destroy()
    except:
        pass

    try:
        tram_dropdown.destroy()
    except:
        pass
    try:
        Languages.destroy()
    except:
        pass
    

    Welcome = Tk()
    Welcome.geometry("1920x1080")

    def func():
        pass

    welcomeLabel = Label(Welcome, text="مرحباً بكم في فِيدباك تريل", font="Roboto 24 bold", fg="#F77C3F")

    deposer_image = PhotoImage(file="images/deposer.png")
    aide_image = PhotoImage(file="images/aide.png")
    propos_image = PhotoImage(file="images/propos.png")
    retour_image = PhotoImage(file="images/retour.png")

    aide_button = Button(Welcome, command=func, image=aide_image, bd=0, relief=RAISED)
    deposer_button = Button(Welcome, command=deposer_ar, image=deposer_image, bd=0, relief=RAISED)
    propos_button = Button(Welcome, image=propos_image, bd=0, relief=RAISED, command=about_func_ar)
    retour_button = Button(Welcome, command=languages, image=retour_image, bd=1, relief=RAISED)

    aide_label = Label(Welcome, text="الحصول على مساعدة", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)
    deposer_label = Label(Welcome, text="تقديم شكوى", font="Roboto 22 bold", fg="#F77C3F", justify=CENTER)
    propos_label = Label(Welcome, text="من نحن", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)
    retour_label = Label(Welcome, text="رجوع", font="Roboto 12 bold", fg="#F77C3F", justify=CENTER)

    welcomeLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

    aide_button.place(relx=0.2, rely=0.6, anchor=CENTER)
    aide_label.place(relx=0.2, rely=0.7, anchor=CENTER)

    deposer_button.place(relx=0.5, rely=0.3, anchor=CENTER)
    deposer_label.place(relx=0.5, rely=0.4, anchor=CENTER)

    propos_button.place(relx=0.8, rely=0.6, anchor=CENTER)
    propos_label.place(relx=0.8, rely=0.7, anchor=CENTER)

    retour_label.place(relx=0.1, rely=0.85, anchor=CENTER)
    retour_button.place(relx=0.1, rely=0.9, anchor=CENTER)

    Welcome.mainloop()

def welcome_en():
    global Welcome
    global welcomeLabel
    global Tram
    Tram = selected_option.get()
    
    def deposer_func_en():
        deposer_en()
    
    def about_func_en():
        about_en()
    
    try:
        tram_dropdown.destroy()
    except:
        pass
    try:
        Deposer.destroy()
    except:
        pass
    
    try:
        About.destroy()
    except:
        pass
    
    try:
        Languages.destroy()
    except:
        pass
    
    Welcome = Tk()
    Welcome.geometry("1920x1080")
    
    def func():
        pass
    
    welcomeLabel = Label(Welcome, text="Welcome to FeedbackTrail", font="Roboto 24 bold", fg="#F77C3F")
    
    deposer_image = PhotoImage(file="images/deposer.png")
    aide_image = PhotoImage(file="images/aide.png")
    propos_image = PhotoImage(file="images/propos.png")
    retour_image = PhotoImage(file="images/retour.png")
    
    deposer_button = Button(Welcome, command=deposer_func_en, image=deposer_image, bd=0, relief=RAISED)
    aide_button = Button(Welcome, command=func, image=aide_image, bd=0, relief=RAISED)
    propos_button = Button(Welcome, image=propos_image, bd=0, relief=RAISED, command=about_func_en)
    retour_button = Button(Welcome, command=languages, image=retour_image, bd=1, relief=RAISED)
    
    deposer_label = Label(Welcome, text="File a\ncomplaint", font="Roboto 22 bold", fg="#F77C3F", justify=CENTER)
    aide_label = Label(Welcome, text="Get\nhelp", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)
    propos_label = Label(Welcome, text="About\nus", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)
    retour_label = Label(Welcome, text="Back", font="Roboto 12 bold", fg="#F77C3F", justify=CENTER)
    
    welcomeLabel.place(relx=0.5, rely=0.1, anchor=CENTER)
    
    deposer_button.place(relx=0.5, rely=0.3, anchor=CENTER)
    deposer_label.place(relx=0.5, rely=0.4, anchor=CENTER)
    
    aide_button.place(relx=0.2, rely=0.6, anchor=CENTER)
    aide_label.place(relx=0.2, rely=0.7, anchor=CENTER)
    
    propos_button.place(relx=0.8, rely=0.6, anchor=CENTER)
    propos_label.place(relx=0.8, rely=0.7, anchor=CENTER)
    
    retour_label.place(relx=0.1, rely=0.85, anchor=CENTER)
    retour_button.place(relx=0.1, rely=0.9, anchor=CENTER)
    
    Welcome.mainloop()

def welcome_fr():
    global Welcome
    global Tram
    Tram = selected_option.get()
    def deposer_func_fr():
        deposer_fr()

    def about_func_fr():
        about_fr()

    def about_func_en():
        about_en()

    def about_func_ar():
        about_ar()

    try:
        Deposer.destroy()
    except:
        pass
    try:
        tram_dropdown.destroy()
    except:
        pass
    try:
        About.destroy()
    except:
        pass

    try:
        Languages.destroy()
    except:
        pass

    Welcome = Tk()
    Welcome.geometry("1920x1080")

    def func():
        pass

    welcomeLabel = Label(Welcome, text="Bienvenue sur FeedbackTrail", font="Roboto 24 bold", fg="#F77C3F")

    deposer_image = PhotoImage(file="images/deposer.png")
    aide_image = PhotoImage(file="images/aide.png")
    propos_image = PhotoImage(file="images/propos.png")
    retour_image = PhotoImage(file="images/retour.png")

    aide_button = Button(Welcome, command=func, image=aide_image, bd=0, relief=RAISED)
    deposer_button = Button(Welcome, command=deposer_func_fr, image=deposer_image, bd=0, relief=RAISED)
    propos_button = Button(Welcome, image=propos_image, bd=0, relief=RAISED, command=about_func_fr)
    retour_button = Button(Welcome, command=languages, image=retour_image, bd=1, relief=RAISED)

    aide_label = Label(Welcome, text="Obtenir de\nl'aide", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)
    deposer_label = Label(Welcome, text="Déposer une\nréclamation", font="Roboto 22 bold", fg="#F77C3F", justify=CENTER)
    propos_label = Label(Welcome, text="A propos de\nnous", font="Roboto 16 bold", fg="#F77C3F", justify=CENTER)
    retour_label = Label(Welcome, text="Retour", font="Roboto 12 bold", fg="#F77C3F", justify=CENTER)

    welcomeLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

    aide_button.place(relx=0.2, rely=0.6, anchor=CENTER)
    aide_label.place(relx=0.2, rely=0.7, anchor=CENTER)

    deposer_button.place(relx=0.5, rely=0.3, anchor=CENTER)
    deposer_label.place(relx=0.5, rely=0.4, anchor=CENTER)

    propos_button.place(relx=0.8, rely=0.6, anchor=CENTER)
    propos_label.place(relx=0.8, rely=0.7, anchor=CENTER)

    retour_label.place(relx=0.1, rely=0.85, anchor=CENTER)
    retour_button.place(relx=0.1, rely=0.9, anchor=CENTER)

    Welcome.mainloop()



def languages():
    global Languages
    Tram = 0
    def francais_button():
        global selected_option
        global tram_dropdown
        global current_language
        current_language = "French"
        tram_dropdown = Toplevel(Languages)
        tram_dropdown.title("TramDropdown")
        tram_dropdown.geometry("1920x1080")

        # Configure the style and aesthetics of the TramDropdown window
        tram_dropdown.configure(bg="#F2F2F2")

        # Create the label in heading style
        label_heading = Label(tram_dropdown, text="Quel tram fait sujet de votre réclamation?", font="TkDefaultFont 24 bold",
                            fg="#F77C3F", bg="#F2F2F2")
        label_heading.pack(pady=10)

        # Customize the style of the dropdown menu
        style = ttk.Style()
        style.configure("TCombobox", selectbackground="#F77C3F", fieldbackground="#FFFFFF", font="TkDefaultFont 12")

        # Create the dropdown menu
        options = [f"Tram{i:02d}" for i in range(1, 46)]
        selected_option = StringVar(tram_dropdown)
        selected_option.set(options[0])  # Set the initial selected option

        drop_down_menu = OptionMenu(tram_dropdown, selected_option, *options)
        drop_down_menu.pack(pady=10)
        label_station = Label(tram_dropdown, text="Station: Technopark", font="TkDefaultFont 20 bold",
                            fg="#F77C3F", bg="#F2F2F2")
        label_station.pack(pady=10)
        # Create the 'Continuer' button with black text and a dark blue background
        continue_button = Button(tram_dropdown, text="Continuer", fg="black", bg="dark blue", command=welcome_fr)
        continue_button.pack(pady=10)  # Add the button to the window with some vertical padding

        tram_dropdown.mainloop()
    def arabic_button():
        global selected_option
        global Tram
        global current_language
        current_language = "Arabic"
        tram_dropdown = Toplevel(Languages)
        tram_dropdown.title("TramDropdown")
        tram_dropdown.geometry("1920x1080")

        # Configure the style and aesthetics of the TramDropdown window
        tram_dropdown.configure(bg="#F2F2F2")

        # Create the label in heading style
        label_heading = Label(tram_dropdown, text="أي ترام هو موضوع شكواك؟", font="TkDefaultFont 24 bold",
                            fg="#F77C3F", bg="#F2F2F2")
        label_heading.pack(pady=10)

        # Customize the style of the dropdown menu
        style = ttk.Style()
        style.configure("TCombobox", selectbackground="#F77C3F", fieldbackground="#FFFFFF", font="TkDefaultFont 12")

        # Create the dropdown menu
        options = [f"Tram{i:02d}" for i in range(1, 46)]
        selected_option = StringVar(tram_dropdown)
        selected_option.set(options[0])  # Set the initial selected option

        drop_down_menu = OptionMenu(tram_dropdown, selected_option, *options)
        drop_down_menu.pack(pady=10)
        label_station = Label(tram_dropdown, text="Station: Technopark", font="TkDefaultFont 20 bold",
                            fg="#F77C3F", bg="#F2F2F2")
        label_station.pack(pady=10)
        
        # Create the 'Continuer' button with black text and a dark blue background
        continue_button = Button(tram_dropdown, text="استمر", fg="black", bg="dark blue", command=welcome_ar)
        continue_button.pack(pady=10)  # Add the button to the window with some vertical padding

        tram_dropdown.mainloop()

    def english_button():
        global selected_option
        global Tram
        global current_language
        current_language = "English"
        tram_dropdown = Toplevel(Languages)
        tram_dropdown.title("TramDropdown")
        tram_dropdown.geometry("1920x1080")

        # Configure the style and aesthetics of the TramDropdown window
        tram_dropdown.configure(bg="#F2F2F2")

        # Create the label in heading style
        label_heading = Label(tram_dropdown, text="Which tram is the subject of your complaint?", font="TkDefaultFont 24 bold",
                            fg="#F77C3F", bg="#F2F2F2")
        label_heading.pack(pady=10)

        # Customize the style of the dropdown menu
        style = ttk.Style()
        style.configure("TCombobox", selectbackground="#F77C3F", fieldbackground="#FFFFFF", font="TkDefaultFont 12")

        # Create the dropdown menu
        options = [f"Tram{i:02d}" for i in range(1, 46)]
        selected_option = StringVar(tram_dropdown)
        selected_option.set(options[0])  # Set the initial selected option

        drop_down_menu = OptionMenu(tram_dropdown, selected_option, *options)
        drop_down_menu.pack(pady=10)
        label_station = Label(tram_dropdown, text="Station: Technopark", font="TkDefaultFont 20 bold",
                            fg="#F77C3F", bg="#F2F2F2")
        label_station.pack(pady=10)
        # Create the 'Continuer' button with black text and a dark blue background
        continue_button = Button(tram_dropdown, text="Continue", fg="black", bg="dark blue", command=welcome_en)
        continue_button.pack(pady=10)  # Add the button to the window with some vertical padding

        tram_dropdown.mainloop()

    try:
        Welcome.destroy()
    except:
        pass
    try:
        FeedbackTrail.destroy()
    except:
        pass
    Languages = Tk()
    Languages.geometry("1920x1080")
    Languages.configure(background = "#A1B2C3")
    francais = Button(Languages, width = 10, bg = "#416FEC", text = "Francais", font ="haha 24 bold", relief= RAISED, bd = 5, command = francais_button)
    arabic = Button(Languages, width = 10, bg = "#416FEC", text = "اَلْعَرَبِيَّةُ", font ="haha 24 bold", relief= RAISED, bd = 5, command = arabic_button)
    english = Button(Languages, width = 10, bg = "#416FEC", text = "English", font ="haha 24 bold", relief= RAISED, bd = 5, command = english_button)
    
    francais.place(relx = 0.5, rely = 0.25, anchor = CENTER)
    arabic.place(relx = 0.5, rely = 0.50, anchor = CENTER)
    english.place(relx = 0.5, rely = 0.75, anchor = CENTER)
    Languages.mainloop()

FeedbackTrail = Tk()

FeedbackTrail.geometry("1920x1080")
FeedbackTrail.configure(background = "#A1B2C3")

def point_update():
    global time, loading_dots, loadingButton_hidden
    if time <= 1000:
        if loadingButton_hidden.cget("text") != "loading...":
            loading_dots += "."
            time += 500
        else:
            loading_dots = "loading."
            time += 500
    else:
        languages()
        return
    loadingButton_hidden.configure(text = loading_dots)        
    FeedbackTrail.after(500, point_update)

FeedbackTrailLabel = Label(FeedbackTrail, text = "FeedbackTrail", font = "Roboto 28 bold", fg= "#F77C3F", bg = "#A1B2C3")
loading_dots = "loading"
loadingButton_hidden = Button(FeedbackTrail, text = loading_dots, font = "TkDefaultFont 14 bold", fg = "#F77C3F", bg = "#A1B2C3", command= point_update, bd = 0)
time = 0

FeedbackTrailLabel.place(relx = 0.5, rely = 0.5, anchor = CENTER)
loadingButton_hidden.place(relx = 0.5, rely = 0.8, anchor = CENTER)
loadingButton_hidden.invoke()


FeedbackTrail.mainloop()
