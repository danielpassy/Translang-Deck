import uuid
from .models import AnonymousUser

"""
General functionalities
"""
# the max input size in bytes
MAX_FILE_SIZE = 5000


def get_create_uuidd(request):
    """
    Retrieve ID of anon user
    If does not exist, create one
    and store it on the DB.
    return the uuid
    """
    if not "userID" in request.session:
        userID = uuid.uuid1().hex
        request.session.__setitem__("userID", userID)
        AnonymousUser.objects.create(userID=userID)
        return userID
    return request.session["userID"]


class FileValidator(object):
    """
    Check if the valid fits the specifications
    return an error object if's the case
    """

    def error(self):
       
        if not hasattr(self, 'message'):
            raise Exception("You must first call .is_valid(file)")

        return self.message

    def is_valid(self, file):

        if (file.content_type != 'text/csv' and file.content_type != 'application/vnd.ms-excel'):
            self.message = 'you should upload a .csv file'
            return False

        if file.size > MAX_FILE_SIZE:
            self.message = f'The file must be smaller than %{MAX_FILE_SIZE/1000}kb'
            return False

        self.message = []
        return True
        

    def __bool__(self):
        if not hasattr(self, 'message'):
            raise Exception("You must first call .is_valid(file)")
        return self.message

    
