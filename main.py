import threading
from pathlib import Path
from tkinter import Button, colorchooser
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames

import customtkinter
from PIL import Image, ImageDraw, ImageFont, ImageTk

from ControlsFrame import ControlsFrame
from DoubleScrolledFrame import DoubleScrolledFrame

# Set image thumbnail size for watermark preview and image list preview frames
THUMBNAIL_SIZE = (125, 125)
FINAL_PREVIEW_SIZE = (690, 690)

customtkinter.set_appearance_mode("light")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1170x720")
        self.title("Mass Watermarker")
        self.minsize(300, 200)
        self.resizable(width=False, height=False)

        # Store image path and associated attributes using the format below
        # {"path": {"rotate": 0, "transparency": 0, "imagetk": None}
        self.image_dictionary = {}

        # Stores path of image currently shown in the watermark preview frame
        self.current_image_path = None

        # Store path of image or text chosen as watermark
        self.current_image_watermark_path = None
        self.current_text_watermark = None

        # Set default watermark size and margin
        self.image_watermark_size = (300, 300)
        self.text_watermark_size = 100
        self.watermark_margin = 40
        self.watermark_text_color = (255, 255, 255)  # Default White
        self.font = "fonts/Roboto-Regular.ttf"

        # Set default watermark opacity
        self.watermark_opacity = 100

        # Set default save location for watermarked images
        self.save_location = "output"

        self.controls_frame = ControlsFrame(self)
        self.controls_frame.add_image_btn.configure(command=lambda: self.new_thread(self.add_image))
        self.controls_frame.delete_all_image_btn.configure(command=self.delete_all_image)
        self.controls_frame.watermark_size_slider.configure(command=self.adjust_watermark_size)
        self.controls_frame.watermark_opacity_slider.configure(command=self.adjust_watermark_opacity)
        self.controls_frame.save_location_btn.configure(command=self.choose_save_location)
        self.controls_frame.choose_image_watermark_btn.configure(command=self.choose_image_watermark)
        self.controls_frame.delete_image_btn.configure(command=self.delete_image)
        self.controls_frame.rotate_image_btn.configure(command=self.rotate_image)
        self.controls_frame.save_images_btn.configure(command=lambda: self.new_thread(self.save_images))
        self.controls_frame.tab_view.configure(command=lambda: self.update_watermark_preview(self.current_image_path))
        self.controls_frame.apply_text_watermark_btn.configure(command=self.get_text_watermark)
        self.controls_frame.text_color_chooser_btn.configure(command=self.get_text_watermark_color)
        self.controls_frame.font_option_menu.configure(command=self.get_font)
        self.controls_frame.save_location_entry.configure(state="normal")
        self.controls_frame.save_location_entry.insert(0, "/output")
        self.controls_frame.save_location_entry.configure(state="readonly")
        self.controls_frame.text_watermark_entry.bind("<Return>", self.get_text_watermark)
        self.controls_frame.grid(row=0, column=0, rowspan=2, padx=(20, 10), pady=20, sticky="nsew")

        # Set watermark position radiobuttons' command to update watermark preview frame
        for buttons in self.controls_frame.radiobuttons:
            buttons.configure(command=lambda: self.update_watermark_preview(self.current_image_path))

        # Create initial image frames on the app window by calling these 2 methods
        self.create_watermark_preview_frame()
        self.create_image_preview_frame()

        # Setup progressbar
        self.progressbar = customtkinter.CTkProgressBar(self)

    def create_image_preview_frame(self):
        """This method will create a DoubleScrolledFrame and display it on the main App window."""
        self.image_preview_frame = DoubleScrolledFrame(
            self, frame="image_preview", width=750, height=120, highlightbackground="#d1d5d8", highlightthickness=2
        )
        self.image_preview_frame.grid(row=1, column=1, pady=(0, 20), sticky="news")

    def create_watermark_preview_frame(self):
        """This method will create a DoubleScrolledFrame and display it on the main App window."""
        self.watermark_preview_frame = DoubleScrolledFrame(
            self, frame="watermark_preview", width=750, height=500, highlightbackground="#d1d5d8", highlightthickness=2
        )
        self.watermark_preview_frame.grid(row=0, column=1, pady=(20, 10), sticky="nsew")

    def add_image(self):
        """This method calls the Open File Dialog menu to let the user add one or more images, then stores the returned
        list of files names to image_dictionary variable.

        Returns:
            None: Returns None to stop this method if the user closed the file dialog menu without selecting
            any image.
        """
        self.file_paths = list(
            askopenfilenames(
                title="Select the image(s) you want to watermark",
                filetypes=[("image files", "*.png;*.jpg"), ("all files", "*.*")],
            )
        )

        # Check if user added image(s). If none, exit this function by returning None
        if self.file_paths != []:
            # Disable add button while images are added to avoid unwated issue during load process
            self.controls_frame.add_image_btn.configure(state="disabled")
            # Store number of items that need to be processed in tasks variable so it can be used
            # to determine progressbar step count
            tasks = len(self.file_paths)
            for index, path in enumerate(self.file_paths):
                # Update progress bar
                index += 1
                self.progress_value = index / tasks
                self.progressbar.set(self.progress_value)
                self.progressbar.grid(row=14, column=0, columnspan=2, sticky="ew")
                self.update_idletasks()

                # Check for duplicates and save any new paths to image_dictionary
                if path not in self.image_dictionary:
                    i = Image.open(path)
                    i.thumbnail(THUMBNAIL_SIZE)
                    self.image_dictionary[path] = {"rotate": 0, "transparency": 0, "imagetk": ImageTk.PhotoImage(i)}
                else:
                    print("Duplicate, skipped!")
        else:
            print("No Image was added")
            return None

        # Hide progressbar once app is done adding all images
        self.progressbar.grid_forget()

        # Set default current_image_path to the 1st image if it's first time importing image(s)
        if not self.current_image_path:
            self.current_image_path = list(self.image_dictionary.keys())[0]

        # Update image preview frames and enable widgets once all images are loaded
        self.update_image_list_preview()
        self.update_watermark_preview(self.current_image_path)
        self.controls_frame.add_image_btn.configure(state="active")
        self.enable_widgets()

    def delete_image(self):
        """This method deletes the image currently displayed in the watermark_preview_frame from the image_dictionary
        variable."""
        # The code below will get the key/path of image next to the current image that will be deleted.
        self.next_image = None
        self.previous_image = None
        temp_dictionary = iter(self.image_dictionary)
        for image_path in temp_dictionary:
            if image_path == self.current_image_path:
                self.next_image = next(temp_dictionary, None)
                break
            self.previous_image = image_path
        self.image_dictionary.pop(self.current_image_path)

        # Update the current_image_path value to store the value of next_image variable, to be displayed in
        # watermark_preview_frame.
        if self.next_image:
            self.current_image_path = self.next_image
        # If next_image is empty and image_dictionary is not empty, change value of current_image_path to the
        # value of image path stored in previous_image variable.
        elif not self.next_image and self.image_dictionary:
            self.current_image_path = self.previous_image
        # If no remaining images in the image_dictionary variable, reset the app widgets to default state.
        else:
            self.current_image_path = None
            self.current_image_watermark_path = None
            self.current_text_watermark = None
            self.image_preview_buttons = None
            self.controls_frame.watermark_location_entry.configure(state="normal")
            self.controls_frame.watermark_location_entry.delete(0, "end")
            self.controls_frame.watermark_location_entry.configure(state="readonly")
            self.controls_frame.watermark_location_entry.delete(0, "end")
            self.disable_widgets()

        self.update_image_list_preview()
        self.update_watermark_preview(self.current_image_path)

    def delete_all_image(self):
        """This methods deletes all images added by user and sets all selected watermark details back to None value."""
        self.image_dictionary.clear()
        self.current_image_path = None
        self.current_image_watermark_path = None
        self.current_text_watermark = None
        self.image_preview_buttons = None
        self.controls_frame.watermark_location_entry.configure(state="normal")
        self.controls_frame.watermark_location_entry.delete(0, "end")
        self.controls_frame.watermark_location_entry.configure(state="readonly")
        self.controls_frame.text_watermark_entry.delete(0, "end")
        self.image_preview_frame.destroy()
        self.watermark_preview_frame.destroy()
        self.create_image_preview_frame()
        self.create_watermark_preview_frame()
        self.disable_widgets()

    def enable_widgets(self):
        """This method enables all widgets that are used for image operations."""
        self.controls_frame.choose_image_watermark_btn.configure(state="active")
        self.controls_frame.text_watermark_entry.configure(state="normal", placeholder_text="Enter your text here")
        self.controls_frame.tab_view.configure(state="normal")
        self.controls_frame.apply_text_watermark_btn.configure(state="active")
        self.controls_frame.text_color_chooser_btn.configure(state="active")
        self.controls_frame.font_option_menu.configure(state="normal")
        self.controls_frame.save_location_btn.configure(state="active")
        self.controls_frame.delete_all_image_btn.configure(state="active")
        self.controls_frame.delete_image_btn.configure(state="active")
        self.controls_frame.rotate_image_btn.configure(state="active")
        self.controls_frame.save_images_btn.configure(state="active")
        self.controls_frame.watermark_opacity_slider.configure(state="normal")
        self.controls_frame.watermark_size_slider.configure(state="normal")
        for buttons in self.controls_frame.radiobuttons:
            buttons.configure(state="normal")

        # Check if image_preview_buttons list is not empty before changing state to avoid error
        if self.image_preview_buttons:
            for button in self.image_preview_buttons:
                button.configure(state="active")

    def disable_widgets(self):
        """This method disables all widgets that are used for image operations."""
        self.controls_frame.choose_image_watermark_btn.configure(state="disabled")
        self.controls_frame.tab_view.configure(state="disabled")
        self.controls_frame.text_watermark_entry.configure(state="disabled")
        self.controls_frame.text_color_chooser_btn.configure(state="disabled")
        self.controls_frame.font_option_menu.configure(state="disabled")
        self.controls_frame.save_location_btn.configure(state="disabled")
        self.controls_frame.apply_text_watermark_btn.configure(state="disabled")
        self.controls_frame.delete_all_image_btn.configure(state="disabled")
        self.controls_frame.delete_image_btn.configure(state="disabled")
        self.controls_frame.rotate_image_btn.configure(state="disabled")
        self.controls_frame.save_images_btn.configure(state="disabled")
        self.controls_frame.watermark_opacity_slider.configure(state="disabled")
        self.controls_frame.watermark_size_slider.configure(state="disabled")
        for radiobutton in self.controls_frame.radiobuttons:
            radiobutton.configure(state="disabled")

        # Check if image_preview_buttons list is not empty before changing state to avoid error
        if self.image_preview_buttons:
            for button in self.image_preview_buttons:
                button.configure(state="disabled")

    def rotate_image(self):
        """This method updates the rotate value of the selected image in the image_dictionary by using the
        current_image_path. It adds 90 degrees when run, and if it exceeds 270 degrees, revert the rotate
        value back to 0.
        """
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
        self.update_image_list_preview()
        self.update_watermark_preview(self.current_image_path)

    def update_watermark_preview(self, image_path):
        """This methods recreates the watermark_preview_frame to update the displayed images whenever there's any
        modification on the selected image to be displayed. For example: An image was added or deleted, or the
        watermark needs to be updated on the selected image.

        Args:
            image_path (str): Full path of the image that will be displayed inside watermark_preview_frame widget.
        """
        self.watermark_preview_frame.destroy()
        self.create_watermark_preview_frame()

        # Exit function if passed image_path is empty/None value
        if not image_path:
            return

        # Update current_image_path to store the selected image_path to show on watermark preview frame
        self.current_image_path = image_path

        # If a watermark image is not available, open the image without applying watermark
        # Otherwise, apply the watermark
        if not self.current_image_watermark_path and not self.current_text_watermark:
            self.result = Image.open(self.current_image_path)
            self.result.thumbnail(FINAL_PREVIEW_SIZE)
            current_angle = self.image_dictionary[self.current_image_path]["rotate"]
            if current_angle > 0:
                self.result = self.result.rotate(angle=current_angle, expand=True)
        else:
            self.result = self.apply_watermark(self.current_image_path)
            self.result.thumbnail(FINAL_PREVIEW_SIZE)

        self.imagetk = customtkinter.CTkImage(light_image=self.result, size=self.result.size)
        self.preview_image = customtkinter.CTkLabel(self.watermark_preview_frame, image=self.imagetk, text="")
        self.preview_image.grid(row=0, column=0, padx=25, pady=10, sticky="news")

    def update_image_list_preview(self):
        """This methods recreates the image_preview_frame to update the displayed images whenever an image is added
        or deleted.
        """
        self.image_preview_frame.destroy()
        self.create_image_preview_frame()
        self.watermark_preview_frame.destroy()
        self.create_watermark_preview_frame()

        # Display all images in a vertical row using button widgets. Clicking each image buttons will call the
        # update_watermark_preview method to update watermark image preview
        self.image_preview_buttons = []
        for index, path in enumerate(self.image_dictionary.keys()):
            self.image_preview_buttons.append(
                Button(
                    self.image_preview_frame,
                    image=self.image_dictionary[path].get("imagetk"),
                    text="",
                    borderwidth=0,
                    command=lambda path=path: self.update_watermark_preview(path),
                )
            )
            self.image_preview_buttons[index].grid(row=0, column=index, padx=10, pady=5)

    def choose_image_watermark(self):
        """This method will prompt the user to choose an image to use as watermark. It then saves the path of selected
        image to current_image_watermark_path variable.
        """
        self.current_image_watermark_path = askopenfilename(title="Choose the watermark image you want to use")
        if self.current_image_watermark_path:
            self.controls_frame.watermark_location_entry.configure(state="normal")
            self.controls_frame.watermark_location_entry.delete(0, "end")
            self.controls_frame.watermark_location_entry.insert(0, self.current_image_watermark_path)
            self.controls_frame.watermark_location_entry.configure(state="readonly")
            self.update_watermark_preview(self.current_image_path)

    def apply_watermark(self, image_path):
        """This method applies a watermark to the passed image path. Depending on the current tab
        selected on the tab_view widget, it will either apply a text or image watermark to the original image.

        Args:
            image_path (str): Full path of the image where the watermark will be applied to.

        Returns:
            PIL Image: Returns a PIL Image Object of the image with applied watermark.
        """
        self.original_image = Image.open(image_path)
        current_angle = self.image_dictionary[image_path]["rotate"]
        if current_angle > 0:
            self.original_image = self.original_image.rotate(angle=current_angle, expand=True)

        self.original_image_width, self.original_image_height = self.original_image.size
        self.watermarked_image = Image.new(
            mode="RGBA", size=(self.original_image_width, self.original_image_height), color=(0, 0, 0, 0)
        )
        self.watermarked_image.paste(self.original_image, (0, 0))

        # Apply the watermark based on the current tab(Image or Text) selected by the user.
        current_tab = self.controls_frame.tab_view.get()
        if current_tab == "Image Watermark" and self.current_image_watermark_path:
            self.watermark = Image.open(self.current_image_watermark_path)

            # Adjust watermark size to be pasted based on the watermark_size value chosen by user. Default is 300px
            self.watermark.thumbnail(self.image_watermark_size)

            # Adjust watermark opacity on a percent scale. Convert image to RGBA if it doesn't have transparency.
            if self.watermark.mode != "RGBA":
                self.watermark = self.watermark.convert("RGBA")
                alpha = Image.new("L", self.watermark.size, 255)
                self.watermark.putalpha(alpha)
            paste_mask = self.watermark.split()[3].point(lambda i: i * self.watermark_opacity / 100.0)
            self.watermarked_image.paste(
                self.watermark, self.get_watermark_position(self.watermark.size), mask=paste_mask
            )

        elif current_tab == "Text Watermark" and self.current_text_watermark:
            # Make a blank image for the text, initialized to transparent text color
            txt = Image.new("RGBA", (self.original_image_width, self.original_image_height), (255, 255, 255, 0))
            # Set a font
            font = ImageFont.truetype(self.font, self.text_watermark_size)
            # Get a drawing context
            d = ImageDraw.Draw(txt)

            # Calculate the size of text watermark input
            text_size = d.textsize(text=self.current_text_watermark, font=font)

            # This section will draw the text.
            # Get the RGB values from self.watermark_text_color and apply it to fill
            R, G, B = self.watermark_text_color
            # This will compute the correct alpha value based on the current percentage value of opacity slider.
            A = int(255 * (self.watermark_opacity * 0.01))
            d.text(
                xy=self.get_watermark_position(text_size),
                text=self.current_text_watermark,
                font=font,
                fill=(R, G, B, A),
            )

            # Combine the watermarked image with the transparent blank image containing the text
            self.watermarked_image = Image.alpha_composite(self.watermarked_image, txt)

        return self.watermarked_image

    def get_text_watermark(self, event=None):
        """This method updates the current_text_watermark variable to store the returned current string from the
        text_watermark_entry widget.

        Args:
            event (_type_, optional): _description_. Defaults to None.
        """
        self.current_text_watermark = self.controls_frame.text_watermark_entry.get()
        self.update_watermark_preview(self.current_image_path)

    def get_font(self, font):
        """This method updates the font variable to store the selected font name by the user using the font_option_menu
        widget.

        Args:
            font (str): This stores the font name value passed on by the font_option_menu widget.
        """
        self.font = f"fonts/{font}.ttf"
        # Call get_text_watermark method to update the text input before applying new font
        self.get_text_watermark()

    def get_text_watermark_color(self):
        """This method will open the colorchooser dialog and stores the returned RGB value of selected color to
        watermark_text_color variable.
        """
        color = colorchooser.askcolor(title="Choose Text Watermark Color")[0]
        if color:
            self.watermark_text_color = color
            # Call get_text_watermark method to update the text input before applying new font color
            self.get_text_watermark()

    def adjust_watermark_size(self, size):
        """This method captures the current value of watermark_size_slider widget and stores it on both
        image_watermark_size and text_watermark_size variables.

        Args:
            size (float): This stores the value passed on by the watermark_size_slider widget.
        """
        # tkinter slider command argument automatically pass in the slider value, so size parameter accepts it
        self.image_watermark_size = (int(size), int(size))
        # Cut the size value by half for text watermark to avoid text from being too big.
        self.text_watermark_size = int(size * 0.50)
        self.update_watermark_preview(self.current_image_path)

    def adjust_watermark_opacity(self, opacity):
        """This method captures the current value of watermark_opacity_slider widget and stores it on both
        watermark_opacity variable.

        Args:
            opacity (float): This stores the value passed on by the variable widget.
        """
        # tkinter slider command argument automatically pass in the slider value, so opacity parameter accepts it
        self.watermark_opacity = int(opacity)
        self.update_watermark_preview(self.current_image_path)

    def get_watermark_position(self, watermark_size):
        """Calculates x and y positions where watermark will be placed based on the image or text watermark size.

        Returns:
            tuple: A tuple containing (x, y) positions in pixels based on the image or text watermark size.
        """

        watermark_width = watermark_size[0]
        watermark_height = watermark_size[1]

        if self.controls_frame.watermark_position.get() == "bottom-left":
            return (self.watermark_margin, self.original_image_height - watermark_height - self.watermark_margin)
        elif self.controls_frame.watermark_position.get() == "top-left":
            return (self.watermark_margin, self.watermark_margin)
        # FIXME - bottom-right alignment of watermark is messed up - FIXED: Issue - I just used watermark_size
        # instead of watermark.size attribute
        elif self.controls_frame.watermark_position.get() == "bottom-right":
            return (
                self.original_image_width - watermark_width - self.watermark_margin,
                self.original_image_height - watermark_height - self.watermark_margin,
            )
        elif self.controls_frame.watermark_position.get() == "top-right":
            return (self.original_image_width - watermark_width - self.watermark_margin, self.watermark_margin)
        elif self.controls_frame.watermark_position.get() == "center":
            return (
                round(self.original_image_width * 0.50 - (watermark_width * 0.50)),
                round(self.original_image_height * 0.50 - (watermark_height * 0.50)),
            )

    def choose_save_location(self):
        """This method will prompt the user to choose a save location for watermarked images, and store the save path
        to save_location variable.
        """
        self.save_location = askdirectory(title="Choose Save Folder location")  # Returns None if user clicked Cancel
        if self.save_location:
            self.controls_frame.save_location_entry.configure(state="normal")
            self.controls_frame.save_location_entry.delete(0, "end")
            self.controls_frame.save_location_entry.insert(0, self.save_location)
            self.controls_frame.save_location_entry.configure(state="readonly")
        else:
            # Set default save location back to output folder if user did not select a save folder when prompted
            self.save_location = "output"

    def save_images(self):
        """This method will save all images that were added to the image_dictionary with the applied watermark.

        Images will be saved to the folder location chosen by user. If save location was not chosen, default save
        location "output" will be used.
        """
        # If default save location was not updated, create output folder inside base folder if it doesn't exists.
        if self.save_location == "output":
            Path("output").mkdir(exist_ok=True)

        # Store number of items that need to be processed in tasks variable so it can be used
        # to determine progressbar step count
        tasks = len(self.image_dictionary)

        # Disable widgets while saving images to avoid unwated user modification during save process
        self.disable_widgets()
        self.controls_frame.add_image_btn.configure(state="disabled")

        for index, image_path in enumerate(self.image_dictionary.keys()):
            # Convert mode of the returned image from apply_watermark method to "RGB" to allow saving image in original
            # format that might not support "RGBA" e.g. JPEG.
            watermarked_image = self.apply_watermark(image_path).convert("RGB")
            watermarked_image.save(
                fp=f"{self.save_location}/{Path(image_path).stem}_watermarked{Path(image_path).suffix}"
            )

            # Update progress bar
            index += 1
            self.progress_value = index / tasks
            self.progressbar.set(self.progress_value)
            self.progressbar.grid(row=2, column=0, columnspan=2, sticky="ew")
            self.update_idletasks()

        # Hide progressbar once app is done saving all images
        self.progressbar.grid_forget()

        # Enable widgets back once done saving all images
        self.controls_frame.add_image_btn.configure(state="active")
        self.enable_widgets()

    def new_thread(self, target):
        """This method will start a new thread for the target callable object.

        Args:
            target (class 'method'): Callable object or method to run.
        """
        thread = threading.Thread(target=target)
        thread.start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
