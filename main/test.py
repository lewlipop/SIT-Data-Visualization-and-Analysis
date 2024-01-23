key = 'b2d0863e0a3646219375639ca53290b7'
geocoder = OpenCageGeocode(key)
for x in postal_list:
    try:
        query = f"{x}, Singapore"

        # no need to URI encode query, module does that for you
        results = geocoder.geocode(query)

        print(u'%f;%f;%s;%s' % (results[0]['geometry']['lat'],
                                results[0]['geometry']['lng'],
                                results[0]['components']['country_code'],
                                results[0]['annotations']['timezone']['name']))
    except Exception as error:
        print(error)