from fastapi import FastAPI, Request, Response
from google.cloud import storage
import re,os
import uuid
app = FastAPI()

def upload_to_gcp_bucket(bucket_name, file_path, key_path, new_filename=None):
    """Uploads a file to a Google Cloud Storage bucket with an optional new filename."""
    # Instantiate a client using the service account key
    client = storage.Client.from_service_account_json(key_path)

    # Get the bucket
    bucket = client.get_bucket(bucket_name)

    # Extract the original filename from the file path
    original_filename = os.path.basename(file_path)

    # Determine the new filename
    if new_filename is None:
        new_filename = original_filename

    # Create a blob object and upload the file with the new filename
    blob = bucket.blob(new_filename)
    blob.upload_from_filename(file_path)

    print(f"File '{file_path}' uploaded to bucket '{bucket_name}' with new filename '{new_filename}' successfully!")



def clean_data(filename):
    with open(filename, 'r') as file:
        content = file.read()

    # Remove \n using regex
    content = re.sub(r'\n', '', content)

    with open(filename, 'w') as file:
        file.write(content)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/handle-button-click")
async def handle_button_click(request: Request):
    filename="default"
    json_data = await request.json()        

    # Save the JSON data as a text file
    with open("received_data.json", "w") as file:
        file.write(str(json_data))
    bucket_name = "checked_upload"
    f = open("received_data.json", "r")
    text_s=f.readline()
    match = re.search(r'"http://localhost:8000/work/([^"]+)"', text_s)
    if match:
        file_name = match.group(1)
        new_filename= file_name
    else:
        new_filename = str(uuid.uuid1())
    
    clean_data("received_data.json")
    # print(extracted_value)
    file_path = "received_data.json"
    key_path = "compfox-key.json"
    # new_filename = uuid.uuid1()
    # new_filename=file_name

    # # Example usage
    # json_file = 'listing_user2.json'
    # id_to_update = file_name
    # new_status = 'success'
    # try:
    #     update_status(json_file, id_to_update, new_status)
    # except:
    #     logging.warning("Could not update status...")

    upload_to_gcp_bucket(bucket_name, file_path, key_path,new_filename)

    return Response(status_code=200)
