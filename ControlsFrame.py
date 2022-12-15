import customtkinter


class ControlsFrame(customtkinter.CTkFrame):
    def __init__(self):
        super().__init__()

        self.add_image_btn = customtkinter.CTkButton(self, text="Add Image(s)")
        self.add_image_btn.grid(row=0, column=0, padx=10, pady=10)
        self.delete_all_image_btn = customtkinter.CTkButton(self, text="Delete All", state="disabled")
        self.delete_all_image_btn.grid(row=0, column=1, padx=10, pady=10)

        # Radiobuttons - Watermark Position
        self.position_label = customtkinter.CTkLabel(self, text="Watermark Position:")
        self.position_label.grid(row=1, column=0, padx=10, pady=10)
        self.modes = [
            ("Bottom-Left", "bottom-left"),
            ("Top-Left", "top-left"),
            ("Bottom-Right", "bottom-right"),
            ("Top-Right", "top-right"),
            ("Center", "center"),
        ]

        self.watermark_position = customtkinter.StringVar()
        self.watermark_position.set("bottom-left")
        row = 2
        self.radiobuttons = []
        for text, pos in self.modes:
            self.watermark_pos_radiobutton = customtkinter.CTkRadioButton(
                master=self,
                text=text,
                variable=self.watermark_position,
                value=pos,
            )
            self.radiobuttons.append(self.watermark_pos_radiobutton)

        for item in self.radiobuttons:
            item.grid(row=row, column=0, padx=10, pady=10, stick="w")
            row += 1

        self.watermark_size_slider = customtkinter.CTkSlider(self, from_=100, to=700, orient="horizontal")
        self.watermark_size_slider.set(300)
        self.watermark_size_slider.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.save_location = customtkinter.CTkButton(self, text="Save Location")
        self.save_location.grid(row=8, column=0, padx=10, pady=10)
        self.save_location_label = customtkinter.CTkLabel(self, text="test", anchor="w")
        self.save_location_label.grid(
            row=9,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="w",
        )

        self.choose_watermark_btn = customtkinter.CTkButton(self, text="Choose Watermark")
        self.choose_watermark_btn.grid(row=10, column=0, padx=10, pady=10)

        self.delete_image_btn = customtkinter.CTkButton(self, text="Delete", state="disabled")
        self.delete_image_btn.grid(row=11, column=0, padx=10, pady=10)
