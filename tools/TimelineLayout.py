"""Pure interval packing for timelines; timestamps and input order stay intact."""


def layout_timeline_records(records, x_for_time, measure_text, *,
                            label_for_record=None, secondary_for_record=None,
                            end_x_for_record=None, gap=8, icon_width=20):
    label_for_record = label_for_record or (lambda record: record.get('skillname', ''))
    items = []
    for index, record in enumerate(records):
        x = float(x_for_time(record['start']))
        widths = [float(icon_width), float(measure_text(str(label_for_record(record))))]
        if secondary_for_record is not None:
            widths.append(float(measure_text(str(secondary_for_record(record)))))
        half = max(widths) / 2
        left, right = x - half, x + half
        if end_x_for_record is not None:
            right = max(right, float(end_x_for_record(record)))
        items.append(dict(record=record, index=index, x=x, left=left, right=right))
    lane_ends = []
    for item in sorted(items, key=lambda row: (row['left'], row['x'], row['index'])):
        lane = next((i for i, end in enumerate(lane_ends)
                     if end + gap <= item['left']), len(lane_ends))
        if lane == len(lane_ends):
            lane_ends.append(item['right'])
        else:
            lane_ends[lane] = item['right']
        item['lane'] = lane
    return dict(items=items, laneCount=len(lane_ends),
                minX=min((row['left'] for row in items), default=0),
                maxX=max((row['right'] for row in items), default=0))
