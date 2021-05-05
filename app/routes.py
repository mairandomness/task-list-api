from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def list_all_tasks():
    """
    Returns a 200 response with a list of all tasks currently
    in the database as the response body
    """
    tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.task_view())
    return jsonify(tasks_response)


@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def post_task():
    """
    Returns a 201 response with a confirmation message as its body in case of
    a successful post

    If any of the expected field is missing in the post request body, it returns
    a 400 response indicating invalid data
    """
    request_body = request.get_json()

    if ("completed_at" not in request_body
        or "description" not in request_body
            or "completed_at" not in request_body
            or "title" not in request_body):
        return make_response({"details": "Invalid data"}, 400)

    task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"])

    db.session.add(task)
    db.session.commit()

    return make_response(jsonify({"task": task.task_view()}), 201)


@tasks_bp.route("/<int:task_id>", methods=["GET", "DELETE", "PUT"], strict_slashes=False)
def handle_task_by_id(task_id):
    """
    GET: Returns a response with the task with given id as body and a 200 code
    when the task is found
    PUT: tries to update the task and returns a response with the updated task 
    and a 200 code
    DELETE: tries to delete the task and returns a 200 response with a success 
    message
    Returns a 404 with no response body in case the task is not found
    """
    task = Task.query.get(task_id)
    if task:
        task_response = {"task": task.task_view()}
        if request.method == "GET":
            return jsonify(task_response)
        elif request.method == "DELETE":
            return delete_task(task)
        elif request.method == "PUT":
            return update_task(task)
    return make_response(jsonify(None), 404)


def delete_task(task):
    """
    Helper function that performs the delete action and returns a 200 response
    with a confirmation message
    """
    db.session.delete(task)
    db.session.commit()
    return make_response(jsonify({"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}), 200)


def update_task(task):
    """
    Helper function that performs the update action and returns a 200 response
    with the newly updated task
    """
    request_body = request.get_json()

    if ("completed_at" not in request_body
        or "description" not in request_body
            or "completed_at" not in request_body
            or "title" not in request_body):
        return make_response({"details": "Invalid data"}, 400)

    task.title = request_body["title"]
    task.description = request_body["description"]
    task.completed_at = request_body["completed_at"]
    db.session.commit()
    return make_response(jsonify({"task": task.task_view()}), 200)
