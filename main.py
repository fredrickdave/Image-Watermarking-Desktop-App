from pathlib import Path
from tkinter import Button
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames

import customtkinter
from PIL import Image, ImageTk

from ControlsFrame import ControlsFrame
from DoubleScrolledFrame import DoubleScrolledFrame

THUMBNAIL_SIZE = (125, 125)
FINAL_PREVIEW_SIZE = (690, 690)

customtkinter.set_appearance_mode("light")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1150x720")
        self.title("Mass Watermarker")
        self.minsize(300, 200)
        self.resizable(width=False, height=False)

        # Store image path and associated attributes using the format below
        # {"path": {"rotate": 0, "transparency": 0, "imagetk": None}
        self.image_dictionary = {}

        # Stores path of image currently shown in the watermark preview frame
        self.current_image_path = None

        # Stores path of image chosen as watermark
        self.current_watermark_path = None

        # Set default watermark size and margin
        self.watermark_size = (300, 300)
        self.watermark_margin = 40

        # Set default watermark opacity
        self.watermark_opacity = 100

        # Set default save location for watermarked images
        self.save_location = "output"

        self.controls_frame = ControlsFrame()
        self.controls_frame.add_image_btn.configure(command=self.add_image)
        self.controls_frame.delete_all_image_btn.configure(command=self.delete_all_image)
        self.controls_frame.watermark_size_slider.configure(command=self.adjust_watermark_size)
        self.controls_frame.watermark_opacity_slider.configure(command=self.adjust_watermark_opacity)
        self.controls_frame.save_location.configure(command=self.choose_save_location)
        self.controls_frame.choose_watermark_btn.configure(command=self.choose_watermark)
        self.controls_frame.delete_image_btn.configure(command=self.delete_image)
        self.controls_frame.rotate_image_btn.configure(command=self.rotate_image)
        self.controls_frame.save_images_btn.configure(command=self.save_images)
        self.controls_frame.save_location_entry.configure(state="normal")
        self.controls_frame.save_location_entry.insert(0, self.save_location)
        self.controls_frame.save_location_entry.configure(state="readonly")
        self.controls_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20, sticky="nsew")

        # Set watermark position radiobuttons' command to update watermark preview frame
        for buttons in self.controls_frame.radiobuttons:
            buttons.configure(command=lambda: self.update_watermark_preview(self.current_image_path))

        # Create initial image frames on the app window by calling these 2 methods
        self.create_watermark_preview_frame()
        self.create_image_preview_frame()

    def create_image_preview_frame(self):
        self.image_preview_frame = DoubleScrolledFrame(
            self, width=750, height=120, highlightbackground="#d1d5d8", highlightthickness=2
        )
        self.image_preview_frame.grid(row=1, column=1, pady=(0, 20), sticky="news")

    def create_watermark_preview_frame(self):
        self.watermark_preview_frame = DoubleScrolledFrame(
            self, width=750, height=500, highlightbackground="#d1d5d8", highlightthickness=2
        )
        self.watermark_preview_frame.grid(row=0, column=1, pady=(20, 10), sticky="nsew")

    def add_image(self):
        print(f"Watermark Position: {self.controls_frame.watermark_position.get()}")
        self.file_paths = list(
            askopenfilenames(
                title="Select the image(s) you want to watermark",
                filetypes=[("image files", "*.png;*.jpg"), ("all files", "*.*")],
            )
        )

        # Check if user added image(s). If none, exit this function
        if self.file_paths != []:
            for path in self.file_paths:
                # Check for duplicates and save any new paths to image_dictionary
                if path not in self.image_dictionary:
                    i = Image.open(path)
                    i.thumbnail(THUMBNAIL_SIZE)
                    self.image_dictionary[path] = {"rotate": 0, "transparency": 0, "imagetk": ImageTk.PhotoImage(i)}
                else:
                    print("Duplicate, skipped!")
                self.enable_image_options()
        else:
            print("No Image was added")
            return None

        # Set default current_image_path to the 1st image if it's first time importing image(s)
        if not self.current_image_path:
            self.current_image_path = list(self.image_dictionary.keys())[0]

        self.update_image_list_preview()
        self.update_watermark_preview(self.current_image_path)
        print(self.image_dictionary)
        # self.update_status_bar()
        print("End of Select Image method")

    def delete_image(self):
        # Get key/path of image next to the current image that will be deleted
        self.next_image = None
        self.previous_image = None
        temp_dictionary = iter(self.image_dictionary)
        for image_path in temp_dictionary:
            if image_path == self.current_image_path:
                print("Current Image", image_path)
                self.next_image = next(temp_dictionary, None)
                print("Next Image", self.next_image)
                break
            self.previous_image = image_path
        print("Previous Image", self.previous_image)
        self.image_dictionary.pop(self.current_image_path)

        if self.next_image:
            self.current_image_path = self.next_image
        # If next_image is empty and image_dictionary is not empty, set current_image_path to the
        # new last image in image_dictionary
        elif not self.next_image and self.image_dictionary:
            self.current_image_path = self.previous_image
        else:
            self.current_image_path = None
            self.disable_image_options()

        self.update_image_list_preview()
        self.update_watermark_preview(self.current_image_path)
        print(self.current_image_path)

    def delete_all_image(self):
        self.image_dictionary.clear()
        self.current_image_path = None
        self.image_preview_frame.destroy()
        self.watermark_preview_frame.destroy()
        self.create_image_preview_frame()
        self.create_watermark_preview_frame()
        self.disable_image_options()
        print("Removed All Images")

    def enable_image_options(self):
        self.controls_frame.choose_watermark_btn.configure(state="active")
        self.controls_frame.delete_all_image_btn.configure(state="active")
        self.controls_frame.delete_image_btn.configure(state="active")
        self.controls_frame.rotate_image_btn.configure(state="active")
        self.controls_frame.save_images_btn.configure(state="active")
        self.controls_frame.watermark_opacity_slider.configure(state="normal")
        self.controls_frame.watermark_size_slider.configure(state="normal")

    def disable_image_options(self):
        self.controls_frame.choose_watermark_btn.configure(state="disabled")
        self.controls_frame.delete_all_image_btn.configure(state="disabled")
        self.controls_frame.delete_image_btn.configure(state="disabled")
        self.controls_frame.rotate_image_btn.configure(state="disabled")
        self.controls_frame.save_images_btn.configure(state="disabled")
        self.controls_frame.watermark_opacity_slider.configure(state="disabled")
        self.controls_frame.watermark_size_slider.configure(state="disabled")

    def rotate_image(self):
        # Update angle value of current image
        current_angle = self.image_dictionary[self.current_image_path]["rotate"]
        if current_angle < 270:
            self.image_dictionary[self.current_image_path]["rotate"] = current_angle + 90
        else:
            self.image_dictionary[self.current_image_path]["rotate"] = 0

        # Update imagetk value to the rotated image
        current_angle = self.image_dictionary[self.current_image_path]["rotate"]
        original_image = Image.open(self.current_image_path)
        original_image.thumbnail(THUMBNAIL_SIZE)
        rotated_image = original_image.rotate(angle=current_angle, expand=True)
        self.image_dictionary[self.current_image_path]["imagetk"] = ImageTk.PhotoImage(rotated_image)
        # print(self.image_dictionary[self.current_image_path])
        self.update_image_list_preview()
        self.update_watermark_preview(self.current_image_path)

    def update_watermark_preview(self, image_path):
        self.watermark_preview_frame.destroy()
        self.create_watermark_preview_frame()
        # print("Image Path", image_path)
        # Exit function if passed image_path is empty/None value
        if not image_path:
            print(f"Stopped update_watermark_preview. current image is {image_path}")
            return

        # Update current_image_path to store the selected image_path to show on watermark preview frame
        self.current_image_path = image_path

        # If a watermark image is not available, open the image without applying watermark
        # Otherwise, apply the watermark
        if not self.current_watermark_path:
            self.result = Image.open(self.current_image_path)
            self.result.thumbnail(FINAL_PREVIEW_SIZE)
            current_angle = self.image_dictionary[self.current_image_path]["rotate"]
            if current_angle > 0:
                self.result = self.result.rotate(angle=current_angle, expand=True)
            print("No chosen watermark yet")
        else:
            self.result = self.apply_watermark(self.current_image_path)
            self.result.thumbnail(FINAL_PREVIEW_SIZE)

        self.imagetk = ImageTk.PhotoImage(self.result)
        self.preview_image = customtkinter.CTkLabel(
            self.watermark_preview_frame,
            image=self.imagetk,
        )
        self.preview_image.grid(row=0, column=0, padx=25, pady=10, sticky="news")

    def update_image_list_preview(self):
        self.image_preview_frame.destroy()
        self.create_image_preview_frame()
        self.watermark_preview_frame.destroy()
        self.create_watermark_preview_frame()

        # FIXME - Correct image is not updating properly in watermark preview frame - FIXED
        # Solution found at:
        # https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments
        for index, path in enumerate(self.image_dictionary.keys()):
            Button(
                self.image_preview_frame,
                image=self.image_dictionary[path].get("imagetk"),
                text="",
                borderwidth=0,
                command=lambda path=path: self.update_watermark_preview(path),
            ).grid(row=0, column=index, padx=10, pady=5)

    def choose_watermark(self):
        self.current_watermark_path = askopenfilename(title="Choose the watermark image you want to use")
        if self.current_watermark_path:
            self.controls_frame.watermark_location_entry.configure(state="normal")
            self.controls_frame.watermark_location_entry.delete(0, "end")
            self.controls_frame.watermark_location_entry.insert(0, self.current_watermark_path)
            self.controls_frame.watermark_location_entry.configure(state="readonly")
            self.update_watermark_preview(self.current_image_path)

    def apply_watermark(self, image_path):
        self.original_image = Image.open(image_path)
        current_angle = self.image_dictionary[image_path]["rotate"]
        if current_angle > 0:
            self.original_image = self.original_image.rotate(angle=current_angle, expand=True)

        self.original_image_width, self.original_image_height = self.original_image.size
        self.watermark = Image.open(self.current_watermark_path)
        # self.watermark.putalpha(self.watermark_opacity)

        # Adjust watermark size to be pasted based on the watermark_size value chosen by user. Default is 300px
        self.watermark.thumbnail(self.watermark_size)

        # Adjust watermark opacity on a percent scale
        if self.watermark.mode != "RGBA":
            alpha = Image.new("L", self.watermark.size, 255)
            self.watermark.putalpha(alpha)
        paste_mask = self.watermark.split()[3].point(lambda i: i * self.watermark_opacity / 100.0)

        print("Watermark Mode", self.watermark.mode)

        print(f"Original image Width: {self.original_image_width}, Height: {self.original_image_height}")
        print("Watermark Position", self.adjust_watermark_position())
        self.watermarked_image = Image.new(
            mode="RGB", size=(self.original_image_width, self.original_image_height), color=(0, 0, 0)
        )
        self.watermarked_image.paste(self.original_image, (0, 0))
        self.watermarked_image.paste(self.watermark, self.adjust_watermark_position(), mask=paste_mask)
        return self.watermarked_image

    def adjust_watermark_size(self, size):
        # tkinter slider command argument automatically pass in the slider value, so size parameter accepts it
        self.watermark_size = (int(size), int(size))

        print("Watermark Size", self.watermark_size)
        self.update_watermark_preview(self.current_image_path)

    def adjust_watermark_opacity(self, opacity):
        # tkinter slider command argument automatically pass in the slider value, so opacity parameter accepts it
        self.watermark_opacity = int(opacity)
        print("Watermark Opacity", self.watermark_opacity)
        self.update_watermark_preview(self.current_image_path)

    def adjust_watermark_position(self):
        """Returns a 2-tuple, containing (x, y) positions in pixels based on the value of watermark_pos variable."""
        print("Watermark Size", self.watermark.size)
        if self.controls_frame.watermark_position.get() == "bottom-left":
            return (self.watermark_margin, self.original_image_height - self.watermark.size[1] - self.watermark_margin)
        elif self.controls_frame.watermark_position.get() == "top-left":
            return (self.watermark_margin, self.watermark_margin)
        # FIXME - bottom-right alignment of watermark is messed up - FIXED: Issue - I just used watermark_size
        # instead of watermark.size attribute
        elif self.controls_frame.watermark_position.get() == "bottom-right":
            return (
                self.original_image_width - self.watermark.size[0] - self.watermark_margin,
                self.original_image_height - self.watermark.size[1] - self.watermark_margin,
            )
        elif self.controls_frame.watermark_position.get() == "top-right":
            return (self.original_image_width - self.watermark.size[0] - self.watermark_margin, self.watermark_margin)
        elif self.controls_frame.watermark_position.get() == "center":
            return (
                round(self.original_image_width * 0.50 - (self.watermark.size[0] * 0.50)),
                round(self.original_image_height * 0.50 - (self.watermark.size[1] * 0.50)),
            )

    def choose_save_location(self):
        self.save_location = askdirectory(title="Choose Save Folder location")
        if self.save_location:
            print(self.save_location)
            self.controls_frame.save_location_entry.configure(state="normal")
            self.controls_frame.save_location_entry.delete(0, "end")
            self.controls_frame.save_location_entry.insert(0, self.save_location)
            self.controls_frame.save_location_entry.configure(state="readonly")
        else:
            print("Clicked cancel")

    def save_images(self):
        print(Path(self.current_image_path).stem)
        Path("output").mkdir(exist_ok=True)
        for image_path in self.image_dictionary.keys():
            print(image_path)
            watermarked_image = self.apply_watermark(image_path)
            watermarked_image.save(fp=f"{self.save_location}/{Path(image_path).stem}_watermarked{Path(image_path).suffix}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
