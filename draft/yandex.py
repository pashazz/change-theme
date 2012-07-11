#-------------------------------------------------------------------------------
# Copyright (c) 2012 Pavel Borisov
# All rights reserved. ChangeTheme and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# Contributors:
#     pasha - initial API and implementation
#-------------------------------------------------------------------------------
'''
Created on 23.06.2012

@author: pasha

Module for get sunset/sunrise time from Yandex
'''
import urllib.error
import urllib.request as request
from xml.etree import ElementTree as eltree
import logging, datetime

log = logging.getLogger('yamodule')
hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
frm = logging.Formatter(style="{", fmt='yamodule: {asctime}: {message}')

hdlr.setFormatter(frm)
log.addHandler(hdlr)

cities_url = 'http://weather.yandex.ru/static/cities.xml'
doc_url = 'http://export.yandex.ru/weather-ng/forecasts/{city}.xml'
class NoCityError(ValueError): pass
class NoDataError(ValueError): pass

class YandexRetreiver:
    def __init__(self, urlErrHandler=None):
        '''download yandex cities XML and parse it. call urlErrHandler '''
        self.fail = False
        def download():
            log.info('Downloading cities list: {0}'.format(cities_url))
            self.__urlerr = urlErrHandler
            if not hasattr(self.__urlerr, '__call__'): #not a function
                self.__urlerr = lambda err: log.error(err)
            #self.elroot = None
            f = request.urlopen(cities_url)
            xmldata = f.readall()
            self.elroot = eltree.fromstring(xmldata)

        
        try:
            download()
        except urllib.error.URLError as err:
            if err.code == 404: #пробуем еще!! (яндекс глючит)
                download()
                self.fail = False
            else:
                self.fail = True
        if not self.fail:
            self.city_data = ''
            self.__dateformat = '%Y-%m-%d'
            self.__timeformat = '%H:%M'
        
    def countriesList(self):
        '''Return countries list in language Russian'''
        return [c.get('name') for c in self.elroot.iter('country')]
    
    def citiesList(self, country):
        '''Return list of dicts(id:city_name) of cities in given country. If no such country, raise ValueError''' 
        celem = self.elroot.find('country[@name="{0}"]'.format(country))
        if not isinstance(celem, eltree.Element):
            raise ValueError('no data aval. for country {0}'.format(country))
        
        assert celem.get('name') == country
        return {int(c.get('id')):c.text for c in celem.iter('city')}
    
    def __check_city(self, id_city):
        #gets city xml if need
        def download():
            try:
                city_req = request.urlopen(doc_url.format(city=id_city))
                log.info('checkCity: file downloaded: {0}'.format(city_req.url))
            except urllib.error.HTTPError as err:
                if err.code == 404:
                    raise NoCityError('No such city (by id): {}'.format(id_city))
                else:
                    self.__urlerr(err)
            else:
                self.city_data = city_req.readall().decode('utf-8')
            
        #  if not len(self.city_data):
        #      download()
        #      return
        
        #  root=eltree.fromstring(self.city_data)
        #  if not int(root.get('id')) == id_city:
        #      download()  
        download()
        self.city_data = self.city_data.replace('xmlns="http://weather.yandex.ru/forecast" ', '') #hack
        root = eltree.fromstring(self.city_data)
        return root
    

        
    
    def sunrise(self, city_id, date=None):
        '''Return sunrise and sunset time for given city_id and date (None = dict(date:(sunrise,sunset)) for week).
            Raise NoDataError/ValueError if inv. date (valid is %Y-%m-%d or datetime.date obj) or no data
        '''
        
        if self.fail:
            raise NoDataError('No data downloaded!')
        
        city_root = self.__check_city(city_id)
        if date == None:
            ret = {}
            for elem in city_root.iter('day[@date]'):
                mydate = datetime.datetime.strptime(elem.get('date'), self.__dateformat).date()
                _sunrise = datetime.datetime.strptime(elem.find('sunrise').text).time()
                _sunset = datetime.datetime.strptime(elem.find('sunset').text).time()
                ret[mydate] = (_sunrise, _sunset)
            return ret
        else:
            if isinstance(date, str):
                mydate = date
            elif isinstance(date, datetime.date):
                mydate = date.strftime(self.__dateformat)
            else:
                raise ValueError('Invalid argument')
            
            node = city_root.find('day[@date="{0}"]'.format(mydate))
            log.debug('find: day [@date="{0}"]'.format(mydate))
            if node is  None:
                raise NoDataError('No data for date {}'.format(mydate))

            return (datetime.datetime.strptime(node.find('sunrise').text, self.__timeformat).time(),
                    datetime.datetime.strptime(node.find('sunset').text, self.__timeformat).time())
    
    def name(self, city_id):
        ''' returns city name or None by id'''
        if not isinstance(city_id, (int, str)):
            raise ValueError    
        for c in self.elroot.iter('country'):
            ct = c.find('city[@id="{0}"]'.format(city_id))
            if ct is not None:
                return ct.text
        return None
                       
            
                
            
                
    
    
        
        
