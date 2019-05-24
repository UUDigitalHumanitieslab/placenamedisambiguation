import os
import geocoder
import requests

class Geocoder:
    '''
    This is a very thin wrapper around the magnificent geocoder library (https://geocoder.readthedocs.io)
    It mainly handles HTTP sessions and errors. Throws EnvironmentError if either GOOGLE_API_KEY or GEONAMES_USERNAME
    is not present as an environment variable. Propagates geocoder's/requests' requests.exceptions.ConnectionError.  
    '''

    def __init__(self, named_entities, language):
        if not "GEONAMES_USERNAME" in os.environ:
            raise EnvironmentError("GEONAMES_USERNAME is not present as an environment variable. Please export it")      
        if not "GOOGLE_API_KEY" in os.environ:
            raise EnvironmentError("GOOGLE_API_KEY is not present as an environment variable. Please export it")
        
        self.named_entities = named_entities
        self.language = language
        self.geonames_username = os.getenv('GEONAMES_USERNAME')

    def geocode_locations(self):
        '''
        Extract all entites tagged LOCATION and attempt to add lat, lng.
        As per geocoder documentation, use sessions when making severall 
        requests to the same service.
        '''
        with requests.Session() as google_session, requests.Session() as osm_session:
            with requests.Session() as gn_session, requests.Session() as gn_detail_session:
                for ent in self.named_entities:
                    if (ent['type'] == 'LOCATION'):
                        self.set_geocode_from_geonames(
                            gn_session, gn_detail_session, ent)
                        self.set_geocode_from_google(google_session, ent)
                        self.set_geocode_from_osm(osm_session, ent)

                        # TODO: keep track of names lat, lng was already collected for and reuse

    def set_geocode_from_geonames(self, session, details_session, named_entity):
        g = geocoder.geonames(
            named_entity['ne'], key=self.geonames_username, featureClass='A')

        if (g.ok):
            g_details = geocoder.geonames(
                g.geonames_id, method='details', key=self.geonames_username, session=details_session)

            if (g_details.ok):
                named_entity['geonames_lat'] = g_details.lat
                named_entity['geonames_lng'] = g_details.lng
            else:
                self.handle_error(g_details)
        else:
            self.handle_error(g)

    def set_geocode_from_osm(self, session, named_entity):
        place_name = named_entity['ne']
        g = geocoder.osm(place_name, session=session)

        if (g.ok):
            named_entity['osm_lat'] = g.lat
            named_entity['osm_lng'] = g.lng
        else:
            self.handle_error(g)

    def set_geocode_from_google(self, session, named_entity):
        place_name = named_entity['ne']
        g = geocoder.google(place_name, session=session, method='places', language=self.language)
        
        if (g.ok):
            named_entity['google_lat'] = g.lat
            named_entity['google_lng'] = g.lng
        else:
            self.handle_error(g)

    def handle_error(self, g):
        if not 'No results found' in g.status:
            print(g.status)
