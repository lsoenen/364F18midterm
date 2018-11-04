###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
import json, requests
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField# Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
## App setup code
app = Flask(__name__)
## All app.config values
app.config['SECRET_KEY'] = 'this string will not be guessed'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/lsoenenMidterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)
######################################
######## HELPER FXNS (If any) ########
######################################
api_key = "m4zcqjsjr8e28jhhadwpcdvk"



##################
##### MODELS #####
##################

class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    position = db.Column(db.String)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))


class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key = True)
    school_name = db.Column(db.String)
    school_mascot = db.Column(db.String)
    players = db.relationship('Player', backref='Player')



###################
###### FORMS ######
###################

class TeamRosterForm(FlaskForm):
    school_name = StringField('Enter the name of the school you would like to see a roster for:', validators=[Required()])
    submit = SubmitField('Submit')

class MascotForm(FlaskForm):
    school_mascot = StringField('Enter the mascot to see a list of all schools with that mascot:', validators=[Required()])
    submit = SubmitField('Submit')


#######################
###### VIEW FXNS ######
#######################


@app.route('/teamrosterform')
def teamrosterform():
    form = TeamRosterForm()
    return render_template('teamrosterform.html', form=form)

@app.route('/teamrosterinfo', methods=['GET','POST'])
def teamrosterinfo():
    form = TeamRosterForm()
    school_name = form.school_name.data
    base_url = "http://api.sportradar.us/ncaafb-t1/teams/" + str(school_name) + "/roster.json?api_key=" + api_key
    response = requests.get(base_url)
    text = response.text
    python_obj = json.loads(text)
    objects = python_obj

    # return render_template('teamrosterinfo.html', objects=objects)
    team = db.session.query(Team).filter_by(school_name=school_name).first()
    if team:
        pass
    else:
        team = Team(school_name=objects['id'], school_mascot=objects['name'])
        db.session.add(team)
        db.session.commit()

        for p in objects['players']:
            player_first = p['name_first']
            player_last = p['name_last']
            player_position = p['position']
            player = Player(first_name=player_first, last_name=player_last, position=player_position, team_id=team.id)
            db.session.add(player)
            db.session.commit()




## Code to run the application...

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
