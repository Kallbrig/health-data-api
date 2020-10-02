import pandas as pd
import json
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import random
from datetime import datetime
from marshmallow import Schema, fields


# https://pythonbasics.org/flask-rest-api/
# https://nordicapis.com/how-to-create-an-api-from-a-dataset-using-python-and-flask/


class ConditionGetSchema(Schema):
    id = fields.Int(required=True)


class ConditionPostSchema(Schema):
    id = fields.Int(required=True)
    heart_rate = fields.Int()
    exercise_minutes = fields.Int()
    food_intake = fields.Int()
    time = fields.DateTime()


class ConditionDeleteSchema(Schema):
    id = fields.Int(required=True)
    time = fields.DateTime(required=True)


app = Flask(__name__)
api = Api(app)
data_get_schema = ConditionGetSchema()
data_post_schema = ConditionPostSchema()
data_delete_schema = ConditionDeleteSchema()


class Condition(Resource):

    def get(self):
        # returns errors if there are any
        errors = data_get_schema.validate(request.args)
        if errors:
            return 400, str(errors)

        # reading in heart rate data as a pandas dataframe
        data_df = pd.read_csv(f'data/{request.args["id"]}_user_data.csv', )

        # TO-DO - ADD A PARAMETER TO GET REQUESTS TO AUTHENTICATE
        # TO-DO - ADD A PARAMETER TO GET REQUESTS TO FILTER RESULTS BY DATE

        # Returns full user information.
        return data_df.to_json()

    def post(self):

        errors = data_post_schema.validate(request.args)
        if errors:
            return 400, str(errors)

        # default values for all information that will be inputted into the dataframe.
        # Keys are column headers and values are defaults.
        info_dict = {'id': request.args['id'], 'heart_rate': -1,
                     'exercise_minutes': -1, 'food_intake': -1,
                     'time': datetime.now()}

        # Replaces the defaults with the values present in the post request parameters.
        # This way we always have a full dataset to analyze later.
        for arg in request.args:
            info_dict[arg] = request.args[arg]

        # TO-DO - MAKE A CREATION METHOD FOR THE DATA FILES.
        # CURRENTLY YOU HAVE TO MANUALLY CREATE EACH PATIENT'S DATA RECORD.

        # Reads the current patient data in as a dataframe.
        data_df = pd.read_csv(f'data/{request.args["id"]}_user_data.csv', index_col='index')
        # appends the new information to the existing dataframe.
        data_df = data_df.append(info_dict, ignore_index=True)
        # saves the dataframe back to the file with the updates applied.
        data_df.to_csv(f'data/{request.args["id"]}_user_data.csv', index=True, index_label='index')

        # This currently returns the new entry only.
        return data_df.tail(1).to_json()

    # DELETE IS INCOMPLETE.
    # IT RETURNS THE ENTRIES TO BE DELETED.
    # THESE ENTRIES ARE CURRENTLY BEING IDENTIFIED USING TIME
    def delete(self, ):

        errors = data_delete_schema.validate(request.args)
        if errors:
            return 400, str(errors)

        data_df = pd.read_csv(f'data/{request.args["id"]}_user_data.csv', )

        entries_to_delete = data_df.loc[(data_df['time'] == request.args['time'])]
        # (data_df['time'] == request.args['time'])
        print(str(entries_to_delete))

        # data_df.to_csv(f'data/{request.args["id"]}_user_data.csv', index=True, index_label='index')
        return entries_to_delete.to_json()



api.add_resource(Condition, '/res/', '/res')

app.run(debug=True)
