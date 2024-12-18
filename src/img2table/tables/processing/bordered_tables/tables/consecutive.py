# coding: utf-8
from typing import List

from img2table.tables.objects.cell import Cell
from img2table.tables.objects.table import Table


def merge_consecutive_tables(tables: List[Table], contours: List[Cell]) -> List[Table]:
    """
    Merge consecutive coherent tables
    :param tables: list of detected tables
    :param contours: list of image contours
    :return: list of processed tables
    """
    if len(tables) == 0:
        return []

    # Create table clusters
    seq = iter(sorted(tables, key=lambda t: t.y1))
    clusters = [[next(seq)]]

    for tb in seq:
        prev_table = clusters[-1][-1]
        # Check if there are elements between the two tables
        in_between_contours = [c for c in contours if c.y1 >= prev_table.y2 and c.y2 <= tb.y1
                               and c.x2 >= min(prev_table.x1, tb.x1)
                               and c.x1 <= max(prev_table.x2, tb.x2)]
        
        # Check table structure compatibility
        prev_tb_cols = sorted([l for l in prev_table.lines if l.vertical], key=lambda l: l.x1)
        tb_cols = sorted([l for l in tb.lines if l.vertical], key=lambda l: l.x1)
        
        # Check if tables have similar boundaries (allowing for merged cells)
        left_aligned = abs(prev_table.x1 - tb.x1) <= 10
        right_aligned = abs(prev_table.x2 - tb.x2) <= 10
        
        # Check vertical spacing
        vertical_spacing = tb.y1 - prev_table.y2
        max_spacing = min(prev_table.height, tb.height) * 0.3  # Reduced from 0.5 to be more strict
        
        # Tables should be merged if they are aligned and close enough
        should_merge = (len(in_between_contours) == 0 and
                       left_aligned and right_aligned and
                       vertical_spacing < max_spacing)
        
        if not should_merge:
            clusters.append([])
        clusters[-1].append(tb)

    # Create merged tables
    merged_tables = list()
    for cl in clusters:
        if len(cl) == 1:
            merged_tables += cl
        else:
            # Create new table
            new_tb = Table(rows=[row for tb in cl for row in tb.items], borderless=False)
            merged_tables.append(new_tb)

    return merged_tables
