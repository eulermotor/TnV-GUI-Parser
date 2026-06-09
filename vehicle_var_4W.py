from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QStatusBar, QSizePolicy,QGraphicsDropShadowEffect,QStackedWidget
)
from PySide6.QtCore import Qt, QSize,QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QColor
# class HoverButton(QPushButton):
#     def __init__(self, text, layout):
#         super().__init__(text)
#         widget = QWidget()
#         widget.setLayout(layout)
#         widget.setAlignment(Qt.AlignCenter)
#         self.secondary_widget = widget
#         self.other_button = None
#         self.second_button = self.other_button
#         self.secondary_widget.hide()  # Initially hidden
#         if self.second_button is not None:
#             self.second_button.show() 
#     def set_pair(self, other_btn):
#         self.other_button = other_btn

#     def enterEvent(self, event):
#         """Show the hidden button on hover."""
#         self.secondary_widget.show()
#         if self.second_button is not None:
#             self.second_button.hide()
#         super().enterEvent(event)

#     def leaveEvent(self, event):
#         """Hide the button when mouse leaves."""
#         self.secondary_widget.hide()
#         if self.second_button is not None:
#             self.second_button.show()
#         super().leaveEvent(event)

# class varientselection(QWidget):
#     vehicle_varient = Signal(str)
#     def __init__(self):
#         super().__init__()
#         main_layout = QVBoxLayout(self)

#         # ===== TITLE =====
#         title = QLabel("Select the Vehicle Varient")
#         title.setAlignment(Qt.AlignCenter)
#         title_container = QWidget()
#         title_layout = QHBoxLayout(title_container)
#         title_layout.setContentsMargins(0, 0, 0, 0)

#         title_layout.addStretch()
#         title_layout.addWidget(title)
#         title_layout.addStretch()
#         # shadow = QGraphicsDropShadowEffect()
#         # shadow.setBlurRadius(40)
#         # shadow.setXOffset(3)           # Horizontal displacement
#         # shadow.setYOffset(3)           # Vertical displacement
#         # shadow.setColor(QColor(0, 0, 0, 255))
#         title.setStyleSheet("font-size: 35px; font-weight: bold; color: #808080; padding: 5px")#808080
#         # title.setGraphicsEffect(shadow)
#         # ===== BUTTON LAYOUT =====
#         button_layout = QHBoxLayout()

#         button_style = """
#             QPushButton {
#                 border: 2px solid #444;
#                 border-radius: 15px;
#                 padding: 20px;
#                 font-size: 20px;
#                 font-weight: bold;
#                 min-width: 120px;
#                 min-height: 60px;
#                 background-color: #f5f5f5;
#             }
#             QPushButton:hover {
#                 background-color: #cce5ff;
#             }
#         """
#         self.turbo_widget = self.Turbo_vehicle()
#         self.storm_widget = self.Storm_vehicles()
#         self.turbo = HoverButton("Turbo",self.turbo_widget)
#         self.turbo.setFixedWidth(200)
#         # turbo.clicked.connect(self.four_wheel)

#         self.storm = HoverButton("Storm",self.storm_widget)
#         self.storm.setFixedWidth(200)
#         # three_W.clicked.connect(self.three_wheel)
#         self.turbo.set_pair(self.storm)
#         self.storm.set_pair(self.turbo)

#         self.turbo.setStyleSheet(button_style)
#         self.storm.setStyleSheet(button_style)

#         button_layout.addStretch()
#         button_layout.addWidget(self.turbo)
#         button_layout.addSpacing(200)
#         button_layout.addWidget(self.storm)
#         button_layout.addStretch()
#         # shadow = QGraphicsDropShadowEffect()
#         # shadow.setBlurRadius(20)
#         # shadow.setOffset(0, 0)
#         # title.setGraphicsEffect(shadow)

#         # ===== ADD TO MAIN =====
#         # main_layout.addStretch()
#         main_layout.addSpacing(50)  # push from top slightly
#         main_layout.addWidget(title_container)

#         main_layout.addSpacing(60)  # space between title and buttons
#         main_layout.addLayout(button_layout)
#         main_layout.addStretch()

#     def Turbo_vehicle(self):
#         vortex_layout = QVBoxLayout()
#         button_style = """
#             QPushButton {
#                 border: 2px solid #444;
#                 border-radius: 2px;
#                 padding: 5px;
#                 font-size: 12px;
#                 font-weight: bold;
#                 min-width: 60px;
#                 min-height: 30px;
#                 background-color: #f5f5f5;
#             }
#             QPushButton:hover {
#                 background-color: #cce5ff;
#             }
#         """
#         #creating buttons
#         V1_button = QPushButton("V1")
#         V1_button.clicked.connect(self.V1_func)
#         V2_button = QPushButton("V2")
#         V2_button.clicked.connect(self.V2_func)
#         V3_button = QPushButton("V3")
#         V3_button.clicked.connect(self.V3_func)

#         #providing them style
#         V1_button.setStyleSheet(button_style)
#         V2_button.setStyleSheet(button_style)
#         V3_button.setStyleSheet(button_style)

#         #aligning the buttons
#         vortex_layout.addStretch()
#         vortex_layout.addWidget(V1_button)
#         vortex_layout.addSpacing(20)
#         vortex_layout.addWidget(V2_button)
#         vortex_layout.addSpacing(20)
#         vortex_layout.addWidget(V3_button)
#         vortex_layout.addStretch()
#         vortex_layout.setAlignment(Qt.AlignCenter)
#         # #adding to the vortex widget
#         # vortex.setLayout(vortex_layout)
#         return vortex_layout

#     def Storm_vehicles(self):
#         # storm = QWidget()
#         storm_layout = QVBoxLayout()
#         button_style = """
#             QPushButton {
#                 border: 2px solid #444;
#                 border-radius: 2px;
#                 padding: 5px;
#                 font-size: 12px;
#                 font-weight: bold;
#                 min-width: 60px;
#                 min-height: 30px;
#                 background-color: #f5f5f5;
#             }
#             QPushButton:hover {
#                 background-color: #cce5ff;
#             }
#         """
#         button_1250 = QPushButton("1250")
#         button_1250.clicked.connect(self.vehicle_1250)
#         button_1750 = QPushButton("1750")
#         button_1750.clicked.connect(self.vehicle_1750)
#         button_LR200 = QPushButton("LR200")
#         button_LR200.clicked.connect(self.vehicle_LR200)

#         button_1250.setStyleSheet(button_style)
#         button_1750.setStyleSheet(button_style)
#         button_LR200.setStyleSheet(button_style)

#         storm_layout.addStretch()
#         storm_layout.addWidget(button_1250)
#         storm_layout.addSpacing(20)
#         storm_layout.addWidget(button_1750)
#         storm_layout.addSpacing(20)
#         storm_layout.addWidget(button_LR200)
#         storm_layout.addStretch()
#         storm_layout.setAlignment(Qt.AlignCenter)
#         # storm.setLayout(storm_layout)

#         return storm_layout
#     def V1_func(self):
#         print("V1 selected!")
#         self.vehicle_varient.emit("V1")
#     def V2_func(self):
#         print("V2 selected!")
#         self.vehicle_varient.emit("V2")
#     def V3_func(self):
#         print("V3 selected!")
#         self.vehicle_varient.emit("V3")
#     def vehicle_1250(self):
#         print("1250 selected!")
#         self.vehicle_varient.emit("1250")
#     def vehicle_1750(self):
#         print("1750 selected!")
#         self.vehicle_varient.emit("1750")
#     def vehicle_LR200(self):
#         print("LR200 selected!")
#         self.vehicle_varient.emit("LR200")
    

class HoverButton(QPushButton):
    def __init__(self, text, secondary_index, stack_widget):
        super().__init__(text)
        self.secondary_index = secondary_index
        self.stack_widget = stack_widget
        self.other_button = None
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.perform_hide)

    def set_pair(self, other_btn):
        self.other_button = other_btn

    def enterEvent(self, event):
        self.hide_timer.stop()
        # Show the correct sub-menu and ensure its container is visible
        self.stack_widget.setCurrentIndex(self.secondary_index)
        self.stack_widget.parentWidget().show() # Show the shadow-container
        if self.other_button:
            self.other_button.hide()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hide_timer.start(300) 
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Force reset when the button is clicked"""
        self.perform_hide()
        super().mousePressEvent(event)

    def perform_hide(self):
        """Actually resets the visibility based on hover state"""
        # If mouse is over the button or the active sub-menu container, don't hide yet
        if not self.underMouse() and not self.stack_widget.parentWidget().underMouse():
            self.stack_widget.parentWidget().hide() # Hide the shadow-container
            if self.other_button:
                self.other_button.show()

class varientselection(QWidget):
    vehicle_variant = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Selection")
        # Ensure minimum size is set
        self.setMinimumSize(850, 450)
        
        # KEY STEP 1: Make this widget's background transparent to allow 
        # the external dark textured background to show through.
        self.setStyleSheet("background: transparent; border: none;")

        main_layout = QVBoxLayout(self)

        # Common style for ALL buttons to have the rounded, elevated look
        # This replaces the list-style and ensures visual consistency.
        GLOBAL_BUTTON_STYLE = """
            QPushButton { 
                font-size: 20px; font-weight: bold; 
                padding: 18px 25px; 
                background: #f5f5f5; 
                border: 2px solid #ccc; 
                border-radius: 12px; 
                color: #2c2c2c;
                min-width: 140px;
            }
            QPushButton:hover { 
                background-color: #cce5ff; 
                border-color: #99cfff;
            }
            QPushButton:pressed {
                background-color: #adcaf0;
            }
        """

        # --- TITLE ---
        # A transparent container for the title prevents the white box.
        title_area_style = "background: transparent;"
        title_container = QWidget()
        title_container.setStyleSheet(title_area_style)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Select the Vehicle Variant")
        title.setStyleSheet("font-size: 38px; font-weight: bold; color: #808080;") # Off-white for dark background
        title.setAlignment(Qt.AlignCenter)
        
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()
        main_layout.addSpacing(50)
        main_layout.addWidget(title_container)

        # --- CENTRAL BUTTON AREA ---
        # Fixed layout to prevent jumping, with transparent containers.
        self.button_layout = QHBoxLayout()
        
        # 1. Create the Central Sub-menu Area (the "Stack") and its shadow-container
        # Instead of list lines, we make the sub-menus contain individual, styled buttons.
        self.sub_area_container = QWidget()
        self.sub_area_container.setStyleSheet("background: transparent;") # Transparent background
        self.sub_area_container.setFixedWidth(200) # Prevents layout shifting
        
        # A. Setup the QStackedWidget
        self.sub_stack = QStackedWidget()
        self.sub_stack.addWidget(self.create_turbo_sub(GLOBAL_BUTTON_STYLE)) # Index 0
        self.sub_stack.addWidget(self.create_storm_sub(GLOBAL_BUTTON_STYLE)) # Index 1
        
        # B. Make the Sub-Area look elevated with a shadow
        # Apply shadow to the whole container
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180)) # Dark shadow, translucent
        shadow.setOffset(0, 3) # Drop shadow, slightly down
        self.sub_area_container.setGraphicsEffect(shadow)
        
        # C. Add the stack to its shadow-container
        sub_layout = QVBoxLayout(self.sub_area_container)
        sub_layout.setContentsMargins(10, 10, 10, 10) # Room for shadow and spacing
        sub_layout.addWidget(self.sub_stack)
        sub_layout.addStretch() # Push everything up
        
        self.sub_area_container.hide() # Initially hidden

        # 2. Create Hover Buttons
        self.turbo_btn = HoverButton("Turbo", 0, self.sub_stack)
        self.storm_btn = HoverButton("Storm", 1, self.sub_stack)
        self.turbo_btn.set_pair(self.storm_btn)
        self.storm_btn.set_pair(self.turbo_btn)

        # Apply common style to main buttons
        self.turbo_btn.setStyleSheet(GLOBAL_BUTTON_STYLE)
        self.storm_btn.setStyleSheet(GLOBAL_BUTTON_STYLE)

        # 3. Assemble Layout: [Turbo] [Stacked Options Area] [Storm]
        # By putting the options in the MIDDLE, buttons stay on the edges
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.turbo_btn)
        self.button_layout.addSpacing(50)
        # We add the shadow-container, not just the stack
        self.button_layout.addWidget(self.sub_area_container)
        self.button_layout.addSpacing(50)
        self.button_layout.addWidget(self.storm_btn)
        self.button_layout.addStretch()

        main_layout.addSpacing(60)
        main_layout.addLayout(self.button_layout)
        main_layout.addStretch()

    def create_turbo_sub(self, style):
        # Creates a transparent widget with vertical, styled buttons
        widget = QWidget()
        widget.setStyleSheet("background: transparent;") # Crucial fix
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.addSpacing(10) # Push from top
        
        # Add a stretch before buttons to center them
        layout.addStretch()
        for name in ["V1", "V2", "V3"]:
            btn = QPushButton(name)
            # Replicate main button style, but with smaller padding
            # Modifying padding for sub-menu
            btn_style = style.replace("padding: 18px 25px;", "padding: 12px 18px; min-width: 120px;")
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda chk, n=name: self.emit_selection(n))
            layout.addWidget(btn)
        layout.addStretch() # Add a stretch after to center
        return widget

    def create_storm_sub(self, style):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;") # Crucial fix
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addStretch()
        for name in ["1250", "1750", "LR200"]:
            btn = QPushButton(name)
            # Replicate main button style, but with smaller padding
            btn_style = style.replace("padding: 18px 25px;", "padding: 12px 18px; min-width: 120px;")
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda chk, n=name: self.emit_selection(n))
            layout.addWidget(btn)
        layout.addStretch()
        return widget

    def emit_selection(self, val):
        print(f"Final Selection: {val}")
        self.vehicle_variant.emit(val)