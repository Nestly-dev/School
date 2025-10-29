[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/VmFwbJXI)
[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/RdMJltzD)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=21219505)
# Guided Learning Activity

## Activity: Optimizing "Soko Yetu" with i18n and Redis

**Estimated Time:** 2 Hours  
**Project:** "Soko Yetu" Django Starter Code

## Overview

In our session, we saw how to cache a fully internationalized Django app. Now, it's your turn to build the entire pipeline from scratch.

You will start with the "Soko Yetu" project before i18n has been implemented. You will first correctly add internationalization (i18n) and localization (l10n) for English and Swahili.

Then, you will measure the "Double Bottleneck" (database + disk I/O) on your local machine.

Finally, you will install and configure a local Redis cache to solve this bottleneck and make your multilingual app blazing fast.

## Learning Objectives

By the end of this activity, you will be able to:

- Implement full i18n and l10n in a Django project (models, templates, and URLs).
- Generate, translate, and compile .po and .mo message files.
- Run a local Redis instance using Docker for development.
- Install and configure django-redis to connect Django to your Redis instance.
- Implement i18n-aware template fragment caching using `{% cache %}`.
- Measure and explain the performance difference between a cached and uncached request.

## Requirements

- The "Soko Yetu" starter project.
- A Python virtual environment (venv).
- A code editor (like VS Code).
- Docker Desktop installed and running. (This is the easiest way to run Redis locally).

## Part 1: Setup & Local Redis (30 Minutes)

### Get the Starter Code
Unzip the soko-yetu-starter project.

### Create Environment
Open a terminal in the project folder.

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate  # Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Redis Locally
Make sure Docker Desktop is open and running.

In your terminal, run this single command:

```bash
docker run -d -p 6379:6379 --name soko-redis redis:alpine
```

This command downloads a tiny Redis image, starts a container named soko-redis, and maps your computer's port 6379 to the container's port 6379. You can see it running in your Docker Desktop dashboard.

### Prepare Django
```bash
python manage.py migrate
python manage.py createsuperuser  # create an admin account
python manage.py runserver
```

### Verify
Open http://127.0.0.1:8000/. You should see the English-only "Soko Yetu" site. Open the admin at /admin/ and add 2-3 produce items (e.g., "Tomatoes", "Maize").

## Part 2: Full i18n Implementation (60 Minutes)

Now, let's fully internationalize the app.

### Configure settings.py

Open `myproject/settings.py`.

Import os.

Add LANGUAGES and LOCALE_PATHS:

```python
from django.utils.translation import gettext_lazy as _

# ...

LANGUAGES = [
    ('en', _('English')),
    ('sw', _('Swahili')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
```

Find the MIDDLEWARE list and add `django.middleware.locale.LocaleMiddleware` (after SessionMiddleware but before CommonMiddleware is a good place).

### Mark Model Strings

Open `farm/models.py`.

Import gettext_lazy: `from django.utils.translation import gettext_lazy as _`

Mark the fields as translatable by adding `_()`:

```python
class Produce(models.Model):
    name = models.CharField(_('name'), max_length=200)
    origin_village = models.CharField(_('origin_village'), max_length=200)
```

Since you changed a model field (by adding the verbose name), you need to make migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Mark Template Strings

Open `farm/templates/farm/base.html`.

Add `{% load i18n %}` at the top.

Change `<title>Soko Yetu</title>` to `<title>{% trans "Soko Yetu" %}</title>`.

Open `farm/templates/farm/produce_list.html`.

Add `{% load i18n %}` at the top (after `{% extends ... %}`).

Mark the strings:

```django
<h2>{% trans "Available Produce" %}</h2>
<p>{% trans "No produce is currently available." %}</p>
```

### Generate Translation Files

Create the locale directory: `mkdir locale`

Run makemessages for Swahili: `python manage.py makemessages -l sw`

### Translate!

Open the new file: `locale/sw/LC_MESSAGES/django.po`.

You will see the strings you marked. Fill in the `msgstr ""` fields with the Swahili translations.

Use these translations:

```po
#: farm/templates/farm/base.html:7
msgid "Soko Yetu"
msgstr "Soko Letu"

#: farm/templates/farm/produce_list.html:6
msgid "Available Produce"
msgstr "Mazao Yanayopatikana"

#: farm/templates/farm/produce_list.html:15
msgid "No produce is currently available."
msgstr "Hakuna mazao yanayopatikana kwa sasa."

#: farm/models.py:5
msgid "name"
msgstr "Jina"

#: farm/models.py:6
msgid "origin_village"
msgstr "Kijiji cha Asili"
```

Save the file.

### Compile Translations

Run: `python manage.py compilemessages`

This creates the .mo file that Django actually uses.

### Enable Language URLs

Open `myproject/urls.py`.

Import i18n_patterns: `from django.conf.urls.i18n import i18n_patterns`

Modify your urlpatterns to wrap the farm app in i18n_patterns. This will create the /en/ and /sw/ URL prefixes.

```python
# Keep admin outside of i18n_patterns
urlpatterns = [
    path('admin/', admin.site.urls),
]

# Add these new patterns
urlpatterns += i18n_patterns(
    path('', include('farm.urls')),
)
```

### Test Your i18n App

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/en/. You should see the English site.

Visit http://127.0.0.1:8000/sw/. You should see the Swahili site!

## Part 3: Baseline the "Double Bottleneck" (15 Minutes)

Before we fix it, let's see the problem.

Open your browser's Dev Tools (F12 or Ctrl+Shift+I).

Go to the Network tab.

Check the "Disable cache" box.

Load http://127.0.0.1:8000/sw/. Look at the Time for the main request. It might be 80ms, 150ms, or more. This is your "slow" baseline.

Refresh the page. The time will be roughly the same.

Load http://127.0.0.1:8000/en/. The time will also be slow.

You are now experiencing the "Double Bottleneck" from our session: For every request, Django is hitting the database (`Produce.objects.all()`) and the disk (to read the .mo file).

## Part 4: Implement Redis Caching (15 Minutes)

Let's fix it.

### Install django-redis

```bash
pip install django-redis
```

Add django-redis to your requirements.txt file.

### Configure CACHES

Open `myproject/settings.py`.

Scroll to the bottom and add the CACHES setting.

```python
# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # This points to your local Docker container
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### Implement Template Caching

Open `farm/templates/farm/produce_list.html`.

At the top, under `{% load i18n %}`, add `{% load cache %}`.

Wrap the entire produce list section in a `{% cache %}` tag. We'll set a 10-minute (600 seconds) cache.

```django
{% extends 'farm/base.html' %}
{% load i18n %}
{% load cache %}

{% block content %}

{% cache 600 produce_list_fragment request.LANGUAGE_CODE %}
  <h2 class="text-2xl font-semibold mb-4">{% trans "Available Produce" %}</h2>

  <div class... >
    {% for produce in produce_list %}
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-lg font-semibold">{{ produce.name }}</h3>
        <p class="text-gray-600">{{ produce.origin_village }}</p>
      </div>
    {% empty %}
      <p>{% trans "No produce is currently available." %}</p>
    {% endfor %}
  </div>
{% endcache %}

{% endblock %}
```

The key is `request.LANGUAGE_CODE`. This tells Django to create a separate cache for 'en' and 'sw'.

## Part 5: Verify & Reflect (15 Minutes)

### Test the Magic

Stop your server (Ctrl+C) and restart it (`python manage.py runserver`).

Go to http://127.0.0.1:8000/sw/. Keep your Network tab open (with "Disable cache" UNCHECKED).

Hard Refresh (Ctrl+Shift+R or Cmd+Shift+R). Note the time. This is the "slow" Cache Miss (~80ms).

Now, Normal Refresh (F5 or Cmd+R). Look at the time. It should be tiny (~5-10ms). This is the Cache Hit!

Switch to English: http://127.0.0.1:8000/en/. The first load will be a "Cache Miss" for English.

Refresh the English page. It will now be a "Cache Hit."

### See the "Stale Cache" Problem

Go to your admin: http://127.0.0.1:8000/admin/.

Add a new item: "Onions" from "Arusha".

Go back to the site (/en/ or /sw/) and refresh. The "Onions" are not there!

This is because Django is serving the fast, 10-minute-old cache. It doesn't know the database has changed.

### Reflection (Your "Deliverable")

Create a new text file named `reflection.txt` and answer the following:

**Q1:** Explain the "Double Bottleneck" problem in your own words. What two "slow" operations were we fixing?

**Q2:** What exactly did `request.LANGUAGE_CODE` do in the `{% cache ... %}` tag? What would happen if you left it out and a user switched from English to Swahili?

**Q3:** You just saw the "stale cache" problem (in Step 5.2). Based on our session, what is the solution to this? What Django feature would you use to automatically delete the cache when a Produce item is saved?

## Bonus Challenge (If you have time)

Read the Django documentation on cache invalidation with signals.

Try to implement it!

- Create a new file `farm/signals.py`.
- Import the Produce model, receiver, post_save, post_delete, and cache.
- Write a function (or two) decorated with `@receiver(post_save, sender=Produce)` and `@receiver(post_delete, sender=Produce)`.
- Inside this function, you need to delete the cache. But how do you get the key name? Read about `make_template_fragment_key` from `django.core.cache.utils`.
- Import and register your signals in `farm/apps.py`.
- Test it! Does adding "Onions" in the admin immediately clear the cache and show the new item on the site?
