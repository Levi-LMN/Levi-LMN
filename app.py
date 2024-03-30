from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'huqweitfiqv676%^$ ^%E% E@F#EIJ%REIQ&^REC I&'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Project(db.Model):
    __tablename__ = 'projects'

    ProjectID = db.Column(db.Integer, primary_key=True)
    ProjectName = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    LanguagesUsed = db.Column(db.String(255), nullable=False)
    GitHubLink = db.Column(db.String(255))
    PreviewLink = db.Column(db.String(255))
    Category = db.Column(db.String(100))

    def __repr__(self):
        return f"<Project {self.ProjectID}: {self.ProjectName}>"


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        # Get form data
        project_name = request.form['project_name']
        description = request.form['description']
        languages_used = ', '.join(request.form.getlist('languages_used'))  # Retrieve selected languages as a list
        github_link = request.form['github_link']
        preview_link = request.form['preview_link']
        category = request.form['category']

        # Create a new project instance
        new_project = Project(
            ProjectName=project_name,
            Description=description,
            LanguagesUsed=languages_used,
            GitHubLink=github_link,
            PreviewLink=preview_link,
            Category=category
        )

        try:
            # Add the new project to the database
            db.session.add(new_project)
            db.session.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('add_project'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding project: {str(e)}', 'danger')

    return render_template('add.html')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/projects', methods=['GET'])
def projects():
    # Fetch all distinct categories from the database
    categories = db.session.query(Project.Category.distinct()).all()
    # Fetch all projects grouped by category
    projects_by_category = {category[0]: Project.query.filter_by(Category=category[0]).all() for category in categories}
    return render_template('home.html', projects_by_category=projects_by_category)


@app.route('/work', methods=['GET'])
def work():
    return render_template('work.html')


@app.route('/all_projects', methods=['GET'])
def all_projects():
    all_projects = Project.query.all()
    return render_template('all_projects.html', all_projects=all_projects)


@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        # Update project details
        project.ProjectName = request.form['project_name']
        project.Description = request.form['description']
        project.LanguagesUsed = ', '.join(request.form.getlist('languages_used'))
        project.GitHubLink = request.form['github_link']
        project.PreviewLink = request.form['preview_link']
        project.Category = request.form['category']

        try:
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('all_projects'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'danger')

    return jsonify({
        'ProjectID': project.ProjectID,
        'ProjectName': project.ProjectName,
        'Description': project.Description,
        'LanguagesUsed': project.LanguagesUsed.split(', '),
        'GitHubLink': project.GitHubLink,
        'PreviewLink': project.PreviewLink,
        'Category': project.Category
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
