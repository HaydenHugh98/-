# 配置文件添加【"hidden_column_count": 2】来获取隐藏列

import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QMessageBox, QSplitter, QFrame, QFileDialog, QHeaderView, QAbstractScrollArea, \
    QScrollArea
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt
import json
from datetime import datetime


class MySQLTableComparator(QWidget):
    def __init__(self):
        super().__init__()
        self.hidden_column_count = 0  # 设置默认值
        self.config_file = 'config.json'
        self.fixed_columns = set()  # 存储固定的列索引
        self.initUI()

    def setUniformRowHeight(self, table_widget, height):
        """设置表格每一行的高度"""
        for row in range(table_widget.rowCount()):
            table_widget.setRowHeight(row, height)

    def initUI(self):
        # Main Layout
        self.layout = QVBoxLayout(self)

        # Database Connection Layout
        self.dbLayout = QHBoxLayout()
        self.hostInput = QLineEdit(self)
        self.hostInput.setPlaceholderText('Database Host')
        self.dbLayout.addWidget(self.hostInput)
        self.portInput = QLineEdit(self)
        self.portInput.setPlaceholderText('Database Port')
        self.dbLayout.addWidget(self.portInput)
        self.userInput = QLineEdit(self)
        self.userInput.setPlaceholderText('Database User')
        self.dbLayout.addWidget(self.userInput)
        self.passwordInput = QLineEdit(self)
        self.passwordInput.setPlaceholderText('Database Password')
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.dbLayout.addWidget(self.passwordInput)
        self.databaseInput = QLineEdit(self)
        self.databaseInput.setPlaceholderText('Database Name')
        self.dbLayout.addWidget(self.databaseInput)
        self.layout.addLayout(self.dbLayout)

        # Buttons
        self.buttonLayout = QHBoxLayout()
        self.connectButton = QPushButton('连接数据库', self)
        self.connectButton.clicked.connect(self.connectToDatabase)
        self.buttonLayout.addWidget(self.connectButton)
        self.loadConfigButton = QPushButton('加载配置项', self)
        self.loadConfigButton.clicked.connect(self.loadConfig)
        self.buttonLayout.addWidget(self.loadConfigButton)
        self.saveConfigButton = QPushButton('保存配置项', self)
        self.saveConfigButton.clicked.connect(self.saveConfig)
        self.buttonLayout.addWidget(self.saveConfigButton)
        self.layout.addLayout(self.buttonLayout)
        self.backupButton = QPushButton('备份', self)
        self.backupButton.clicked.connect(self.backupTable)
        self.buttonLayout.addWidget(self.backupButton)
        self.layout.addLayout(self.buttonLayout)

        # Table Selection Layout
        self.tableSelectionLayout = QVBoxLayout()
        self.table1ComboBox = QComboBox(self)
        self.tableSelectionLayout.addWidget(QLabel('备份数据表:', self))
        self.tableSelectionLayout.addWidget(self.table1ComboBox)
        self.table2ComboBox = QComboBox(self)
        self.tableSelectionLayout.addWidget(QLabel('当前数据表:', self))
        self.tableSelectionLayout.addWidget(self.table2ComboBox)
        self.tableSelectionLayout.addWidget(QLabel('选择唯一主键:', self))
        self.uniqueComboBox = QComboBox(self)
        self.tableSelectionLayout.addWidget(self.uniqueComboBox)
        self.compareButton = QPushButton('一键比较', self)
        self.compareButton.clicked.connect(self.compareTables)
        self.tableSelectionLayout.addWidget(self.compareButton)
        self.layout.addLayout(self.tableSelectionLayout)

        # Add Clear Fixed Columns Button
        self.clearFixedColumnsButton = QPushButton('清除固定列', self)
        self.clearFixedColumnsButton.clicked.connect(self.clearFixedColumns)
        self.tableSelectionLayout.addWidget(self.clearFixedColumnsButton)

        self.layout.addLayout(self.tableSelectionLayout)

        # Splitter for Table Widgets
        self.splitter = QSplitter(Qt.Horizontal)

        # 这部分是固定框的内容，调整先后顺序改变位置
        # Create fixed column widget with scroll area
        self.fixedColumnScrollArea = QScrollArea()
        self.fixedColumnScrollArea.setWidgetResizable(True)
        self.fixedColumnScrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded)  # Ensure horizontal scrollbar is available

        self.fixedColumnWidget = QTableWidget()
        self.fixedColumnScrollArea.setWidget(self.fixedColumnWidget)

        # Add fixed column widget to the layout
        self.fixedColumnLayout = QVBoxLayout()
        self.fixedColumnLayout.addWidget(QLabel('固定列', self))
        self.fixedColumnLayout.addWidget(self.fixedColumnScrollArea)

        self.fixedColumnFrame = QFrame()
        self.fixedColumnFrame.setLayout(self.fixedColumnLayout)
        self.splitter.addWidget(self.fixedColumnFrame)

        # Set splitter proportions 固定框的初始大小
        self.splitter.setSizes([100, 500, 500])  # Adjust proportions as needed

        # 固定框到此位置

        self.leftFrame = QFrame()
        self.leftLayout = QVBoxLayout()
        self.leftLayout.addWidget(QLabel('备份数据（标蓝为被删除数据）', self))
        self.table1Widget = QTableWidget()
        self.leftLayout.addWidget(self.table1Widget)
        self.leftFrame.setLayout(self.leftLayout)

        self.rightFrame = QFrame()
        self.rightLayout = QVBoxLayout()
        self.rightLayout.addWidget(QLabel('当前数据（标红为新增数据）', self))
        self.table2Widget = QTableWidget()
        self.rightLayout.addWidget(self.table2Widget)
        self.rightFrame.setLayout(self.rightLayout)

        self.splitter.addWidget(self.leftFrame)
        self.splitter.addWidget(self.rightFrame)

        # Ensure that the splitter takes available space
        self.layout.addWidget(self.splitter)

        # Set Layout and Window Title
        self.setLayout(self.layout)
        self.setWindowTitle('MySQL Table Comparator')
        self.resize(800, 600)  # Default window size

        # Synchronize Scroll Bars
        self.table1Widget.verticalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.table1Widget.verticalScrollBar(), self.table2Widget.verticalScrollBar()))
        self.table2Widget.verticalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.table2Widget.verticalScrollBar(), self.table1Widget.verticalScrollBar()))
        self.table1Widget.horizontalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.table1Widget.horizontalScrollBar(),
                                       self.table2Widget.horizontalScrollBar()))
        self.table2Widget.horizontalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.table2Widget.horizontalScrollBar(),
                                       self.table1Widget.horizontalScrollBar()))

        # Synchronize Scroll Bars
        self.table1Widget.verticalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.table1Widget.verticalScrollBar(), self.table2Widget.verticalScrollBar()))
        self.table2Widget.verticalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.table2Widget.verticalScrollBar(),
                                       self.fixedColumnWidget.verticalScrollBar()))
        self.fixedColumnWidget.verticalScrollBar().valueChanged.connect(
            lambda: self.syncScrollBar(self.fixedColumnWidget.verticalScrollBar(),
                                       self.table1Widget.verticalScrollBar()))

        # Connect the combo box signals to populate unique columns
        self.table1ComboBox.currentIndexChanged.connect(self.populateUniqueColumns)
        self.table2ComboBox.currentIndexChanged.connect(self.populateUniqueColumns)

        # 为 QTableWidget 的表头添加点击事件监听
        self.table1Widget.horizontalHeader().sectionClicked.connect(self.onSectionClicked)
        self.table2Widget.horizontalHeader().sectionClicked.connect(self.onSectionClicked)

        # 设置默认行高
        default_row_height = 30  # 你可以调整为合适的高度值

        # 设置表格行高
        self.setUniformRowHeight(self.table1Widget, default_row_height)
        self.setUniformRowHeight(self.table2Widget, default_row_height)
        self.setUniformRowHeight(self.fixedColumnWidget, default_row_height)

        # Ensure all table widgets have consistent row height
        self.table1Widget.resizeRowsToContents()
        self.table2Widget.resizeRowsToContents()
        self.fixedColumnWidget.resizeRowsToContents()

    def syncScrollBar(self, sourceScrollBar, targetScrollBar):
        targetScrollBar.setValue(sourceScrollBar.value())

    def clearFixedColumns(self):
        # Clear the fixed columns set
        self.fixed_columns.clear()

        # Update the table view and fixed column view
        self.updateView()
        self.updateFixedColumnView()

    def connectToDatabase(self):
        self.conn_info = {
            'host': self.hostInput.text(),
            'port': self.portInput.text() or '3306',  # Default to port 3306 if empty
            'user': self.userInput.text(),
            'password': self.passwordInput.text(),
            'database': self.databaseInput.text()
        }

        try:
            conn = mysql.connector.connect(
                host=self.conn_info['host'],
                port=self.conn_info['port'],
                user=self.conn_info['user'],
                password=self.conn_info['password'],
                database=self.conn_info['database']
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            self.table1ComboBox.clear()
            self.table2ComboBox.clear()
            self.table1ComboBox.addItems(table_names)
            self.table2ComboBox.addItems(table_names)

            # Populate unique columns based on current table selection
            self.populateUniqueColumns()

        except mysql.connector.Error as err:
            self.handleDatabaseError(err)
        finally:
            if 'conn' in locals():
                conn.close()
            if 'cursor' in locals():
                cursor.close()

    def populateUniqueColumns(self):
        table1 = self.table1ComboBox.currentText()
        table2 = self.table2ComboBox.currentText()

        if not table1 or not table2:
            self.uniqueComboBox.clear()
            return

        try:
            conn = mysql.connector.connect(
                host=self.conn_info['host'],
                port=self.conn_info['port'],
                user=self.conn_info['user'],
                password=self.conn_info['password'],
                database=self.conn_info['database']
            )
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {table1}")
            table1_structure = cursor.fetchall()

            cursor.execute(f"DESCRIBE {table2}")
            table2_structure = cursor.fetchall()

            columns = [col[0] for col in table1_structure if col[0] in [col[0] for col in table2_structure]]

            self.uniqueComboBox.clear()
            self.uniqueComboBox.addItems(columns)

        except mysql.connector.Error as err:
            self.handleDatabaseError(err)
        finally:
            if 'conn' in locals():
                conn.close()
            if 'cursor' in locals():
                cursor.close()

    def handleDatabaseError(self, err):
        error_code = err.errno if hasattr(err, 'errno') else None
        error_msg = str(err)
        if error_code == 1049:  # Unknown database
            QMessageBox.critical(self, 'Database Error', 'Database name is incorrect. Please check and try again.')
            self.databaseInput.clear()
        elif error_code == 1045:  # Access denied
            QMessageBox.critical(self, 'Authentication Error',
                                 'Username or password is incorrect. Please check and try again.')
            self.userInput.clear()
            self.passwordInput.clear()
        elif error_code == 2003:  # Can't connect to MySQL server
            QMessageBox.critical(self, 'Connection Error',
                                 'Host is incorrect or MySQL server is not running. Please check and try again.')
            self.hostInput.clear()
        else:
            QMessageBox.critical(self, 'Error', f'An error occurred: {error_msg}')
            self.hostInput.clear()
            self.userInput.clear()
            self.passwordInput.clear()
            self.databaseInput.clear()

    def compareTables(self):
        table1 = self.table1ComboBox.currentText()
        table2 = self.table2ComboBox.currentText()
        unique_column = self.uniqueComboBox.currentText()

        if not table1 or not table2 or not unique_column:
            QMessageBox.warning(self, 'Warning', 'Please select both tables and a unique column!')
            return

        try:
            conn = mysql.connector.connect(
                host=self.conn_info['host'],
                port=self.conn_info['port'],
                user=self.conn_info['user'],
                password=self.conn_info['password'],
                database=self.conn_info['database']
            )
            cursor = conn.cursor()

            # 获取表1和表2的结构
            cursor.execute(f"DESCRIBE {table1}")
            table1_structure = cursor.fetchall()

            cursor.execute(f"DESCRIBE {table2}")
            table2_structure = cursor.fetchall()

            # 比较表结构是否一致
            if table1_structure != table2_structure:
                differences = []
                table1_columns = {col[0]: col for col in table1_structure}
                table2_columns = {col[0]: col for col in table2_structure}
                all_columns = set(table1_columns.keys()).union(set(table2_columns.keys()))

                for col in all_columns:
                    if col not in table2_columns:
                        differences.append(f'{col} exists in {table1} but not in {table2}')
                    elif col not in table1_columns:
                        differences.append(f'{col} exists in {table2} but not in {table1}')
                    elif table1_columns[col] != table2_columns[col]:
                        differences.append(f'{col} structure mismatch')

                QMessageBox.warning(self, 'Warning',
                                    f'Table structures do not match!\nDifferences:\n' + '\n'.join(differences))
                return

            # 获取表1和表2的数据
            cursor.execute(f"SELECT * FROM {table1}")
            table1_data = cursor.fetchall()

            cursor.execute(f"SELECT * FROM {table2}")
            table2_data = cursor.fetchall()

            # 将数据存储为字典，键为主键（即第一列）
            table1_dict = {row[0]: row for row in table1_data}
            table2_dict = {row[0]: row for row in table2_data}

            # 获取主键并排序
            all_keys = sorted(set(table1_dict.keys()).union(set(table2_dict.keys())))

            # 准备结果列表
            rows = []

            # 处理匹配和不匹配的数据
            for key in all_keys:
                row1 = table1_dict.get(key)
                row2 = table2_dict.get(key)

                if row1 and row2:
                    if row1 == row2:
                        # 如果匹配，直接添加
                        rows.append((row1, row2, True))
                    else:
                        # 如果不匹配，添加不同的行
                        rows.append((row1, row2, False))
                elif row1:
                    # 左侧有数据，右侧无数据
                    rows.append((row1, None, False))
                elif row2:
                    # 右侧有数据，左侧无数据
                    rows.append((None, row2, False))

            # 按照匹配情况排序，将不匹配的放到最后
            rows.sort(key=lambda x: (x[2] == False))

            # 设置表格结构
            self.table1Widget.setColumnCount(len(table1_structure))
            self.table1Widget.setHorizontalHeaderLabels([col[0] for col in table1_structure])
            self.table1Widget.setRowCount(0)  # Clear existing data

            self.table2Widget.setColumnCount(len(table2_structure))
            self.table2Widget.setHorizontalHeaderLabels([col[0] for col in table2_structure])
            self.table2Widget.setRowCount(0)  # Clear existing data

            # 隐藏前几列
            self.table1Widget.setColumnHidden(0, True)
            self.table2Widget.setColumnHidden(0, True)
            for i in range(1, self.hidden_column_count):
                self.table1Widget.setColumnHidden(i, True)
                self.table2Widget.setColumnHidden(i, True)

            # 填充数据
            row_idx = 0
            for row1, row2, matched in rows:
                if row1 and row2 and row1 == row2:
                    continue

                if row1:
                    self.table1Widget.insertRow(row_idx)
                    for col_idx, col_value in enumerate(row1):
                        item = QTableWidgetItem(str(col_value))
                        if row2 and row2[col_idx] != col_value:
                            item.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow for differences
                        self.table1Widget.setItem(row_idx, col_idx, item)

                if row2:
                    self.table2Widget.insertRow(row_idx)
                    for col_idx, col_value in enumerate(row2):
                        item = QTableWidgetItem(str(col_value))
                        if row1 and row1[col_idx] != col_value:
                            item.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow for differences
                        self.table2Widget.setItem(row_idx, col_idx, item)

                if row1 and row2:
                    if row1 != row2:
                        for col_idx in range(len(row1)):
                            if row1[col_idx] != row2[col_idx]:
                                item1 = self.table1Widget.item(row_idx, col_idx)
                                item2 = self.table2Widget.item(row_idx, col_idx)
                                if item1:
                                    item1.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
                                if item2:
                                    item2.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
                elif row1:
                    for col_idx in range(len(row1)):
                        item1 = self.table1Widget.item(row_idx, col_idx)
                        if item1:
                            item1.setBackground(QBrush(QColor(173, 216, 230)))  # Light blue
                    self.table2Widget.insertRow(row_idx)
                    for col_idx in range(len(row1)):
                        self.table2Widget.setItem(row_idx, col_idx, QTableWidgetItem(''))
                elif row2:
                    for col_idx in range(len(row2)):
                        item2 = self.table2Widget.item(row_idx, col_idx)
                        if item2:
                            item2.setBackground(QBrush(QColor(255, 192, 192)))  # Light red
                    self.table1Widget.insertRow(row_idx)
                    for col_idx in range(len(row2)):
                        self.table1Widget.setItem(row_idx, col_idx, QTableWidgetItem(''))

                row_idx += 1

            # 调整列宽
            self.adjustColumnWidths()

            # 隐藏第一列
            # self.table1Widget.setColumnHidden(0, True)
            # self.table2Widget.setColumnHidden(0, True)

        except mysql.connector.Error as err:
            self.handleDatabaseError(err)
        finally:
            if 'conn' in locals():
                conn.close()
            if 'cursor' in locals():
                cursor.close()

    def adjustColumnWidths(self):
        # 获取列数
        num_columns = self.table1Widget.columnCount()

        for col_idx in range(num_columns):
            header_width = self.table1Widget.horizontalHeader().sectionSize(col_idx)
            new_width = header_width
            self.table1Widget.setColumnWidth(col_idx, new_width)
            self.table2Widget.setColumnWidth(col_idx, new_width)

        # 保证两个表格的列宽同步
        self.syncColumnWidths()

    def syncColumnWidths(self):
        # 确保左右两个表格列宽同步
        num_columns = self.table1Widget.columnCount()

        for col_idx in range(num_columns):
            width = self.table1Widget.columnWidth(col_idx)
            self.table2Widget.setColumnWidth(col_idx, width)

    def backupTable(self):
        table1 = self.table1ComboBox.currentText()  # 备份表
        table2 = self.table2ComboBox.currentText()  # 当前表

        if not table1 or not table2:
            QMessageBox.warning(self, 'Warning', '请先选择备份表和当前表!')
            return

        try:
            conn = mysql.connector.connect(
                host=self.conn_info['host'],
                port=self.conn_info['port'],
                user=self.conn_info['user'],
                password=self.conn_info['password'],
                database=self.conn_info['database']
            )
            cursor = conn.cursor()

            # 清空表a (可选)
            cursor.execute(f"DELETE FROM {table1}")

            # 复制表b数据到表a
            cursor.execute(f"INSERT INTO {table1} SELECT * FROM {table2}")
            conn.commit()

            # 记录备份时间
            backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.saveBackupTime(backup_time)

            QMessageBox.information(self, 'Backup', f'数据已成功备份到 {table1}.\n备份时间: {backup_time}')

        except mysql.connector.Error as err:
            self.handleDatabaseError(err)
        finally:
            if 'conn' in locals():
                conn.close()
            if 'cursor' in locals():
                cursor.close()

    def saveBackupTime(self, backup_time):
        config = self.loadConfig()
        config['last_backup_time'] = backup_time
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            QMessageBox.critical(self, 'Save Configuration', f'Error saving backup time: {e}')

    def saveConfig(self):
        config = {
            'host': self.hostInput.text(),
            'port': self.portInput.text(),
            'user': self.userInput.text(),
            'password': self.passwordInput.text(),
            'database': self.databaseInput.text(),
            'table1': self.table1ComboBox.currentText(),
            'table2': self.table2ComboBox.currentText(),
            'unique_column': self.uniqueComboBox.currentText()
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(self, 'Save Configuration', 'Configuration saved successfully.')
        except IOError as e:
            QMessageBox.critical(self, 'Save Configuration', f'Error saving configuration: {e}')

    def loadConfig(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.hostInput.setText(config.get('host', ''))
                self.portInput.setText(config.get('port', ''))
                self.userInput.setText(config.get('user', ''))
                self.passwordInput.setText(config.get('password', ''))
                self.databaseInput.setText(config.get('database', ''))
                table1 = config.get('table1', '')
                table2 = config.get('table2', '')
                unique_column = config.get('unique_column', '')

                # Load tables and unique columns after setting input values
                if self.hostInput.text() and self.userInput.text() and self.databaseInput.text():
                    self.connectToDatabase()  # Reload table list and unique columns

                self.table1ComboBox.setCurrentText(table1)
                self.table2ComboBox.setCurrentText(table2)
                self.uniqueComboBox.setCurrentText(unique_column)

                # 读取要隐藏的列数，默认为0
                self.hidden_column_count = config.get('hidden_column_count', 0)

                last_backup_time = config.get('last_backup_time', '无上次备份时间')
                QMessageBox.information(self, 'Last Backup', f'上次备份时间: {last_backup_time}')

                return config  # 确保返回的是config对象

        except FileNotFoundError:
            QMessageBox.warning(self, 'Load Configuration', 'Configuration file not found.')
        except json.JSONDecodeError:
            QMessageBox.warning(self, 'Load Configuration', 'Configuration file is corrupted or invalid.')

        return {}  # 返回一个空的字典对象

    def toggleColumnFixed(self, column_index, shift_pressed):
        if shift_pressed:
            if column_index in self.fixed_columns:
                self.fixed_columns.remove(column_index)
            else:
                self.fixed_columns.add(column_index)
            self.updateView()

    # 为 QTableWidget 的表头添加点击事件监听
    def onSectionClicked(self, column_index):
        shift_pressed = QApplication.keyboardModifiers() & Qt.ShiftModifier
        self.toggleColumnFixed(column_index, shift_pressed)

    def fixColumn(self, table, column_index):
        table.setColumnWidth(column_index, table.columnWidth(column_index))
        table.horizontalHeader().setSectionResizeMode(column_index, QHeaderView.Fixed)
        self.updateView()

    def unfixColumn(self, table, column_index):
        table.horizontalHeader().setSectionResizeMode(column_index, QHeaderView.Interactive)
        self.updateView()

    def updateFrozenColumns(self, table):
        # 通过调整顺序确保固定列在最前面
        for column_index in sorted(self.fixed_columns):
            table.horizontalHeader().moveSection(column_index, 0)

    def repositionFrozenColumns(self, table):
        # 保证固定列的位置，其他列不受影响
        for column_index in sorted(self.fixed_columns):
            table.horizontalHeader().moveSection(column_index, 0)
        # 调整固定列的宽度和表头位置
        self.updateView()

    def updateView(self):
        for table in [self.table1Widget, self.table2Widget]:
            header = table.horizontalHeader()
            header.setStretchLastSection(False)
            for column_index in range(table.columnCount()):
                if column_index in self.fixed_columns:
                    header.setSectionResizeMode(column_index, QHeaderView.Fixed)
                else:
                    header.setSectionResizeMode(column_index, QHeaderView.Interactive)

        # Update fixed columns view
        self.updateFixedColumnView()

        # Ensure all tables have uniform row height
        row_height = self.table1Widget.rowHeight(0) if self.table1Widget.rowCount() > 0 else 30
        self.setUniformRowHeight(self.table1Widget, row_height)
        self.setUniformRowHeight(self.table2Widget, row_height)
        self.setUniformRowHeight(self.fixedColumnWidget, row_height)

    def updateFixedColumnView(self):
        # Update the fixed column table with the current data
        for table in [self.table1Widget, self.table2Widget]:
            num_columns = table.columnCount()
            if not self.fixed_columns:
                self.fixedColumnWidget.clear()
                self.fixedColumnWidget.setRowCount(0)
                self.fixedColumnWidget.setColumnCount(0)
                return

            self.fixedColumnWidget.setColumnCount(len(self.fixed_columns))
            self.fixedColumnWidget.setRowCount(table.rowCount())

            # Update fixed column headers and data
            fixed_col_indices = sorted(self.fixed_columns)
            for i, col_index in enumerate(fixed_col_indices):
                self.fixedColumnWidget.setHorizontalHeaderItem(i, QTableWidgetItem(
                    table.horizontalHeaderItem(col_index).text()))
                for row in range(table.rowCount()):
                    item = table.item(row, col_index)
                    if item:
                        self.fixedColumnWidget.setItem(row, i, QTableWidgetItem(item.text()))

        # Ensure fixed column widget has uniform row height
        row_height = self.table1Widget.rowHeight(0) if self.table1Widget.rowCount() > 0 else 30
        self.setUniformRowHeight(self.fixedColumnWidget, row_height)

        self.fixedColumnWidget.resizeColumnsToContents()
        self.fixedColumnWidget.resizeRowsToContents()
        self.fixedColumnWidget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn)  # Enable horizontal scrollbar if needed
        self.fixedColumnWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fixedColumnWidget.horizontalHeader().setStretchLastSection(False)

    def syncScrollBar(self, sourceScrollBar, targetScrollBar):
        # 保持两个表格的水平滚动条同步
        targetScrollBar.setValue(sourceScrollBar.value())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MySQLTableComparator()
    ex.show()  # Show window
    sys.exit(app.exec_())
