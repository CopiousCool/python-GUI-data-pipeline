import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QLineEdit, QMessageBox, QTableView
from PyQt5.QtCore import Qt
import pandas as pd
import sqlite3
import mysql.connector
import psycopg2

class TableModel(pd.DataFrame):
    """
    Subclass of pandas DataFrame that implements the Qt model interface.
    """
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self.iloc[index.row(), index.column()])
        return None

class TableView(QTableView):
    """
    Custom QTableView that sets the model and enables sorting and filtering.
    """
    def __init__(self, data):
        super().__init__()
        self.setModel(TableModel(data))
        self.setSortingEnabled(True)
        self.setFilterDuplicates(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Display startup dialog window to select data source
    sources = ['CSV', 'Spreadsheet', 'SQL', 'MySQL', 'PostgreSQL']
    source, ok = QInputDialog.getItem(None, 'Select Data Source', 'Select the data source:', sources, 0, False)
    if not ok:
        sys.exit()

    # Load data from selected data source
    if source == 'CSV':
        # Open file dialog window to select CSV file
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('CSV Files (*.csv)')
        if file_dialog.exec_() == QFileDialog.Accepted:
            filename = file_dialog.selectedFiles()[0]
        else:
            sys.exit()

        # Load data from CSV file
        data = pd.read_csv(filename)
    elif source == 'Spreadsheet':
        # Open file dialog window to select Excel or CSV file
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Excel Files (*.xls *.xlsx);;CSV Files (*.csv)')
        if file_dialog.exec_() == QFileDialog.Accepted:
            filename = file_dialog.selectedFiles()[0]
        else:
            sys.exit()

        # Load data from Excel or CSV file
        if filename.endswith('.xls') or filename.endswith('.xlsx'):
            data = pd.read_excel(filename)
        elif filename.endswith('.csv'):
            data = pd.read_csv(filename)
    elif source in ['SQL', 'MySQL', 'PostgreSQL']:
        # Prompt user for database credentials
        host, ok = QInputDialog.getText(None, 'Database Credentials', 'Enter the database host:')
        if not ok:
            sys.exit()
        user, ok = QInputDialog.getText(None, 'Database Credentials', 'Enter the database user:')
        if not ok:
            sys.exit()
        password, ok = QInputDialog.getText(None, 'Database Credentials', 'Enter the database password:', QLineEdit.Password)
        if not ok:
            sys.exit()
        database, ok = QInputDialog.getText(None, 'Database Credentials', 'Enter the database name:')
        if not ok:
            sys.exit()

        # Connect to database and retrieve data
        try:
            if source == 'SQL':
                conn = sqlite3.connect(database)
            elif source == 'MySQL':
                conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
            elif source == 'PostgreSQL':
                conn = psycopg2.connect(host=host, user=user, password=password, dbname=database)
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))
            sys.exit()

        query, ok = QInputDialog.getText(None, 'Enter SQL Query', 'Enter the SQL query:')
        if not ok:
            sys.exit()

                # Execute query and load data into pandas
        data = pd.read_sql_query(query, conn)
        conn.close()
    else:
        # Invalid source selected
        QMessageBox.critical(None, 'Error', 'Invalid source selected')
        sys.exit()

    # Display data in table view
    view = TableView(data)
    view.show()
    sys.exit(app.exec_())
