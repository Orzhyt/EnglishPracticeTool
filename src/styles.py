STYLESHEET = """
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

/* Sidebar */
#sidebar {
    background-color: #1e293b;
}
#sidebarTitle {
    color: #f8fafc;
}
#sidebarSubtitle {
    color: #94a3b8;
    font-size: 13px;
}

/* Nav Buttons */
#navButton {
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding-left: 16px;
    font-size: 15px;
}
#navButton:hover {
    background-color: #334155;
    color: #f1f5f9;
}
#navButton:checked {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

/* Main Content */
#descLabel {
    color: #64748b;
    font-size: 14px;
}

#contentCard {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

#placeholder {
    color: #94a3b8;
    font-size: 15px;
    min-height: 180px;
}

/* Primary Button */
#primaryButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
}
#primaryButton:hover {
    background-color: #2563eb;
}
#primaryButton:pressed {
    background-color: #1d4ed8;
}

/* Main Window Background */
QMainWindow {
    background-color: #ffffff;
}
"""
