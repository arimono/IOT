from connection import dbCre

allowed_tables = ["sensor", "demo"]  
allowed_columns = {
        "sensor": ["temp", "humidity"],
        "demo": ["message"]
    }
def checkTables(table_name):
    if table_name not in allowed_tables:
        raise ValueError(f"Invalid table name: {table_name}")
    
def checkCol(table_name,columns):
    if table_name in allowed_columns:
        for col in columns:
            if col not in allowed_columns[table_name]:
                raise ValueError(f"Invalid column: {col} for table {table_name}")
    else:
        raise ValueError(f"No column definition for table: {table_name}")

def update(table_name, columns, values):
    
    checkTables(table_name)
    checkCol(table_name, columns)
    sqlCursor = dbCre.cursor()
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(values))
    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    sqlCursor.execute(sql, values)
    dbCre.commit()
    print(sqlCursor.rowcount, "record inserted.")

def selectAll(table_name):
    checkTables(table_name)
    sqlCursor = dbCre.cursor(buffered=True)
    sqlCursor.execute(f"Select * from {table_name}")
    dbCre.close()
    return sqlCursor
