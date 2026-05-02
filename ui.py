"""
ui.py — Cosmic Byte Ares Controller Manager
Full UI with all fixes:
- Correct button names (A B X Y LB RB LT RT L3 R3 Back Start)
- D-pad as cross layout (reads from hat)
- Joystick visualizer with circle and dot
- Connection status indicator (Green/Yellow/Red)
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QComboBox,
    QGroupBox, QProgressBar, QLineEdit, QMessageBox,
    QGridLayout, QTabWidget, QListWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor

from controller import ControllerManager
import profiles as profile_manager


# ─── JOYSTICK WIDGET ────────────────────────────────────────────────────────
class JoystickWidget(QWidget):
    def __init__(self, label="Joystick"):
        super().__init__()
        self.label = label
        self.x = 0.0
        self.y = 0.0
        self.setMinimumSize(150, 170)
        self.setMaximumSize(150, 170)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height() - 20  # leave space for label
        cx, cy = w // 2, h // 2
        radius = min(w, h) // 2 - 10

        # Outer circle background
        painter.setPen(QPen(QColor("#45475a"), 2))
        painter.setBrush(QBrush(QColor("#181825")))
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # Crosshair lines
        painter.setPen(QPen(QColor("#45475a"), 1))
        painter.drawLine(cx - radius, cy, cx + radius, cy)
        painter.drawLine(cx, cy - radius, cx, cy + radius)

        # Dot position
        dot_x = int(cx + self.x * radius)
        dot_y = int(cy - self.y * radius)
        dot_radius = 10

        # Dot glow effect
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(137, 180, 250, 60)))
        painter.drawEllipse(dot_x - dot_radius - 4, dot_y - dot_radius - 4,
                            (dot_radius + 4) * 2, (dot_radius + 4) * 2)

        # Dot
        painter.setPen(QPen(QColor("#89b4fa"), 2))
        painter.setBrush(QBrush(QColor("#89b4fa")))
        painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius,
                            dot_radius * 2, dot_radius * 2)

        # Label
        painter.setPen(QPen(QColor("#cdd6f4")))
        painter.drawText(0, h + 2, w, 18, Qt.AlignCenter, self.label)


# ─── MAIN WINDOW ────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 Cosmic Byte Ares Controller Manager")
        self.setMinimumSize(850, 650)
        self.controller_mgr = ControllerManager()
        self.last_input_time = 0
        self.no_input_threshold = 5000  # 5 seconds

        self.init_ui()
        self.apply_dark_theme()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_inputs)
        self.timer.start(50)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.addWidget(self.build_top_bar())

        tabs = QTabWidget()
        tabs.addTab(self.build_input_tab(), "📊 Live Input")
        tabs.addTab(self.build_calibration_tab(), "⚙️ Calibration")
        tabs.addTab(self.build_remap_tab(), "🔁 Button Remap")
        tabs.addTab(self.build_profiles_tab(), "💾 Profiles")
        main_layout.addWidget(tabs)

        self.status_label = QLabel("No controller connected.")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

    # ─── TOP BAR ────────────────────────────────────────────────
    def build_top_bar(self):
        group = QGroupBox("Controller")
        layout = QHBoxLayout(group)

        self.controller_combo = QComboBox()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.controller_info_label = QLabel("—")

        # Connection status indicator
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setStyleSheet("""
            background: #313244;
            border-radius: 5px;
            padding: 5px 12px;
            color: #f38ba8;
            font-weight: bold;
        """)

        self.refresh_btn.clicked.connect(self.refresh_controllers)
        self.connect_btn.clicked.connect(self.connect_controller)
        self.disconnect_btn.clicked.connect(self.disconnect_controller)

        layout.addWidget(QLabel("Select Controller:"))
        layout.addWidget(self.controller_combo)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
        layout.addWidget(self.controller_info_label)
        layout.addWidget(self.connection_status)

        self.refresh_controllers()
        return group

    # ─── LIVE INPUT TAB ─────────────────────────────────────────
    def build_input_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Joysticks
        joy_group = QGroupBox("Joysticks")
        joy_layout = QHBoxLayout(joy_group)
        self.left_joystick = JoystickWidget("Left Stick")
        self.right_joystick = JoystickWidget("Right Stick")
        joy_layout.addStretch()
        joy_layout.addWidget(self.left_joystick)
        joy_layout.addStretch()
        joy_layout.addWidget(self.right_joystick)
        joy_layout.addStretch()
        layout.addWidget(joy_group)

        # Axes
        axes_group = QGroupBox("Analog Axes")
        axes_layout = QGridLayout(axes_group)
        axis_names = ["Left X", "Left Y", "Right X", "Right Y", "LT Axis", "RT Axis"]
        self.axis_bars = []
        for i in range(6):
            label = QLabel(f"{axis_names[i]}:")
            bar = QProgressBar()
            bar.setRange(-100, 100)
            bar.setValue(0)
            bar.setFormat("%v%")
            axes_layout.addWidget(label, i, 0)
            axes_layout.addWidget(bar, i, 1)
            self.axis_bars.append(bar)
        layout.addWidget(axes_group)

        # Buttons — Cosmic Byte Ares layout (12 buttons)
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QGridLayout(buttons_group)
        self.button_names = [
            "A", "B", "X", "Y",
            "LB", "RB", "LT", "RT",
            "L3", "R3",
            "Back", "Start"
        ]
        self.button_labels = []
        for i, name in enumerate(self.button_names):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background: #313244; border-radius: 4px; padding: 6px; min-width: 45px;")
            buttons_layout.addWidget(lbl, i // 6, i % 6)
            self.button_labels.append(lbl)
        layout.addWidget(buttons_group)

        # D-Pad as cross layout
        dpad_group = QGroupBox("D-Pad")
        dpad_layout = QGridLayout(dpad_group)
        self.dpad_up    = QLabel("▲ Up")
        self.dpad_down  = QLabel("▼ Down")
        self.dpad_left  = QLabel("◀ Left")
        self.dpad_right = QLabel("▶ Right")
        for lbl in [self.dpad_up, self.dpad_down, self.dpad_left, self.dpad_right]:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background: #313244; border-radius: 4px; padding: 6px; min-width: 60px;")
        dpad_layout.addWidget(self.dpad_up,    0, 1)
        dpad_layout.addWidget(self.dpad_left,  1, 0)
        dpad_layout.addWidget(self.dpad_right, 1, 2)
        dpad_layout.addWidget(self.dpad_down,  2, 1)
        layout.addWidget(dpad_group)

        return widget

    # ─── CALIBRATION TAB ────────────────────────────────────────
    def build_calibration_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        dz_group = QGroupBox("Dead Zone")
        dz_layout = QVBoxLayout(dz_group)
        self.dz_label = QLabel("Dead Zone: 0.10")
        self.dz_slider = QSlider(Qt.Horizontal)
        self.dz_slider.setRange(0, 100)
        self.dz_slider.setValue(10)
        self.dz_slider.valueChanged.connect(self.update_dead_zone)
        dz_layout.addWidget(self.dz_label)
        dz_layout.addWidget(self.dz_slider)
        layout.addWidget(dz_group)

        sens_group = QGroupBox("Sensitivity")
        sens_layout = QVBoxLayout(sens_group)
        self.sens_label = QLabel("Sensitivity: 1.00x")
        self.sens_slider = QSlider(Qt.Horizontal)
        self.sens_slider.setRange(10, 200)
        self.sens_slider.setValue(100)
        self.sens_slider.valueChanged.connect(self.update_sensitivity)
        sens_layout.addWidget(self.sens_label)
        sens_layout.addWidget(self.sens_slider)
        layout.addWidget(sens_group)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_calibration)
        layout.addWidget(reset_btn)
        layout.addStretch()

        return widget

    # ─── BUTTON REMAP TAB ───────────────────────────────────────
    def build_remap_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel("Remap a button: choose original button and the new button to assign it to.")
        info.setWordWrap(True)
        layout.addWidget(info)

        remap_layout = QHBoxLayout()
        self.remap_from = QComboBox()
        self.remap_to = QComboBox()
        for name in self.build_button_name_list():
            self.remap_from.addItem(name)
            self.remap_to.addItem(name)

        remap_btn = QPushButton("Apply Remap")
        remap_btn.clicked.connect(self.apply_remap)
        remap_layout.addWidget(QLabel("From:"))
        remap_layout.addWidget(self.remap_from)
        remap_layout.addWidget(QLabel("To:"))
        remap_layout.addWidget(self.remap_to)
        remap_layout.addWidget(remap_btn)
        layout.addLayout(remap_layout)

        reset_remap_btn = QPushButton("Reset All Remaps")
        reset_remap_btn.clicked.connect(self.reset_remaps)
        layout.addWidget(reset_remap_btn)
        layout.addStretch()

        return widget

    def build_button_name_list(self):
        return ["A", "B", "X", "Y", "LB", "RB", "LT", "RT", "L3", "R3", "Back", "Start"]

    # ─── PROFILES TAB ───────────────────────────────────────────
    def build_profiles_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.profile_list = QListWidget()
        self.refresh_profiles()
        layout.addWidget(QLabel("Saved Profiles:"))
        layout.addWidget(self.profile_list)

        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("Profile name (e.g. FPS, Racing, Default)")
        layout.addWidget(self.profile_name_input)

        btn_layout = QHBoxLayout()
        save_btn   = QPushButton("💾 Save Profile")
        load_btn   = QPushButton("📂 Load Profile")
        delete_btn = QPushButton("🗑️ Delete Profile")
        save_btn.clicked.connect(self.save_profile)
        load_btn.clicked.connect(self.load_profile)
        delete_btn.clicked.connect(self.delete_profile)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        return widget

    # ─── CONTROLLER ACTIONS ─────────────────────────────────────
    def refresh_controllers(self):
        self.controller_combo.clear()
        controllers = self.controller_mgr.get_connected_controllers()
        if controllers:
            for idx, name in controllers:
                self.controller_combo.addItem(f"{idx}: {name}", idx)
        else:
            self.controller_combo.addItem("No controllers found")

    def connect_controller(self):
        idx = self.controller_combo.currentData()
        if idx is None:
            return
        if self.controller_mgr.connect(idx):
            info = self.controller_mgr.get_controller_info()
            self.controller_info_label.setText(
                f"{info['name']} | Axes: {info['axes']} | Buttons: {info['buttons']}"
            )
            self.status_label.setText(f"✅ Connected: {info['name']}")
            self.set_connection_status("connected")
        else:
            self.status_label.setText("❌ Failed to connect.")
            self.set_connection_status("disconnected")

    def disconnect_controller(self):
        self.controller_mgr.disconnect()
        self.controller_info_label.setText("—")
        self.status_label.setText("Disconnected.")
        self.set_connection_status("disconnected")

    def set_connection_status(self, status):
        if status == "connected":
            self.connection_status.setText("🟢 Connected")
            self.connection_status.setStyleSheet("""
                background: #313244; border-radius: 5px;
                padding: 5px 12px; color: #a6e3a1; font-weight: bold;
            """)
        elif status == "idle":
            self.connection_status.setText("🟡 Idle — No Input")
            self.connection_status.setStyleSheet("""
                background: #313244; border-radius: 5px;
                padding: 5px 12px; color: #f9e2af; font-weight: bold;
            """)
        elif status == "disconnected":
            self.connection_status.setText("🔴 Disconnected")
            self.connection_status.setStyleSheet("""
                background: #313244; border-radius: 5px;
                padding: 5px 12px; color: #f38ba8; font-weight: bold;
            """)

    # ─── INPUT UPDATE LOOP ──────────────────────────────────────
    def update_inputs(self):
        if not self.controller_mgr.controller:
            self.set_connection_status("disconnected")
            return

        now = QDateTime.currentMSecsSinceEpoch()
        any_input = False

        # Update axes
        for i, bar in enumerate(self.axis_bars):
            try:
                val = self.controller_mgr.get_axis(i)
                bar.setValue(int(val * 100))
                if abs(val) > 0.05:
                    any_input = True
            except Exception:
                bar.setValue(0)

        # Update buttons
        for i, lbl in enumerate(self.button_labels):
            try:
                pressed = self.controller_mgr.controller.get_button(i)
                if pressed:
                    any_input = True
                lbl.setStyleSheet(
                    "background: #00AA00; border-radius: 4px; padding: 6px; min-width: 45px;"
                    if pressed else
                    "background: #313244; border-radius: 4px; padding: 6px; min-width: 45px;"
                )
            except Exception:
                pass

        # Update joysticks
        try:
            lx = self.controller_mgr.get_axis(0)
            ly = self.controller_mgr.get_axis(1)
            rx = self.controller_mgr.get_axis(2)
            ry = self.controller_mgr.get_axis(3)
            self.left_joystick.update_position(lx, -ly)
            self.right_joystick.update_position(rx, -ry)
        except Exception:
            pass

        # Update D-Pad (reads from hat — your controller sends dpad as hat)
        try:
            hat = self.controller_mgr.get_hat()
            if hat != (0, 0):
                any_input = True

            self.dpad_up.setStyleSheet(
                "background: #00AA00; border-radius: 4px; padding: 6px; min-width: 60px;"
                if hat[1] == 1 else
                "background: #313244; border-radius: 4px; padding: 6px; min-width: 60px;"
            )
            self.dpad_down.setStyleSheet(
                "background: #00AA00; border-radius: 4px; padding: 6px; min-width: 60px;"
                if hat[1] == -1 else
                "background: #313244; border-radius: 4px; padding: 6px; min-width: 60px;"
            )
            self.dpad_left.setStyleSheet(
                "background: #00AA00; border-radius: 4px; padding: 6px; min-width: 60px;"
                if hat[0] == -1 else
                "background: #313244; border-radius: 4px; padding: 6px; min-width: 60px;"
            )
            self.dpad_right.setStyleSheet(
                "background: #00AA00; border-radius: 4px; padding: 6px; min-width: 60px;"
                if hat[0] == 1 else
                "background: #313244; border-radius: 4px; padding: 6px; min-width: 60px;"
            )
        except Exception:
            pass

        # Connection status based on activity
        if any_input:
            self.last_input_time = now
            self.set_connection_status("connected")
        else:
            if now - self.last_input_time > self.no_input_threshold:
                self.set_connection_status("idle")
            else:
                self.set_connection_status("connected")

    # ─── CALIBRATION ACTIONS ────────────────────────────────────
    def update_dead_zone(self, value):
        dz = value / 100.0
        self.controller_mgr.set_dead_zone(dz)
        self.dz_label.setText(f"Dead Zone: {dz:.2f}")

    def update_sensitivity(self, value):
        sens = value / 100.0
        self.controller_mgr.set_sensitivity(sens)
        self.sens_label.setText(f"Sensitivity: {sens:.2f}x")

    def reset_calibration(self):
        self.dz_slider.setValue(10)
        self.sens_slider.setValue(100)
        self.status_label.setText("Calibration reset to defaults.")

    # ─── REMAP ACTIONS ──────────────────────────────────────────
    def apply_remap(self):
        frm = self.remap_from.currentIndex()
        to = self.remap_to.currentIndex()
        self.controller_mgr.remap_button(frm, to)
        names = self.build_button_name_list()
        self.status_label.setText(f"'{names[frm]}' remapped to '{names[to]}'")

    def reset_remaps(self):
        self.controller_mgr.reset_button_map()
        self.status_label.setText("All remaps reset.")

    # ─── PROFILE ACTIONS ────────────────────────────────────────
    def refresh_profiles(self):
        self.profile_list.clear()
        for p in profile_manager.list_profiles():
            self.profile_list.addItem(p)

    def save_profile(self):
        name = self.profile_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a profile name.")
            return
        profile_manager.save_profile(
            name,
            self.controller_mgr.dead_zone,
            self.controller_mgr.sensitivity,
            self.controller_mgr.button_map
        )
        self.refresh_profiles()
        self.status_label.setText(f"Profile '{name}' saved.")

    def load_profile(self):
        selected = self.profile_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a profile to load.")
            return
        data = profile_manager.load_profile(selected.text())
        if data:
            self.controller_mgr.set_dead_zone(data["dead_zone"])
            self.controller_mgr.set_sensitivity(data["sensitivity"])
            self.controller_mgr.button_map = data.get("button_map", {})
            self.dz_slider.setValue(int(data["dead_zone"] * 100))
            self.sens_slider.setValue(int(data["sensitivity"] * 100))
            self.status_label.setText(f"Profile '{data['name']}' loaded.")

    def delete_profile(self):
        selected = self.profile_list.currentItem()
        if not selected:
            return
        profile_manager.delete_profile(selected.text())
        self.refresh_profiles()
        self.status_label.setText("Profile deleted.")

    # ─── DARK THEME ─────────────────────────────────────────────
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: Segoe UI;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 6px;
                margin-top: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #89b4fa;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #45475a; }
            QPushButton:pressed { background-color: #89b4fa; color: #1e1e2e; }
            QSlider::groove:horizontal {
                height: 6px; background: #45475a; border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa; width: 16px; height: 16px;
                margin: -5px 0; border-radius: 8px;
            }
            QProgressBar {
                background-color: #313244; border: 1px solid #45475a;
                border-radius: 4px; text-align: center;
            }
            QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }
            QComboBox {
                background-color: #313244; border: 1px solid #45475a;
                border-radius: 4px; padding: 4px;
            }
            QLineEdit {
                background-color: #313244; border: 1px solid #45475a;
                border-radius: 4px; padding: 4px;
            }
            QListWidget {
                background-color: #181825; border: 1px solid #45475a; border-radius: 4px;
            }
            QTabWidget::pane { border: 1px solid #45475a; }
            QTabBar::tab {
                background: #313244; color: #cdd6f4;
                padding: 8px 16px;
                border-top-left-radius: 4px; border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { background: #89b4fa; color: #1e1e2e; }
        """)
