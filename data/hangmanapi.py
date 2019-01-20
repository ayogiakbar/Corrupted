import requests

class HangmanAPI():
    def CreateNewGame(self):
        return requests.post('http://hangman-api.herokuapp.com/hangman').json()

    def Guess(self, token, letter):
        data = {
            'token':token,
            'letter':letter
        }
        return requests.put('http://hangman-api.herokuapp.com/hangman', data=data).json()

    def Solution(self, token):
        data = {
            'token':token
        }
        return requests.get('http://hangman-api.herokuapp.com/hangman', data=data).json()

    def Hint(self, token):
        data = {
            'token':token
        }
        return requests.get('http://hangman-api.herokuapp.com/hangman/hint', data=data).json()