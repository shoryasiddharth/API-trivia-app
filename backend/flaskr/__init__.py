import os
from sre_parse import CATEGORIES
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    The after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization, true")

        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")

        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

    """
    An endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_all_categories():
        try:
            categories = Category.query.all()
            formatted_category = {}
            for category in categories:
                formatted_category[category.id] = category.type

            return jsonify({
                'categories': formatted_category
            })
        except Exception as e:
            print(e)
            abort(400)

    """
    An endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_all_questions():
        try:
            page = request.args.get("page", 1, type=int)
            start = (page-1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            questions = Question.query.order_by(Question.id).all()
            len_questions = len(questions)
            categories = Category.query.all()
            formatted_category = {}
            for category in categories:
                formatted_category[category.id] = category.type
            # formatted_category = [a.format() for a in categories]

            page_questions = questions[start:end]
            if (len(page_questions) == 0):
                abort(404)
            formatted_page_question = [a.format() for a in page_questions]

            return jsonify({
                'success': True,
                'questions': formatted_page_question,
                'total_questions': len_questions,
                'categories': formatted_category
            })
        except Exception as e:
            print(e)
            abort(400)

    """
    An endpoint to DELETE question using a question ID
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:

            question = Question.query.filter_by(id=question_id).one_or_none()
            if (question):

                question.delete()

                return jsonify({
                    'success': True,
                })
            else:
                abort(404)
        except Exception as e:
            print(e)
            abort(404)

    """
    An endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def post_new_questions():
        body = request.get_json()

        question_new = body.get('question')
        answer_new = body.get('answer')
        difficulty_new = body.get('difficulty')
        category_new = body.get('category')

        try:
            post_row_question = Question(
                question=question_new, answer=answer_new, category=category_new, difficulty=difficulty_new)
            post_row_question.insert()
            return jsonify({
                'success': True,
                'question': question_new
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    A POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/search-questions', methods=['POST'])
    def get_ques_by_searchTerm():
        try:
            body = request.get_json()

            searchTerm = body.get('searchTerm')

            questions = Question.query.filter(
                Question.question.ilike('%'+searchTerm+'%')).all()
            if questions:
                formatted_page_question = [a.format()
                                           for a in questions]
                return jsonify({
                    'success': True,
                    'questions': formatted_page_question,
                    'total_questions': len(formatted_page_question)
                })
            else:
                abort(404)

        except Exception as e:
            print(e)
            abort(400)

    """
    A GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_ques_by_categories(id):
        try:
            category = Category.query.filter_by(id=id).one_or_none()
            if category:
                # retrive all questions in a category
                questions_in_Category = Question.query.filter_by(
                    category=str(id)).all()
                formatted_page_question = [a.format()
                                           for a in questions_in_Category]

                return jsonify({
                    'success': True,
                    'questions': formatted_page_question,
                    'total_questions': len(formatted_page_question),
                    'current_category': category.type
                })
            else:
                abort(404)
        except Exception as e:
            print(e)
            abort(404)
    """
    A POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json()
        quizCategory = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')
        try:
            if (quizCategory['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quizCategory['id']).all()
            randomIndex = random.randint(0, len(questionsQuery)-1)
            nextQuestion = questionsQuery[randomIndex]
            while nextQuestion.id not in previousQuestion:
                nextQuestion = questionsQuery[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.category,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                    'previousQuestion': previousQuestion
                })

        except Exception as e:
            print(e)
            abort(404)

    """
    Error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_recource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable recource"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    return app
