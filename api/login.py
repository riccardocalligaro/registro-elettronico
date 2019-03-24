import json
import re
from datetime import datetime
from json.decoder import JSONDecodeError
from urllib.parse import quote_plus
import requests
from datetime import datetime
from flask import send_file


class AuthenticationFailedError(Exception):
    """
    Authentication failed error: bad username or password
    """

    def __init__(self):
        self.message = "Bad username or password"


class NotLoggedInError(Exception):
    """
    Not logged in error: you must logged in to use this method
    """

    def __init__(self):
        self.message = "You must logged in to use this method."


class NotLoggedInError(Exception):
    """
    Not logged in error: you must logged in to use this method
    """

    def __init__(self):
        self.message = "You must logged in to use this method."

class Utils:
    def __init__(self):
        return

    @staticmethod
    def convert_dt(dt=datetime.now()):
        return dt.strftime("%Y%m%d")

class Session:
    """
    Main session object
    """
    rest_api_url = "https://web.spaggiari.eu/rest/v1"
    utils = Utils()

    def __init__(self):
        self.logged_in = False
        self.first_name = None
        self.last_name = None
        self.id = None

        self.username = None
        self.password = None
        self.token = None

    def login(self, username: str = None, password: str = None):
        """
        Login to Classe Viva API
        :param username: Classe Viva username or email
        :param password: Classe Viva password
        :type username: str
        :type password: str
        :return: ID, first name and last name
        :rtype: dict
        """

        r = requests.post(
            url=self.rest_api_url + "/auth/login/",
            headers={
                "User-Agent": "zorro/1.0",
                "Z-Dev-Apikey": "+zorro+",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "uid": username if username else self.username,
                "pass": password if username else self.password,
            })
        )
        result = r.json()

        if 'authentication failed' in result.get('error', ''):
            raise AuthenticationFailedError()

        self.logged_in = True
        self.first_name = result['firstName']
        self.last_name = result['lastName']
        self.token = result['token']
        self.id = re.sub(r"\D", "", result['ident'])

        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    def logout(self):
        """
        Logout from Classe Viva API
        :return: Always True
        :rtype: bool
        """
        self.logged_in = False
        self.first_name = None
        self.last_name = None
        self.token = None
        return True

    def _request(self, *path, use_api_schema=True):
        if not self.logged_in:
            raise NotLoggedInError()

        url = self.rest_api_url + '/' + \
            ('students' + '/' + self.id) if use_api_schema else ''
        for x in path:
            url += '/' + quote_plus(x)

        r = requests.get(
            url=url,
            headers={
                "User-Agent": "zorro/1.0",
                "Z-Dev-Apikey": "+zorro+",
                "Z-Auth-Token": self.token,
                "Content-Type": "application/json",
            },
        )

        try:
            r = r.json()
            if r.get('error'):
                if 'auth token expired' in r['error']:
                    self.login()

            r = requests.get(
                url=url,
                headers={
                    "User-Agent": "zorro/1.0",
                    "Z-Dev-Apikey": "+zorro+",
                    "Z-Auth-Token": self.token,
                    "Content-Type": "application/json",
                },
            )
            try:
                return r.json()
            except JSONDecodeError:
                return r.text

        except JSONDecodeError:
            return r.text

    def absences(self, begin=utils.convert_dt(datetime.now()), end=utils.convert_dt(datetime.now())):
        """
        Get the student's absences
        :param begin: datetime object of start date (optional)
        :param end: datetime object of end date (optional)
        :type begin: datetime
        :type end: datetime
        :return: student's absences
        :rtype: dict
        """
        if begin == end:
            return self._request('absences', 'details')

        return self._request('absences',
                             'details',
                             self.utils.convert_dt(begin),
                             self.utils.convert_dt(end))

    def agenda(self, begin, end, event_filter='all'):
        """
        Get the student's agenda
        :param begin: datetime object of start date
        :param end: datetime object of end date
        :param event_filter: filter events by type, "all" / "homework" / "other" (optional, default "all")
        :type begin: datetime
        :type end: datetime
        :type event_filter: str
        :return: student's absences
        :rtype: dict
        """
        return self._request('agenda',
                             ('all' if event_filter == 'all' else (
                                 'AGHW' if event_filter == 'homeworks' else 'AGNT')),
                             self.utils.convert_dt(begin),
                             self.utils.convert_dt(end))

    def didactics(self):
        """
        Get the student's educational files list
        :return: student's educational files list
        :rtype: dict
        """
        return self._request('didactics')

    def _download_file(self, content_id):
        # TODO: File download
        pass

    def _noticeboard(self):
        # TODO: Noticeboard
        pass

    def schoolbooks(self):
        """
        Get the student's schoolbooks
        :return: student's schoolbooks
        :rtype: dict
        """
        return self._request('schoolbooks')

    def calendar(self):
        """
        Return the school calendar
        :return: school calendar
        :rtype: dict
        """
        return self._request('calendar', 'all')

    def cards(self):
        """
        Get the student's cards
        :return: student's cards
        :rtype: dict
        """
        return self._request('cards')

    def grades(self, subject=None):
        """
        Get the student's grades
        :param subject: filter results by subject (optional)
        :type subject: str
        :return: student's grades
        :rtype: dict
        """
        if not subject:
            return self._request('grades')

        return self._request('grades', 'subject', subject)

    def lessons(self, day='today', begin=None, end=None):
        """
        Get the student's lessons
        :param day: query lessons for a specific day (optional, default "today")
        :param begin: query lessons for a specific period (optional)
        :param end: query lessons for a specific period (optional)
        :type day: datetime
        :type begin: datetime
        :type end: datetime
        :return: student's lessons
        :rtype: dict
        """
        if begin and end:
            return self._request('lessons',
                                 self.utils.convert_dt(begin),
                                 self.utils.convert_dt(end))

        return self._request('lessons',
                             self.utils.convert_dt(day) if day != 'today' else 'today')

    def notes(self):
        """
        Get all of the the student's notes
        :return: student's notes
        :rtype: dict
        """
        return self._request('notes', 'all')

    def periods(self):
        """
        Get the student's periods
        :return: student's periods
        :rtype: dict
        """
        return self._request('periods')

    def subjects(self):
        """
        Get all of the student's subjects and teachers
        :return: student's subjects and teachers
        :rtype: dict
        """
        return self._request('subjects')
    def noticeboard(self):
        """
        Get all of the student's notices
        :return: student's Noticeboard
        :rtype: dict
        """
        return self._request('noticeboard')

    def download_file_request(self, *path, use_api_schema=True):
        if not self.logged_in:
            raise NotLoggedInError()

        url = self.rest_api_url + '/' + ('students' + '/' + self.id) if use_api_schema else ''

        for x in path:
            url += '/' + quote_plus(x, safe='')
            #url += '/' + quote_plus(x)
            print(quote_plus(x, safe=''))

        r = requests.get(url=url,headers={
                "User-Agent": "zorro/1.0",
                "Z-Dev-Apikey": "+zorro+",
                "Z-Auth-Token": self.token,
                "Content-Type": "application/json",
        },stream=True)
        print(r.status_code)

        parts = r.headers['Content-Disposition'].split("\"")
        # name
        name = parts[-2][:-3]
        # estensione
        extension = parts[-2].split('.')[-1]

        if r.status_code == 200:
            with open(str(name) + '.' +str(extension), 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        return send_file(f, attachment_filename=(str(name) + '.' +str(extension)))



    def didactics_download(self, content_id):
        return self.download_file_request('didactics', 'item', content_id)
