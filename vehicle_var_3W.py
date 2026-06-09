from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QStatusBar, QSizePolicy,QGraphicsDropShadowEffect,QStackedWidget
)
from PySide6.QtCore import Qt, QSize,QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QColor


# class HoverButton(QPushButton):
#     def __init__(self, text, secondary_index, stack_widget):
#         super().__init__(text)
#         self.secondary_index = secondary_index
#         self.stack_widget = stack_widget
#         self.other_button_1 = None
#         self.other_button_2 = None
#         self.other_button_3 = None
        
#         self.hide_timer = QTimer(self)
#         self.hide_timer.setSingleShot(True)
#         self.hide_timer.timeout.connect(self.perform_hide)

#     def set_pair(self, other_btn_1,other_btn_2,other_btn_3):
#         self.other_button_1 = other_btn_1
#         self.other_button_2 = other_btn_2
#         self.other_button_3 = other_btn_3

#     def enterEvent(self, event):
#         self.hide_timer.stop()
#         # Show the correct sub-menu and ensure its container is visible
#         self.stack_widget.setCurrentIndex(self.secondary_index)
#         self.stack_widget.parentWidget().show() # Show the shadow-container
#         if self.other_button_1 or self.other_button_2 or self.other_button_3:
#             self.other_button_1.hide()
#             self.other_button_2.hide()
#             self.other_button_3.hide()
#         super().enterEvent(event)

#     def leaveEvent(self, event):
#         self.hide_timer.start(300) 
#         super().leaveEvent(event)

#     def mousePressEvent(self, event):
#         """Force reset when the button is clicked"""
#         self.perform_hide()
#         super().mousePressEvent(event)

#     def perform_hide(self):
#         """Actually resets the visibility based on hover state"""
#         # If mouse is over the button or the active sub-menu container, don't hide yet
#         if not self.underMouse() and not self.stack_widget.parentWidget().underMouse():
#             self.stack_widget.parentWidget().hide() # Hide the shadow-container
#             if self.other_button_1 or self.other_button_2 or self.other_button_3:
#                 self.other_button_1.show()
#                 self.other_button_2.show()
#                 self.other_button_3.show()

# class varientselection(QWidget):
#     vehicle_variant = Signal(str)

#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Vehicle Selection")
#         # Ensure minimum size is set
#         self.setMinimumSize(850, 450)
        
#         # KEY STEP 1: Make this widget's background transparent to allow 
#         # the external dark textured background to show through.
#         self.setStyleSheet("background: transparent; border: none;")

#         main_layout = QVBoxLayout(self)

#         # Common style for ALL buttons to have the rounded, elevated look
#         # This replaces the list-style and ensures visual consistency.
#         GLOBAL_BUTTON_STYLE = """
#             QPushButton { 
#                 font-size: 20px; font-weight: bold; 
#                 padding: 18px 25px; 
#                 background: #f5f5f5; 
#                 border: 2px solid #ccc; 
#                 border-radius: 12px; 
#                 color: #2c2c2c;
#                 min-width: 140px;
#             }
#             QPushButton:hover { 
#                 background-color: #cce5ff; 
#                 border-color: #99cfff;
#             }
#             QPushButton:pressed {
#                 background-color: #adcaf0;
#             }
#         """

#         # --- TITLE ---
#         # A transparent container for the title prevents the white box.
#         title_area_style = "background: transparent;"
#         title_container = QWidget()
#         title_container.setStyleSheet(title_area_style)
#         title_layout = QHBoxLayout(title_container)
#         title_layout.setContentsMargins(0, 0, 0, 0)
        
#         title = QLabel("Select the Vehicle Variant")
#         title.setStyleSheet("font-size: 38px; font-weight: bold; color: #808080;") # Off-white for dark background
#         title.setAlignment(Qt.AlignCenter)
        
#         title_layout.addStretch()
#         title_layout.addWidget(title)
#         title_layout.addStretch()
#         main_layout.addWidget(title_container)

#         # --- CENTRAL BUTTON AREA ---
#         # Fixed layout to prevent jumping, with transparent containers.
#         self.button_layout = QHBoxLayout()
        
#         # 1. Create the Central Sub-menu Area (the "Stack") and its shadow-container
#         # Instead of list lines, we make the sub-menus contain individual, styled buttons.
#         self.sub_area_container = QWidget()
#         self.sub_area_container.setStyleSheet("background: transparent;") # Transparent background
#         self.sub_area_container.setFixedWidth(200) # Prevents layout shifting
        
#         # A. Setup the QStackedWidget
#         self.sub_stack = QStackedWidget()
#         self.sub_stack.addWidget(self.create_HiLoad_sub(GLOBAL_BUTTON_STYLE)) # Index 0
#         self.sub_stack.addWidget(self.create_HiCity_sub(GLOBAL_BUTTON_STYLE)) # Index 1
#         self.sub_stack.addWidget(self.create_HiRange_sub(GLOBAL_BUTTON_STYLE)) # Index 2
#         self.sub_stack.addWidget(self.create_NeoEco_sub(GLOBAL_BUTTON_STYLE)) # Index 3
        
#         # B. Make the Sub-Area look elevated with a shadow
#         # Apply shadow to the whole container
#         shadow = QGraphicsDropShadowEffect(self)
#         shadow.setBlurRadius(20)
#         shadow.setColor(QColor(0, 0, 0, 180)) # Dark shadow, translucent
#         shadow.setOffset(0, 3) # Drop shadow, slightly down
#         self.sub_area_container.setGraphicsEffect(shadow)
        
#         # C. Add the stack to its shadow-container
#         sub_layout = QVBoxLayout(self.sub_area_container)
#         sub_layout.setContentsMargins(5, 5, 5, 5) # Room for shadow and spacing
#         sub_layout.addWidget(self.sub_stack)
#         sub_layout.addStretch() # Push everything up
        
#         self.sub_area_container.hide() # Initially hidden

#         # 2. Create Hover Buttons
#         self.Hiload_btn = HoverButton("Hiload", 0, self.sub_stack)
#         self.Hicity_btn = HoverButton("Hicity", 1, self.sub_stack)
#         self.Hirange_btn = HoverButton("Hirange", 2, self.sub_stack)
#         self.neoeco_btn = HoverButton("Neo Eco", 3, self.sub_stack)

#         self.Hiload_btn.set_pair(self.Hicity_btn,self.Hirange_btn,self.neoeco_btn)
#         self.Hicity_btn.set_pair(self.Hiload_btn,self.Hirange_btn,self.neoeco_btn)
#         self.Hirange_btn.set_pair(self.Hicity_btn,self.Hiload_btn,self.neoeco_btn)
#         self.neoeco_btn.set_pair(self.Hicity_btn,self.Hiload_btn,self.Hirange_btn)

#         # Apply common style to main buttons
#         self.Hiload_btn.setStyleSheet(GLOBAL_BUTTON_STYLE)
#         self.Hicity_btn.setStyleSheet(GLOBAL_BUTTON_STYLE)
#         self.Hirange_btn.setStyleSheet(GLOBAL_BUTTON_STYLE)
#         self.neoeco_btn.setStyleSheet(GLOBAL_BUTTON_STYLE)

#         # 3. Assemble Layout: [Turbo] [Stacked Options Area] [Storm]
#         # By putting the options in the MIDDLE, buttons stay on the edges
#         self.button_layout.addStretch()
#         self.button_layout.addWidget(self.Hiload_btn)
#         self.button_layout.addSpacing(10)
#         # We add the shadow-container, not just the stack
#         self.button_layout.addWidget(self.sub_area_container)
#         self.button_layout.addSpacing(10)
#         self.button_layout.addWidget(self.Hicity_btn)
#         self.button_layout.addSpacing(10)
#         # We add the shadow-container, not just the stack
#         self.button_layout.addWidget(self.sub_area_container)
#         self.button_layout.addSpacing(10)
#         self.button_layout.addWidget(self.Hirange_btn)
#         self.button_layout.addSpacing(10)
#         # We add the shadow-container, not just the stack
#         self.button_layout.addWidget(self.sub_area_container)
#         self.button_layout.addSpacing(10)
#         self.button_layout.addWidget(self.neoeco_btn)
#         self.button_layout.addStretch()

#         main_layout.addSpacing(60)
#         main_layout.addLayout(self.button_layout)
#         main_layout.addStretch()

#     def create_HiLoad_sub(self, style):
#         # Creates a transparent widget with vertical, styled buttons
#         widget = QWidget()
#         widget.setStyleSheet("background: transparent;") # Crucial fix
#         layout = QVBoxLayout(widget)
#         layout.setContentsMargins(0, 0, 0, 0)
#         # layout.addSpacing(10) # Push from top
        
#         # Add a stretch before buttons to center them
#         layout.addStretch()
#         for name in ["SR_HL", "TR_HL", "XR_HL"]:
#             btn = QPushButton(name)
#             # Replicate main button style, but with smaller padding
#             # Modifying padding for sub-menu
#             btn_style = style.replace("padding: 18px 25px;", "padding: 12px 18px; min-width: 120px;")
#             btn.setStyleSheet(btn_style)
#             btn.clicked.connect(lambda chk, n=name: self.emit_selection(n))
#             layout.addWidget(btn)
#         layout.addStretch() # Add a stretch after to center
#         return widget

#     def create_HiCity_sub(self, style):
#         widget = QWidget()
#         widget.setStyleSheet("background: transparent;") # Crucial fix
#         layout = QVBoxLayout(widget)
#         layout.setContentsMargins(0, 0, 0, 0)
        
#         layout.addStretch()
#         for name in ["SR_HC", "TR_HC", "XR_HC"]:
#             btn = QPushButton(name)
#             # Replicate main button style, but with smaller padding
#             btn_style = style.replace("padding: 18px 25px;", "padding: 12px 18px; min-width: 120px;")
#             btn.setStyleSheet(btn_style)
#             btn.clicked.connect(lambda chk, n=name: self.emit_selection(n))
#             layout.addWidget(btn)
#         layout.addStretch()
#         return widget
#     def create_HiRange_sub(self, style):
#         widget = QWidget()
#         widget.setStyleSheet("background: transparent;") # Crucial fix
#         layout = QVBoxLayout(widget)
#         layout.setContentsMargins(0, 0, 0, 0)
        
#         layout.addStretch()
#         for name in ["SR_HR", "TR_HR", "XR_HR"]:
#             btn = QPushButton(name)
#             # Replicate main button style, but with smaller padding
#             btn_style = style.replace("padding: 18px 25px;", "padding: 12px 18px; min-width: 120px;")
#             btn.setStyleSheet(btn_style)
#             btn.clicked.connect(lambda chk, n=name: self.emit_selection(n))
#             layout.addWidget(btn)
#         layout.addStretch()
#         return widget
#     def create_NeoEco_sub(self, style):
#         widget = QWidget()
#         widget.setStyleSheet("background: transparent;") # Crucial fix
#         layout = QVBoxLayout(widget)
#         layout.setContentsMargins(0, 0, 0, 0)
        
#         layout.addStretch()
#         for name in ["SR_NEO", "TR_NEO", "XR_NEO"]:
#             btn = QPushButton(name)
#             # Replicate main button style, but with smaller padding
#             btn_style = style.replace("padding: 18px 25px;", "padding: 12px 18px; min-width: 120px;")
#             btn.setStyleSheet(btn_style)
#             btn.clicked.connect(lambda chk, n=name: self.emit_selection(n))
#             layout.addWidget(btn)
#         layout.addStretch()
#         return widget

#     def emit_selection(self, val):
#         print(f"Final Selection: {val}")
#         self.vehicle_variant.emit(val)
class ButtonStack(QStackedWidget):
    """A container that holds a Main Button (Page 0) and its Sub-Menu (Page 1)"""
    def __init__(self, main_text, sub_options, emit_callback, global_style):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        
        # 1. THE MAIN BUTTON (Page 0)
        self.main_button = QPushButton(main_text)
        self.main_button.setStyleSheet(global_style)
        self.addWidget(self.main_button)

        # 2. THE SUB-MENU (Page 1)
        self.sub_menu_widget = QWidget()
        self.sub_menu_widget.setStyleSheet("background: transparent;")
        sub_layout = QVBoxLayout(self.sub_menu_widget)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.setSpacing(10)
        
        sub_layout.addStretch()
        for name in sub_options:
            btn = QPushButton(name)
            # Smaller version of the global style for sub-buttons
            sub_style = global_style.replace("padding: 18px 25px;", "padding: 10px 15px; font-size: 16px;")
            btn.setStyleSheet(sub_style)
            btn.clicked.connect(lambda chk, n=name: emit_callback(n))
            layout_item = sub_layout.addWidget(btn)
        sub_layout.addStretch()
        
        # Add shadow to the sub-menu container only
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.sub_menu_widget.setGraphicsEffect(shadow)
        
        self.addWidget(self.sub_menu_widget)

        # 3. HOVER LOGIC
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.show_main_button)

        # Connect events
        self.main_button.installEventFilter(self)
        self.sub_menu_widget.installEventFilter(self)

    def enterEvent(self, event):
        self.hide_timer.stop()
        self.setCurrentIndex(1) # Show sub-menu
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hide_timer.start(400) # Give user time to move mouse
        super().leaveEvent(event)

    def show_main_button(self):
        if not self.underMouse():
            self.setCurrentIndex(0)

class varientselection3W(QWidget):
    vehicle_variant = Signal(str)

    def __init__(self):
        super().__init__()
        # self.setMinimumSize(1000, 500)
        self.setStyleSheet("background: transparent; border: none;")

        main_layout = QVBoxLayout(self)

        GLOBAL_BUTTON_STYLE = """
            QPushButton { 
                font-size: 20px; font-weight: bold; 
                padding: 18px 25px; 
                background: #f5f5f5; 
                border: 2px solid #ccc; 
                border-radius: 12px; 
                color: #2c2c2c;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #cce5ff; border-color: #99cfff; }
        """

        # --- TITLE ---
        title = QLabel("Select the Vehicle Variant")
        title.setStyleSheet("font-size: 38px; font-weight: bold; color: #808080;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # --- BUTTON AREA ---
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(30) # Space between the 4 stacks
        self.button_layout.setAlignment(Qt.AlignCenter)
        # Define your 4 cases
        cases = {
            "Hiload": ["SR_HL", "TR_HL", "XR_HL"],
            "Hicity": ["SR_HC", "TR_HC", "XR_HC"],
            "Hirange": ["SR_HR", "TR_HR", "XR_HR"],
            "Neo Eco": ["SR_NEO", "TR_NEO", "XR_NEO"]
        }

        self.button_layout.addStretch()
        
        # Create a stack for each case
        for main_text, options in cases.items():
            stack = ButtonStack(main_text, options, self.emit_selection, GLOBAL_BUTTON_STYLE)
            self.button_layout.addWidget(stack)
            
        self.button_layout.addStretch()

        main_layout.addSpacing(40)
        main_layout.addLayout(self.button_layout)
        main_layout.addStretch()

    def emit_selection(self, val):
        print(f"Final Selection: {val}")
        self.vehicle_variant.emit(val)