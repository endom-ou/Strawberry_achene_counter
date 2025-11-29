# Strawberry Achene Counter

This is a simple web application that estimates the number and density of achenes from RGB images of strawberry fruits.

## Basic Functions

- Upload images of strawberry fruits
- Automatic detection of strawberry fruits and achenes through image analysis
- Calculation of achenes density
- Scale adjustment based on a 1cm square blue sticker or piece of paper (please include a sticker/paper in the image)

## Requirements

- Python 3.7 or higher
- OpenCV
- Flask
- NumPy

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/strawberry-archine-counter.git
cd strawberry-archine-counter
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python app.py
```

4. Open your browser and go to http://localhost:5000

## Usage

1. Prepare an RGB image showing a strawberry fruit and a 1 cm square blue sticker (or a piece of paper).
2. Upload the image for analysis to the web application.
3. Display the analysis results (number of achenes, fruit surface area, and achenes density).
*Note that the fruit surface area does not take into account the roundness of the fruit surface.
*In case you are unable to analyze the image properly, please adjust the fruit and achenes detection parameters.  

## Recommended Image Requirements

- Supported formats: PNG, JPG, JPEG
- Maximum file size: 16MB
- RGB
- A blue 1cm square sticker or paper should be placed as a scale reference
- The strawberry fruit should be clearly visible (preferably photographed on a uniform background such as a desk)

##Technical Specifications

- Backend: Flask (Python)
- Image Processing: OpenCV
- Color Space Conversion: Color detection in HSV color space
- Morphological Processing: Noise removal and edge detection

## License

Apache License Version 2.0

## Author

遠藤みのり Minori Hikawa-Endo
Okayama University
endom@okayama-u.ac.jp
