# Real Commercial Finder

Welcome to the Real Commercial Finder! This tool is designed to help you efficiently retrieve and analyze property data. For optimal results and ease of use, this project is designed to run on Google Colab, a platform that offers free access to GPUs and a consistent environment for running Jupyter Notebooks.

## How to Run the Project on Google Colab

### Step 1: Open Google Colab
Start by visiting [Google Colab](https://colab.research.google.com/).

### Step 2: Open a new Notebook
Once inside Colab:
1. Click on `File` in the top left corner.
2. Choose `New notebook`.

### Step 3: Clone the Git Repository
In the new notebook, enter the following in a code cell to clone the repository:

```python
!git clone https://github.com/RickWangPerth/realcommercial-finder.git
%cd realcommercialfinder
```

Run the cell to download the project and change the working directory.

### Step 4: Set Up the Environment

To ensure all dependencies are properly installed, copy and paste the following into a new code cell:

```python
!pip install requests beautifulsoup4 pandas
!pip install selenium
!apt-get update
!apt install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
```

Execute the cell to set up the environment.

### Step 5: Run the Script
Now, you're ready to run the `realcommercialfinder.py` script. In a new code cell, enter:

```python
!python realcommercialfinder.py
```

This will execute the script, and upon completion, your data will be stored in a CSV file.

## Collecting Your Data

After the script has finished executing, a file named `property_data.csv` will be generated. You can easily download this to your local machine from the Colab environment.

Happy property hunting!
