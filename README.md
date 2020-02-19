# film_mapmaker
### Description goes here.

This module is made **entirely for coding practice** and is for the most part useless for anyone but me and my programming teacher.
It takes your coordinates, and the desired year, and by parsing locations.list outputs 10 closest films to your location.
The output is generated in an index.html file.

The map also had a third layer which demonstrates the amount of films produced in each country.
This can be toggled on and off.

### Html description
The index.html file is comprised of two parts: the **tags** and the **text** itself.

In our _index.html_, the biggest par by far is the <script></script> tag, which contains a whole lot of JS code.
This is the work of Leaflet.js.

At the beginning <!DOCTYPE html> - declares that this is an html document.
Everything in the <head> tag are things that need to be prepared before everything else.
<meta charset='UTF-8'>, for example, allows us to use all utf-8 characters in our text.
4 script tags download the JS libraries to work with later in the document,
then 6 link tags reference the .css files.

In the <body> tag there is only one thing - <div> with a reference to the folium map in it.
This is to dedicate a whole section of the page to the Folium map itself.

The last part is the giant script tag. It contains a JS version of everything we do to the map -
 add markers, circle markers, layer control, etc.

### Conclusion
This project shows us that making practical and useful maps with Python
is actually pretty easy. We can manipulate geographical information
with geopy and draw it with folium. Neat!

### Example of launch
```
Enter your latitude: 50
Enter your longitude: 20
Please input a year: 2017
HTML map created! Please open index.html in your browser.
```
![Map screenshot](https://github.com/RavenbornJB/film_mapmaker/blob/master/map_screenshot.png)