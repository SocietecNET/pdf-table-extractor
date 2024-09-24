import xml.etree.ElementTree as ET

def get_images_from_svg(svg_content):
    root = ET.fromstring(svg_content)
    namespaces = {'xlink': 'http://www.w3.org/1999/xlink'}
    base64_images = []
    for image in root.findall('.//{http://www.w3.org/2000/svg}image', namespaces):
        href = image.get('{http://www.w3.org/1999/xlink}href')
        if href and href.startswith('data:image'):
            base64_images.append(href.split(',')[1])

    return base64_images