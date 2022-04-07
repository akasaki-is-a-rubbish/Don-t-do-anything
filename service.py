import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

AIP_HOME = 'https://tmonit.akasaki.space/api'


class Service():
    def __init__(self, enID):
        '''
        param: enID: encrypted vehicle id
        '''
        self.enID = enID

    def newevent(self, ch, image):
        '''
        param:
        ch: event description
            ch: 'smoke' 'drink' 'phone' 'fatigue'
            to-> 'ch1'   'ch2'   'ch3'    'ch4'
            level: 1       1       2        3
        image: image file
        '''
        url = AIP_HOME + '/events/new'

        if ch == 'smoke':
            ch = 'ch1'
            level = 1
        elif ch == 'drink':
            ch = 'ch2'
            level = 1
        elif ch == 'phone':
            ch = 'ch3'
            level = 2
        elif ch == 'fatigue':
            ch = 'ch4'
            level = 3

        data = {
            'vehicleIdEncrypted': self.enID,
            'description': ch,
            'dangerousLevel': level
        }
        string = json.dumps(data)
        r = requests.post(
            url,
            data=string,
            headers={"Content-Type": "application/json"},
        )

        if r.status_code == 200:
            print('new event success')
            enventID = r.json()['id']
            self.uploadimage(enventID, image)
        else:
            print('new event fail')

    def uploadimage(self, eventID, image):
        '''
        param: eventID: event id
        param: image: image file binary
        '''
        url = AIP_HOME + '/events' + '/' + eventID + '/image'

        binfile = open(image, 'rb')
        headers = {}
        data = MultipartEncoder(
            fields={
                'formFile': ("1.jpg", binfile, "image/jpg"),
                'encryptedVehicleId': self.enID,
            },
            boundary='----WebKitFormBoundary7MA4YWxkTrZu0gW')
        headers['Content-Type'] = data.content_type
        r = requests.put(url, data=data, headers=headers)
        print(r)
        if r.status_code == 200:
            print('upload image success')


# if __name__ == '__main__':
#     service = Service(
#         'MtinlX1CCTRQrMp84cRJkPH8LuItqbF0EZ0mqs4HYE2yHmpBcjfy+9NX7uRV8sDDbHHvGbnU6jvKt+6o0N8cpeSUwU1/89wHPL++TjaRiopKHLWhBkL4WORwI7tBSsmxKROcDfNZCBiY1hQJaLw5fuA0rhFXKwxJxPX2aB8t9qo='
#     )
#     service.newevent('smoke', './R-C.jpg')
