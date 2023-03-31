class FileAlreadyExists(Exception):
    
    def __init__(self, file, message):
        
        self.file = file
        self.message = message
        super().__init__(self.message)