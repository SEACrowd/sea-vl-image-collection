'''
Workflow:

* Read data from metadata
* For each file/folder:
    * if folder -- pick one, add all, move folder to done
    * if file -- pick file, move file to done
'''
import csv
from datetime import date
import os
from pathlib import Path
from PIL import Image, ImageTk
import re
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import urllib
import uuid
import yaml


INPUT_DIR = Path(".") / "to_upload"
DUMP_DIR = Path(".") / "processing_complete" # where to dump processed images
DATA_DIR = Path("..") / "data" # the output image/data folder
CONTRIB_FNAME = "contributor_details.yaml"
RESULT_CSV = "seavl_batch_labels - %s.csv"
DATA_URL = "https://raw.githubusercontent.com/SEACrowd/sea-vl-image-collection/refs/heads/main/data/"

class BatchUploadCSVCreator():
    def __init__(self):
        with open(CONTRIB_FNAME, "r") as contrib_f:
            contrib_props = yaml.safe_load(contrib_f)
        
        assert contrib_props["name"], "ERROR: Please fill out your name in contributor_details.yaml"
        assert contrib_props["native language"], "ERROR: Please fill out your native language"\
            " in contributor_details.yaml"
        assert bool(re.match(r'^.+ \([A-Za-z]{3}\)$', contrib_props["native language"])), "ERROR: The native language"\
            " must be the name of the language followed by the language code in paranthesis, for"\
            " example `Indonesian (ind)`"

        self.name = contrib_props["name"]
        self.native_lang = contrib_props["native language"]

        self.result_csv = RESULT_CSV%self.name

        if os.path.exists(self.result_csv):
            response = input(f"WARNING: The file {self.result_csv} already exists. If it has"\
            " already been submitted, please delete it and restart this script. If it has not,"\
            " press `y` to proceed, and any new rows will be appended to the end of the file."\
            "\nProceed? (y/[n]):  ")

            if response.lower() not in ["y", "yes", "yep", "yeah", "lezzgo homies"]:
                sys.exit()
        else:
            with open(self.result_csv, "a") as out_csv:
                out_csv.write("annotation_id,annotator,email,created_at,timestamp,"\
                    "id,image,lead_time,text_cap_en,text_cap_native,text_culture_loc,"\
                    "text_image_loc,text_submitter_native_lang,updated_at\n")
    
    def add_line(self, image_name, cap_en, cap_native, culture_loc, image_loc, id=""):
        '''
        Add a line into the csv
        '''
        current_date = date.today()
        curr_date = current_date.strftime("%d/%m/%Y")

        if not cap_native and self.native_lang == "English (eng)":
            cap_native = cap_en

        if not cap_en and self.native_lang == "English (eng)":
            cap_en = cap_native

        with open(self.result_csv, "a") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(["","","seacrowd.research@gmail.com",curr_date,curr_date,
                    id,image_name,"",cap_en,cap_native,culture_loc,
                    image_loc,self.native_lang,""])
    
    def get_image_destination_path(self, img_path):
        '''
        Convert the image name to add in the name at the end
        '''
        dest_filename = img_path.stem + " - " + self.name + img_path.suffix
        return DATA_DIR / dest_filename
    
    def get_named_uuid(self):
        '''
        Get a UUID that includes the name
        '''
        return str(uuid.uuid4()) + "-" + self.name.replace(' ', '_')

    def process_single_image(self, img_path, cap_en, cap_native, culture_loc, img_loc, id=""):
        '''
        Process a single image, resizing it, moving it, and adding in a line into the csv
        '''
        dest_path = self.get_image_destination_path(img_path)
        resize_and_write_image(img_path, dest_path)
        self.add_line(get_img_github_path(dest_path), cap_en, cap_native, culture_loc, img_loc, id)

    def process_file_or_folder(self, fpath, cap_en, cap_native, culture_loc, img_loc):
        '''
        Process a file or a set of closely related images present in a folder
        '''
        if os.path.isfile(fpath):
            self.process_single_image(fpath, cap_en, cap_native, culture_loc, img_loc)
        else:
            subdir = fpath
            assert os.path.isdir(subdir), f"{subdir} is not a"\
                " file and not a directory? What sorcery is this?"
            subdir_img_group = \
                [f for f in os.listdir(subdir) if not (f.startswith('.') or f.startswith('__'))]
            
            id_prefix = self.get_named_uuid() + "-"
            
            self.process_single_image(fpath / subdir_img_group[0], cap_en, cap_native, culture_loc, img_loc, id_prefix + "0")
            
            for idx, img in enumerate(subdir_img_group[1:]):
                self.process_single_image(subdir / img, cap_en, cap_native, culture_loc, img_loc, id_prefix + str(idx+1))
            
        shutil.move(fpath, DUMP_DIR / "")

    def get_next_image(self):
        '''
        Get the next image or folder to be processed in `INPUT_DIR`
        '''
        for f in sorted(os.listdir(INPUT_DIR)):
            if f.startswith('.') or f.startswith('__'):
                print(f"Ignoring file {f}")
                continue
            yield INPUT_DIR / f
        yield None



class UIRepresentation():
    def __init__(self):
        self.batch_uploader = BatchUploadCSVCreator()
        self.root = tk.Tk()
        self.root.title("SEA-VL Batch Uploader")

        self.frame = self.root

        self.image_label = tk.Label(self.frame)
        self.image_label.pack()

        native_text_var = tk.StringVar()
        native_text_var.set("Native Language Description")

        self.native_label = tk.Label(self.frame, 
                        textvariable=native_text_var)
        self.native_label.pack()

        self.native_text_entry = tk.Text(self.frame, height=5, width=40)
        self.native_text_entry.pack()

        en_text_var = tk.StringVar()
        en_text_var.set("English Description")

        self.en_label = tk.Label(self.frame, 
                        textvariable=en_text_var)
        self.en_label.pack()

        self.en_text_entry = tk.Text(self.frame, height=5, width=40)
        self.en_text_entry.pack()

        def radio_button_selected():
            print("Selected option:", option_var.get())

        culture_var = tk.StringVar()
        culture_var.set("This image portrays culturally-relevant information in...")

        self.culture_label = tk.Label(self.frame, 
                        textvariable=culture_var)
        self.culture_label.pack()

        option_var = tk.StringVar()  # Create a variable to store the selected option
        
        self.CULTURE_LIST = ["Brunei", "Cambodia", "East Timor", "Indonesia", 
            "Laos", "Malaysia", "Myanmar", "Philippines", "Singapore", "Thailand", "Vietnam"]
        self.culture_var_list = []
        self.culture_checkbox_list = []

        for c in self.CULTURE_LIST:
            var = tk.IntVar()
            cbox = tk.Checkbutton(self.frame, text=c, variable=var, onvalue=1, offvalue=0)
            cbox.pack(padx=40, anchor="w")

            self.culture_var_list.append(var)
            self.culture_checkbox_list.append(cbox)

        photo_loc_var = tk.StringVar()
        photo_loc_var.set("City, Country where photo was clicked")

        self.photo_loc = tk.Label(self.frame, 
                        textvariable=photo_loc_var)
        self.photo_loc.pack(padx=10, anchor="w")

        self.photo_loc_text_entry = tk.Text(self.frame, height=1, width=40)
        self.photo_loc_text_entry.pack()

        submit_button = tk.Button(self.frame, text="Submit", command=self.process_image_and_populate_next)
        submit_button.pack()

        skip_button = tk.Button(self.frame, text="Skip", command=self.populate_ui_with_next)
        skip_button.pack()

        self.img_iterator = self.batch_uploader.get_next_image()

        self.populate_ui_with_next()

        self.root.mainloop()

    def populate_ui_with_next(self):
        '''
        Load next image into UI
        '''
        next_img_path = next(self.img_iterator)
        print(f"Image shown: {next_img_path}")

        if not next_img_path:
            self.root.destroy()
            print("All images completed!")
            sys.exit(0)
        
        if os.path.isdir(next_img_path):
            subdir_img_group = \
                [f for f in os.listdir(next_img_path) if not (f.startswith('.') or f.startswith('__'))]
            
            if subdir_img_group:
                self.curr_img = next_img_path
                self.populate_image(next_img_path / subdir_img_group[0])
            else:
                self.populate_ui_with_next()
        else:
            self.curr_img = next_img_path
            self.populate_image(next_img_path)


    def populate_image(self, path):
        '''
        Add specific image in `path` into UI
        '''
        image = Image.open(path)
        image.thumbnail(get_image_resized_dims(image, 400))  # Resize the image
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to the image

    def process_image_and_populate_next(self):
        '''
        Process the current image and populate the next one into the UI
        '''
        cap_en = self.en_text_entry.get("1.0", tk.END)
        cap_native = self.native_text_entry.get("1.0", tk.END)
        img_loc = self.photo_loc_text_entry.get("1.0", tk.END)

        culture_loc_list = []

        for var, place in zip(self.culture_var_list, self.CULTURE_LIST):
            if var.get():
                culture_loc_list.append(place)

        culture_loc = ', '.join(culture_loc_list)

        self.batch_uploader.process_file_or_folder(self.curr_img, cap_en, cap_native, culture_loc, img_loc)

        self.populate_ui_with_next()

def get_image_resized_dims(img, max_edge=2000):
    '''
    Get dimensions of an image in which the largest edge is `max_edge`
    '''
    (w, h) = img.size

    if w > max_edge or h > max_edge:
        if w > h:
            h = int(h * 1.0 * max_edge / w) 
            w = max_edge 
        else:
            w = int(w * 1.0 * max_edge / h)
            h = max_edge
    
    return (w, h)

def resize_and_write_image(input_path, output_path):
    '''
    Resize image in `input_path` and write it to `output_path`
    '''
    image = Image.open(input_path)
    (w, h) = get_image_resized_dims(image)
    image = image.resize((w, h), Image.BILINEAR) 
    image.save(output_path)

def get_img_github_path(img_path):
    '''
    Given an image at `img_path`, return the (expected) Github URL
    '''
    url_encoded_fname = urllib.parse.quote(img_path.name)
    return DATA_URL + url_encoded_fname

if __name__ == '__main__':
    u = UIRepresentation()
