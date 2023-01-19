from tkinter import *
from tkinter import filedialog
import animals
import live_tracking
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import cm
import os

'''
This file contains the Graphic-User Interface developed to perform animal
tracking on video.

This video may be either a live video feed or a previously recorded video.
Once the tracking process is finished, it is possible to open the trajectory
file and plot the data. The left plot is the time evolution of the trajectory.
The right plot is a 2D histogram that shows the number of data points in each
xy coordinate combination.

IMPORTANT: It is important to point out that either form of video must show
only the region where the animal is allowed to move. Walls, the floor or any
object that is not related to the experiment must not be on video. The 
boundaries of the video feed must be the boundaries of the area the animal
is allowed to move in.

Also, there are three quantities that can be computed: the animal's total
displacement, the amount of time it spent inside the squared/rectangular 
region bounded by x1,x2,y1 and y2 and the amount of time spent by the animal
outside a region of the same kind.

These last two regions might be different, i.e., the user may want to compute
the time spent by the animal in the center of a box and on its borders without
considering the borders to be the space that is not considered the center.
However, if the user actually wants to compute the time spent inside and 
outside the same region, the regions are the same and the arguments for both
functions are equal.

The arguments x1, x2, y1 and y2 must be floats. To get these values, use
a ruler or a similar object to measure the xy coordinates of each corner that
delimits the squared/rectangular region you are interested in. The x1 and y1
coordinates are the coordinates of the corner that is closest to the origin
placed on the top left corner of the screen. The x2 and y2 coordinates are
mapped to the region's corner that is diagonal to x1 and y1 and,
therefore, they describe the region's corner that is further away from the origin.

To perform the tracking on a live video feed, the user should use the
`Cam Test` feature by filling the input field to the right of the 
corresponding button with integer values starting from zero. To begin,
insert the number zero and press the `Cam Test` button. If a live video feed
pops up on the screen, the number zero is the `cam code` that maps the
tracking algorithm to your camera. To close the window showing the
live video, press `q` on the keyboard. However, if the live video does not
pop up, it means the user should try another integer such as the number one.
This is quite useful if the user has more than one camera and needs to map
the tracking algorithm to a specific video source.

HOW TO TRACK THE ANIMAL: 

To actually track the object of interest and extract its xy coordinates,
the user must fill the following input fields where the arguments must
be separated by commas:

  Insert live/rec, cam code(int)/video path, file name:
    live = track on live video feed
    rec = track on previously recorded video
    cam code = the code of the camera that will be used to perform live tracking
    video path = the full path of the previously recorded video
    file name = the name of the .txt file where the xy coordinates will be saved
        + the name of the .mp4 video where the tracking process will be stored
        .... if a full path is provided, both the txt and mp4 files will
             be saved in that path
      
  Insert object's width,height: (must be provided wether tracking live or on video)
    width = the largest measurement of the animal as float in centimeters
    height = the other measurement as float in centimeters
    .... the unit of measurement provided by the user determines the
         unit the xy data stored will be in

Once these steps are finished, the `Track!` button must be pressed to track!

HOW TO COMPUTE THE FEATURES OF INTEREST: 

First, open the .txt file by clicking the `Open File` button, find
the corresponding file and open it as usual.
To compute the Displacement, Time on site (the time spent inside
the squared/rectangular region) and Time outside site (the time 
spent outside the squared/rectangular region), the user must
check the corresponding boxes to the left of the calculation of
interest. It is possible to compute all features at once or separately.

To compute the Displacement, only check its box and hit `Compute`.
To compute the Time on site/outside site or both, fill the
corresponding input fields with the proper information, check the boxes
and hit `Compute`.

note: The order of the results will always be (Displacement, Time on site,
Time ouside site), no matter in what order the user checked the boxes. 

To CLEAR the numerical results, press the `Clear` button. Also, if the user
checked one box, computed its feature and then decided to compute another,
press the `Clear` button select only the feature to be computed.
'''




print("Tcl Version: {}".format(Tcl().eval('info patchlevel')))
class trajpy_animals_gui:
    
    def __init__(self, master):
        self.app = master
        self.init_window()
        self.app.resizable(False, False)

        self.title_label = Label(self.app, text="OnTrack",font=("Arial Bold", 35)) #title label
        self.version_label = Label(self.app, text="Object Tracking", font=("Arial Bold", 8)) #version label
        self.test_label = Label(self.app,text='Insert 0,1,...',font=('Helvetica 12 bold')) #test label
        self.first_label = Label(self.app,text='Insert live/rec, cam code(int)/video path, file name',font=('Helvetica 16'))# first label
        self.second_label = Label(self.app,text="Insert object's width,height (in cm)",font=('Helvetica 16'))#second label
        self.third_label = Label(self.app,text="Insert site corners for t inside(x1,x2,y1,y2)",font=('Helvetica 16'))#third label
        self.fourth_label = Label(self.app,text="Insert site corners for t ouside(x1,x2,y1,y2)",font=('Helvetica 16'))#fourth label
        self.results = []


        self.test_entry = Entry(self.app,width=10,font=('Arial',12)) #test_entry
        #self.test_entry.insert(0, "Insert 0,1,...")
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.file_entry = Entry(self.app,width=63,font=('Arial',12)) #file entry
        #self.file_entry.insert(0,"Insert live/rec, cam code(int)/video path, file name")
        self.number_entry = Entry(self.app,width=63,font=('Arial',12)) #number entry
        #self.number_entry.insert(0,"Insert object's width,height")
        self.center_entry = Entry(self.app,width=63,font=('Arial',12)) #center_entry
        #self.center_entry.insert(0,"Insert site corners for t inside(x1,x2,y1,y2)")
        self.edges_entry = Entry(self.app,width=63,font=('Arial',12)) #edges_entry
        #self.edges_entry.insert(0,"Insert site corners for t ouside(x1,x2,y1,y2)")


        self.track_button = Button(self.app,text='Track!',command=self.track_function,font=('Arial',20)) #track button
        self.test_button = Button(self.app,text='Cam Test',command=self.test_function,font=('Arial',20)) #test button
        self.open_button = Button(self.app,text='Open File',command=self.open_function,font=('Arial',20)) #open button
        self.compute_button = Button(self.app,text='Compute',command=self.compute_selected,font=('Arial',20)) #compute button
        self.clear_button = Button(self.app,text='Clear',command=self.clear_function,font=('Arial',20)) #clear button
        self.plot_button = Button(self.app,text='Plot',command=self.plot_function,font=('Arial',20)) #plot button
        self.var1 = StringVar()
        self.var2 = StringVar()
        self.var3 = StringVar()
        self.c1_button = Checkbutton(self.app,text='Displacement',variable=self.var1,onvalue='On',offvalue='Off',command=self.add_var1,font=('Arial',16))
        self.c1_button.deselect()
        self.c2_button = Checkbutton(self.app,text='Time on site',variable=self.var2,onvalue='On',offvalue='Off',command=self.add_var2,font=('Arial',16))
        self.c2_button.deselect()
        self.c3_button = Checkbutton(self.app,text='Time ouside site',variable=self.var3,onvalue='On',offvalue='Off',command=self.add_var3,font=('Arial',16))
        self.c3_button.deselect()

        self.features = []
        
        
        self.placement()


    def init_window(self):
        self.app.title('TrajPy Animals GUI')
        self.app.geometry('600x500')

    def placement(self):
        self.title_label.place(x=230,y=0)
        self.version_label.place(x=247,y=50)
        self.test_label.place(x=295,y=65)
        self.first_label.place(x=12,y=120)
        self.second_label.place(x=12,y=180)
        self.third_label.place(x=12,y=240)
        self.fourth_label.place(x=12,y=300)

        self.track_button.place(x=10,y=70)
        self.test_button.place(x=150,y=70)
        self.open_button.place(x=400,y=70)
        self.compute_button.place(x=20,y=390)
        self.clear_button.place(x=220,y=390)
        self.plot_button.place(x=430,y=390)
        self.c1_button.place(x=10,y=360)
        self.c2_button.place(x=200,y=360)
        self.c3_button.place(x=350,y=360)
        self.test_entry.place(x=295,y=85)
        self.file_entry.place(x=10,y=150)
        self.number_entry.place(x=10,y=210)
        self.center_entry.place(x=10,y=270)
        self.edges_entry.place(x=10,y=330)

    def add_var1(self):
        if self.var1.get() == 'On':
            self.features.append('Displacement')
        elif self.var1.get() == 'Off':
            self.features.remove('Displacement')

    def add_var2(self):
        if self.var2.get() == 'On':
            self.features.append('Center')
        elif self.var2.get() == 'Off':
            self.features.remove('Center')

    def add_var3(self):
        if self.var3.get() == 'On':
            self.features.append('Edges')
        elif self.var3.get() == 'Off':
            self.features.remove('Edges')

    def track_function(self):
        number_variables = self.number_entry.get().split(',')
        file_variables = self.file_entry.get().split(',')
        if file_variables[0] == 'live':
            live_tracking.capture(str(file_variables[0]),int(file_variables[1]),file_variables[2],float(number_variables[0]),float(number_variables[1]))
        elif file_variables[0] == 'rec':
            live_tracking.capture(str(file_variables[0]),str(file_variables[1]),file_variables[2],float(number_variables[0]),float(number_variables[1]))

    def test_function(self):
        import cv2
        test_variables = self.test_entry.get()
        cap = cv2.VideoCapture(int(test_variables))
        while(True):
            ret, frame = cap.read()
            if not ret:
                break
            stop_text = 'Press "q" to stop'
            cv2.putText(frame,stop_text,(50,50),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            cv2.line(frame,(0,0),(511,0),(255,0,0),5)
            cv2.putText(frame,'X',(250,25),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            cv2.line(frame,(0,0),(0,511),(255,0,0),5)
            cv2.putText(frame,'Y',(20,250),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def open_function(self):
        self.filename = filedialog.askopenfilename(parent=self.app,initialdir=self.path,
        title='Please select a file',filetypes=[('txt files','.txt')])

    def compute_selected(self):
        if "Displacement" in self.features:
            self.results.append(animals.displacement(self.filename) + 'cm')
        if 'Center' in self.features:
            center_variables = self.center_entry.get().split(',')
            self.results.append(animals.time_center(float(center_variables[0]),float(center_variables[1]),float(center_variables[2])
            ,float(center_variables[3]),self.filename) + 's')
        if 'Edges' in self.features:
            edges_variables = self.edges_entry.get().split(',')
            self.results.append(animals.time_edges(float(edges_variables[0]),float(edges_variables[1]),float(edges_variables[2])
            ,float(edges_variables[3]),self.filename) + 's')
        self.label1 = Label(self.app,text=', '.join(self.results),font=('Helvetica 20'),background='white')

        self.label1.place(x=12,y=450)        

    def clear_function(self):
        self.results.clear()
        self.label1.destroy()

    def plot_function(self):
        data = np.loadtxt(self.filename,delimiter=',')
        x = data[:,1]
        y = data[:,2]
        time = data[:,0]/60.0
        plt.figure(dpi=150)
        plt.subplot(121)
        points = np.array([x, y]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-2],points[1:-1], points[2:]], axis=1)
        lc = LineCollection(segments, cmap=cm.viridis, linewidth=3)
        lc.set_array(time)
        plt.gca().add_collection(lc)
        plt.gca().autoscale()
        cbar = plt.colorbar(lc,orientation="horizontal")
        cbar.set_label(r'$t~$[min]',fontsize=12)
        plt.xlabel(r'$x~$[cm',fontsize=12)
        plt.ylabel(r'$y~$[cm]',fontsize=12)
        

        plt.subplot(122)
        plt.hist2d(x, y, bins=25,cmap='Blues')
        plt.xlabel(r'$x~$[cm]',fontsize=12)
        plt.ylabel(r'$y~$[cm]',fontsize=12)
        cb = plt.colorbar(orientation="horizontal")
        cb.set_label('Number of occurrences')
        plt.tight_layout()
        plt.show()
    










if __name__ == '__main__':
    root = Tk()
    tj_AGui = trajpy_animals_gui(root)
    root.mainloop()