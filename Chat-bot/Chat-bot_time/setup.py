from setuptools import setup

setup(
    name="chatbot_time",
    version="0.1",
    py_modules=["local_bot"],
    install_requires=[
        "langgraph>=0.0.5",
        "langchain-community>=0.0.11",
        "ollama>=0.1.2"
    ],
    entry_points={
        'console_scripts': [
            'chatbot-time=local_bot:main',  # Связываем команду
        ],
    },
)