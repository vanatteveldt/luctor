Kooklessen
===

Installation
---

```{sh}
git clone https://github.com/vanatteveldt/luctor
cd luctor
virtualenv --python=python3 env
. env/bin/activate
pip install -r requirements.txt
python manage.py
```

Setting up the data(base)
---

If you have a database already, simply unpack it into the `/data` folder and you're done

If not, you will need to create the initial database, load in the files, and reindex:

```{sh}
python manage.py migrate
python 0_addfiles.py /link/to/folder
python 1_rawtext.py
python 2_title.py
python manage.py rebuild_index
```

You probably also need to create a first superuser:

```{sh}
python manage.py createsuperuser
```

Running the server
---

```{sh}
python manage.py runserver
```
