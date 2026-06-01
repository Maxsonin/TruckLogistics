from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

# --- Light palette colors ---
LIGHT = {
    "bg": "#FFFFFF",
    "surface": "#F7F7F7",
    "border": "#E0E0E0",
    "text": "#1A1A1A",
    "subtext": "#6B6B6B",
    "danger": "#C62828",
    "danger_hover": "#B71C1C",
}

# --- Dark palette colors ---
DARK = {
    "bg": "#121212",
    "surface": "#1E1E1E",
    "border": "#2E2E2E",
    "text": "#F0F0F0",
    "subtext": "#9E9E9E",
    "danger": "#EF5350",
    "danger_hover": "#E53935",
}


def _colors() -> dict[str, str]:
    return DARK if ThemeManager.is_dark() else LIGHT


def colors() -> dict[str, str]:
    return _colors()


class ThemeManager:
    _dark: bool = False

    @classmethod
    def init(cls) -> None:
        try:
            scheme = QApplication.styleHints().colorScheme()
            cls._dark = scheme == Qt.ColorScheme.Dark
        except AttributeError:
            cls._dark = False
        cls._apply()

    @classmethod
    def toggle(cls) -> None:
        cls._dark = not cls._dark
        cls._apply()

    @classmethod
    def is_dark(cls) -> bool:
        return cls._dark

    @classmethod
    def _apply(cls) -> None:
        c = DARK if cls._dark else LIGHT
        palette = QPalette()
        bg = QColor(c["bg"])
        surface = QColor(c["surface"])
        text = QColor(c["text"])
        subtext = QColor(c["subtext"])
        border = QColor(c["border"])

        palette.setColor(QPalette.ColorRole.Window, bg)
        palette.setColor(QPalette.ColorRole.WindowText, text)
        palette.setColor(QPalette.ColorRole.Base, bg)
        palette.setColor(QPalette.ColorRole.AlternateBase, surface)
        palette.setColor(QPalette.ColorRole.Text, text)
        palette.setColor(QPalette.ColorRole.BrightText, text)
        palette.setColor(QPalette.ColorRole.Button, surface)
        palette.setColor(QPalette.ColorRole.ButtonText, text)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(c["text"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(c["bg"]))
        palette.setColor(QPalette.ColorRole.PlaceholderText, subtext)
        palette.setColor(QPalette.ColorRole.Mid, border)
        palette.setColor(QPalette.ColorRole.Midlight, surface)
        palette.setColor(QPalette.ColorRole.Dark, border)

        # Disabled state
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, subtext)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, subtext)

        QApplication.setPalette(palette)
