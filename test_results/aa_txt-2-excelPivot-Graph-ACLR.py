import tkinter as tk
from tkinter import filedialog
import win32com.client as win32

def main():
    # File dialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls *.txt")]
    )

    if not file_path:
        print("No file selected")
        return

    # Open Excel
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = True

    wb = excel.Workbooks.Open(file_path)
    ws = wb.Sheets(1)

    # -----------------------------------
    # Step 1: Text to Columns (Column A)
    # -----------------------------------
    ws.Columns("A:A").TextToColumns(
        Destination=ws.Range("A1"),
        DataType=1,                 # xlDelimited
        TextQualifier=1,            # xlTextQualifierDoubleQuote
        Comma=True
    )

    # Detect last row / col
    last_row = ws.Cells(ws.Rows.Count, 1).End(-4162).Row        # xlUp
    last_col = ws.Cells(4, ws.Columns.Count).End(-4159).Column  # xlToLeft

    data_range = ws.Range(ws.Cells(4, 1), ws.Cells(last_row, last_col))
    # data_range.Interior.Color = 6553  # Yellow

    # -----------------------------------
    # Step 2: Create Pivot Table
    # -----------------------------------
    pivot_sheet = wb.Sheets.Add()
    pivot_sheet.Name = "PivotTable"

    pivot_cache = wb.PivotCaches().Create(SourceType=1, SourceData=data_range)
    pivot_table = pivot_cache.CreatePivotTable(
        TableDestination=pivot_sheet.Cells(4, 1),
        TableName="ACLR_Pivot"
    )

    # Fields
    pivot_table.PivotFields("Power[dBm]").Orientation = 1   # xlRowField
    pivot_table.PivotFields("Leveling").Orientation = 2     # xlColumnField
    pivot_table.PivotFields("VSA_extra").Orientation = 2    # xlColumnField
    pivot_table.PivotFields("VSG_extra").Orientation = 2    # xlColumnField
    pivot_table.PivotFields("Freq").Orientation = 2         # xlColumnField

    pivot_table.AddDataField(
        pivot_table.PivotFields("ACLR_adj-[dBc]"),
        "Sum of ACLR_adj-[dBc]",
        -4157  # xlSum
    )

    # Turn off grand totals
    pivot_table.RowGrand = False
    pivot_table.ColumnGrand = False

    # Turn off subtotals
    for field in pivot_table.PivotFields():
        if field.Orientation in [1, 2]:
            field.Subtotals = (False,) * 12

    # -----------------------------------
    # Step 3: Create Chart
    # -----------------------------------
    chart_obj = pivot_sheet.ChartObjects().Add(400, 50, 800, 400)
    chart = chart_obj.Chart

    pivot_range = pivot_sheet.Range("A4").CurrentRegion
    chart.SetSourceData(pivot_range)

    chart.ChartType = 4  # xlLine

    # Legend at bottom
    chart.HasLegend = True
    chart.Legend.Position = -4107           # xlLegendPositionBottom
    chart.HasTitle = True
    chart.ChartTitle.Text = "ACLR vs Power"

    # X-axis settings
    x_axis = chart.Axes(1)                  # xlCategory axis
    x_axis.HasMajorGridlines = True         # Gridlines on
    x_axis.TickMarkSpacing = 5              # Tick marks every 5 units

    # Y-axis settings
    y_axis = chart.Axes(2)                  # xlValue axis
    y_axis.MinimumScale = -60
    y_axis.MaximumScale = -20
    y_axis.CrossesAt = -100

    output_path = file_path.replace(".txt", ".xlsx")
    wb.SaveAs(output_path, FileFormat=51)

    print("✅ Pivot table and chart created successfully!")

if __name__ == "__main__":
    main()
