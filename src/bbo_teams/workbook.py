from openpyxl import load_workbook


def get_named_range_values(path: str) -> dict:
    wb = load_workbook(
        filename=path, data_only=True
    )  # data_only=True to get calculated values
    result = {}

    for name, defn in wb.defined_names.items():
        # Skip names that don't point to cells
        if not defn.destinations:
            continue

        values = []
        for sheet_name, coord in defn.destinations:
            ws = wb[sheet_name]
            cells = ws[coord]

            # Handle single cell vs range
            if hasattr(cells, "value"):  # single Cell
                values.append(cells.value)
            else:  # tuple of cells / rows
                for row in cells:
                    if hasattr(row, "value"):  # single row of cells
                        values.append(row.value)
                    else:  # multiple rows
                        values.append([c.value for c in row])

        # Store single value or list depending on how many cells the name covers
        result[name] = values[0] if len(values) == 1 else values

    return result
