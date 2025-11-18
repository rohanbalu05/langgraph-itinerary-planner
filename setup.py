"""
Setup script for LangGraph Travel Itinerary Planner
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='langgraph-trip-planner',
    version='0.2.0',
    description='AI Travel Itinerary Planner with Conversational Editing',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='LangGraph Travel Team',
    author_email='contact@example.com',
    url='https://github.com/rohanbalu05/langgraph-itinerary-planner',
    license='MIT',

    # Package discovery
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),

    # Include non-Python files
    include_package_data=True,
    package_data={
        '': ['*.yml', '*.yaml', '*.txt', '*.md'],
        'nlp_service': ['*.yml', '*.yaml'],
    },

    # Python version requirement
    python_requires='>=3.12,<4.0',

    # Dependencies
    install_requires=read_requirements('requirements.txt'),

    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=8.3.0',
            'pytest-cov>=6.0.0',
            'black>=24.0.0',
            'flake8>=7.0.0',
            'mypy>=1.13.0',
        ],
        'minimal': read_requirements('requirements-minimal.txt'),
    },

    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'itinerary-planner=run:main',
            'itinerary-demo=demo_chat_workflow:main',
        ],
    },

    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],

    # Keywords
    keywords='travel itinerary ai langgraph llm nlp chatbot planning',

    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/rohanbalu05/langgraph-itinerary-planner/issues',
        'Source': 'https://github.com/rohanbalu05/langgraph-itinerary-planner',
        'Documentation': 'https://github.com/rohanbalu05/langgraph-itinerary-planner/blob/main/README.md',
    },
)
