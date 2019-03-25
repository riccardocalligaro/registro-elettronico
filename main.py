from flask import Flask, render_template, redirect, url_for, request, send_file
from api.login import Session
from api.login import AuthenticationFailedError
from datetime import datetime
import pandas as pd
import numpy as np
import time
import  requests
app = Flask(__name__)


# TODO: aggiungere hoover info profilo
# TODO: aggiungere estensione voti
    # TODO: voto minimo per avere 6

# TODO: risolvere bug data prossimi eventi
# TODO: possibilmente nel grafico tenere solo 2 cifre decimali
@app.route('/', methods=['GET', 'POST'])
def login():

    user_session = Session()
    error = None

    if request.method == 'POST':
        try:
            user_session.login(request.form['username'], request.form['password'])

            # prende tutti i dati necessari per la dashboard
            lessons = user_session.lessons()
            grades = user_session.grades()
            periods = user_session.periods()
            absences = user_session.absences()
            noticeboard = user_session.noticeboard()
            didactics = user_session.didactics()
            cards = user_session.cards()

            return render_template("dashboard.html",

            lessons=lessons,

            #eventi
            events=get_events(user_session),

            parse_event_date=parse_event_date,

            #grafici
            #media
            graph_media=graph_media(grades),

            # media durante i periodi (Q1: 7.50, Q2 = 8.00)
            media_periodi = get_medie_periods(periods, grades),

            # voti durante anno
            gradesData=graph_grades(grades),

            # ultimi voti
            grades=parse_grades(grades),

            # assenze per la dashboard, review
            absences_review = get_totale_assenze(absences),

            absences_data = get_months_absences(absences),

            log_out = log_out(),
            noticeboard_titles = get_noticeboard_titles(noticeboard),

            noticeboard_dates = get_noticeboard_dates(noticeboard),

            didactics = didactics,

            cards = cards['cards']
            )
        except AuthenticationFailedError as e:
            error = "Username o password errati"
            return render_template('login.html', error=error)

    return render_template('login.html', error=error)


#dashboard
@app.route("/dashboard")
def dashboard():
    return redirect(url_for('login'))



@app.route("/logout")
def log_out():
    return render_template('login.html')



# box prossimi eventi
# elaborazione data (2018-10-22) --> 22-10-2018
def parse_event_date(event_date):
    parts = event_date.split("-")
    return parts[2][:2] + "/" + parts[1]

#prende gli eventi dal giorno 'today' fino alla fine della scuola

def get_events(user_session):
    begin = datetime(2019,3,22)
    end = datetime(2019,6,9)
    return user_session.agenda(begin,end)




# ultimi 5 voti --> grades=parse_grades(grades)
def parse_grades(grades):
    # trasforma i voti in un dataframe
    df = pd.DataFrame.from_dict(grades['grades'])
    # converte la colonna evt date in time
    df['evtDate'] = pd.to_datetime(df['evtDate'], format='%Y-%m-%d')
    # ordina le varie date in ordine cronologico decrescente (utlimo --> primo)
    df = df.sort_values('evtId', ascending=False)
    # prende i primi 5 voti
    gradeslist = df.iloc[0:5].values.tolist()

    return gradeslist


# gradesData=graph_grades(grades) --> elabora dati per grafico dei voti durante l'anno
def graph_grades(grades):

    # ordina in base alla data (crescente)
    results = sorted(grades['grades'],key=lambda x : time.strptime(x['evtDate'],"%Y-%m-%d"))
    output=""
    # per ogni data prende i valori che non sono None e crea un output ( {x: 'data', y: 'voto'}) che andrá nel grafico
    for result in results:
        if str(result['decimalValue']) == 'None':
            pass
        else:
            output += "{ x: '" + result['evtDate'] + "', y: " + str(result['decimalValue']) +  "},"
    #toglie la virgola iniziale
    return output[:-1]

# graph_media=graph_media(grades) fa un grafico della media dei voti
def graph_media(grades):
    media = 0
    output=""
    # ordina in base alla data (crescente)
    results = sorted(grades['grades'],key=lambda x : time.strptime(x['evtDate'],"%Y-%m-%d"))
    i = 1
    for result in results:
        if str(result['decimalValue']) == 'None':
            pass
        else:
            # calcola la media in quel giorno
            media += result['decimalValue']
            output += "{ x: '" + result['evtDate'] + "', y: " + str(media/i) +  "},"
            i+=1
    return output


#    media_voti = get_media(grades), tipo list
def get_media(grades):
    media = 0
    div = 1
    for grade in grades['grades']:
        if str(grade['decimalValue']) == 'None' :
            pass
        else:
            media += grade['decimalValue']
            div += 1
    return media/div;
    # TODO: finire funzione media, sbagliata


def get_medie_periods(periods, grades):
    periods_medie = []
    periods_pos = []
    df = pd.DataFrame.from_dict(grades['grades'])
    for period in periods['periods']:
        periods_pos.append(period['periodPos'])

    output = ""
    for period in periods_pos:
    #    output +
        periods_medie.append(df['decimalValue'][df['periodPos'] == period].mean())
    return periods_medie

def get_totale_assenze(absences):

    df = pd.DataFrame.from_dict(absences['events'])

    assenze = df[df['evtCode'] == 'ABA0'].values.tolist()
    uscite = df[df['evtCode'] == 'ABU0'].values.tolist()
    ritardi = df[df['evtCode'] == 'ABR0'].values.tolist()
    ritardibrevi =df[df['evtCode'] == 'ABR1'].values.tolist()
    not_justified = df[df['isJustified'] == False].values.tolist()

    output = [len(assenze), len(uscite), len(ritardi), len(ritardibrevi), len(not_justified)]
    return output

def get_months_absences(absences):

    output = []

    assenze = [0,0,0,0,0,0,0,0,0,0,0,0]
    uscite = [0,0,0,0,0,0,0,0,0,0,0,0]
    ritardi = [0,0,0,0,0,0,0,0,0,0,0,0]

    for event in absences['events']:
        if event['evtCode'] == 'ABA0':
            assenze[int(event['evtDate'].split('-')[1])-1] += 1
        elif event['evtCode'] == 'ABU0':
            uscite[int(event['evtDate'].split('-')[1])-1] += 1
        else:
            ritardi[int(event['evtDate'].split('-')[1])-1] += 1

    output.append(assenze[-4:] + assenze[:6])
    output.append(uscite[-4:] + uscite[:6])
    output.append(ritardi[-4:] + ritardi[:6])

    return output

def get_noticeboard_titles(noticeboard):
    output = []
    url = 'https://web.spaggiari.eu/sif/app/default/bacheca_utente.php?action=file_download&com_id='

    for i in range(0, 5):
        if noticeboard['items'][i]['cntHasAttach'] == True:
            output.append([noticeboard['items'][i]['cntTitle'], elabora_data(noticeboard['items'][i]['pubDT']), url+str(noticeboard['items'][i]['cntId'])])
        else:
            output.append([noticeboard['items'][i]['cntTitle'], elabora_data(noticeboard['items'][i]['pubDT']), ''])

    return output

def get_noticeboard_dates(noticeboard):
    return 0
    #output = []
    #for i in range(0, 5):
    #    output.append(elabora_data(noticeboard['items'][i]['pubDT']))

def elabora_data(dt):
    '''
    input: 2019-03-21T15:11:18+01:00
    output: 21-03-2019
    '''
    parts = dt.split('-')

    return parts[2][:2] + "-" + parts[1] + "-" + parts[0]

# def get_didactics(didactics):
#     output = []
#
#     for materials in didactics['didacticts']
#         materials_content = []
#         for material in materials:
#             materials_content.append(material['folderName'], material['lastShareDT'])
#         output.append([materials['teacherName'].lower().capitalize(), materials_content])






if __name__ == "__main__":
    app.run(debug=True)
