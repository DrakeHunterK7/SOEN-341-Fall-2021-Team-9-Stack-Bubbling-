from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource, reqparse, inputs
from pymongo import MongoClient
from datetime import timedelta
from flask_cors import CORS
import datetime
import uuid
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)

# CORS
CORS(app)

# JWT
app.config["JWT_SECRET_KEY"] = "SuperSecuredSecretKey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1000)
# app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.datetime.utcnow() + datetime.timedelta(days=24)
jwt = JWTManager(app)
# RestFul
api = Api(app)

# connect with DB
connectionString = "mongodb+srv://SOEN341T300:Soen_341_T_300@cluster0.qvzq2.mongodb.net/test?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true"
client = MongoClient(connectionString)

# Register Info
RegisterInfo = reqparse.RequestParser()
RegisterInfo.add_argument('username', help='Username cannot be blank', required=True)
RegisterInfo.add_argument('email', help='emailAddress cannot be blank', required=True)
RegisterInfo.add_argument('password', help='Password cannot be blank', required=True)
RegisterInfo.add_argument('confirmPassword', help='Confirm Password cannot be blank', required=True)

# Login Info
LoginInfo = reqparse.RequestParser()
LoginInfo.add_argument('email', help='emailAddress cannot be blank', required=True)
LoginInfo.add_argument('password', help='Password cannot be blank', required=True)

# Post Question Info
PostQuestionInfo = reqparse.RequestParser()
PostQuestionInfo.add_argument('title', help='question title cannot be empty', required=True, type=str)
PostQuestionInfo.add_argument('body', help='question body cannot be empty', required=True, type=str)

# Post Answer Info
PostAnswerInfo = reqparse.RequestParser()
PostAnswerInfo.add_argument('question_id', help='Question_ID cannot be empty', required=True, type=str)
PostAnswerInfo.add_argument('body', help='Answer body cannot be empty', required=True, type=str)

# Vote Question Info
VoteQuestionInfo = reqparse.RequestParser()
VoteQuestionInfo.add_argument('question_id', help='question_id cannot be empty', required=True, type=str)
VoteQuestionInfo.add_argument('is_upvote', help='is_upvote cannot be empty', required=True, type=inputs.boolean)

# Vote Answer Info
VoteAnswerInfo = reqparse.RequestParser()
VoteAnswerInfo.add_argument('question_id', help='question_id cannot be empty', required=True, type=str)
VoteAnswerInfo.add_argument('answer_id', help='answer_id cannot be empty', required=True, type=str)
VoteAnswerInfo.add_argument('is_upvote', help='is_upvote cannot be empty', required=True, type=inputs.boolean)

# Best Answer Info
BestAnswerInfo = reqparse.RequestParser()
BestAnswerInfo.add_argument('question_id', help='question_id cannot be empty', required=True, type=str)
BestAnswerInfo.add_argument('answer_id', help='answer_id cannot be empty', required=True, type=str)

# Get Question Info
GetQuestionInfo = reqparse.RequestParser()
GetQuestionInfo.add_argument('question_id', help='question_id cannot be empty', required=True, type=str)


# Update Notification Info
UpdateNotificationInfo = reqparse.RequestParser()
UpdateNotificationInfo.add_argument("type", help="the type of notification", required=True, type=str)
UpdateNotificationInfo.add_argument("question_id", help="the type of notification", required=True, type=str)
UpdateNotificationInfo.add_argument("answer_id", help="the type of notification", required=False, type=str)

#For Testing Purposes
# Test Reset Answer Info
TestResetAnswerInfo = reqparse.RequestParser()
TestResetAnswerInfo.add_argument('question_id', help='question_id cannot be empty', required=True, type=str)
TestResetAnswerInfo.add_argument('answer_id', help='answer_id cannot be empty', required=True, type=str)

DB = client["Stack-Bubbling"]
UserCollection = DB["Users"]
QuestionCollection = DB["Questions"]


class Register(Resource):
    @staticmethod
    def post():
        data = RegisterInfo.parse_args()
        res = UserCollection.find_one({
            "email": data.email
        })
        sameUsername = UserCollection.find_one({
            "username": data.username
        })
        if data.confirmPassword != data.password:
            return make_response(jsonify({"message": "Please check that your password and confirm password match."}),201)
        if res is not None:
            return make_response(jsonify({"message": "The email you entered has already been used. Please enter a new one."}), 201)
        if sameUsername is not None:
            return make_response(jsonify({"message": "The username you chose has been taken. Please choose a different one."}), 201)
        else:
            UserCollection.insert_one({
                "_id": uuid.uuid1(),
                "username": data.username,
                "email": data.email,
                "password": data.password,
                "createdAt": datetime.datetime.today()
            })
            return make_response(jsonify({"message": "register successful, please login"}), 200)


class Login(Resource):
    @staticmethod
    def post():
        data = LoginInfo.parse_args()
        # validation of email and pass
        res = UserCollection.find_one({
            "email": data.email,
            "password": data.password
        })
        if res is not None:
            # create token
            access_token = create_access_token(identity={"email": data.email})
            result = {
                "access_token": access_token,
                "username": res["username"]
            }
            return make_response(jsonify(result), 201)
        else:
            return make_response(jsonify({
                "message": "the email or password is invalid"
            }), 203)

        # things to do after
        # sorting the token at the frontend
        # for logout function, the frontend will do some operation remove token in the frontend
        # write the @jwt_required() before the post and get


class PostAnswer(Resource):
    @staticmethod
    @jwt_required()
    def post():
        # Parse the request info
        info = PostAnswerInfo.parse_args()
        # Check the identity of User
        identity = get_jwt_identity()
        currentUser = None
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify({"message": "The User identity is invalid"}), 401)
        # Convert question_id received to uuid
        # Check if question exist
        question_id = uuid.UUID(info["question_id"])
        currentQuestion = None
        currentQuestion = QuestionCollection.find_one({"_id": question_id})
        if currentQuestion is None:
            return make_response(jsonify({"message": "The Question identity is invalid"}), 401)
        answer_id = uuid.uuid1()
        newAnswer = {
            "_id": answer_id,
            "username": currentUser["username"],
            "user_id": currentUser["_id"],
            "body": info["body"],
            "createdAt": datetime.datetime.today(),
            "is_best_answer": False,
            "vote_count": 0
        }
        # Append the new Answer to answers of question
        QuestionCollection.update(
            {"_id": question_id},
            {"$push": {"answers": newAnswer}})

        # Add Notification to question owner
        questionOwnerId = QuestionCollection.find_one({"_id":question_id})["user_id"]

        UserCollection.update(
            {
                "_id": questionOwnerId
            },
            {
                "$push": 
                {
                    "notifications": 
                    {
                        "type": "AnswerPosted",
                        "questionID": question_id,
                        "viewed": False
                    }
                }
            }
        )
        return make_response(jsonify(
            {
                "message": "The Answer posted successfully",
                "newAnswer": newAnswer,
                "question_id": info["question_id"]
            }), 201)

class QuestionList(Resource):	
    @staticmethod
    def get():
	# get 100 questions
        res = QuestionCollection.aggregate([
            {
                '$lookup': 
                {
                    'from': 'Users', 
                    'localField': 'user_id', 
                    'foreignField': '_id', 
                    'as': 'name'
                }
            },
            {
                '$sort': 
                {
                    'createdAt':-1
                }
            },
            {
                '$limit' : 100
            },
            {
                "$project": 
                {
                    'Username': 
                    {
                        "$cond": 
                        {
    				        "if": 
                            {
                                "$anyElementTrue": ["$name.username"]
                            },
                            "then": "$name.username",
                            "else": ["deleted user"]
                        }
                    },
                    'title':'$title',
            		'body':'$body',
            		'createdAt': '$createdAt',
            		'vote_count': '$vote_count',
            		'_id': '$_id',
                    'answerCount': {'$size': '$answers'}
                    
                }
            }
        ])
        return make_response(jsonify(list(res)), 201)

class PostQuestion(Resource):
    # This decorator is needed when we need to check the identity of the user
    # When using this decorator, the request must have a header["Authorization"] with value "Bearer [jwt_token]"
    @staticmethod
    @jwt_required()
    def post():
        # Parse the Json received in request to [info]
        info = PostQuestionInfo.parse_args()
        # get_jwt_identity() will get the [email] from token sent through header["Authorization"] of the request
        identity = get_jwt_identity()
        currentUser = None
        # Get the current user using his [email]
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify({"message": "Unable to perform operation, User identity invalid"}), 401)
        newQuestion = {
            "_id": uuid.uuid1(),
            "username": currentUser["username"],
            "user_id": currentUser["_id"],
            "title": info["title"],
            "body": info["body"],
            "createdAt": datetime.datetime.today(),
            "vote_count": 0,
            "answers": []
        }
        QuestionCollection.insert_one(newQuestion)
        return make_response(jsonify(
            {
                "message": "Question was posted successfully",
                "newQuestion": newQuestion
            }), 201)
    # Things to do
    # Handle the response info in the front end
    # Design & Implement a refresh token


class ListAnswers(Resource):
    @staticmethod
    def get():
        # Get the current Question's ID
        questionID = uuid.UUID(request.args.get("question_id"))
        question = QuestionCollection.find_one({"_id": questionID})
        # List all the answers associated with that Question using the ID
        res = QuestionCollection.aggregate([		
            {
                "$match" : 
                {
                    "_id": questionID
                } 
            },
            {
                '$unwind':'$answers'
            },
            {
                '$lookup':
                {
                    'from': 'Users', 
                    'localField': "answers.user_id", 
                    'foreignField': '_id', 
                    'as': 'name'
                }
            },
            {
                '$project': 
                {
                    'Username':
                    {
                        "$cond": 
                        {
                            "if": 
                            {
    					       "$anyElementTrue": ["$name.username"]
                            },
                            "then": "$name.username",
                            "else": ["deleted user"]
                        }
                    },
                    'body':'$answers.body',
                    'createdAt': '$answers.createdAt',
                    'vote_count': '$answers.vote_count',
                    '_id': '$answers._id',
                    'user_id': '$answers.user_id',
                    'is_best_answer': '$answers.is_best_answer'
                }
            }	 
        ])

        result = {
            "answerList": list(res),
            "questionVoteCount": question["vote_count"]
        }
		
        return make_response(jsonify(result), 201)

class ListMyAnswers(Resource):   
    @staticmethod
    @jwt_required()
    def get():
        identity = get_jwt_identity()
        currentUser = None
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify({"message": "Unable to perform operation, User identity invalid"}), 401)
        answers = QuestionCollection.aggregate([
            {
                "$project": 
                {
                    "myanswer": 
                    {
                        "$filter": 
                        {
                            "input": "$answers",
                            "as": "answer",
                            "cond": 
                            {
                                "$eq": 
                                [
                                    "$$answer.user_id",
                                    currentUser["_id"]
                                ]
                            }
                        }
                    },
                    "_id": 1
                }
            },
            {
                "$unwind": "$myanswer"
            },
            {
                "$project":
                {
                    "myanswer.user_id":0,
                    "myanswer.username":0
                }
            }
        ])
        return make_response(
            jsonify(list(answers)), 201)

class ListMyQuestions(Resource):   
    @staticmethod
    @jwt_required()
    def get():
    # get 100 questions
        identity = get_jwt_identity()
        currentUser = None
        # Get the current user using his [email]
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify({"message": "Unable to perform operation, User identity invalid"}), 401)
        questions = QuestionCollection.find(
            {
                "user_id": currentUser["_id"]
            }, 
            {
                "_id": 1, 
                "title": 1, 
                "createdAt": 1, 
                "vote_count": 1
            })
        return make_response(
            jsonify(list(questions)), 201)

class VoteAnswer(Resource):
    @staticmethod
    @jwt_required()
    def post():
        info = VoteAnswerInfo.parse_args()
        identity = get_jwt_identity()
        responseMessage = ""
        actionTaken = ""
        currentUser = UserCollection.find_one(
            {
                "email": identity["email"]
            })
        voteChange = 0
        questionID = uuid.UUID(info["question_id"])
        answerID = uuid.UUID(info["answer_id"])
        # No Votes at all
        if "votes" not in currentUser:
            if info["is_upvote"]:
                voteChange += 1
            else:
                voteChange -= 1
            actionTaken = "NewVote"
            UserCollection.update(
                {
                    "_id" : currentUser["_id"]
                },
                {
                    "$push": 
                    {
                        "votes": 
                        {
                            "post_id" : answerID,
                            "is_upvote": info["is_upvote"]
                        }
                    }
                })
        else:
            for vote in currentUser["votes"]:
                # Vote on this answer exist
                if vote["post_id"] == answerID:
                    # Cancel vote
                    if vote["is_upvote"] == info["is_upvote"]:
                        if info["is_upvote"]:
                            voteChange -= 1
                        else:
                            voteChange += 1
                        actionTaken = "CancelVote"
                        UserCollection.update(
                        {
                            "_id": currentUser["_id"]
                        },
                        {
                            "$pull" : 
                            {
                                "votes": 
                                {
                                    "post_id": answerID
                                }
                            }
                        })                    
                        break
                    # Change vote
                    else:
                        if info["is_upvote"]:
                            voteChange += 2
                        else:
                            voteChange -= 2                            
                        actionTaken = "ChangeVote"
                        UserCollection.update(
                        {
                            "_id": currentUser["_id"],
                            "votes.post_id": answerID
                        },
                        {
                            "$set": 
                            {
                                "votes.$.is_upvote": info["is_upvote"]
                            }
                        })
                        break
            # No vote on this answer
            if voteChange == 0:
                if info["is_upvote"]:
                    voteChange += 1
                else:
                    voteChange -= 1
                actionTaken = "NewVote"
                UserCollection.update(
                    {
                        "_id": currentUser["_id"]
                    },
                    {
                        "$push": 
                        {
                            "votes" : 
                            {
                                "post_id" : answerID,
                                "is_upvote": info["is_upvote"]
                            }
                        }
                    })
        # Now change vote count of answer
        QuestionCollection.update(
            {
                "_id": questionID,
                "answers._id": answerID
            },
            {
                "$inc": 
                {
                    "answers.$.vote_count": voteChange
                }
            })
        agg = QuestionCollection.aggregate([
            {
                "$match":
                {
                    "_id": questionID
                },
            },
            {
                "$unwind": "$answers"
            },
            {
                "$match": 
                {
                    "answers._id": answerID
                }
            },
            {
                "$project":
                {
                    "answerOwnerUserID": "$answers.user_id",
                    "_id": 0 
                }
            }])
        aggList = list(agg)
        answerOwnerUserID = aggList[0]["answerOwnerUserID"]

        # Now push Notification
        UserCollection.update(
            {
                "_id": answerOwnerUserID
            },
            {
                "$push":
                {
                    "notifications": 
                    {
                        "type": "VoteAnswer",
                        "questionID": questionID,
                        "answerID": answerID,
                        "viewed": False,
                        "vote_change": voteChange
                    }
                }
            })
        if actionTaken == "NewVote":
            responseMessage = "Upvoted" if info["is_upvote"] else "Downvoted"
        elif actionTaken == "ChangeVote":
            responseMessage = "Changed vote to upvote" if info["is_upvote"] else "Changed vote to downvote"
        else:
            responseMessage = "Cancelled upvote" if info["is_upvote"] else "Cancelled downvote"
        return make_response(jsonify(
            {
                "message": responseMessage,
                "actionTaken": actionTaken,
                "is_upvote": info["is_upvote"]
            }), 200)
        
class VoteQuestion(Resource):
    @staticmethod
    @jwt_required()
    def post():
        info = VoteQuestionInfo.parse_args()
        identity = get_jwt_identity()
        responseMessage = ""
        actionTaken = ""
        currentUser = UserCollection.find_one(
            {
                "email": identity["email"]
            })
        voteChange = 0
        questionID = uuid.UUID(info["question_id"])
        # No Votes at all
        if "votes" not in currentUser:
            if info["is_upvote"]:
                voteChange += 1
            else:
                voteChange -= 1
            actionTaken = "NewVote"
            UserCollection.update(
                {
                    "_id" : currentUser["_id"]
                },
                {
                    "$push": 
                    {
                        "votes": 
                        {
                            "post_id" : questionID,
                            "is_upvote": info["is_upvote"]
                        }
                    }
                })
        else:
            for vote in currentUser["votes"]:
                # Vote on this answer exist
                if vote["post_id"] == questionID:
                    # Cancel vote
                    if vote["is_upvote"] == info["is_upvote"]:
                        if info["is_upvote"]:
                            voteChange -= 1
                        else:
                            voteChange += 1
                        actionTaken = "CancelVote"
                        UserCollection.update(
                        {
                            "_id": currentUser["_id"]
                        },
                        {
                            "$pull" : 
                            {
                                "votes": 
                                {
                                    "post_id": questionID
                                }
                            }
                        })                    
                        break
                    # Change vote
                    else:
                        if info["is_upvote"]:
                            voteChange += 2
                        else:
                            voteChange -= 2                            
                        actionTaken = "ChangeVote"
                        UserCollection.update(
                        {
                            "_id": currentUser["_id"],
                            "votes.post_id": questionID
                        },
                        {
                            "$set": 
                            {
                                "votes.$.is_upvote": info["is_upvote"]
                            }
                        })
                        break
            # No vote on this answer
            if voteChange == 0:
                if info["is_upvote"]:
                    voteChange += 1
                else:
                    voteChange -= 1
                actionTaken = "NewVote"
                UserCollection.update(
                    {
                        "_id": currentUser["_id"]
                    },
                    {
                        "$push": 
                        {
                            "votes" : 
                            {
                                "post_id" : questionID,
                                "is_upvote": info["is_upvote"]
                            }
                        }
                    })
        # Now change vote count of answer
        QuestionCollection.update(
            {
                "_id": questionID
            },
            {
                "$inc": 
                {
                    "vote_count": voteChange
                }
            })
        # Add Notification to question owner
        questionOwnerId = QuestionCollection.find_one({"_id":questionID})["user_id"]

        UserCollection.update(
            {
                "_id": questionOwnerId
            },
            {
                "$push": 
                {
                    "notifications": 
                    {
                        "type": "VoteQuestion",
                        "questionID": questionID,
                        "vote_change": voteChange,
                        "viewed": False
                    }
                }
            }
        )

        if actionTaken == "NewVote":
            responseMessage = "Upvoted" if info["is_upvote"] else "Downvoted"
        elif actionTaken == "ChangeVote":
            responseMessage = "Changed vote to upvote" if info["is_upvote"] else "Changed vote to downvote"
        else:
            responseMessage = "Cancelled upvote" if info["is_upvote"] else "Cancelled downvote"
        return make_response(jsonify(
            {
                "message": responseMessage,
                "actionTaken": actionTaken,
                "is_upvote": info["is_upvote"]
            }), 200)


class Notifications(Resource):
    @staticmethod
    @jwt_required()
    def get():
        identity = get_jwt_identity()
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify(
                {
                    "message": "access_token not valid, User not found"
                }))
        else:
            # Get Notifications
            res = UserCollection.aggregate([
            {
                "$match": 
                {
                    "_id": currentUser["_id"],
                }
            },
            {
                "$unwind": "$notifications"
            },
            {
                "$match": 
                {
                    "notifications.viewed": False
                }
            },            
            {
                "$group": 
                {
                    "_id": 
                    {
                        "questionID": "$notifications.questionID",
                        "answerID": "$notifications.answerID",
                        "type": "$notifications.type"
                    },
                    "count": 
                    {
                        "$sum": 
                        {
                            "$cond": 
                            {
                                "if": 
                                {
                                    "$or":
                                    [{
                                        "$eq": 
                                        [
                                            "$notifications.type",
                                            "VoteQuestion"
                                        ]
                                    },{
                                        "$eq":
                                        [
                                            "$notifications.type",
                                            "VoteAnswer"
                                        ]
                                    }]
                                },
                                "then": "$notifications.vote_change",
                                "else": 1
                            }
                        }
                    }
                }
            },
            {
                "$project": 
                {
                    "_id": "$_id",
                    "count": "$count"
                }
            }])
            return make_response(jsonify(list(res)), 200)

    @staticmethod
    @jwt_required()
    def put():
        identity = get_jwt_identity()
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify(
                {
                    "message": "access_token not valid, User not found"
                }))
        else:
            info = UpdateNotificationInfo.parse_args()
            question_id = uuid.UUID(info["question_id"])
            print("question_id")
            print(question_id)
            answer_id = None
            answer_id_to_string = None
            try:
                answer_id = uuid.UUID(info["answer_id"])
            except Exception as e:
                pass
            if answer_id == None:
                print("1) answer_id")
                print(answer_id)
                print("type")
                print(info["type"])
                UserCollection.update_one(
                {
                    "_id": currentUser["_id"],
                    "notifications.type": info["type"],
                    "notifications.questionID": question_id
                },{
                    "$set":{
                        "notifications.$[elem].viewed": True
                    }
                }, 
                array_filters=[{
                        "elem.type": info["type"],
                        "elem.questionID": question_id
                    }])
            else:
                print("2) answer_id")
                print(answer_id)
                print("type")
                print(info["type"])
                UserCollection.update_one(
                {
                    "_id": currentUser["_id"],
                    "notifications.type": info["type"],
                    "notifications.questionID": question_id,
                    "notifications.answerID": answer_id
                },{
                    "$set":{
                        "notifications.$[elem].viewed": True
                    }
                },
                array_filters = [{
                    "elem.type": info["type"],
                    "elem.questionID": question_id,
                    "elem.answerID": answer_id
                }])
                answer_id_to_string = info["answer_id"]
                
                # PUT does not return message
                return make_response(jsonify({
                    "message": "Selected Notifications are viewed",
                    "question_id": info["question_id"],
                    "answer_id": answer_id_to_string
                    }),200)  

    @staticmethod
    @jwt_required()
    def delete():
        identity = get_jwt_identity()
        currentUser = UserCollection.find_one({"email": identity["email"]})
        if currentUser is None:
            return make_response(jsonify(
                {
                    "message": "access_token not valid, User not found"
                }))
        else:
            # Delete Notifications
            UserCollection.update(
            {
                "_id": currentUser["_id"]
            },
            {
                "$set": 
                {
                    "notifications": []
                }
            })
            return make_response(jsonify({"message": "Notifications Cleared"}), 200)

class DeclareBestAnswer(Resource):
    @staticmethod
    @jwt_required()
    def post():
        info = BestAnswerInfo.parse_args()
        identity = get_jwt_identity()
        responseMessage = ""
        currentUser = UserCollection.find_one(
            {
                "email": identity["email"]
            })
        questionID = uuid.UUID(info["question_id"])
        answerID = uuid.UUID(info["answer_id"])
        print(questionID)
        print(answerID)
        if currentUser is not None:
            bestAnswer = QuestionCollection.find_one(
                {
                    "_id": questionID,
                    "answers.is_best_answer": True
                })
            if bestAnswer is None:
                QuestionCollection.update(
                {
                    "_id" : questionID,
                    "answers._id": answerID
                },
                {
                    "$set":  
                    {
                        "answers.$.is_best_answer": True
                    }
                })
                responseMessage = "Best Answer Declared!"
                returnCode = 201
                agg = QuestionCollection.aggregate([
                    {
                        "$match":
                        {
                            "_id": questionID
                        }
                    },
                    {
                        "$unwind": "$answers"
                    },
                    {
                        "$match":
                        {
                            "answers._id": answerID
                        }
                    },
                    {
                        "$project":
                        {
                            "answerOwnerUserID": "$answers.user_id",
                            "_id": 0
                        }
                    }])
                aggList = list(agg)
                answerOwnerUserID = aggList[0]["answerOwnerUserID"]
                UserCollection.update(
                    {
                        "_id": answerOwnerUserID
                    },
                    {
                        "$push": 
                        {
                            "notifications": 
                            {
                                "type": "BestAnswer",
                                "questionID": questionID,
                                "viewed": False,
                                "answerID": answerID
                            }
                        }
                    }
                )
            else:
                responseMessage = "There's already another best answer for this question"
                returnCode = 200
        else:
            responseMessage = "You have to be logged in to do this"
            returnCode = 203
            
        result = {
            "message": responseMessage
        }
        return make_response(jsonify(result), returnCode)
          
class GetQuestion(Resource):
    @staticmethod
    def get():
        info = GetQuestionInfo.parse_args()
        question_id = uuid.UUID(info["question_id"])
        targetQuestion = QuestionCollection.find_one({"_id": question_id})
        if targetQuestion is not None:
            return make_response(jsonify(targetQuestion), 200)
        else:
            result = {
            "message": "No such question found!"
            }
            return make_response(jsonify(result), 200)
          
class TEST_ResetBestAnswer(Resource):
    @staticmethod
    @jwt_required()
    def post():
        info = TestResetAnswerInfo.parse_args()
        identity = get_jwt_identity()
        responseMessage = ""
        currentUser = UserCollection.find_one(
            {
                "email": identity["email"]
            })
        questionID = uuid.UUID(info["question_id"])
        answerID = uuid.UUID(info["answer_id"])
        if currentUser is not None:
                QuestionCollection.update(
                {
                    "_id" : questionID,
                    "answers._id": answerID
                },
                {
                    "$set":  
                    {
                        "answers.$.is_best_answer": False
                    }
                })
                responseMessage = "Best Answer Removed!"
                result = {
                    "message": responseMessage
                }
                return make_response(jsonify(result), 201)
        else:
            responseMessage = "You have to be logged in to do this"
            result = {
                "message": responseMessage
            }
            return make_response(jsonify(result), 203)

api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(PostAnswer, "/postanswer")
api.add_resource(QuestionList, '/questionlist')
api.add_resource(PostQuestion, '/postquestion')
api.add_resource(ListAnswers, '/listanswers')
api.add_resource(ListMyAnswers, '/listmyanswers')
api.add_resource(ListMyQuestions, "/listmyquestions")
api.add_resource(VoteQuestion, '/votequestion')
api.add_resource(VoteAnswer, '/voteanswer')
api.add_resource(Notifications, '/notifications')
api.add_resource(DeclareBestAnswer, '/declarebestanswer')
api.add_resource(TEST_ResetBestAnswer, '/test_resetbestanswer')
api.add_resource(GetQuestion, '/getquestion')


if __name__ == "__main__":
    app.debug = True
    app.run(host='localhost', port=5000)