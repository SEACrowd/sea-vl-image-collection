
# Image Bulk Submission Guide

If you have many images to contribute to SEAVL, you are welcome to refer to this guide for bulk upload to the [SEA-VL image collection Github Repo](https://github.com/SEACrowd/sea-vl-image-collection ).

## UI Tool-based Upload

There is now a UI tool that can help make the process of adding in the image descriptions and generating the required CSVs much easier.

1. Fill out your details in the `contributor_details.yaml` file. You only need to do this the first time.
2. Place images in the `./to_upload` folder as follows:
	* Any individual images may be kept directly in the `./to_upload` folder
	* If submitting multiple images that are very closely related to each other (for example, the same object or food photographed from multiple angles or with different levels of zoom), place all such images in a single sub-folder within the `./to_upload` folder
3. Run `process_and_label.py`:
	* if the csv (`seavl_batch_labels - YOUR NAME.csv`) already exists, the script will warn you: type in `y` to continue, and the script will append to the existing csv. *IMPORTANT:* if you have already submitted the csv, type in `n`, manually delete the csv, and restart the script; otherwise, duplicate entries will be created in subsequent steps of the SEA-VL pipeline
	* for each image shown, fill in the English and native language boxes, and click next. The following will happen:
		* a new line will be added to the csv
		* the image (or all the images, if the image shown was part of a sub-folder) will be added to the `../data` folder after being processed (resized and renamed as required)
		* the image or sub-folder will be moved into the `./processing_complete` folder
4. Submit your hard work! Thank you for you contribution:
	* raise a PR with the new images added into the `../data/` folder
	* send us the `seavl_batch_labels - YOUR NAME.csv` CSV through discord / email and we will review the CSV and images. If there is no issue, we will push the photos to the annotation platform


## Manual Upload

1. Upload the images to the `data` folder in this [repo](https://github.com/SEACrowd/sea-vl-image-collection).
	 - ⚠️ Please follow the current naming convention, each photo file should be named as `{file_name} - {your_name}.{extension}`.

	 - ⚠️ Keep the maximum image width/height to 2000px, so you might need to resize some images, you can use the following code to resize the image.
		```
		from PIL import Image
		image = Image.open(input_path)
		(w, h) = image.size
		if w > 2000 or h > 2000:
		    if w > h:
		        h = int(h * 2000. / w) 
		        w = 2000 
		    else:
		        w = int(w * 2000. / h)
		        h = 2000
		image = image.resize((w, h), Image.BILINEAR) 
		image.save(output_path)
		```
2. Use the CSV sample ([link](https://www.dropbox.com/scl/fi/xiae0op7nj58ajt1l2yky/seavl_bulk_upload_format.csv?rlkey=izd3c28vy0b35grc1utykoxsk&dl=0)) to provide more details on the submitted photos. 
	- ⚠️ Keep the empty column as empty.
	- ⚠️ For the `email` column just fill it with seacrowd.research@gmail.com.
	- ⚠️ For the `image` column, please fill it with `https://raw.githubusercontent.com/SEACrowd/sea-vl-image-collection/refs/heads/main/data/%7Bfile_name%7D`. `file_name` should be the same as the one you submitted to the repository.
3.  As the last step, you can send us the CSV through Discord / email (contact.ruochen@gmail.com or samuel.cahyawijaya@gmail.com) and we will review the CSV and images. If there is no issue, we will push the photos to the annotation platform.

**Any questions?** Message `@rc.z` or `@samuelcahyawijaya` on [Discord](https://discord.gg/URdhUGsBUQ)!
