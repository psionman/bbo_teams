from openpyxl import load_workbook


def get_named_range_values(path: str) -> dict:
    wb = load_workbook(
        filename=path, data_only=True
    )  # data_only=True to get calculated values

    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    result = {}

    for name, defn in wb.defined_names.items():
        # Skip names that don't point to cells
        if not defn.destinations:
            continue

        values = []
        for sheet_name, coord in defn.destinations:
            ws = wb[sheet_name]
            cells = ws[coord]

            # Single cell
            if hasattr(cells, "value"):
                values.append(cells.value)

            # Multi-cell range
            else:
                for row in cells:
                    if hasattr(row, "value"):
                        # Single row
                        values.append(row.value)
                    else:
                        # Multiple rows
                        values.extend(cell.value for cell in row)
        # Store single value or list depending on how
        # many cells the name covers
        result[name] = values[0] if len(values) == 1 else values
    return result


def update_scores(path: str, scores: dict) -> None:
    wb = load_workbook(filename=path)
    for section in [1, 2]:
        for round in [1, 2, 3, 4]:
            score = scores[section][round]
            if score > 0:
                range_name = f"score_{section}_{round}_home"
            else:
                score = -1 * score
                range_name = f"score_{section}_{round}_away"
            set_named_range_value(wb, range_name, score)
    wb.save(path)


def set_named_range_value(wb, range_name: str, value):
    defined_name = wb.defined_names[range_name]
    sheet_name, cell_reference = next(defined_name.destinations)
    wb[sheet_name][cell_reference] = value
