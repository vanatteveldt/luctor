import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

from django.contrib.auth.models import User
import sys, csv, string, random, os
from mail import send_email

GMAIL_USER = "vanatteveldt@gmail.com"
GMAIL_PWD = os.environ['GMAIL_PASSWORD']

dict = {'Email': 'email', 'Achternaam': 'last_name', 'Voornaam': 'first_name'}

#new = {"tom" : "KA4L84B0",
#       "fred" : "6Z8LW1CF"}
new = {
    'jan': 'TTGVR2WC',
    'lammert': 'LCKGR1SF',
    'robbi': '13WII0H9',
#    'eveline': 'JDID0ULA',
#    'moos': 'Y8QZM3TC',
    'tineke': 'C2NN9ZGQ',
    'danielle': '76E61LCD',
    'brigitte': 'EMYEW5IQ',
    'ellen2': 'OSIO6W3K',
    'els': '3DM3KHT3',
    'isabel': '6ATXG8G3',
    'marijke': 'ZMKP05JY',
    'maurits': 'SAQYZDG9',
    'nanke': '9JNVMEFH',
    'aletta': 'PLPJKR65',
    'anna': '6QYALD75',
    'christoph': 'MNA9GBKE',
    'erik': 'C3DSW1JN',
    'jasper': 'XGB0952A',
    'jim': 'DR08OIIJ',
    'mart': 'AHJCL5ZQ',
    'eef': 'HBATS6US',
    'ger': '3DZHNJN3',
    'henriette': 'P3ZOW31F',
    'kirsti': '7SZD4YCW',
    'manous': 'D2W8329F',
    'mary': 'YK3JMUKG',
    'stefan': 'TKSYJDUR',
    'wieke': '501W021Q',
    }

MAIL_PRE = """Dag {aanhef},

Zoals je wellicht weet zijn we al een tijdje bezig met een website voor de kooklessen van Mieke. Volgens ons is de site is nu zo ver dat hij getest en gebruikt kan worden."""

MAIL_DETAILS = """
Gebruikersnaam: {un}  (let op: kleine letters)
Email: {u.email}
Voornaam: {u.first_name}
Achternaam: {u.last_name}
"""

MAIL_LOGIN = "\nJe kunt inloggen op: http://kookboot.com/login/ en dan ook direct je gegevens aanvullen/wijzigen.\n"

MAIL_POST = """
Op de kooksite kun je als het goed is van alle lessen waar je geweest bent de recepten doorzoeken en bekijken en foto's en opmerkingen toevoegen. Je kunt ook recepten delen met mensen van buiten de kookles door gewoon de link uit de adresbalk te kopieren. We hebben nu de lessen vanaf 2015 ingevoerd, hopelijk kunnen we de eerdere lessen snel toevoegen.

Mocht er iets niet werken, of mocht je ideeen hebben om de site te verbeteren, mail dan met wouter@vanatteveldt.com of (nog beter) maak direct een issue aan op https://github.com/vanatteveldt/luctor/issues.

Als je mee wilt helpen met het ontwikkelen van de site laat het dan ook even weten!

Veel kookplezier, mede namens Mieke, 

-- Wouter"""

MAIL_EXISTING = (MAIL_PRE + "\n\nHieronder staan de gegevens zoals we die nu van je hebben:\n" + MAIL_DETAILS + MAIL_LOGIN + "\nJe wachtwoord weet je als het goed is zelf. Mocht je deze vergeten zijn, dan kan je het laten resetten met de 'lost password' link op de inlogpagina. Als je emailadres hierboven niet klopt en je bent je wachtwoord vergeten, mail dan even naar wouter@vanatteveldt.com.\n" + MAIL_POST)

MAIL_NEW = (MAIL_PRE + "\n\nWe hebben de volgende account voor je gemaakt:\n" + MAIL_DETAILS + 
                 "Wachtwoord: {pwd}  (let op: hoofdletters)\n" + MAIL_LOGIN + MAIL_POST)

for row in csv.DictReader(sys.stdin):
    un = row['Username']
    try:
        u = User.objects.get(username = un)
        print("USER {u} EXISTS".format(**locals()))
        for nl, en in dict.items():
            v = row[nl].strip()
            if v and v != getattr(u, en):
                print(un, en, repr(v), " WAS ", repr(getattr(u, en)))
                setattr(u, en, v)
                u.save()
        aanhef = u.first_name.strip() or un
        
        mail = MAIL_EXISTING.format(**locals())
        if not u.email:
            print("MISSING {un}".format(**locals()))
            continue
        #print("SENDING MAIL TO {un} at {u.email}".format(**locals()))
        #send_email(GMAIL_USER, GMAIL_PWD, u.email, "De kooklessen van Mieke op kookboot.com", mail)
        
    except User.DoesNotExist:
        if not row['Email']:
            print("SKIPPING {un}, no email".format(**locals()))
            continue
        
        pwd = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        extra = {'first_name': row['Voornaam'], 'last_name': row['Achternaam']}
        extra = {k:v for (k,v) in extra.items() if v and v.strip()}
        u = User.objects.create_user(un, row['Email'], password=pwd, **extra)
        print("CREATED USER {un} WITH PWD {pwd}".format(**locals()))
        new[un] = pwd
              
for un, pwd in new.items():
    u = User.objects.get(username=un)
    if not u.email:
        print("DELETING USER {un}".format(**locals()))
        u.delete()
        continue
    aanhef = u.first_name.strip() or un
    mail = MAIL_NEW.format(**locals())
    print("SENDING MAIL TO {un} at {u.email}".format(**locals()))
    send_email(GMAIL_USER, GMAIL_PWD, u.email, "De kooklessen van Mieke op kookboot.com", mail)
    #print(mail)
#{'Achternaam': 'Olthuis', 'Aantal_lessen': '35', 'Opmerkingen': '', 'Account bestaat?': 'Ja', 'Email': '', 'Username': 'kees', 'Voornaam': 'Kees'}
