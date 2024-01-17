import typing
from PyQt5 import QtCore
from qtpy.QtWidgets import QWidget, QTabWidget, QGridLayout, QStyle, QTableWidget, QTableWidgetItem, QTextEdit, QPushButton, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QScrollArea, QComboBox, QFileDialog, QSpacerItem, QFrame, QGroupBox, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy, QWidget
from PyQt5.QtGui import QIcon, QStandardItem
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from magicgui import magicgui
import pickle
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import copy


from skimage.io.collection import alphanumeric_key
from skimage.io import imread
import numpy as np
from dask import delayed
import dask.array as da
from dask_image.imread import imread
import tqdm
from glob import glob
from skimage.util import map_array
import pandas as pd
import trackpy as tp
import threading
import random



class SuperViewer(QWidget):
    def __init__(self,viewer):
        super().__init__()

        ### Import variables

        self.viewer = viewer                                            #Napari Viewer
        self.fov = 0                                                    #Set FOV to 0 as a base

        self.layout = QVBoxLayout()                                     #Create Layout for class

        self.title = QLabel('Superviewer')                              #Create title for widget
        self.title.setStyleSheet("font-size: 20pt;")                    #Set title size
        self.title.setAlignment(Qt.AlignCenter)                         #Aligne title

        ''' Settings '''                                                #Settings to load experiments/fovs

        self.path_edit = QLineEdit()                                #Edit line that initially shows the preentered path
        self.path_button = QPushButton('Set path')                      #Button to change path
        self.path_button.clicked.connect(self.set_max_fov)              #Connect button to function to set new path
        self.path_edit.textChanged.connect(self.update_update_label)

        self.directory_button = QPushButton('Choose directory')         #Button to choose directory
        self.directory_button.clicked.connect(self.choose_directory)    #Connect button to function

        self.recent_combobox = QComboBox()
        self.recent_combobox.currentIndexChanged.connect(self.set_path)

        self.fov_choice_combox = QComboBox()                            #SpinBox to choose between fovs
        self.fov_choice_combox.addItem('0')                             #Set the minimum value to 0 as normal    
        self.fov_choice_combox.currentIndexChanged.connect(self.get_fov)        #Connect uppon change of value to set fov

        self.load_new_fov = QPushButton('Load FOV')                     #Button to calculate Tracks and process Images
        self.load_new_fov.clicked.connect(self.load_fov)                #Conenct button to function

        self.exp_info = QLineEdit()
        self.exp_info.setPlaceholderText('Add Experiment comment')
        self.exp_info_button = QPushButton('Edit')
        self.exp_info_button.clicked.connect(self.exp_info_edit)

        self.fov_info = QLineEdit()
        self.fov_info.setPlaceholderText('Add FOV comment')
        self.fov_info_button = QPushButton('Edit')
        self.fov_info_button.clicked.connect(self.fov_info_edit)

        self.fav_exp_button = QPushButton('Exp' + " \u2606 ")
        self.fav_exp_button.clicked.connect(self.favorite_exp_listing)
        self.fav_fov_button = QPushButton('FOV' + " \u2606 ")
        self.fav_fov_button.clicked.connect(self.favorite_fov_listing)


        self.update_label = QLabel('Update')                            #Label to display updates


        ''' Visulisation '''                                            #Code for whole visulatisation steps of graphs

        self.figure_layout = QGridLayout()                              #Layout for graphs
        
        self.to_plot_box = QComboBox()                                  #ComboBox to choose which value is plotted              
        
        self.to_plot_button = QPushButton('Define')                     #Button to define the to_plot ComboBox value
        self.to_plot_button.clicked.connect(self.define_to_plot)        #Connect button to function

        self.stimulation_edit = QLineEdit()                             #Edit to read
        self.stimulation_edit.setPlaceholderText('Enter Numbers separated by a "," for stim lines') #Stim frames lineedit
        self.set_stimulation_button = QPushButton('Set Stimulation')    #Button to set stimulation
        self.set_stimulation_button.clicked.connect(self.set_stimulation)   #Connect button to function

        self.plot_button = QPushButton('Plot')                          #Button to plot graphs
        self.plot_button.clicked.connect(self.plot)                     #Connect button to function

        self.erase_plots = QPushButton('Erase Plots')                   #Button to erase all graphs
        self.erase_plots.clicked.connect(self.erase)                    #Connect button to function


        self.information_label = QLabel()

        self.scroll_area = QScrollArea()                                #Scroll area for graphs
        self.scroll_area.setWidgetResizable(True)                       #Set size alterations true
        self.scroll_area.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)   #Set policy for resizing

        self.scroll_widget = QWidget()                                  #Create widget for graphs
        self.scroll_widget.setLayout(self.figure_layout)                #Add widget to layout

        self.scroll_area.setWidget(self.scroll_widget)                  #Set widget to scroll area



        ''' Layout '''                                                  #Layout section

        self.layout.addWidget(self.title)
        
        self.settings_group_box = QGroupBox('Settings')                 #Create groupbox for settings
        self.settings_layout = QGridLayout()                            #Set layout for groupbox

        self.settings_layout.addWidget(self.path_edit,0,0,1,1)          #Add widgets to layout
        self.settings_layout.addWidget(self.path_button,0,1,1,1)
        self.settings_layout.addWidget(self.recent_combobox,1,0,1,1)        
        self.settings_layout.addWidget(self.directory_button,1,1,1,1)
        self.settings_layout.addWidget(self.exp_info,2,0,1,1)
        self.settings_layout.addWidget(self.exp_info_button,2,1,1,1)
        self.settings_layout.addWidget(self.fov_choice_combox,3,0,1,1)
        self.settings_layout.addWidget(self.load_new_fov,3,1,1,1)
        self.settings_layout.addWidget(self.fov_info,4,0,1,1)
        self.settings_layout.addWidget(self.fov_info_button,4,1,1,1)
        self.settings_layout.addWidget(self.fav_fov_button,5,0,1,1)
        self.settings_layout.addWidget(self.fav_exp_button,5,1,1,1)

        self.settings_group_box.setLayout(self.settings_layout)         #Set layout to groupbox
        self.layout.addWidget(self.settings_group_box)                  #Add groupbox to layout




        self.update_group_box = QGroupBox('Information Display')             #Create groupbox for Update label
        self.update_layout = QGridLayout()                              #Set layout for groupbox

        self.update_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed), 0, 0, 1, 2)   #Add space
        self.update_layout.addWidget(self.update_label,1,0,1,2,Qt.AlignCenter)                                  #Add update widget
        self.update_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed), 2, 0, 1, 2)   #Add space

        self.update_group_box.setLayout(self.update_layout)             #Set layout to groupbox
        self.layout.addWidget(self.update_group_box)                    #Add groupbox to Layout




        self.graphs_group_box = QGroupBox('Graphs Settings')            #Create groupbox for Graphs settings
        self.graphs_layout = QGridLayout()                              #Set layout for groupbox

        self.graphs_layout.addWidget(self.to_plot_box,0,0,1,1)          #Add widgets to label
        self.graphs_layout.addWidget(self.to_plot_button,0,1,1,1)
        self.graphs_layout.addWidget(self.stimulation_edit,1,0,1,1)
        self.graphs_layout.addWidget(self.set_stimulation_button,1,1,1,1)
        self.graphs_layout.addWidget(self.plot_button,2,0,1,2)
        self.graphs_layout.addWidget(self.erase_plots,3,0,1,2)

        self.graphs_group_box.setLayout(self.graphs_layout)             #Set layout to groupbox
        self.layout.addWidget(self.graphs_group_box)                    #Add groupbox to layout




        self.plots_group_box = QGroupBox('Plots')                       #Create groupbox for Plots
        self.plots_group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)    #Set resizing policy
        self.plots_layout = QVBoxLayout()                               #Set layout for groupbox

        self.plots_layout.addWidget(self.information_label)
        self.plots_layout.addWidget(self.scroll_area)                   #Add Scroll widget

        self.plots_group_box.setLayout(self.plots_layout)               #Set layout to groupbox
        self.layout.addWidget(self.plots_group_box)                     #Add groupbox to Layout



        self.setLayout(self.layout)                                     #Set Layout




        ''' Create necessary files/folder at frst initiation '''


        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        folder_path = os.path.join(script_dir, 'files')
        graph_path = os.path.join(script_dir, 'graphs')
        file_path = os.path.join(folder_path, 'recent_files.pkl')
        img_path = os.path.join(folder_path, 'superviewer.png')
        var_path = os.path.join(folder_path, 'variable_file.csv')
        com_path = os.path.join(folder_path, 'comments_file.csv')
        fav_path = os.path.join(folder_path, 'favorites.csv')
        plt_path = os.path.join(folder_path, 'superplots')
        

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


        if not os.path.exists(file_path):
            with open(file_path, 'wb') as file:
                pickle.dump(['enter/any/folder/directory/'], file)
            
        if not os.path.exists(img_path):
            create_background(img_path)

        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        self.standard_graph_path = graph_path

        if not os.path.exists(plt_path):
            os.makedirs(plt_path)

        self.plt_path = plt_path

        if not os.path.exists(var_path):
            variables = {
                'variable':['tracks','intensity','duration','stim'],
                'available':[True,True,True,True],
                'pseudonym':['tracks','led_intensity','stim_duration','stim']
            }
            df_variables = pd.DataFrame(variables)
            df_variables['available'] = df_variables['available'].astype(bool)
            df_variables.to_csv(var_path, index=False)

        self.variable_file_path = var_path

        if not os.path.exists(fav_path):
            fav_cols = ['fav_type','path','fav']
            df_fav = pd.DataFrame(columns=fav_cols)
            df_fav.to_csv(fav_path,index=False)

        self.fav_path = fav_path


        if not os.path.exists(com_path):
            columns = ['experiment_dir','fov_num','comment']
            df_comments = pd.DataFrame(columns=columns)
            df_comments.to_csv(com_path,index=False)

        self.com_path = com_path
            


        image = Image.open(img_path)
        image_array = np.array(image)
        self.viewer.add_image(image_array, name='SuperViewer')

        ''' Definition of some variables '''

        self.star_icon = self.style().standardIcon(QStyle.SP_DialogYesButton)

        self.stim_list = []                                             #List of stimlation frames for lines


        self.to_plot_dic = {'ERK Ratio':'ratio_c_1',                    #Dictionary for 'to_plot'
                            'ERK Ratio normed':'ratio_norm_c_1'}
        
        self.to_plot_box.addItems(self.to_plot_dic.keys())              #Add to_plot dic to ComboBox


        self.set_widgets_status([self.erase_plots,self.plot_button,self.set_stimulation_button,self.to_plot_box,self.to_plot_button,self.stimulation_edit,self.fov_choice_combox,self.load_new_fov, self.fov_info, self.fov_info_button, self.exp_info, self.exp_info_button,self.fav_exp_button,self.fav_fov_button],
                                [False,False,False,False,False,False,False,False,False,False,False,False,False,False])
        
        self.update_recent_combobox()
    
    ''' Functions '''

    def set_widgets_status(self,widgets,status):
        
        for widget, stat in zip(widgets,status):
            if isinstance(widget,QLineEdit):
                widget.setReadOnly(not stat)

            elif isinstance(widget,QPushButton):
                widget.setEnabled(stat)

            elif isinstance(widget,QComboBox):
                widget.setEnabled(stat)


    def set_path(self):                                                 #Function to set path to Edit when recent combobox changed value
        current_path = self.recent_combobox.currentText()

        current_path = current_path.replace("\u2606", "").replace("\u2605", "").strip()

        self.path_edit.setText(current_path)

    def update_recent_combobox(self):                                   #Function to update combobox when added new recent
        self.recent_combobox.clear()

        with open('files/recent_files.pkl','rb') as file:
                self.recent_files = pickle.load(file)
        
        df_favs = pd.read_csv(self.fav_path)

        for url in self.recent_files:
            item = url
            if url in df_favs[df_favs['fav'] != '0']['fav'].values:
                item = " \u2605 " + url
            
            self.recent_combobox.addItem(item)

    

    def define_to_plot(self):                                           #Function to define to_plot from ComboBox
        key = self.to_plot_box.currentText()
        self.to_plot = self.to_plot_dic[key]
        self.set_widgets_status([self.plot_button],
                                [True])

    def update_label_text(self,text):                                   #Function to change update_label
        self.update_label.setText(text)

    def set_stimulation(self):                                          #Function to set stimulation_frame_list from Lineedit 
        stim_str = self.stimulation_edit.text()
        self.stim_list = [int(num) for num in stim_str.split(',')]
    
    def erase(self):                                                    #Function to erease plots
        for i in reversed(range(self.figure_layout.count())):
            item = self.figure_layout.itemAt(i)
            if item.widget() is not None:
                item.widget().setParent(None)
            elif item.layout() is not None:
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        


        self.saved_plots.clear()  # Clear the list of saved plots

        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        self.checkboxes.clear()     

        self.set_widgets_status([self.erase_plots],
                                [False])

    def choose_directory(self):                                         #Function to choose directory of data
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly

        directory_path = QFileDialog.getExistingDirectory(self, "Choose Directory", "", options=options)
        if directory_path != '':
            directory_path = directory_path + '/'
            self.path_edit.setText(directory_path)

    def update_update_label(self):
        self.update_label.setText('Set path to load Experiment FOVs')

    def favorite_exp_listing(self):
        url = self.project_path
        df_favs = pd.read_csv(self.fav_path)

        if url in df_favs[df_favs['fav'] != '0']['fav'].values:
            df_favs = df_favs[df_favs['fav'] != url]
            self.fav_exp_button.setText('Exp' + " \u2606 ")

        else:
            new_row = {'fav_type': 'exp', 'path':'', 'fav': url}  # Create a new row
            df_favs = pd.concat([df_favs, pd.DataFrame([new_row])], ignore_index=True)
            self.fav_exp_button.setText('Exp' + " \u2605 ")
        
        df_favs.to_csv(self.fav_path, index=False)
        self.update_recent_combobox()

    def favorite_fov_listing(self):
        url = self.project_path
        fov = self.fov
        df_favs = pd.read_csv(self.fav_path)

        df_favs_fov_only = df_favs[df_favs['path']==url]


        if str(fov) in df_favs_fov_only['fav'].values:
            df_favs = df_favs[~((df_favs['fav'] == str(fov)) & (df_favs['path'] == url))]
            self.fav_fov_button.setText('Fov' + " \u2606 ")
            
        else:
            new_row = {'fav_type': 'fov', 'path': url, 'fav': fov}  # Create a new row
            df_favs = pd.concat([df_favs, pd.DataFrame([new_row])], ignore_index=True)
            self.fav_fov_button.setText('Fov' + " \u2605 ")
        
        df_favs.to_csv(self.fav_path, index=False)
        self.update_fov_combox()

         
                
    def plot(self):
        self.checkboxes = []
        self.saved_plots = []
        self.plot_list = []
        self.plots = []
        nb_groups = 4
        selected_list = self.selected_list
        tracks = self.tracks
        try:
            to_plot = self.to_plot
        except Exception as e:
            self.update_label.setText(f'Define to plot:\n{e}')

        colors = ['#ffaaff','#55aaff','#ffaa7f','#55aa7f']

        for group in range(nb_groups+1):
            row = group*3

            figure, ax = plt.subplots(figsize=(5,3),dpi = 200)
            group_value  = selected_list[group]  

            if group < nb_groups:
                if not group_value:
                    continue

            if group == nb_groups:
                plt.title("Mean per group")
                plt.xlabel('ERK activity')

                for group in range(nb_groups):
                    selected_particles = selected_list[group]   
                    gp =tracks[tracks['particle'].isin(selected_particles)].groupby(['frame'])[to_plot].mean().plot(ax=ax,legend  = [], color = colors[group], alpha = 1,linewidth = 3)
                    if len(self.stim_list) != 0:
                        for frame in self.stim_list:
                            ax.axvline(frame, color='red', alpha=0.5)
                                
            elif group < nb_groups:
                plt.title(f'Group {group}')
                plt.xlabel('ERK activity')
                selected_particles = selected_list[group]

                try:
                    gp =tracks[tracks['particle'].isin(selected_particles)].groupby(['particle']).plot(x='frame',y=to_plot, ax=ax,legend  = [], color = colors[group], alpha = 0.5)
                except Exception as e:
                    self.update_label.setText(f'ERROR while selecting tracks for plot:\n{e}')
                if len(self.stim_list) != 0:
                    for frame in self.stim_list:
                        ax.axvline(frame, color='red', alpha=0.5)
            
            plot_widget = PlotWidget(figure, group)
            self.figure_layout.addWidget(plot_widget, row, 0, 3, 2)

            self.saved_plots.append(plot_widget)

            self.plot_list.append(figure)


        self.plot_directory_edit = QLineEdit(self.standard_graph_path)
        self.plot_directory_button = QPushButton('Choose directory')
        self.plot_directory_button.clicked.connect(self.choose_plot_directory)
        self.figure_layout.addWidget(self.plot_directory_edit,(nb_groups+1)*3,0,1,1)
        self.figure_layout.addWidget(self.plot_directory_button,(nb_groups+1)*3,1,1,1)
        
        save_button = QPushButton('Save Selected Plots', self)
        save_button.clicked.connect(self.save_selected_plots)
        self.figure_layout.addWidget(save_button,(nb_groups+1)*3+1,0,1,2)

        for f in self.plot_list:
            self.plots.append(copy.deepcopy(f))

        self.saveforplotwindow()
        self.set_widgets_status([self.erase_plots], [True])  
        

    def save_selected_plots(self):

        directory = self.plot_directory_edit.text()

        for plot_widget in self.saved_plots:  # Iterate over the list of plots to save
            checkbox_state = plot_widget.get_checkbox_state()


            if checkbox_state == False:
                continue

            figure = plot_widget.figure
            name = plot_widget.plot_name_edit.text()
            title = plot_widget.plot_title_edit.text()

            if not name:
                any_num = random.randint(1,150000)
                filename = f'plot_{any_num}.png'
            else:
                filename = f'{name}.png'


            figure.axes[0].set_title(f'{title}')  # Set the title
            figure.axes[0].set_xlabel('ERK ratio')  # Set the x-label

            figure.savefig(os.path.join(directory, filename))
            plt.close(figure)  # Close the figure to release resources

            plot_widget.set_checkbox_state(False)


    def choose_plot_directory(self):                                         #Function to choose directory of data
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly

        directory_path = QFileDialog.getExistingDirectory(self, "Choose Directory", "", options=options)
        if directory_path != '':
            directory_path = directory_path + '/'
            self.plot_directory_edit.setText(directory_path)
            self.standard_graph_path = directory_path


    def update_fov_combox(self):

        current_fov = self.fov
        self.fov_choice_combox.clear()

        max_fov = self.total_fovs(self.project_path)
        df_com = pd.read_csv(self.com_path)
        df_favs = pd.read_csv(self.fav_path)

        try:
            for i in range(max_fov):
        
                row = df_com.loc[(df_com['experiment_dir'] == self.project_path) & (df_com['fov_num'] == str(i))]
                if not row.empty:
                    comment = row['comment'].iloc[0]  # Get the first matching row

                    if pd.isna(comment):
                        comment = ''
                else:
                    comment = ''

                df_favs_filtered = df_favs[(df_favs['fav'] == str(i)) & (df_favs['path'] == self.project_path)]
                
                if not df_favs_filtered.empty:

                    fov_comment = f'\u2605 {i}: {comment}'
                else:

                    fov_comment = f'{i}: {comment}'  

                self.fov_choice_combox.addItem(fov_comment)
   
        except Exception as e:
            self.update_label.setText(f'ERROR while loading FOVS:\n {e}')
        
        self.fov_choice_combox.setCurrentIndex(current_fov)


    def set_max_fov(self):
                                             #Function to set fov count of experiment folder
        project_path = self.path_edit.text()
        self.project_path = project_path

        try:
            self.update_fov_combox()
        except Exception as e:
            self.update_label.setText(f'ERROR while updating fov choices:\n{e}')

        df_com = pd.read_csv(self.com_path)

        # Find the row directly without storing a boolean condition
        row = df_com.loc[(df_com['experiment_dir'] == self.project_path) & (df_com['fov_num'] == 'exp_description')]

        if not row.empty:

            try:
                exp_info_text = row['comment'].values[0]
                if pd.isna(exp_info_text):
                    exp_info_text = ''
                self.exp_info.setText(exp_info_text)
            except Exception as e:
                self.update_label.setText(f'ERROR while getting experiment comment from file:\n{e}')

        else:
 
            new_row = {
                'experiment_dir': self.project_path,
                'fov_num': 'exp_description',
                'comment': ''
            }
            try:
                df_com = pd.concat([df_com, pd.DataFrame([new_row])], ignore_index=True)
                df_com.to_csv(self.com_path, index=False)
                self.exp_info.clear()
            except Exception as e:
                self.update_label.setText(f'ERROR while modifying experiment comment:\n{e}')
        
        df_favs = pd.read_csv(self.fav_path)

        if project_path in df_favs[df_favs['fav'] != '0']['fav'].values:
            self.fav_exp_button.setText('Exp \u2605')
        else:
            self.fav_exp_button.setText('Exp \u2606')

        self.add_recent_project_path(project_path)
        self.update_recent_combobox()
        self.update_label.setText('Choose FOV and load image data')
        self.set_widgets_status([self.fov_choice_combox,self.load_new_fov,self.exp_info_button,self.fav_exp_button],
                                [True,True,True,True])


    def add_recent_project_path(self,file_path):
        try:
            with open('files/recent_files.pkl','rb') as file:
                self.recent_files = pickle.load(file)
        except FileNotFoundError as e:
            self.update_label.setText(f'ERROR while loading recent_files.pkl:\n{e}')
        
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0,file_path)
        self.recent_files = self.recent_files[:8]

        try:
            with open('files/recent_files.pkl', 'wb') as file:
                pickle.dump(self.recent_files, file)
        except FileNotFoundError as e:
            self.update_label.setText(f'ERROR while saving recent_files.pkl:\n{e}')

    
    def get_fov(self,value):                                            #Function to get fov from SpinBox
        self.fov = value

    def load_fov_data(self):                                            #Function to load stacks of data

        self.update_label.setText('Loading Image Stacks')
        
        project_path = self.project_path
        fov = self.fov
        
        stack_raw = tiff_to_lazy_da(project_path, "raw", fov)                   #The imaging data
        stack_light = tiff_to_lazy_da(project_path, "stim", fov)                #The optogenetic stimulation image
        stack_labels = tiff_to_lazy_da(project_path, "mask", fov)               #The labels
        # stack_light_mask = tiff_to_lazy_da(project_path, "light_mask", fov)     #The stimulation mask data

        stack_labels = np.array(stack_labels)
        #stack_light = np.array(stack_light)
        # stack_light_mask = np.array(stack_light_mask)

        return stack_raw, stack_light, stack_labels



    def load_tracks_data(self,var_data):                     #Function to get tracks and calculations
                                                
        self.update_label.setText('Loading Tracks Data')
        
        project_path = self.project_path
        fov = self.fov
        
        tracks_name = var_data['tracks']['name']

        pkl_path, latest_nr = latest_track(fov,project_path,tracks_name)

        
        tracks = pd.read_pickle(pkl_path)
        tracks = tp.filter_stubs(tracks=tracks,threshold=latest_nr)

        
        if var_data['intensity']['available'] or var_data['duration']['available']:

            # try:
            intensity, duration = int_dur_of_stim(tracks,var_data)

            if intensity == 0:
                int_text = 'No stimulation intensity detected'
            else:
                int_text = f'Stimulation intensity: {intensity}'

            if duration == 0:
                dur_text = 'No stimulation duration detected'
            else:
                dur_text = f'Stimulation Duration: {duration}'

            self.information_label.setText(f'Latest Track Nr is {latest_nr}\n{int_text}\n{dur_text}')
        
            # except Exception as e:
            #     self.update_label.setText(f'ERROR extracting stimulation information:\n{e}')
        
        lag_time = 10   # Over what time interval should the diplacement be calculated? 
        ##########################

        tracks = tracks.reset_index(drop =True)

        for particle in tracks['particle'].unique():

            temp = tracks[(tracks['particle']==particle)][['frame','x','y',]]
            temp.set_index('frame',drop=True)
            values = temp.values

            diffs = []

            start = int(lag_time/2)
            diffs = values[lag_time:]-values[:-lag_time] # time_diff, x_diff, y_diff

            frames = values[:,0]
            frames_with_values = frames[start:-start]
            displacement_x = diffs[:,1]
            displacement_y = diffs[:,2]
            displacement_xy = np.sqrt(np.square(displacement_x)+np.square(displacement_y))
            tracks.loc[(tracks['particle']==particle)&(tracks['frame'].isin(frames_with_values)),'displacement_xy'] = displacement_xy

        #shows the mean displacement of all particles over time
        #tracks.groupby(['frame']).mean()['displacement_xy'].plot()

        int_channels = [substring for substring in tracks.columns if 'intensity' in substring] 

        nb_channels = int(len(int_channels)/2)
        for c in range(nb_channels):
            c_ratio = 'ratio_c_'+str(c)
            c_ratio_norm = 'ratio_norm_c_'+str(c)
            c_nuc = int_channels[c]
            c_ring = int_channels[c+nb_channels]

            tracks[c_ratio] = tracks[c_ring]/tracks[c_nuc]

            grouped = tracks.groupby(['particle'])[c_ratio]
            for particle, group in grouped:
                tracks.loc[tracks['particle']==particle, [c_ratio_norm]] = (tracks[tracks['particle']==particle][c_ratio].values - np.nanmean(tracks[tracks['particle']==particle][c_ratio].values))/np.nanstd(tracks[tracks['particle']==particle][c_ratio].values)

        return tracks

    def get_vars(self,variable_df):

        variable_names = variable_df['variable'].unique()
        variable_dicts = {}

        for var_name in variable_names:
            var_available = variable_df[variable_df['variable'] == var_name]['available'].values[0]
            var_pseudonym = variable_df[variable_df['variable'] == var_name]['pseudonym'].values[0]

            variable_dict = {
                'available': var_available,
                'name': var_pseudonym
            }

            variable_dicts[var_name] = variable_dict
        
        return variable_dicts
                
    def load_fov(self):                                                 #Function that contains previous function to load all data

        self.update_label_text('Loading FOV Data')

        variable_df = pd.read_csv(self.variable_file_path)

        try:
            var_data = self.get_vars(variable_df)
        except Exception as e:
            self.update_label.setText(f'ERROR while loading variables:\n{e}')

        self.set_widgets_status([self.set_stimulation_button,self.stimulation_edit,self.to_plot_button,self.to_plot_box,self.plot_button],
                    [False,False,False,False,False])


        viewer = self.viewer

        viewer.layers.select_all()                                      #Delete all layers
        viewer.layers.remove_selected()
        nb_groups = 4
        nb_channels = 2

        try:
            stack_raw, stack_light, stack_labels = self.load_fov_data() #Get stacks
        except Exception as e:
            self.update_label.setText(f'ERROR while loading the stack_raw/stack_light/stack_labels:\n{e}')
        

        if var_data['tracks']['available']:     
            try:
   
                tracks = self.load_tracks_data(var_data)                            #Get tracks
                self.tracks = tracks

            except Exception as e:
                self.update_label.setText(f'ERROR while loading the tracks:\n{e}')

            try:
                stack_particles = labels_to_particles(stack_labels, tracks) #Get Particle tracks/stack
            except Exception as e:
                self.update_label.setText(f'ERROR while converting stack_labels with tracks to stack_particles:\n{e}')


            if var_data['stim']['available']:
                stim_column_name = var_data['stim']['name']
                stim_frame_list = stim_frames(tracks,stim_column_name)                           #Get unique stim frame list
                self.stimulation_edit.setText(', '.join(map(str, stim_frame_list))) #Set stim frame list to Lineedit
                self.set_stimulation()

        layers_c = []
        for channel in range(nb_channels):                              #Add layers for both channels
            stack_raw_layer_c = viewer.add_image(stack_raw[:,channel,:,:], rgb=False)
            stack_raw_layer_c.blending = 'translucent'
            stack_raw_layer_c.colormap = 'magma'
            stack_raw_layer_c.name = f'Image Channel {channel}'
            layers_c.append(stack_raw_layer_c)


        if var_data['tracks']['available']:  
            stack_particles_layer = viewer.add_labels(stack_particles[:,:,:],opacity =1)
            stack_particles_layer.contour = 2
            stack_particles_layer.name = 'Labels'

        light_mask_layer = viewer.add_image(stack_light, name='light_mask',opacity =1, gamma =1.75)
        light_mask_layer.blending = 'additive'
        light_mask_layer.contrast_limits = (113, 5956)
        light_mask_layer.gamma = 1.75

        point_layers = []
        selected_list = []

        hotkeys = ['e','d','r','f']
        colors = ['#ffaaff','#55aaff','#ffaa7f','#55aa7f']

        if var_data['tracks']['available']: 
            def display_selected(group):
                points = tracks[tracks['particle'].isin(selected_list[group])][['frame','x','y']]
                point_layers[group].data = points

            for group in range(nb_groups):
                layer = viewer.add_points(n_dimensional=3,ndim=3, face_color= colors[group],edge_color='black')
                layer.name = f"Group {group}"
                point_layers.append(layer)
                selected_list.append([])


                @viewer.bind_key(key = hotkeys[group],overwrite=True)
                def add_label_to_selection(viewer = viewer, group = group):
                    particle = stack_particles_layer.selected_label
                    selected = selected_list[group]
                    if particle in selected:
                        selected.remove(particle)
                    else:
                        selected.append(particle)
                    
                    display_selected(group)

            @viewer.bind_key(key = 'q',overwrite=True)
            def delete_all_layers(viewer = viewer):
                for group in range(nb_groups):
                    selected_list[group] = []
                    display_selected(group)

            @viewer.bind_key(key = 'a',overwrite=True)
            def choose_all_layers(viewer = viewer):
                label_list = selected_list[0]
                for label in range(stack_particles_layer.data.max() + 1):
                    if label not in label_list:
                        label_list.append(label)
                display_selected(0)

            #data = [ID, T, Y, X]
            data = tracks.reset_index()[['particle','frame','x','y']].values.astype(int)
            features = tracks.copy()
            features['displacement_xy'] = tracks['displacement_xy'].fillna(0)
            tracks_layer = viewer.add_tracks(data=data, features=features,colormap = 'plasma',color_by ='displacement_xy',blending='translucent')
            tracks_layer.name = 'Tracks'
            selected_list.append([])

            self.selected_list = selected_list

            self.set_widgets_status([self.set_stimulation_button,self.stimulation_edit,self.to_plot_button,self.to_plot_box],
                                [True,True,True,True])

            self.update_label.setText(f'Choose cell-tracks on "Labels layer" with "Pick Mode":\n{nb_groups} avaible groups. Groupkeys: {hotkeys}\nDelete all picked cells using "q"\nChoose all labels using "a".')

        else:
            self.update_label.setText(f'FOV loaded\nNo Plots available')


        df_com = pd.read_csv(self.com_path)
        row = df_com.loc[(df_com['experiment_dir'] == self.project_path) & (df_com['fov_num'] == str(self.fov))]

        self.fov_info.clear()
        if not row.empty:
            # Get the comment from the matching row

            comment = row['comment'].iloc[0]  # Get the first matching row

            if pd.isna(comment):
                comment = ''

            self.fov_info.setText(comment)

        else:

            new_row = {
                'experiment_dir' : self.project_path,
                'fov_num' : self.fov,
                'comment' : ''
            }
            df_com = pd.concat([df_com, pd.DataFrame([new_row])], ignore_index=True)
            df_com.to_csv(self.com_path, index=False)
            self.fov_info.clear()


        df_favs = pd.read_csv(self.fav_path)
        df_favs_filtered = df_favs[(df_favs['fav'] == str(self.fov)) & (df_favs['path'] == self.project_path)]

  
        if not df_favs_filtered.empty:

            self.fav_fov_button.setText('Fov \u2605')
        else:

            self.fav_fov_button.setText('Fov \u2606')

        self.set_widgets_status([self.fov_info_button,self.fav_fov_button],[True,True])


    def load_fov_threaded(self):                                        #Create threading for smoother napari running
        thread = threading.Thread(target=self.load_fov)
        thread.start()

    def total_fovs(self,project_path):                                           #Function to get total fovs of experiment
        # Get a list of all files in the "raw" folder
        folder_path = os.path.join(project_path, 'raw/')

        try:
            files = glob(os.path.join(folder_path, '*.tiff'))
        except Exception as e:
            self.update_label.setText(f'ERROR while loading raw data:\n{e}')

        # Extract FOV numbers from file names
        fov_numbers = set([int(os.path.basename(f).split('_')[0]) for f in files])
        # Count the number of unique FOVs
        num_fovs = len(fov_numbers)

        return num_fovs


    def fov_info_edit(self):

        self.set_widgets_status([self.fov_info],[True])
        self.fov_info_button.clicked.disconnect()
        self.fov_info_button.clicked.connect(self.fov_info_save)
        self.fov_info_button.setText('Save')


    def fov_info_save(self):

        comment = self.fov_info.text()
        df_com = pd.read_csv(self.com_path)
        df_com.loc[(df_com['experiment_dir'] == self.project_path) & (df_com['fov_num'] == str(self.fov)),'comment'] = comment
        df_com.to_csv(self.com_path, index=False)

        self.set_widgets_status([self.fov_info],[False])
        self.fov_info_button.clicked.disconnect()
        self.fov_info_button.clicked.connect(self.fov_info_edit)
        self.fov_info_button.setText('Edit')
        self.update_fov_combox()




    def exp_info_edit(self):
        self.set_widgets_status([self.exp_info],[True])
        self.exp_info_button.clicked.disconnect()
        self.exp_info_button.clicked.connect(self.exp_info_save)
        self.exp_info_button.setText('Save')

    def exp_info_save(self):
        comment = self.exp_info.text()
        df_com = pd.read_csv(self.com_path)
        df_com.loc[(df_com['experiment_dir'] == self.project_path) & (df_com['fov_num'] == 'exp_description'), 'comment'] = comment  
        df_com.to_csv(self.com_path, index=False)

        self.set_widgets_status([self.exp_info],[False])
        self.exp_info_button.clicked.disconnect()
        self.exp_info_button.clicked.connect(self.exp_info_edit) 
        self.exp_info_button.setText('Edit')

    def saveforplotwindow(self):
        file_list = os.listdir(self.plt_path)

        # Iterate over the files and delete each one
        for file_name in file_list:
            file_path = os.path.join(self.plt_path, file_name)
            os.remove(file_path)

        for i, fig in enumerate(self.plots):  
            fig.savefig(os.path.join(self.plt_path, f'super_plot_{i}'), dpi=400)












    




def tiff_to_lazy_da(path,folder,fov):
    '''Read in all tiff files form the same FOV in a folder and load them lazily with dask. '''
    file_name_pattern = str(fov).zfill(2)+"_*.tiff"
#     filenames = os.listdir(path + os.path.join(str(folder))
    filenames = sorted(glob(os.path.join(path,folder, file_name_pattern)), key=alphanumeric_key)
    # read the first file to get the shape and dtype
    # ASSUMES THAT ALL FILES SHARE THE SAME SHAPE and TYPE

    sample = imread(filenames[0])
    
    lazy_imread = delayed(imread)  # lazy reader
    lazy_arrays = [lazy_imread(fn) for fn in filenames]
    dask_arrays = [
        da.from_delayed(delayed_reader, shape=sample.shape, dtype=sample.dtype)
        for delayed_reader in lazy_arrays
    ]
    # Stack into one large dask.array
    stack = da.stack(dask_arrays, axis=0)
    stack = np.squeeze(stack)
    return stack

def labels_to_particles(labels_stack, tracks):
    '''Takes in a segmentation mask with labels and replaces them with track IDs that are consistent over time.'''
    # For every frame
    #labels_stack = np.array(labels_stack)
    particles_stack = np.zeros_like(labels_stack)
    for frame in tqdm.tqdm(range(labels_stack.shape[0])):
        #For every label
        labels_f = np.array(labels_stack[frame,:,:])
        tracks_f = tracks[(tracks['frame'] == frame)]
        #particle_f = np.zeros((1024,1024))
        from_label=tracks_f['label'].values
        to_particle=tracks_f['particle'].values
        particle_f = map_array(labels_f, from_label, to_particle, out=particles_stack[frame,:,:])
    #particles_stack
    return particles_stack



def latest_track(fov, project_path,tracks_name):                                    #Function to get highest track number file 
    # Get a list of all files in the ,directory
    folder_path = project_path + tracks_name +'/'
    files = glob(os.path.join(folder_path, f"{str(fov).zfill(2)}_*.pkl"))

    # Extract numbers from file names and sort them
    file_numbers = sorted([int(os.path.basename(f).split('_')[1].split('.')[0]) for f in files])

    # Get the path of the file with the highest number
    latest_file_path = os.path.join(folder_path, f"{str(fov).zfill(2)}_{str(file_numbers[-1]).zfill(5)}.pkl")
    latest_nr = file_numbers[-1]

    return latest_file_path, latest_nr



def stim_frames(tracks,stim_column_name):                                                #Function to get frames with stim==True
    frames_with_stim = tracks.groupby('frame')[stim_column_name].any()
    frames_with_stim_true = frames_with_stim[frames_with_stim].index.unique().tolist()

    return frames_with_stim_true


def int_dur_of_stim(tracks,var_data):

    int_name = var_data['intensity']['name']
    _int_ = var_data['intensity']['available']
    dur_name = var_data['duration']['name']
    _dur_ = var_data['duration']['available']
        
    intensity = 0
    duration = 0

    try:
        stim_true_rows = tracks[tracks['stim'] == True]
    except Exception as e:
        return intensity, duration

    if _int_:    
        intensity = stim_true_rows[int_name].iloc[0]
    if _dur_:
        duration = stim_true_rows[dur_name].iloc[0]

    return intensity, duration


def create_background(path):
    width, height = 1600, 1000
    background_color = (255, 255, 255)  # RGB for white
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Set font properties
    font_size_text1 = 200
    font_size_text2 = 60  # Smaller font size for text2
    font_color = (0, 0, 0)  # RGB for black
    # font_path = "C:/Users/joeld/OneDrive/Desktop/Dinge/Dokumente/Fonts/romanserif/RomanSerif.ttf"  # Replace with the path to your preferred font file
    font_names = [f.name for f in fm.fontManager.ttflist]
    
    font_name = font_names[43]

    # Load the selected font
    font_text1 = ImageFont.truetype(fm.findfont(fm.FontProperties(family=font_name)), font_size_text1)
    font_text2 = ImageFont.truetype(fm.findfont(fm.FontProperties(family=font_name)), font_size_text2)

    # If you don't have a custom font, you can use the default font
    # font = ImageFont.load_default()
    # font = ImageFont.truetype(font_path, font_size)

    # Calculate the position to center the text1
    text1 = "SUPERVIEWER"
    text2 = "by JF"

    text1_bbox = draw.textbbox((0, 0), text1, font=font_text1)

    # Calculate the position to center the text1
    x_position1 = (width - (text1_bbox[2] - text1_bbox[0])) // 2
    y_position1 = (height - (text1_bbox[3] - text1_bbox[1])) // 2 - 120

    # Draw the text1 on the image
    draw.text((x_position1, y_position1), text1, font=font_text1, fill=font_color)

    # Get the bounding box of the text2
    text2_bbox = draw.textbbox((0, 0), text2, font=font_text2)

    # Calculate the position to center the text2
    x_position2 = (width - (text2_bbox[2] - text2_bbox[0])) // 2 
    y_position2 = y_position1 + (text1_bbox[3] - text1_bbox[1]) + 80 # Adjust the vertical spacing

    # Draw the text2 on the image
    draw.text((x_position2, y_position2), text2, font=font_text2, fill=font_color)

    # Convert the PIL image to a NumPy array
    dpi = 5000
    image.save(path,dpi=(dpi, dpi))





class PlotWidget(QWidget):
    def __init__(self, figure, group, parent=None):
        super().__init__(parent)
        self.figure = figure
        self.group = group



        self.canvas = FigureCanvas(figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(750, 450)


        self.plot_name_edit = QLineEdit()
        self.plot_name_edit.setPlaceholderText('Enter File Name')
        

        self.plot_title_edit = QLineEdit()
        self.plot_title_edit.setPlaceholderText('Enter Title')
        

        self.checkbox = QCheckBox(f'Plot {group}', self)
        self.checkbox.stateChanged.connect(self.checkbox_changed)

        self.delete_button = QPushButton('X', self)
        self.delete_button.clicked.connect(self.delete_plot)


        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText('Alter displayed title')
        self.edit_title.textChanged.connect(self.alter_title)


        self.save_label = QLabel('Save plot options')


        self.layout = QVBoxLayout() 
        self.options_box = QGroupBox('Graphs Settings')      
        self.options_layout = QGridLayout(self)

        self.options_layout.addWidget(self.canvas,0,0,5,1)
        self.options_layout.addWidget(self.delete_button,0,1,1,2)
        self.options_layout.addWidget(self.edit_title,1,1,1,2)
        self.options_layout.addWidget(self.save_label,2,1,1,1)
        self.options_layout.addWidget(self.checkbox,2,2,1,1)
        self.options_layout.addWidget(self.plot_name_edit,3,1,1,2)
        self.options_layout.addWidget(self.plot_title_edit,4,1,1,2)

        
        self.options_box.setLayout(self.options_layout)             #Set layout to groupbox
        self.layout.addWidget(self.options_box)
        self.setLayout(self.layout)


    def delete_plot(self):
        self.setParent(None)

    def alter_title(self):
        new_title = self.edit_title.text()
        self.figure.axes[0].set_title(new_title)
        self.canvas.draw()  # Update the figureSuperviewer/superaddons/superaddon.py
    
    def checkbox_changed(self, state):
        self.save = state == Qt.Checked
        self.set_widgets_status([self.plot_name_edit,self.plot_title_edit],[True,True])

    def get_checkbox_state(self):
        state_info = self.checkbox.isChecked()
        return state_info
    
    def set_checkbox_state(self,state):
        self.checkbox.setChecked(state)
        if state == False:
            self.set_widgets_status([self.plot_name_edit,self.plot_title_edit],[False,False])
    
    def set_widgets_status(self,widgets,status):
        
        for widget, stat in zip(widgets,status):
            if isinstance(widget,QLineEdit):
                widget.setReadOnly(stat)

            elif isinstance(widget,QPushButton):
                widget.setEnabled(stat)

            elif isinstance(widget,QComboBox):
                widget.setEnabled(stat)




class VariableData(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.options_layout = QGridLayout()
        self.options_group_box = QGroupBox('Variable Settings')

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.variable_file_path = os.path.join(script_dir, 'files/variable_file.csv')

        variable_df = pd.read_csv(self.variable_file_path)

        self.cb_list = []
        self.edit_list = []
        self.standard_list = []
        self.var_list = []
        self.standard_button = []


        variables = [
            ('Tracks', 'tracks', 'Tracks available', 'Enter your correspondent Tracks', 'tracks'),
            ('Intensity', 'intensity', 'Intensity available', 'Enter your correspondent Intensity', 'led_intensity'),
            ('Duration', 'duration', 'Duration available', 'Enter your correspondent Duration', 'stim_duration'),
            ('Stim Frame Column', 'stim', 'Stim available', 'Enter your correspondent Stim Frame column', 'stim')
        ]

        for i, (label_text, var_name, cb_label_text, edit_placeholder, standard_text) in enumerate(variables):
            label = QLabel(label_text)
            checkbox = QCheckBox(cb_label_text)
            checkbox.stateChanged.connect(lambda _, var=var_name: self.checkbox_alter(var))
            

            bool_var = variable_df.loc[variable_df['variable'] == var_name, 'available'].iloc[0]

            if bool_var:
                checkbox.setChecked(True)

            edit = QLineEdit()
            edit.setPlaceholderText(edit_placeholder)
            standard = QLabel(standard_text)
            standard_button = QPushButton('Reset to standard:')
            standard_button.clicked.connect(lambda _, edit=edit, std=standard_text: self.set_standard(edit, std))

            self.var_list.append(var_name)
            self.cb_list.append(checkbox)
            self.edit_list.append(edit)
            self.standard_list.append(standard_text)
            self.standard_button.append(standard_button)


            self.options_layout.addWidget(label, i*2, 0)
            self.options_layout.addWidget(checkbox, i*2, 2)
            self.options_layout.addWidget(edit, i*2+1, 0, 1, 2)
            self.options_layout.addWidget(standard_button,i*2+1,2)
            self.options_layout.addWidget(standard, i*2+1, 3)

            num = i



        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_variables)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_variables)

        self.options_layout.addWidget(self.save_button,num*2+2,0,1,3)
        self.options_layout.addWidget(self.reset_button,num*2+2,3,1,1)


        self.options_group_box.setLayout(self.options_layout)             #Set layout to groupbox
        self.layout.addWidget(self.options_group_box) 

        self.setLayout(self.layout)         



        if self.cb_list[0].isChecked():
            for var_edit, var_cb, var_button in zip(self.edit_list[1:],self.cb_list[1:],self.standard_button[1:]):
                self.set_widgets_status([var_edit, var_cb, var_button],[True, True, True])
        else:
            for var_edit, var_cb, var_button in zip(self.edit_list[1:],self.cb_list[1:],self.standard_button[1:]):
                self.set_widgets_status([var_edit, var_cb, var_button],[False, False, False])
   

        
    def checkbox_alter(self,var):

        cb = self.sender()

        variable_df = pd.read_csv(self.variable_file_path)
        
        if cb.isChecked():

            variable_df.loc[variable_df['variable'] == var, 'available'] = True
  
            if var == 'tracks':
                for var_edit, var_cb, var_button in zip(self.edit_list[1:],self.cb_list[1:],self.standard_button[1:]):
                    self.set_widgets_status([var_edit, var_cb, var_button],[True, True, True])


        else:

            variable_df.loc[variable_df['variable'] == var, 'available'] = False

            if var == 'tracks':

                for var_edit, var_cb, var_button in zip(self.edit_list[1:],self.cb_list[1:],self.standard_button[1:]):
                    self.set_widgets_status([var_edit, var_cb, var_button],[False, False, False])


                
        variable_df.to_csv(self.variable_file_path, index=False)

    
    def save_variables(self):
        variable_df = pd.read_csv(self.variable_file_path)


        for var, edit, cb in zip(self.var_list, self.edit_list, self.cb_list):

            edit_text = edit.text()
            if edit_text:
                variable_df.loc[variable_df['variable'] == var, 'pseudonym'] = edit_text
            if cb.isChecked():
                variable_df.loc[variable_df['variable'] == var, 'available'] = True
            else:
                variable_df.loc[variable_df['variable'] == var, 'available'] = False
    
        variable_df.to_csv(self.variable_file_path, index=False)


    def reset_variables(self):
        variable_df = pd.read_csv(self.variable_file_path)

        for var, std_text in zip(self.var_list, self.standard_list):
            variable_df.loc[variable_df['variable'] == var, 'pseudonym'] = std_text
            
        variable_df.to_csv(self.variable_file_path, index=False)

        for edit, std_text in zip(self.edit_list,self.standard_list):
            edit.setText(std_text)



    def set_standard(self, edit, std):
        edit.setText(std)



    def set_widgets_status(self,widgets,status):

        
        for widget, stat in zip(widgets,status):
            if isinstance(widget,QLineEdit):
                widget.setReadOnly(not stat)

            elif isinstance(widget,QPushButton):
                widget.setEnabled(stat)

            elif isinstance(widget,QComboBox):
                widget.setEnabled(stat)
            
            elif isinstance(widget,QCheckBox):
                widget.setEnabled(stat)




class EnCellClopedia(QWidget):
    def __init__(self):
        super().__init__()

        ''' Title '''

        self.title = QLabel('EnCellClopedia')


        ''' Comment search '''

        self.search_title = QLabel('Bioogle')


        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Search with Bioogle')

        self.search_button = QPushButton('Naviplate')
        self.search_button.clicked.connect(self.searching)

        ''' Filters '''

        self.filter_label = QLabel('Filters')


        self.exp_filter_label = QLabel('Experiment_dir')
        self.exp_filter_box = QComboBox()
        self.exp_filter_box.currentIndexChanged.connect(self.exp_filter_box_alter)
        self.exp_filter_edit = QLineEdit()
        self.exp_filter_edit.setPlaceholderText('Add exp directory for filtering')


        self.exp_fov_filter_label = QLabel('Column filter')
        self.exp_fov_filter_box = QComboBox()
        self.exp_fov_filter_box.addItems(['None','Experiment','FOV'])


        self.col_to_search_filter_label = QLabel('Column to search')
        self.col_to_search_filter_box = QComboBox() 


        ''' Comment Results '''

        self.result_search_title = QLabel('Bioogle Results')

        self.result_sort_button = QPushButton('Sort')
        self.result_sort_button.clicked.connect(self.sorting)

        self.result_search_table = QTableWidget()


        ''' Layout '''

        self.layout = QVBoxLayout()

        self.search_layout = QGridLayout()
        self.search_group_box = QGroupBox('Bioogle')

        self.search_layout.addWidget(self.search_title,0,0,1,3)
        self.search_layout.addWidget(self.search_edit,1,0,1,2)
        self.search_layout.addWidget(self.search_button,1,2,1,1)

        self.search_group_box.setLayout(self.search_layout)


        self.filter_layout = QGridLayout()
        self.filter_group_box = QGroupBox('Filters')

        self.filter_layout.addWidget(self.filter_label,0,0,1,3)

        self.filter_layout.addWidget(self.exp_filter_label,1,0,1,1)
        self.filter_layout.addWidget(self.exp_filter_box,2,0,1,1)
        self.filter_layout.addWidget(self.exp_filter_edit,3,0,1,1)

        self.filter_layout.addWidget(self.exp_fov_filter_label,1,1,1,1)
        self.filter_layout.addWidget(self.exp_fov_filter_box,2,1,1,1)

        self.filter_layout.addWidget(self.col_to_search_filter_label,1,2,1,1)
        self.filter_layout.addWidget(self.col_to_search_filter_box,2,2,1,1)
 
        self.filter_group_box.setLayout(self.filter_layout)


        self.result_search_layout = QGridLayout()
        self.result_search_group_box = QGroupBox('Results')

        self.result_search_layout.addWidget(self.result_search_title,0,0,1,4) 
        self.result_search_layout.addWidget(self.result_sort_button,0,4,1,1)
        self.result_search_layout.addWidget(self.result_search_table,1,0,1,5)          
        
        self.result_search_group_box.setLayout(self.result_search_layout)


        self.layout.addWidget(self.title)
        self.layout.addWidget(self.search_group_box)
        self.layout.addWidget(self.filter_group_box)
        self.layout.addWidget(self.result_search_group_box)

        self.setLayout(self.layout)

        ''' Define Variables '''

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_path = os.path.join(script_dir, 'files')
        self.com_path = os.path.join(folder_path, 'comments_file.csv')

        available_cols = []

        df = pd.read_csv(self.com_path)
        for col in df.columns:
            available_cols.append(col)
        
        self.col_to_search_filter_box.addItems(available_cols)
        self.col_to_search_filter_box.setCurrentText('comment')
        self.update_exp_filter_box()

        self.result_search_table.setSortingEnabled(True)
        self.sorting_factor = 0

    


       
    ''' Filter Functions'''

    def exp_filter_box_alter(self,value):
        current_value = self.exp_filter_box.itemText(value)
        self.exp_filter_edit.setText(current_value)

    def update_exp_filter_box(self):                                   #Function to update combobox when added new recent
        self.exp_filter_box.clear()

        with open('files/recent_files.pkl','rb') as file:
                self.recent_files = pickle.load(file)
        self.exp_filter_box.addItem('None')
        self.exp_filter_box.addItems(self.recent_files)


    def sorting(self):

        df = self.search_result_df
        col_count = len(df.columns)

        self.sorting_factor += 1
        if self.sorting_factor == col_count*2+1 or self.sorting_factor > col_count*2:
            self.sorting_factor = 0

        if self.sorting_factor % 2 == 0 and self.sorting_factor != 0:
            if col_count % 2 == 0:
                if self.sorting_factor < col_count:
                    way = True
                else:
                    way = False
            else:
                way = True

        elif self.sorting_factor % 2 == 1:
            if col_count % 2 == 0:
                if self.sorting_factor < col_count:
                    way = False
                else:
                    way = True
            else:
                way = False
        
        if self.sorting_factor != 0:
            col_num = self.sorting_factor % col_count
            df = df.sort_values(by=df.columns[col_num], ascending=way)

            if way:
                button_text = df.columns[col_num] + ' ascending'
            else: 
                button_text = df.columns[col_num] + ' descending'

        else:
            button_text = ''
        

        
        self.result_sort_button.setText(f'Sort {button_text}')
        
        self.df_to_table(df)

        




    ''' Search and Table function '''

    def searching(self):

        df_com = pd.read_csv(self.com_path)
        search_word = self.search_edit.text()

        search_column = self.col_to_search_filter_box.currentText()
        search_type = self.exp_fov_filter_box.currentText()
        search_exp = self.exp_filter_edit.text()

        if search_type == 'Experiment':

            df_com_filtered = df_com.dropna(subset=[search_column])

            search_result_df = df_com_filtered[df_com_filtered[search_column].str.contains(search_word, case=False)& (df_com_filtered['fov_num'] == 'exp_description')]

        elif search_type == 'FOV':
            
            df_com_filtered = df_com.dropna(subset=[search_column])
            search_result_df = df_com_filtered[df_com_filtered[search_column].str.contains(search_word, case=False) & df_com_filtered['fov_num'].str.isnumeric()]

        else:
            # Drop rows with NaN values in the search column
            df_com_filtered = df_com.dropna(subset=[search_column])
            # Perform the search on the filtered DataFrame
            search_result_df = df_com_filtered[df_com_filtered[search_column].str.contains(search_word, case=False)]

        
        if search_exp != 'None' and search_exp != '':

            search_result_df = search_result_df[search_result_df['experiment_dir'] == search_exp]


        self.df_to_table(search_result_df)


        self.search_result_df = search_result_df
        
    
    def df_to_table(self, search_result_df):

        self.result_search_table.clearContents()
        self.result_search_table.setRowCount(0)

        df_rows = search_result_df.shape[0]
        df_cols = search_result_df.shape[1]

        self.result_search_table.setRowCount(df_rows)
        self.result_search_table.setColumnCount(df_cols)
        self.result_search_table.setHorizontalHeaderLabels(('Experiment Dir','FOV','Comment'))

        for row_index, row in enumerate(search_result_df.itertuples(index=False)):
            # Loop over the columns of the row
            for col_index, value in enumerate(row):
                # Set values in the QTableWidget
                self.result_search_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        self.result_search_table.setColumnWidth(0, 400)  # Set the width of the first column to 150 pixels
        self.result_search_table.setColumnWidth(1, 250)  # Set the width of the second column to 200 pixels
        self.result_search_table.setColumnWidth(2, 350)  # Set the width of the third column to 100 pixels



class Help(QWidget):
    def __init__(self):
        super().__init__()

        ''' Title '''

        self.title = QLabel('How to be Super')
        self.title.setStyleSheet("font-size: 20pt;")

        ''' Tab Widget '''
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("font-size: 15pt;")

        # Create tabs and add them to the tab widget
        tab_bioogle = QWidget()
        tab_comments = QWidget()
        tab_favorites = QWidget()
        tab_variables = QWidget()
        tab_plotviewer = QWidget()

        self.tabs.addTab(tab_bioogle, "Bioogle")
        self.tabs.addTab(tab_comments, "Comments")
        self.tabs.addTab(tab_favorites, "Favorites")
        self.tabs.addTab(tab_variables, 'Tracks Variables')
        self.tabs.addTab(tab_plotviewer, 'Super Plot')

        # Content for Tab 1 (tab_bioogle)
        tab1_layout = QVBoxLayout()
        tab1_label = QLabel('Bioogle is a search engine within the Super Environment, the EnCellClopedia:\n'
                            '\n'
                            'In Bioogle you can look through your comment database. For each Fov and Experiment, a comment can be stored which ultimately is a description that helps to refind experiments/fovs.\n'
                            'The Bioogle window can be opened by pressing "Bioogle" in the "Super Menu"\n'
                            'There are 3 different filters available: "Experiment_dir", "Column filter" and "Column to search"\n'
                            '\n'
                            '1. The "Experiment_dir" allows to filter for experiment. It can either be entered directly or chosen from the recent used experiments.\n'
                            '2. The "Column filter" allows to determine if it searches within the comments of the experiment or the fov.\n'
                            '3. The "Column to search" defines the column in where the input will be searched in. Standard it is set to comment.\n'
                            '\n'
                            'Additionally the Bioogle includes a sorting system in which one of all the columns can be sorted by ascending or descending')
        tab1_label.setStyleSheet("font-size: 14pt;")
        tab1_layout.addWidget(tab1_label)
        tab_bioogle.setLayout(tab1_layout)

        # Content for Tab 2 (tab_comments)
        tab2_layout = QVBoxLayout()
        tab2_label = QLabel('A comment can be added to each experiment and fov.\n'
                            '\n'
                            'As soon as an experiment is loaded, the Edit button for the comment becomes usable.\n'
                            'Once clicked it allows to write a comment into the field next to it. Clicking again on the button, which is now labeled with "Save", stores the comment and is displayed.\n'
                            'The same applies to the comments for the fovs. First a fov needs to be loaded and then the button becomes clickable and the comment can be edited and saved.')
        tab2_label.setStyleSheet("font-size: 14pt;")
        tab2_layout.addWidget(tab2_label)
        tab_comments.setLayout(tab2_layout)

        # Content for Tab 3 (tab_favorites)
        tab3_layout = QVBoxLayout()
        tab3_label = QLabel('Adding experiments and fovs to favorites is another way to faclitate the search.\n'
                            '\n'
                            'At the bottom of the Settings box are 2 buttons located, for the fov and for the experiment. When pressed, the current loaded fov/experiment will be added to favorites.\n'
                            'There are 2 states: \n'
                            '\u2605, which indicates a "saved" status and \u2606 which indicates a "not-saved" status.\n'
                            '\n'
                            'Additionally, the Stars will be showed on the recent directory list and the fov list of each experiment.')
        tab3_label.setStyleSheet("font-size: 14pt;")
        tab3_layout.addWidget(tab3_label)
        tab_favorites.setLayout(tab3_layout)

        # Content for Tab 4 (tab_variables)
        tab4_layout = QVBoxLayout()
        tab4_label = QLabel('The tracks Variables widget allows to define names of files from the experiment, so the Superviewer is able to open them.\n'
                            'The tracks dataframe contains all the information of the cell tracking, the stimulation and more. If there is no tracks dataframe available, it can be turned off in those settings.\n'
                            'Other column names of the dataframe such as stimulation intensity, stimulation duration and the Stim fram can be altered and fitted to used dataframe.\n'
                            '\n'
                            'The tracks variable widget can be added by pressing "Tracks Variables" in the Super Menu\n'
                            '\n'
                            'Without Tracks dataframe, no plots can be created. Yet the program can be still used as a Viewer')
        tab4_label.setStyleSheet("font-size: 14pt;")
        tab4_layout.addWidget(tab4_label)
        tab_variables.setLayout(tab4_layout)

        tab5_layout = QVBoxLayout()
        tab5_label = QLabel('The Plot Viewer helps to review the plots in a larger scale.\n'
                            '\n'
                            'After Loading the plots in Napari, the Plot Viewer can be chosen in the super menu. With the refresh button, the plots from Napari are displayed.')
        tab5_label.setStyleSheet("font-size: 14pt;")
        tab5_layout.addWidget(tab5_label)
        tab_plotviewer.setLayout(tab5_layout)

        ''' Main Layout '''
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)



class PlotWindow(QWidget):
    def __init__(self,viewer):
        super().__init__()

        self.viewer = viewer

        self.layout = QVBoxLayout()
        self.figure_layout = QVBoxLayout()
        
        self.title = QLabel('Super Plots')
        self.title.setStyleSheet("font-size: 20pt;")
        self.layout.addWidget(self.title)  

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh)
        self.layout.addWidget(self.refresh_button)
        
        self.tabs = QTabWidget()

        self.setLayout(self.layout)

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_path = os.path.join(script_dir, 'files')
        self.plt_path = os.path.join(folder_path, 'superplots')

        file_list = os.listdir(self.plt_path)
        if not file_list:
            self.refresh()


    def refresh(self):
        file_list = os.listdir(self.plt_path)

        # Clear existing tabs
        self.tabs.clear()

        for i, plt_file in enumerate(file_list):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            self.tabs.addTab(tab, f"Plot {i}")

            plt_path = os.path.join(self.plt_path, plt_file)

            # Create a Matplotlib figure without axes
            figure = Figure(figsize=(8, 4), dpi=400)
            ax = figure.add_axes([0, 0, 1, 1])  # Add axes that cover the whole figure

            # Load the PNG file using Matplotlib's mpimg module
            img = mpimg.imread(plt_path)

            # Display the image on the Matplotlib axes
            ax.imshow(img)
            ax.axis('off')  # Turn off the axes

            # Embed the Matplotlib figure into a PyQt widget
            canvas = FigureCanvas(figure)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            canvas.updateGeometry()

            # Add the Matplotlib canvas to the tab layout
            tab_layout.addWidget(canvas)

            # Add Matplotlib NavigationToolbar for zooming and panning
            toolbar = NavigationToolbar(canvas, self)
            tab_layout.addWidget(toolbar)

            tab.setLayout(tab_layout)

        # Add the tabs to the main layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
