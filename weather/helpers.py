# -*- coding: utf-8 -*-



def weather_reading_to_report_line(reading, sep):
    data = [reading.station,
            str(reading.local_time),
            str(reading.latitude),
            str(reading.longitude),
            reading.conditions.name,
            str(reading.temperature),
            str(reading.pressure),
            str(reading.humidity)]
    return sep.join(data)


def write_data(data, output_file, line_processor):
    with open(output_file, 'w') as f:
        for record in data:
            line_processor(line_processor(record) + '\n')



