import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag_id, value in info.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_data[sub_tag] = value[t]
                exif_data[tag] = gps_data
            else:
                exif_data[tag] = value
    return exif_data

def get_decimal_coordinates(info):
    def convert_to_degrees(value):
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1] / 60.0
        s = value[2][0] / value[2][1] / 3600.0
        return d + m + s

    lat = lon = None
    if "GPSLatitude" in info and "GPSLatitudeRef" in info:
        lat = convert_to_degrees(info["GPSLatitude"])
        if info["GPSLatitudeRef"] != "N":
            lat = -lat

    if "GPSLongitude" in info and "GPSLongitudeRef" in info:
        lon = convert_to_degrees(info["GPSLongitude"])
        if info["GPSLongitudeRef"] != "E":
            lon = -lon

    return (lat, lon) if lat and lon else None

st.title('Photo Location Visualizer')

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    exif_data = get_exif_data(image)
    
    if 'GPSInfo' in exif_data:
        coordinates = get_decimal_coordinates(exif_data['GPSInfo'])
        if coordinates:
            st.write(f"Coordinates: {coordinates}")

            m = folium.Map(location=coordinates, zoom_start=10)
            folium.Marker(coordinates, popup="Photo Location").add_to(m)
            folium_static(m)
        else:
            st.write("No GPS coordinates found in the image.")
    else:
        st.write("No EXIF data found in the image.")