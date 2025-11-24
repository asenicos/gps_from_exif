import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from urllib.parse import quote
    
def dms_to_decimal(dms, ref):
    """Преобразование координат из формата DMS в десятичный формат."""
    degrees = dms[0]  # Градусы
    minutes = dms[1] / 60.0  # Минуты в градусы
    seconds = dms[2] / 3600.0  # Секунды в градусы
    decimal_degrees = degrees + minutes + seconds
    
    # Проверка на северное/восточное (положительное) или южное/западное (отрицательное) направление
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def get_gps_info(image_path):
    """Извлечение GPS-данных из изображения."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None
        
        gps_info = {}
        for tag, value in exif_data.items():
            if TAGS.get(tag) == 'GPSInfo':
                for key in value.keys():
                    decoded = GPSTAGS.get(key, key)
                    gps_info[decoded] = value[key]
                break
        
        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = dms_to_decimal(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
            lon = dms_to_decimal(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
            return lat, lon
        
    except Exception as e:
        print(f"Ошибка при обработке файла {image_path}: {e}")
    
    return None

def read_gps_data_from_directory(directory):
    """Чтение GPS-данных из всех JPEG-изображений в каталоге и подкаталогах."""
    gps_data = []
    
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(('.jpg', '.jpeg')):  # Поддержка .jpg и .jpeg
                image_path = os.path.join(dirpath, filename)
                gps_coordinates = get_gps_info(image_path)
                if gps_coordinates:
                    gps_data.append((image_path, gps_coordinates[0], gps_coordinates[1]))
    return gps_data

def save_gps_data_to_file(gps_data, output_file):
    """Сохранение GPS-данных в текстовый файл."""
    with open(output_file, 'w') as f:
        for file_path, lat, lon in gps_data:
            f.write(f"{file_path}: Latitude: {lat}, Longitude: {lon}\n")

def main():
    directory = "d:\\my_site\\asenic.ru\\photo"
    output_txt_file = "d:\\2020\\gps.txt"
    output_file = "d:\\2020\\gps.htm"

    gps_data = read_gps_data_from_directory(directory)

   
    # Сохраняем GPS данные в текстовый файл
    save_gps_data_to_file(gps_data, output_txt_file)

    print(f"GPS координаты успешно сохранены в файл {output_txt_file}")
    
    """Генерация HTML файла с картой OpenStreetMap и GPS координатами."""
    with open(output_file, 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>GPS Coordinates Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        #map { height: 600px; }
    </style>
</head>
<body>
    <h1>GPS Coordinates Map</h1>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([0, 0], 2); // Начальная позиция карты

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);
''')
        for file_path, lat, lon in gps_data:
        # Заменяем обратные слеши на прямые для корректного URL
            file_path = file_path.replace("d:\\my_site\\" , "http://")
            file_path = file_path.replace('\\', '/')    
            # Отладка: выводим закодированный путь
            print(f"Encoded file path: {file_path}")

            f.write(f'''
                    var marker = L.marker([{lat}, {lon}]).addTo(map)
                .bindPopup('<a href="{file_path}" target="_blank">Открыть изображение</a>');
            ''')
    
        f.write('''
    </script>
</body>
</html>
''')

if __name__ == "__main__":
    main()


