# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build

# class GoogleCalendar:
#     def __init__(self, token):
#         self.credentials = Credentials(token=token)
#         self.service = build('calendar', 'v3', credentials=self.credentials)

#     def create_event(self, summary, description, start_time, end_time):
#         event = {
#             'summary': summary,
#             'description': description,
#             'start': {'dateTime': start_time},
#             'end': {'dateTime': end_time},
#         }
#         event = self.service.events().insert(calendarId='primary', body=event).execute()
#         return event.get('id')
