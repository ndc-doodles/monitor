import cloudinary.uploader
from django.conf import settings

def upload_to_cloudinary(images):
    uploaded_images = []
    
    for image in images:
        image_file = image.get('file')  # Ensure the image file is passed in the data
        
        if image_file:
            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(image_file)
            
            uploaded_images.append({
                'url': upload_result.get('secure_url'),
                'public_id': upload_result.get('public_id')
            })
    
    return uploaded_images
