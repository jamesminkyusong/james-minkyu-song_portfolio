import asl_classifier.util as util
import numpy as np
import pandas as pd
from PIL import Image

# load image files
def load_image_paths():
    directory_path = util.get_path("dataset", "asl_data")
    all_iamge_files = util.list_all_files(directory_path)
    return all_iamge_files

# load labels by path, the letter is the parent folder name, the person is the grandparent folder name
def label_image_path(image_path):
    parts = image_path.split("\\") # change for mac os
    letter = parts[-2]
    person = parts[-3]
    return letter, person

# read image with PIL, return image object
def read_image(image_path):
    return Image.open(image_path)

# resize image to 28 by 28 pixels
def resize_image(image):
    return image.resize((28, 28))

# convert image to grayscale
def shift_to_grayscale(image):
    return image.convert("L")

# save images as numpy arrays
def convert_to_np_arr(image):
    return np.array(image).flatten()

def preprocess_image(n, image_path):
    image = read_image(image_path)
    curr_letter, curr_person = label_image_path(image_path)
    resized_image = resize_image(image)
    grayscaled_image = shift_to_grayscale(resized_image)
    image_np_arr = convert_to_np_arr(grayscaled_image)
    image_post_data = [str(n).zfill(6), curr_letter, curr_person]
    image_post_data.extend(image_np_arr.tolist())
    return image_post_data

def preprocess_image_folder():
    images = load_image_paths()
    all_rows = []
    for n, image in enumerate(images):
        curr_image_data = preprocess_image(n, image)
        all_rows.append(curr_image_data)

    return all_rows


def main():
    all_rows = preprocess_image_folder()
    df = pd.DataFrame(all_rows)
    util.write_to_csv(df, "output", "asl_preprocess_post")

if __name__ == "__main__":
    main()