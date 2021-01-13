# Trivia API Project
This API is created as part of the Trivia game, one of Udacity's Full-stack nanodegree projects.
This API provides the following:
- getting all available questions either general or based on a selected category, including the answer, category, and difficulty
- adding questions
- deleting questions
- searching questions
- getting random question either general or based on a selected category, where it can be used for a quiz game
### Getting Started
Installing dependencies:

```bash
pip install -r requirements.txt
```
### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```
### Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Reference
Base URL: The API is hosted locally, and it's base address is http://localhost:3000

Authentication: no authentication required

API Keys: no API keys required 

### Error handling
The API will return one of the following errors if a request fails:

- 400 – bad request
- 404 – result not found
- 422 – un-processable

in case of failure, error response will be returned as JSON in the following format:
```
{
    "success": False,
    "error": 400,
    "message": "bad request"
}
```
### Endpoints
#### GET /categories
This endpoint returns the id and type of all available categories in the database.
The response is returned as JSON object.
sample request ```curl http://localhost:3000/categories```

#### GET /questions
This endpoint returns all available categories and questions in the database.
The response is returned as JSON object.
sample request ```curl http://localhost:3000/questions```

#### GET /categories/< int:category_id>/questions
This endpoint returns all available categories and questions in the database.
The response is returned as JSON object.
sample request ```curl http://localhost:3000/questions/4/questions```

#### DELETE /questions/< int:question_id>
This endpoint fulfills the deletion of a question from database based on question id.
The response is returned as JSON object.
sample request ```curl -X DELETE http://localhost:3000/questions/12```

#### POST /questions
This endpoint fulfills the deletion of a question from database based on question id.
The response is returned as JSON object.
sample request ```curl -X POST http://localhost:3000/questions -d '{"question": "What nanodegree is this?", "answer": "FSND", "category": 2, "difficulty": 2}' -H "Content-Type: application/json"```

#### POST /questions/search
This endpoint search for question based on search term. 
The response is returned as JSON object.
sample request ```curl -X POST http://localhost:3000/questions/search -d '{"searchTerm": "what"}' -H "Content-Type: application/json"```

#### POST /quizzes
This endpoint returns one random question either general or based on a specific category.
The response is returned as JSON object.
sample request ```curl -X POST http://localhost:3000/quizzes -d '{"quiz_category": {"id": 2}, "previous_questions": [3, 8]}' -H "Content-Type: application/json"```
