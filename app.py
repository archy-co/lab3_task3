import requests
import folium
from flask import Flask, render_template, request

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy import distance

app = Flask(__name__)

final_mapname = 'friends.html'

@app.route('/', methods=["POST", "GET"])
def required_data():
    if request.method == 'GET':
        return render_template('index.html')

    bearer_token = request.form.get('bearer')
    account_name = request.form.get('account')
    if not account_name or not bearer_token:
        return render_template('empty_input.html')

    dict_data = get_json_as_dict(bearer_token, account_name)

    if 'errors' in dict_data:
        error_messages = ''
        for error in dict_data['errors']:
            error_messages += error['message'] + '\n'

        return error_messages

    if 'users' not in dict_data:
        return 'No friends'

    users_data_list = []
    for user in dict_data['users']:
        if user['location']:
            users_data_list.append([user['screen_name'], user['location']])

    users_data_list = coordinate_users(users_data_list)

    build_map(users_data_list)

    return render_template(final_mapname)


def build_map(users_data_list):
    mappy = folium.Map(tiles='openstreetmap', zoom_start=6)
    friends_locs = folium.FeatureGroup(name='Friends\' Locations')

    for user in users_data_list:
        friends_locs.add_child(folium.Marker(location=user[-1],
                                         popup='@'+str(user[0]),
                                         icon=folium.Icon(icon='star', color='lightblue')))

    mappy.add_child(friends_locs)
    mappy.save('/home/archy2go/tweelocator/templates/' + final_mapname)


def coordinate_users(users_data_list):
    geolocator = Nominatim(user_agent='tweelocator')
    user_data_coord_list = []
    for user in users_data_list:
        try:
            loc_gcode = geolocator.geocode(user[1])
            location = tuple([loc_gcode.latitude, loc_gcode.longitude])

            user_coord = user + [location]
            user_data_coord_list.append(user_coord)
        except GeocoderUnavailable:
            continue
        except AttributeError:
            continue

    return user_data_coord_list


def get_json_as_dict(bearer_token: str, account_name: str, count=15) -> dict:
    '''
    This function takes bearer_token and account_name, sends request to twitter API and returns
    JSON reponse as dictionary
    '''
 
    search_url = 'https://api.twitter.com/1.1/friends/list.json'
    search_headers = {'Authorization': f'Bearer {bearer_token}'}

    search_params = {
        'screen_name': account_name,
        'count': count
    }

    response = requests.get(search_url, headers=search_headers, params=search_params)
    json_response = response.json()

    return json_response


if __name__ == '__main__':
    app.run(debug=True)

