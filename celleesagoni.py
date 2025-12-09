import math
import os

# --- CONFIGURAZIONE ---
# Coordinate fornite: 
# Lat: 39°28'24.17"N
# Lon: 0°20'13.20"O (Ovest)

# Conversione in decimali:
SITE_LAT =39.486828
SITE_LON = -0.338314

SITE_NAME = "Nuovo_Sito_Algiros"
RAGGIO = 229  # Raggio della cella in metri
FILENAME = "sito_trisettoriale_8.kml"

# --- FUNZIONI DI CALCOLO ---

def get_destination_point(lat, lon, distance_meters, bearing_degrees):
    """
    Calcola un nuovo punto data una distanza e un angolo (azimuth)
    dal punto di partenza.
    """
    R_EARTH = 6378137 # Raggio terra in metri
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_degrees)
    
    new_lat = math.asin(math.sin(lat_rad) * math.cos(distance_meters / R_EARTH) +
                        math.cos(lat_rad) * math.sin(distance_meters / R_EARTH) * math.cos(bearing_rad))
    
    new_lon = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(distance_meters / R_EARTH) * math.cos(lat_rad),
                                   math.cos(distance_meters / R_EARTH) - math.sin(lat_rad) * math.sin(new_lat))
    
    return (math.degrees(new_lat), math.degrees(new_lon))

def get_hex_coords(center_lat, center_lon, radius):
    """Genera le coordinate del perimetro dell'esagono."""
    coords = ""
    
    # Angolo impostato a 0 affinché il vertice punti verso il centro,
    # permettendo l'incastro a trifoglio.
    start_angle = 0 
    
    points = []
    for i in range(6):
        angle = 60 * i + start_angle
        pt = get_destination_point(center_lat, center_lon, radius, angle)
        points.append(pt)
    points.append(points[0]) # Chiudi il poligono
    
    for p in points:
        coords += f"{p[1]},{p[0]},0 "
    return coords

def create_kml_header():
    return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Sito Tri-Settoriale (Fit Perfetto)</name>
    
    <!-- Stile Esagono -->
    <Style id="hexStyle">
      <LineStyle>
        <color>ff0000ff</color> <!-- Rosso -->
        <width>2</width>
      </LineStyle>
      <PolyStyle>
        <color>200000ff</color> <!-- Rosso trasparente -->
      </PolyStyle>
    </Style>
    
    <!-- Stile Frecce -->
    <Style id="arrowStyle">
      <LineStyle>
        <color>ff00ffff</color> <!-- Giallo -->
        <width>4</width>
      </LineStyle>
    </Style>

    <!-- Stile Sito -->
    <Style id="siteStyle">
      <IconStyle>
        <scale>1.1</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/triangle.png</href>
        </Icon>
      </IconStyle>
    </Style>
"""

def create_sector(site_lat, site_lon, azimuth, sector_id):
    # 1. Calcoliamo il CENTRO dell'esagono (cella)
    hex_center = get_destination_point(site_lat, site_lon, RAGGIO, azimuth)
    
    # 2. Generiamo l'esagono attorno a quel centro
    hex_geometry = get_hex_coords(hex_center[0], hex_center[1], RAGGIO)
    
    # 3. Creiamo la freccia dal sito al centro cella
    arrow_coords = f"{site_lon},{site_lat},0 {hex_center[1]},{hex_center[0]},0"
    
    return f"""
    <Folder>
      <name>Settore {sector_id} (Az {azimuth}°)</name>
      <Placemark>
        <name>Cella {sector_id}</name>
        <styleUrl>#hexStyle</styleUrl>
        <Polygon>
          <outerBoundaryIs><LinearRing><coordinates>{hex_geometry}</coordinates></LinearRing></outerBoundaryIs>
        </Polygon>
      </Placemark>
      <Placemark>
        <styleUrl>#arrowStyle</styleUrl>
        <LineString>
          <coordinates>{arrow_coords}</coordinates>
        </LineString>
      </Placemark>
    </Folder>
    """

def main():
    kml = create_kml_header()
    
    # Sito Centrale
    kml += f"""
    <Placemark>
      <name>{SITE_NAME}</name>
      <styleUrl>#siteStyle</styleUrl>
      <Point>
        <coordinates>{SITE_LON},{SITE_LAT},0</coordinates>
      </Point>
    </Placemark>
    """
    
    # I 3 Settori (Nord: 0°, Sud-Est: 120°, Sud-Ovest: 240°)
    azimuths = [0, 120, 240]
    
    for i, az in enumerate(azimuths):
        kml += create_sector(SITE_LAT, SITE_LON, az, i+1)
        
    kml += "</Document></kml>"
    
    with open(FILENAME, "w") as f:
        f.write(kml)
    
    # Apertura e info
    full_path = os.path.abspath(FILENAME)
    print("\n" + "="*50)
    print(f"SALVATO IN: {full_path}")
    print("="*50 + "\n")
    
    try:
        # Tenta di aprire il file automaticamente (funziona su Windows)
        os.startfile(FILENAME)
    except AttributeError:
        # Fallback per Linux/Mac
        try:
            import subprocess
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, FILENAME])
        except:
            print(f"File creato. Apri manualmente: {FILENAME}")

if __name__ == "__main__":
    main()