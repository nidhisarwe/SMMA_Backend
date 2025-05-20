import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary
cloudinary.config(
    cloud_name="dgk4su3ne",
    api_key="358123544468283",
    api_secret="hMVxeTmAvRCgOY_0dxxTWcEoPQg"
)

# Function to upload image to Cloudinary and get URL
def upload_image_to_cloudinary(image_path):
    try:
        response = cloudinary.uploader.upload(image_path)
        return response['url']
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None
