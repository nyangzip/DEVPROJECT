import requests,xmltodict
import urllib.parse
# 서울특별시 코로나19 자치구별 확진자 발생동향
serviceurl = 'http://openAPI.seoul.go.kr:8088/5343646e4762616b3637774c504971/xml/TbCorona19CountStatusJCG/1/5/2021.08.10.00'
resp = requests.get(serviceurl)
dictdata = xmltodict.parse(resp.content)
dictdata['TbCorona19CountStatusJCG']['row']

# 서울특별시 코로나19 확진자 발생동향
serviceurl = 'http://openapi.seoul.go.kr:8088/617478567462616b3130316442507261/xml/TbCorona19CountStatus/1/5/2021.08.10.00'
resp = requests.get(serviceurl)
dictdata = xmltodict.parse(resp.content)
dictdata['TbCorona19CountStatus']['row']

# 서울특별시 코로나19 백신 예방접종 현황

serviceurl = 'http://openapi.seoul.go.kr:8088/414576754662616b39365249765061/xml/tvCorona19VaccinestatNew/1/5/2021.08.10.00'
resp = requests.get(serviceurl)
dictdata = xmltodict.parse(resp.content)
dictdata['tvCorona19VaccinestatNew']['row']

# 서울특별시 코로나19 확진자 현황
serviceurl = 'http://openapi.seoul.go.kr:8088/557342765962616b3130316b58684d65/xml/Corona19Status/1/5/2021.08.10.00'
resp = requests.get(serviceurl)
dictdata = xmltodict.parse(resp.content)
dictdata['Corona19Status']['row']

