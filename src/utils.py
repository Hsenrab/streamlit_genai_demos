def pdftoimages(pdf_path):
    
    pdf_document = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        
        # Save image locally
        output_dir = "output_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        image_path = os.path.join(output_dir, f'{pdf_name}_page{page_num}.jpg')
        pix.save(image_path)
        
        image_paths.append(image_path)
        
    return image_paths


def create_data_url(image_path):
    binary_fc       = open(image_path, 'rb').read()
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')

    ext= image_path.split('.')[-1]
    dataurl = f'data:image/{ext};base64,{base64_utf8_str}'
    
    return dataurl