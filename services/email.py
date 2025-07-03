import os
import dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

mail = Mail(app)