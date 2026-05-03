\# Image Filter App (Semester Project)





\## Description



This project is a Python-based image filtering application that allows users to apply different visual effects to an image. The program demonstrates object-oriented programming concepts such as inheritance by implementing a base filter class and multiple derived filter classes.







\## Features



\* Grayscale filter

\* Blur filter

\* Edge detection filter

\* Cartoonify filter

\* Resizable GUI window with dynamic image scaling







\## Technologies Used



\* Python 3.14.4

\* OpenCV

\* NumPy

\* Pillow (PIL)

\* Tkinter (for GUI)







\## Installation



1\. Clone the repository:



```bash

git clone https://github.com/ShaneMilner/SemesterProject.git

cd SemesterProject

```



2\. Create and activate a Conda environment:



```bash

conda create -n imagefilter python=3.14

conda activate imagefilter

```



3\. Install dependencies:



```bash

pip install -r requirements.txt

```



\## How to Run



Run the main program:



```bash

python src/Milner_CS3080_SemesterProject.py

```



Then:



\* Open an image

\* Select a filter

\* View the processed output in the window







\## Project Structure



```

SemesterProject/

│

├── src/

│   └── Milner_CS3080_SemesterProject.py

│

├── images/

│   └── sample.jpg

│

├── README.md

├── requirements.txt

├── .gitignore

```







\## Concepts Demonstrated



\* Object-Oriented Programming (OOP)

\* Inheritance and polymorphism

\* Image processing techniques

\* GUI development in Python







\## Known Issues



\* Cartoonify filter may not produce highly stylized results on all images

\* Very large images may impact performance







\## Future Improvements



\* Add more advanced filters (AI-based cartoon effects)

\* Improve UI layout and responsiveness

\* Improve export options (additional formats, compression settings)







\## Author



Randall Milner







\## License



This project is for educational purposes.



