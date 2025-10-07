#!/usr/bin/python3

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys, os, io, atexit
from contextlib import redirect_stdout, redirect_stderr
import multiprocessing

sys.path.append("..")
from yt2music import downloadUrls, downloadSections 

# sys.path.append("./LIBS/lib/python3.13/site-packages/")

class Variables:
    def __init__(self, path:str="", file:str="", url:str="", metadata:str="", sections_file:str="", default_sections:bool=False, pid:int=0) -> None:
        self.path: str = path 
        self.file: str = file 
        self.url: str = url 
        self.metadata: str = metadata 
        self.sections_file: str = sections_file 
        self.default_sections: bool = default_sections
        self.pid: int = pid

variables = Variables()

class MainUI(QMainWindow,):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # uic.loadUi(os.path.join(sys._MEIPASS, 'mainWindow.ui')) # Pyinstaller tmp path
        uic.loadUi("mainWindow.ui", self)
        # Qt::AlignHCenter -> Replace in the ui file
         
        self.path_button.clicked.connect(self.browse_path)
        self.file_checkbox.stateChanged.connect(self.use_file)
        self.run_button.clicked.connect(self.run)
        self.sections_checkbox.stateChanged.connect(self.use_sections)
        self.st_checkbox.stateChanged.connect(self.use_default_section_title)
        self.status_button.clicked.connect(self.status)
        self.cancel_button.clicked.connect(self.cancel_process)

        self.path: str = ""
        self.file: str = ""
        self.url: str = ""
        self.metadata: str = ""
        self.sections_file: str = ""
        self.default_sections: bool = False
       
        self.thread = QThread()

    def browse_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path: self.path_browser.setText(path); self.path = path

    def search_file(self, text_browser: str, attribute: str) -> None:
        """
        Spawn file dialog
        Check if the attribute 'text_browser' exist, which is a Qtextbrowser
        and if 'attribute' exist which is a attribute of the class (variable),
        set the filename text value to the Qtextbrowser and 
        the filename text value to the attribute of the class
        """
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select a txt file", os.getcwd(), "TXT Files (*.txt)", options=options
        )
        if filename:
            if hasattr(self, text_browser) and hasattr(self, attribute):
                browser = getattr(self, text_browser)
                browser.clear(); browser.setText(filename)
                attr = getattr(self, attribute); attr = filename

    def disable_useURL(self, disable: bool) -> None:
        if disable:
            self.url_edit.setEnabled(False); self.url_edit.clear()
        else:
            self.url_edit.setEnabled(True)

    def disable_useFile(self, disable: bool) -> None:
        if disable:
            self.file_checkbox.setEnabled(False); self.file_checkbox.setChecked(False)
            self.file_browser.clear()
        else:
            self.file_checkbox.setEnabled(True)
    
    def disable_useSections(self, disable: bool) -> None:
        if disable:
            self.sections_checkbox.setEnabled(False); self.sections_checkbox.setChecked(False)
            self.sf_browser.clear()
            self.st_checkbox.setEnabled(False); self.st_checkbox.setChecked(False)
        else:
            self.sections_checkbox.setEnabled(True)

    def use_file(self, value) -> None:
        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked:
            self.search_file("file_browser", "file")
            self.disable_useFile(False); self.disable_useSections(True); self.disable_useURL(True)
        
        elif state == Qt.CheckState.Unchecked:
            self.disable_useURL(False); self.disable_useFile(False); self.disable_useSections(False); self.file_browser.clear()

    def use_sections(self, value) -> None:
        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked:
            self.search_file("sf_browser", "sections_file")
            self.disable_useSections(False); self.disable_useFile(True)
            self.st_checkbox.setEnabled(True)
        
        elif state == Qt.CheckState.Unchecked:
            self.disable_useFile(False); self.disable_useSections(False)
            self.st_checkbox.setEnabled(False); self.sf_browser.clear(); self.st_checkbox.setChecked(False)

    def use_default_section_title(self, value) -> None:
        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked: self.default_sections = True
        elif state == Qt.CheckState.Unchecked: self.default_sections = False

    def message_box(self, info: str, type_: str) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning) if type_ == "warning" else msg.setIcon(QMessageBox.Information) 
        msg.setText(info)
        msg.setWindowTitle("Warning") if type_ == "warning" else msg.setWindowTitle("Finished")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        revtal = msg.exec_()

    def run(self) -> None:
        self.url = self.url_edit.text() # URL Qline edit
        self.metadata = self.metadata_edit.text() # Metadata Qline edit
        self.sections_file = self.sf_browser.toPlainText() # Retrieve text from Qtextbrowser 
        self.file = self.file_browser.toPlainText()

        if not self.path: self.message_box("Select a Path", "warning"); return
        
        elif not self.url and not self.file and not self.sections_file: self.message_box("Use on the following:\nURL\nFile\nSections", "warning"); return
        
        elif not self.metadata: self.message_box("Write the Metadata", "warning"); return
        
        elif self.sections_file and not self.url: self.message_box("Write the URL", "warning"); return
       
        variables.path = self.path
        variables.file = self.file
        variables.url = self.url
        variables.metadata = self.metadata
        variables.sections_file = self.sections_file
        variables.default_sections = self.default_sections

        try:
            # self.thread = QThread()
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.finished)
            self.thread.start()
            self.run_button.setStyleSheet("background-color: rgb(255, 94, 94); color:rgb(0,0,0);")
        except Exception as e: print(e)

    def status(self) -> None:
        if not self.thread.isRunning(): self.message_box("Download not started", "info"); return
        if not self.thread.isFinished():
            try: 
                with open(".status", "r") as f: status = f.readlines()
            except Exception as e: status = ["Failed reading status"]
            self.message_box(status[0], "info")
        else: self.message_box("Finished", "info")

    def finished(self) -> None:
        try: os.remove(".status")
        except Exception as e: pass
        self.run_button.setStyleSheet("background-color: rgb(85, 255, 127); color: rgb(0, 0, 0);")
        self.message_box("Finished", "info")

    def cancel_process(self) -> None:
        if self.thread.isRunning():
            try: os.remove(".status")
            except Exception: pass
            try: self.worker.stop(); self.thread.terminate()
            except Exception as e: print(e)
            self.message_box("Canceled", "warning")
        else: self.message_box("No running process", "info"); self.run_button.setStyleSheet("background-color: rgb(85, 255, 127); color: rgb(0, 0, 0);")

class Worker(QThread):
    finished = pyqtSignal()
    
    def __init__(self) -> None:
        super().__init__()
        self.path: str = variables.path
        self.file: str = variables.file
        self.url: str = variables.url
        self.metadata: str = variables. metadata
        self.sections_file: str = variables.sections_file
        self.default_sections: bool = variables.default_sections

    def run(self) -> None:
        self.process = multiprocessing.Process(target=self.download)
        self.process.start()

    def download(self) -> None:
        variables.pid = int(multiprocessing.current_process().pid)
        if not self.sections_file:
            if self.url: 
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()): downloadUrls(True, self.file, self.url, self.metadata, self.path)
            else:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()): downloadUrls(False, self.file, self.url, self.metadata, self.path)
        else: 
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                downloadSections(self.sections_file, self.url, self.path, self.default_sections, self.metadata)

        self.finished.emit()

    def stop(self) -> None:
        try: self.process.terminate(); self.process.join()
        except Exception as e: print(e)

if __name__ == "__main__":
    @atexit.register
    def clean() -> None:
        try: os.remove(".status")
        except Exception as e: pass
        try: os.remove("url.txt")
        except Exception as e: pass

    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec_() 
    
