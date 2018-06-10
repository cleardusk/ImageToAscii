## Intro
This is a simple, light and optimized image-to-ascii converter. I implement it for fun.

## Usage

`-f | --file` is input image path.

`-s | --scale` controls the output size.

`-a | --aspect` controls the aspect of height and width.

`-w | --write-file` is the output ascii txt path.

```
# lazy style: the default output is ${img_file}.txt
python img_to_sacii.py -f imgs/erke.jpg

# adjust sampling step, the output is larger if it is samller
python img_to_sacii.py -f imgs/erke.jpg -s 2

# complete style
python img_to_sacii.py -f imgs/erke.jpg -s "auto" -w out.txt
```

## Samples
<p align="center">
    <img src="imgs/kenan_screen.jpg", width="800px">
</p>

<p align="center">
    <img src="imgs/chijing_screen.jpg", width="800px">
</p>

<p align="center">
    <img src="imgs/erke_screen.jpg", width="800px">
</p>

## Notes
You can adjust the font size of text editor for better view.

