import tkinter
from tkinter import filedialog
import sys
import cv2 as cv
import numpy as np
from PIL import Image
from PIL import ImageTk
from tkinter import messagebox
import image_processing as ip
from ImageConverter import ImageConverter

#Graphic User Interface
class MyTkinter():

    def __init__(self):
        self.window = tkinter.Tk()

        self.img_source = 0 #실제, 소스, 타겟 이미지
        self.img_target = 0

        self.img_sourceTK = 0 #렌더링 
        self.img_targetTK = 0

        self.ip = 0 #이미지 처리 객체
        self.cam_update_id = 0 #캠을 관리하는 id

        self.selected_option = tkinter.IntVar(value=0) #라디오 버튼

        self.classNum=0

        self.imgGroupList = []


        
    def initialize(self):

        self.window.title("AI based Computer Vision Class")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_width = 500
        window_height = 500
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2

        self.window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}") #"500x500+200+200" #500x500 프레임웍의 크기 @ 200, 200 위치
        self.window.resizable(True, True) #사이즈를 조정 가능하도록 허용

        self.frameLeft = self.createFrame(self.window, "left")
        self.frameCenter = self.createFrame(self.window, "left")
        self.frameRight = self.createFrame(self.window, "left")
        self.frameRight2 = self.createFrame(self.window, "left")
        
        self.b1 = self.createButtonGrid(self.frameLeft, "image open", 0, 0)
        self.b2 = self.createButtonGrid(self.frameLeft, "apply", 0, 1)

        self.b3 = self.createButtonGrid(self.frameLeft, "thresholding", 1, 0)
        self.b6 = self.createButtonGrid(self.frameLeft, "circle detection", 1, 1)

        self.b4 = self.createButtonGrid(self.frameLeft, "web cam mode", 2, 0)
        self.b5 = self.createButtonGrid(self.frameLeft, "close cam", 2, 1)   

        self.b7 = self.createButtonGrid(self.frameLeft, "capture", 3, 0)
        self.b8 = self.createButtonGrid(self.frameLeft, "new class", 3, 1)

        self.l1 = self.createLabel(self.frameCenter)
        self.l2 = self.createLabel(self.frameRight)

        self.b1.config(command=self.imgRead)
        self.b2.config(command=self.apply)
        self.b3.config(command=self.thresholding)
        self.b4.config(command=self.getCam)
        self.b5.config(command=self.stopCam)
        self.b6.config(command=self.circleDetection)

        self.b7.config(command=self.capture)
        self.b8.config(command=self.newClass)




    def selectionRadio(self):
        return self.selected_option.get()

    def createRadio(self, window, name, val, r, c):
        radio = tkinter.Radiobutton(window, text=name, variable=self.selected_option, value=val, command=self.selectionRadio)
        radio.grid(row = r, column = c)
        return radio
        
    def createFrame(self, window, pos, rel = "solid", border=2):
        frame = tkinter.Frame(window, relief=rel, bd=border)
        frame.pack(side=pos, fill="both", expand=True)
        return frame
    
    def createLabel(self, window):
        label = tkinter.Label(window)
        label.pack(expand=True)
        #
        return label
    
    
    def createLabelGrid(self, window, r, c):
        label = tkinter.Label(window)
        label.grid(row = r, column = c, padx=2, pady=2)
         #side="top"
        return label
        
    def createButtonPlace(self, window, name, px=0, py=0, w=30, h=30):
        button = tkinter.Button(window, text = name)
        button.place(x=px, y=py, width=w, height=h)  
        return button
    
    def createButtonGrid(self, window, name, r, c):
        button = tkinter.Button(window, text = name)
        button.grid(row = r, column = c)
        return button

    def buttonEvent(self, button, event):
        button.config(command=event)


    def newClass(self):
        self.createRadio(self.frameLeft, "class " + str(self.classNum), self.classNum, 4 + self.classNum, 0)
        self.imgGroupList.append([])
        self.classNum += 1 

    def showThumbImage(self, imgArr):

        columns = 5  # 한 줄에 4개의 버튼
        self.thumb_images = []  # 클래스의 속성으로 저장

        for i in range(len(imgArr)):
            row = i // columns
            col = i % columns
            label = self.createLabelGrid(self.frameRight2, row, col)
            resized_img = cv.resize(imgArr[i], (50, 50))
            photo = ImageConverter.toPhotoImage(resized_img)
            self.thumb_images.append(photo)  # 참조 유지
            label.config(image=photo)


    def capture(self):

        self.imgGroupList[self.selectionRadio()].append(self.img_target)
        for i in range(len(self.imgGroupList)):# print(len(self.imgGroupList))
            print(i, len(self.imgGroupList[i]))

        self.showThumbImage(self.imgGroupList[self.selectionRadio()])



    def getCam(self):
        cap = cv.VideoCapture(0) #, cv.CAP_DSHOW

        if not cap.isOpened():
            messagebox.showinfo("Info", "fail to open camera")
            return
        
        def update_frame():
            ret, img = cap.read()
            if ret:
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)  
                # OpenCV는 BGR, tkinter는 RGB를 사용하므로 변환 필요

                self.window.geometry(f"{int(img.shape[1]*2.5)}x{img.shape[0]}")

                self.img_target = img #self.img_source.copy()
                self.img_source = ImageConverter.toPIL(self.img_target)#Image.fromarray(img)
                self.img_sourceTK = ImageConverter.toPhotoImage(self.img_source)#ImageTk.PhotoImage(image=self.img_source)

                self.l1.config(image=self.img_sourceTK)

            # 10ms 후에 다시 프레임 업데이트 (이렇게 하면 tkinter의 이벤트 루프가 멈추지 않음)
            self.cam_update_id = self.window.after(10, update_frame)

        update_frame()


    def stopCam(self):
        if self.cam_update_id is not None:
            self.window.after_cancel(self.cam_update_id)  # after 호출 취소
            self.cam_update_id = None  # ID 초기화

        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
    def imgRead(self):

        file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("img files", "*.jpg"), ("All files", "*.*")])
        img = cv.imread(file_path)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.img_source = img
        print(img.shape)

        self.window.geometry(str(int(img.shape[1]*2.5)) + "x"+ str(int(img.shape[0])) +"+200+200")

        self.img_source = ImageConverter.toPIL(self.img_source) #Image.fromarray(self.img_source)
        self.img_target = self.img_source.copy()
        self.img_sourceTK = ImageConverter.toPhotoImage(self.img_source) #ImageTk.PhotoImage(image=self.img_source)
        self.l1.config(image = self.img_sourceTK)

        self.ip = ip.ImageProcessing(np.array(self.img_source))

    def thresholding(self):
        img = self.ip.sourceImg
        gray_img = self.ip.toGrayScale(img)
        thresholded = self.ip.thresholding(gray_img)
        self.ip.targetImg = thresholded
        self.img_target = self.ip.targetImg #self.ip.cvtTarget2PIL()
        
        messagebox.showinfo("Info", "processing done")
        
    def circleDetection(self):
        img = self.ip.sourceImg
        gray_img = self.ip.toGrayScale(img)
        self.ip.circleDetection(gray_img)
        self.img_target = self.ip.targetImg
        messagebox.showinfo("Info", "Circle Detection is done")


    def apply(self):
        # self.img_target = Image.fromarray(self.img_target)
        # self.img_targetTK = ImageTk.PhotoImage(image=self.img_target)
        # self.l2.config(image = self.img_targetTK)

        self.img_target = ImageConverter.toPIL(self.img_target)
        self.img_targetTK = ImageConverter.toPhotoImage(self.img_target)
        self.l2.config(image = self.img_targetTK)


    def render(self):
        self.window.mainloop()

tk = MyTkinter()
tk.initialize()

tk.render()


        
