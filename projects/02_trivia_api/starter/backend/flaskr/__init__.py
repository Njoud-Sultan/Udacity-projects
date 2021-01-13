import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10
CATEGORIES = [1, 2, 3, 4, 5, 6]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={'/': {'origins': '*'}})

    '''
      @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
      '''
    '''
      @TODO: Use the after_request decorator to set Access-Control-Allow
      '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    '''
      @TODO: 
      Create an endpoint to handle GET requests 
      for all available categories.
      '''

    # endpoint to return all existing categories
    @app.route('/categories')
    def get_categories():
        all_categories = Category.query.all()
        categories = {category.id: category.type for category in all_categories}
        return jsonify({
            'success': True,
            'categories': categories
        })

    '''
      @TODO: 
      Create an endpoint to handle GET requests for questions, 
      including pagination (every 10 questions). 
      This endpoint should return a list of questions, 
      number of total questions, current category, categories. 
      '''

    # endpoint to return 10 questions per page
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # get page number
        page = request.args.get('page', 1, type=int)
        questions = Question.query.all()
        all_categories = Category.query.all()

        formatted_questions = [question.format() for question in questions]
        categories = {category.id: category.type for category in all_categories}

        # set start and end to display 10 question per page
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'total_questions': len(questions),
            'categories': categories,
            'current_category': None
        })

    '''
      TEST: At this point, when you start the application
      you should see questions and categories generated,
      ten questions per page and pagination at the bottom of the screen for three pages.
      Clicking on the page numbers should update the questions. 
      '''

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    '''

    # endpoint to delete a question
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # query question based on the id passed
        question = Question.query.get(question_id)

        # if no question based on the passed id then abort
        if question is None:
            abort(422)

        db.session.delete(question)
        db.session.commit()
        return jsonify({
            'success': True
        })

    '''
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    '''

    # endpoint to add a new question to the the database
    @app.route('/questions', methods=['POST'])
    def add_questions():
        form = request.get_json()
        # get the submitted question form
        question = form.get('question')
        answer = form.get('answer')
        # check if there is empty values then abort
        if question == '' or answer == '':
            abort(400)

        # insert new question to the database
        question = Question(question=form.get('question'),
                            answer=form.get('answer'),
                            difficulty=form.get('difficulty'),
                            category=form.get('category'))
        db.session.add(question)
        db.session.commit()
        return jsonify({
            'success': True
        })

    '''
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    '''

    # endpoint to search for questions based on a search term
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        form = request.get_json()
        # get the search term
        search_term = form.get('searchTerm')
        if search_term == '':
            abort(400)
        # query question based on the search term
        match_questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

        if not match_questions:
            abort(404)

        questions = [question.format() for question in match_questions]

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(match_questions),
            'current_category': None
        })

    '''
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    @app.route('/')
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    # endpoint to return questions based on category
    @app.route('/categories/<int:category_id>/questions')
    def get_by_category(category_id):
        # get page number
        page = request.args.get('page', 1, type=int)
        # handle invalid category id
        if category_id not in CATEGORIES:
            abort(400)

        questions = Question.query.filter_by(category=category_id).all()
        # if no question returned based on the category, abort
        if not questions:
            abort(404)

        formatted_questions = [question.format() for question in questions]
        # set start and end to display 10 question per page
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'total_questions': len(questions),
            'current_category': category_id
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    # endpoint to return random question based on all or specific category for quiz game
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        data = request.get_json()
        # check if needed data is missing then abort
        if 'quiz_category' not in data or 'previous_questions' not in data:
            abort(400)

        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')
        # query questions based on category, and not already returned
        if quiz_category['id'] == 0:
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']) \
                .filter(Question.id.notin_(previous_questions)).all()

        # select one random question of the list of questions
        if questions:
            question = random.choice(questions)
            question = question.format()
        else:
            question = None

        print(question)
        return jsonify({
            'success': True,
            'question': question
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "results not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "un-processable"
        }), 422

    return app
