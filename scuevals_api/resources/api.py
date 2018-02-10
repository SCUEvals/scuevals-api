from flask_restful import Resource


class APIStatusResource(Resource):

    @staticmethod
    def get():
        return {'status': 'ok'}
