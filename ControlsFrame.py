import customtkinter


class ControlsFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Radiobuttons - Watermark Position
        self.position_label = customtkinter.CTkLabel(self, text="Watermark Position:")
        self.position_label.grid(row=1, column=0)
        self.modes = [
            ("Bottom-Left", "bottom-left"),
            ("Top-Left", "top-left"),
            ("Bottom-Right", "bottom-right"),
            ("Top-Right", "top-right"),
            ("Center", "center"),
        ]

        self.watermark_position = customtkinter.StringVar()
        self.watermark_position.set("bottom-left")
        self.radiobuttons = []
        for text, pos in self.modes:
            self.watermark_pos_radiobutton = customtkinter.CTkRadioButton(
                master=self,
                text=text,
                variable=self.watermark_position,
                value=pos,
            )
            self.radiobuttons.append(self.watermark_pos_radiobutton)

        row = 2
        column = 0
        for item in self.radiobuttons:
            if column > 1:
                column = 0
                row += 1
            item.grid(row=row, column=column, padx=20, pady=5, stick="w")
            column += 1

        self.watermark_size_slider = customtkinter.CTkSlider(
            self, from_=100, to=700, orientation="horizontal", state="disabled"
        )
        self.watermark_size_slider.set(300)
        self.watermark_size_slider.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Opacity Slider value is based on percentage
        self.watermark_opacity_slider = customtkinter.CTkSlider(
            self, from_=10, to=100, orientation="horizontal", state="disabled"
        )
        self.watermark_opacity_slider.set(100)
        self.watermark_opacity_slider.grid(row=13, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.save_location = customtkinter.CTkButton(self, text="Save Location")
        self.save_location.grid(row=8, column=0, padx=10, pady=10)
        self.save_location_entry = customtkinter.CTkEntry(self, placeholder_text="/output", width=325, state="readonly")
        self.save_location_entry.grid(
            row=9,
            column=0,
            columnspan=2,
            padx=10,
            pady=(0, 10),
            sticky="w",
        )

        self.rotate_image_btn = customtkinter.CTkButton(self, text="Rotate", state="disabled")
        self.rotate_image_btn.grid(row=12, column=0, padx=10, pady=10)
        self.delete_image_btn = customtkinter.CTkButton(self, text="Delete", state="disabled")
        self.delete_image_btn.grid(row=12, column=1, padx=10, pady=10)

        # Setup Tab view that contains text and image watermark widgets
        self.tab_view = customtkinter.CTkTabview(self, height=130)
        self.tab_view.grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 10))
        self.image_watermark_tab = self.tab_view.add("Image Watermark")
        self.text_watermark_tab = self.tab_view.add("Text Watermark")

        self.choose_image_watermark_btn = customtkinter.CTkButton(
            self.image_watermark_tab, text="Choose Image", state="disabled"
        )
        self.choose_image_watermark_btn.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.watermark_location_entry = customtkinter.CTkEntry(self.image_watermark_tab, width=300, state="readonly")
        self.watermark_location_entry.grid(
            row=1,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="w",
        )

        self.text_watermark_entry = customtkinter.CTkEntry(self.text_watermark_tab, width=300, state="readonly")
        self.text_watermark_entry.grid(
            row=1,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="w",
        )

        self.add_image_btn = customtkinter.CTkButton(self, text="Add Image(s)")
        self.add_image_btn.grid(row=15, column=1, padx=10, pady=10)
        self.delete_all_image_btn = customtkinter.CTkButton(self, text="Delete All", state="disabled")
        self.delete_all_image_btn.grid(row=15, column=0, padx=10, pady=10)
        self.save_images_btn = customtkinter.CTkButton(self, text="Save All Images", state="disabled")
        self.save_images_btn.grid(row=16, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
