import folium as fl
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy import distance
from resources import country_names, popular_countries, country_locations


def do_geocode(geopy_object: object, address: str):
    """ object, str -> str

    Does geocode. This functions retries the requsset if a timeout occured.
    This will happen until the request goes through successfully.
    """
    try:
        return geopy_object.geocode(address)
    except GeocoderTimedOut:
        return do_geocode(geopy_object, address)


def read_locations(desired_year: int, filename: str):
    """ int, str -> dict, dict

    Returns a dictionary of {'title': {set_of_locations}, ...}
    Films in the dictionary are only from the desired_year.

    Also returns a dictionary of {'country': num_of_films, ...}
    This does not depend on the year and is a total count.

    This function is created to read the locations.list file,
    and may not work for reading other files.
    Consider modifying it.
    """
    desired_year = str(desired_year)
    film_info = {}
    country_film_count = {}

    with open(filename, encoding='iso-8859-1') as locs:
        file = locs.readlines()

    for line in file[15:-2]:
        line = line.rstrip().split('\t')
        line = [item for item in line if item]

        info = line[0]
        location = line[1]
        country = location.split(', ')[-1]
        country_film_count[country] = country_film_count.get(country, 0) + 1

        year_start = info.find('(')
        year = info[year_start + 1: year_start + 5]
        if not year.isdigit() or year != desired_year:
            continue
        year = int(year)

        title = info[:year_start - 1]
        if title not in film_info:
            film_info[title] = set()
        film_info[title].add(location)

    return film_info, {country: country_film_count[country] for country in country_film_count if country_film_count[country] > 10}


def coordinate_finder(geopy_object: object, location: str):
    """ str -> tuple

    Returns the coordinates of the location as provided by
    the Geopy module.

    geopy_object is a geopy.geocoders.Nominatim object
    that you have to create first.
    """
    location = location.split(', ')
    while len(location) > 1:
        coordinates = do_geocode(geopy_object, ', '.join(location))
        if coordinates is None:
            location = location[1:]
        else:
            break

    lat = coordinates.latitude
    long = coordinates.longitude

    return (lat, long)


def main(pos: tuple, year: int, geopy_object: object, locations: dict):
    """ tuple, int, object, dict -> list

    Returns a list of ten (or less) films of a given year closest to you.
    Every film entry looks like ('title', dist_from_you, (lat, long))

    geopy_object is a geopy.geocoders.Nominatim object
    that you have to create first.
    """
    closest_films = []

    geo_pos = f'{pos[0]}, {pos[1]}'
    your_location = str(geopy_object.reverse(geo_pos, language='en')).split(', ')
    country = your_location[-1]
    country = country_names.get(country, country)
    if len(your_location) > 3:
        second_factor = your_location[-2] if not your_location[-2].isdigit() else your_location[-3]
    else:
        second_factor = None

    for film in locations:
        for loc in locations[film]:
            data = loc.split(', ')
            if len(data) < 3:
                continue
            second = data[-2] if not data[-2].isdigit() else data[-3]

            if data[-1] == country:
                if second_factor is not None and country in popular_countries and second != second_factor:
                    continue
                coordinates = coordinate_finder(geopy_object, loc)
                dist = float(str(distance.distance(pos, coordinates))[:-3])
                closest_films.append((film, dist, coordinates))

    closest_films.sort(key=lambda x: x[1])
    closest_films = closest_films[:10]
    return closest_films


def revise_films(film_list: list):
    """ list -> list

    Modifies the input list. The new list looks like ['title', (lat, long)].

    If any number of films happen to share the same locations, this function
    will shift their latitudes by 0.0001 degrees each
    until no films are in the same spot.
    """
    revised_film_list = []
    distances = []
    for film in film_list:
        title = film[0]
        repetitions = distances.count(film[1])
        coordinates = (film[2][0], film[2][1] + repetitions / 10000)
        distances.append(film[1])
        revised_film_list.append((title, coordinates))
    return revised_film_list


def create_map(position: tuple, films: list, countries: dict):
    """ tuple, list, dict -> None

    Creates a folium lib map of your position.
    On the map are markers of all films in your films list.

    This map also has an additional layer where
    every country has a CircleMarker in the middle.
    The radius and color of the marker correspond to the
    total number of films made in that country (from locations.list)

    The map is then saved in index.html in your working directory.
    """
    world = fl.Map(location=position, zoom_start=9)
    fl.Marker(
          location=position,
          tooltip='Your location',
          icon=fl.Icon(color='red', icon='cloud', icon_color='white')
    ).add_to(world)

    ff = fl.FeatureGroup(name='Top 10 closest films')
    for film in films:
        ff.add_child(fl.Marker(
              location=film[1],
              popup=f'<i>{film[0]}</i>',
              tooltip='Film location'
        ))
    world.add_child(ff)

    fc = fl.FeatureGroup(name="Film count")
    for country in countries:
        if country in country_locations:
            fc.add_child(fl.CircleMarker(
                     location=country_locations[country],
                     radius=countries[country]/5000,
                     popup=country,
                     color=color(countries[country]),
                     fill=True,
                     fill_color=color(countries[country])
            ))
    world.add_child(fc)

    world.add_child(fl.LayerControl())

    world.save('index.html')


def color(num: int):
    """ int -> str

    This function corresponds an integer number to a color.

    (-inf, 10000000) - green.
    [10000000, 20000000) - orange.
    [20000000, +inf) - red.
    """
    if num < 1000:
        return 'blue'
    elif num < 20000:
        return 'green'
    elif num < 200000:
        return 'orange'
    else:
        return 'red'



if __name__ == "__main__":
    geolocator = Nominatim(user_agent='film_checker')

    lat = input('Enter your latitude: ')
    long = input('Enter your longitude: ')
    year = input('Please input a year: ')

    try:
        lat, long = float(lat), float(long)
        year = int(year)
        pos = (lat, long)
    except ValueError:
        print('Your data is wrong. Terminating the program.')
    else:
        locations, country_count = read_locations(2012, 'locations.list')

        close_films = main(pos, year, geolocator, locations)
        revised_film_list = revise_films(close_films)

        create_map(pos, revised_film_list, country_count)
        print('HTML map created! Please open index.html in your browser.')
